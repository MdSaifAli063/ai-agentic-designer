from pydantic import BaseModel, ValidationError

from ai_agentic_designer.agents.planner_agent import PlannedPage


def _dump_model(model: BaseModel) -> dict:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


def generate_ui(prompt: str, pages: dict, design: dict) -> dict:
    raw_pages = pages.get("pages", [])

    try:
        validated_pages = [PlannedPage(**page) for page in raw_pages]
    except ValidationError as exc:
        raise ValueError(f"UI validation failed: {exc}") from exc

    return {
        "pages": [
            {
                "name": page.name,
                "route": page.route,
                "ui_sections": [_dump_model(section) for section in page.ui_sections],
            }
            for page in validated_pages
        ]
    }
