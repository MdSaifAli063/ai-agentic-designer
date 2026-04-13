import json
from ai_agentic_designer.agents.llm import llm


SYSTEM_PROMPT = """
You are a UI Planning Agent.

Your job is to analyze user prompts and create a structured UI plan.

You must return JSON only.

Generate:
- pages
- ui sections
- theme style
- assets required


Return format:

{
  "pages": [],
  "ui": [],
  "theme": "",
  "assets": []
  
}
"""


def planner(prompt):

    planning_prompt = f"""
    User Request:
    {prompt}

    Create UI plan.
    """

    response = llm(planning_prompt, system_prompt=SYSTEM_PROMPT)

    try:
        plan = json.loads(response)
    except:
        plan = {
            "pages": ["home"],
            "ui": ["navbar", "hero", "footer"],
            "theme": "modern",
            "assets": ["icons"]
           
        }

    return plan