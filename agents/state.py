from typing import TypedDict


class AgentState(TypedDict, total=False):
    prompt: str
    plan: dict
    design: dict
    pages: dict
    ui: dict
    files: dict
    current_agent: str
    errors: list[str]
