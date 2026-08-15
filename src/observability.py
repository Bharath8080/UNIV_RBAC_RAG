import os
from dotenv import load_dotenv

load_dotenv()

LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY", "")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "univ-rbac-rag")
LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")


def setup_langsmith() -> None:
    if not LANGSMITH_API_KEY:
        return
    os.environ["LANGSMITH_TRACING"]  = "true"
    os.environ["LANGSMITH_API_KEY"]  = LANGSMITH_API_KEY
    os.environ["LANGSMITH_PROJECT"]  = LANGSMITH_PROJECT
    os.environ["LANGSMITH_ENDPOINT"] = LANGSMITH_ENDPOINT


def get_langsmith_callback():
    if not LANGSMITH_API_KEY:
        return None
    from langchain_core.tracers import LangChainTracer
    return LangChainTracer(project_name=LANGSMITH_PROJECT)
