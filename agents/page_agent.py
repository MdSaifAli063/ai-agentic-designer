from pydantic import BaseModel, ValidationError

from ai_agentic_designer.agents.planner_agent import PlannedPage


def _dump_model(model: BaseModel) -> dict:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


def generate_pages(prompt: str, plan: dict) -> dict:
    raw_pages = plan.get("pages", [])

    if isinstance(raw_pages, dict):
        raw_pages = raw_pages.get("pages", [])

    try:
        validated_pages = [PlannedPage(**page) for page in raw_pages]
    except ValidationError as exc:
        raise ValueError(f"Page validation failed: {exc}") from exc

    return {
        "pages": [
            {
                "name": page.name,
                "route": page.route,
                "type": page.type,
                "goal": page.goal,
                "sections": page.sections,
            }
            for page in validated_pages
        ]
    }
