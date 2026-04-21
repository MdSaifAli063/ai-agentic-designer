from typing import TypedDict


class AgentState(TypedDict):
  prompt: str
  pages: dict
  ui: dict
  design: dict
  plan: dict

