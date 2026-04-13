from typing import TypedDict


class AgentState(TypedDict):
  prompt: str
  pages: dict
  ui_layout: dict
  theme: dict
  assets: dict
  plan: str
