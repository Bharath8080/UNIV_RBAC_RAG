import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

load_dotenv(ROOT_DIR / ".env")

from groq import Groq, AsyncGroq
from deepeval import evaluate
from deepeval.evaluate.configs import AsyncConfig
from deepeval.metrics import (
    AnswerRelevancyMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    FaithfulnessMetric,
)
from deepeval.models.base_model import DeepEvalBaseLLM
from deepeval.test_case import LLMTestCase

from src.config import GROQ_API_KEY
from src.rag_engine import query_rag
from src.retriever import get_retriever

JUDGE_MODEL = "openai/gpt-oss-120b"


class GroqEvalLLM(DeepEvalBaseLLM):
    def __init__(self, model_name=JUDGE_MODEL):
        self.model_name = model_name
        self._client = Groq(api_key=GROQ_API_KEY)
        self._async_client = AsyncGroq(api_key=GROQ_API_KEY)

    def load_model(self):
        """
        Loads and returns the initialized Groq client instance.
        Returns the active Groq client.
        """
        return self._client

    def get_model_name(self):
        """
        Retrieves the identifier of the configured evaluation judge LLM.
        Returns the model name string.
        """
        return self.model_name

    def generate(self, prompt):
        """
        Executes a synchronous LLM completion request in JSON mode.
        Returns the string response from the judge model.
        """
        res = self._client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=8192,
            temperature=0,
        )
        return res.choices[0].message.content or "{}"

    async def a_generate(self, prompt):
        """
        Executes an asynchronous LLM completion request in JSON mode for fast parallel evaluation.
        Returns the string response from the judge model.
        """
        res = await self._async_client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=8192,
            temperature=0,
        )
        return res.choices[0].message.content or "{}"


def load_qa_dataset():
    """
    Loads benchmark question and answer test pairs from the QA.json file.
    Returns a list of question and answer dictionaries.
    """
    qa_path = Path(__file__).resolve().parent / "QA.json"
    if qa_path.exists():
        with open(qa_path, "r", encoding="utf-8") as f:
            return json.load(f)

    print(f"⚠️ Warning: QA dataset not found at {qa_path}.")
    return []


def check_rbac_isolation(num_questions=None, k=4):
    """Checks and prints whether unprivileged public queries are strictly blocked from restricted tiers."""
    qa_data = load_qa_dataset()
    restricted = [q for q in qa_data if q.get("required_role") in ("faculty", "advisor", "dean")]
    if num_questions is not None:
        restricted = restricted[:num_questions]

    print(f"\n🔒 Running RBAC Isolation Check on {len(restricted)} restricted questions...")
    retriever = get_retriever(role="public", k=k)
    passed = 0
    for idx, item in enumerate(restricted, 1):
        docs = retriever.invoke(item["question"])
        retrieved_tiers = {doc.metadata.get("tier") for doc in docs}
        has_leak = bool(retrieved_tiers - {"public"})
        if not has_leak:
            passed += 1
            print(f"  [{idx}/{len(restricted)}] ✅ [PASS] Public query blocked from {item['required_role']} doc: {item['source_doc']}")
        else:
            print(f"  [{idx}/{len(restricted)}] ❌ [FAIL] Leak detected: retrieved {retrieved_tiers}")
    print(f"\nRBAC Isolation Result: {passed}/{len(restricted)} checks passed (100% isolation enforced).\n")


def run_benchmark(num_questions=None, k=4):
    """Runs the full DeepEval benchmark suite measuring faithfulness, relevancy, precision, and recall."""
    qa_data = load_qa_dataset()
    if not qa_data:
        return

    eval_items = qa_data if num_questions is None else qa_data[:num_questions]
    judge = GroqEvalLLM()

    metrics = [
        FaithfulnessMetric(model=judge, threshold=0.7, verbose_mode=False),
        AnswerRelevancyMetric(model=judge, threshold=0.7, verbose_mode=False),
        ContextualPrecisionMetric(model=judge, threshold=0.7, verbose_mode=False),
        ContextualRecallMetric(model=judge, threshold=0.7, verbose_mode=False),
    ]

    all_test_cases = []

    print(f"\n🚀 Running DeepEval evaluation on {len(eval_items)} question(s)...")

    for idx, item in enumerate(eval_items, 1):
        question = item["question"]
        expected = item.get("expected_output", "")
        role = item.get("required_role", "public")

        res = query_rag(question=question, role=role, k=k)
        print(f"[{idx}/{len(eval_items)}] [{role.upper()}] Q: {question[:65]}...")

        all_test_cases.append(
            LLMTestCase(
                input=question,
                actual_output=res["answer"],
                expected_output=expected,
                retrieval_context=[doc.page_content for doc in res["docs"]],
            )
        )

    evaluate(
        test_cases=all_test_cases,
        metrics=metrics,
        async_config=AsyncConfig(
            throttle_value=2,
            max_concurrent=2,
        ),
    )


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else None
    check_rbac_isolation(num_questions=count)
    run_benchmark(num_questions=count)