from pydantic import BaseModel, ValidationError

from agents.planner_agent import DesignSystem


def _dump_model(model: BaseModel) -> dict:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


def generate_design(prompt: str, plan: dict) -> dict:
    try:
        if "design" in plan:
            design = DesignSystem(**plan["design"])
        else:
            design = DesignSystem(**plan)
    except ValidationError as exc:
        raise ValueError(f"Design validation failed: {exc}") from exc

    return _dump_model(design)
