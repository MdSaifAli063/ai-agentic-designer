import json
from ai_agentic_designer.agents.llm import llm


SYSTEM_PROMPT = """
You are a UI Planning Agent.

Your job is to analyze user prompts and create a structured UI plan.

Return only valid JSON.

Generate:
- pages
- style
- layout
- assets
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
            "style": "modern",
            "layout": ["navbar", "hero", "footer"],
            "assets": ["icons"]
        }

    return plan