import os
from dotenv import load_dotenv
from langchain_core.tracers import LangChainTracer

load_dotenv()


def get_langsmith_callback():
    # Return LangChain tracer callback if LangSmith API key is configured
    if os.getenv("LANGSMITH_API_KEY"):
        return LangChainTracer(project_name=os.getenv("LANGSMITH_PROJECT", "univ-rbac-rag"))
    return None