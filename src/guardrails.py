import re

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

from src.config import GROQ_API_KEY, GROQ_MODEL
from src.prompts import GUARDRAIL_EVAL_PROMPT


class GuardrailException(ValueError):
    pass


# ---------------------------------------------------------------------------
# Guardrail 1 — Prompt Injection & Length Guard (Instant regex, 0ms)
# ---------------------------------------------------------------------------
_INJECTION_PATTERNS = re.compile(
    r"(ignore (all |previous |above |your )?(instructions?|rules?|prompt|context))"
    r"|(forget (everything|your role|you are|all))"
    r"|(act as|pretend (you are|to be)|you are now|you must)"
    r"|(jailbreak|dan mode|developer mode|override)",
    re.IGNORECASE,
)


def check_prompt_injection(question: str) -> None:
    if len(question) > 500:
        raise GuardrailException("Query exceeds 500 characters limit.")
    if _INJECTION_PATTERNS.search(question):
        raise GuardrailException("Prompt injection detected. Request blocked.")


# ---------------------------------------------------------------------------
# Guardrail 2 — Dynamic LLM Safety, Toxicity & Domain Guard (1 fast call)
# ---------------------------------------------------------------------------
_llm = ChatGroq(
    model=GROQ_MODEL,
    groq_api_key=GROQ_API_KEY,
    temperature=0,
    reasoning_effort="none",
    max_retries=2,
)

_guardrail_eval_prompt = ChatPromptTemplate.from_template(GUARDRAIL_EVAL_PROMPT)


def check_safety_and_relevance(question: str) -> None:
    chain = _guardrail_eval_prompt | _llm | StrOutputParser()
    verdict = chain.invoke({"question": question}).strip()
    if not verdict.upper().startswith("ALLOWED"):
        reason = verdict.split("BLOCKED:", 1)[-1].strip() if "BLOCKED:" in verdict else (
            "Off-topic or unsupported query."
        )
        raise GuardrailException(reason)


# ---------------------------------------------------------------------------
# Guardrail 3 — Output Hallucination Guard (post-generation, non-blocking)
# ---------------------------------------------------------------------------
_NO_INFO_SIGNALS = (
    "i don't have", "i do not have", "i cannot find",
    "no information", "not available", "not found",
    "i'm unable", "i am unable", "cannot answer",
)


def check_output_quality(answer: str, docs: list) -> dict:
    answer_lower = answer.lower()
    no_docs = len(docs) == 0
    no_info = any(signal in answer_lower for signal in _NO_INFO_SIGNALS)
    if no_docs or no_info:
        return {
            "low_confidence": True,
            "reason": "No supporting documents found in knowledge base.",
        }
    return {"low_confidence": False, "reason": None}


def run_input_guardrails(question: str) -> None:
    check_prompt_injection(question)
    check_safety_and_relevance(question)
