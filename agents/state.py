from typing import TypedDict


class AgentState(TypedDict, total=False):
    prompt: str
    site_spec: dict
    figma_result: 