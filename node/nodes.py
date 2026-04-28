import logging

from ai_agentic_designer.agents.code_agent import generate_code
from ai_agentic_designer.agents.planner_agent import planner
from ai_agentic_designer.agents.state import AgentState


logger = logging.getLogger(__name__)


def planner_node(state: AgentState):
    try:
        print("[agent] planner: started", flush=True)
        result = planner(state["prompt"])
        page_count = len(result.get("pages", {}).get("pages", []))
        print(f"[agent] planner: completed ({page_count} pages)", flush=True)
        logger.info("Planner node completed")
        return {
            "plan": result["plan"],
            "design": result["design"],
            "pages": result["pages"],
            "ui": result["ui"],
            "current_agent": "planner",
        }
    except Exception as exc:
        logger.exception("Planner node failed")
        errors = list(state.get("errors", []))
        errors.append(f"planner: {exc}")
        raise RuntimeError(f"Planner node failed: {exc}") from exc


def code_node(state: AgentState):
    try:
        page_count = len(state.get("pages", {}).get("pages", []))
        print(f"[agent] code: started ({page_count} pages)", flush=True)
        result = generate_code(state=state)
        file_count = len(result.get("files", {}))
        print(f"[agent] code: completed ({file_count} files)", flush=True)
        logger.info("Code node completed")
        return {
            "files": result["files"],
            "current_agent": "code",
        }
    except Exception as exc:
        logger.exception("Code node failed")
        errors = list(state.get("errors", []))
        errors.append(f"code: {exc}")
        raise RuntimeError(f"Code node failed: {exc}") from exc
