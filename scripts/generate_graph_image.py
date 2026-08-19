import sys
from pathlib import Path

# Ensure project root is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent
from src.graph_router import llm, _make_tools
from src.prompts import AGENT_SYSTEM_PROMPT


def main():
    assets_dir = ROOT_DIR / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    output_path = assets_dir / "langgraph_agent.png"

    print("📊 Compiling LangGraph ReAct Agent...")
    agent = create_react_agent(
        model=llm,
        tools=_make_tools("public"),
        prompt=SystemMessage(AGENT_SYSTEM_PROMPT.format(role="public")),
    )

    print("🖼️ Rendering and downloading Mermaid diagram...")
    graph = agent.get_graph()
    png_bytes = graph.draw_mermaid_png()

    output_path.write_bytes(png_bytes)
    print(f"✅ Success! LangGraph diagram saved to: {output_path}")


if __name__ == "__main__":
    main()
