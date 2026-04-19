import json
from ai_agentic_designer.agents.llm import llm


SYSTEM_PROMPT = """
You are a UI Planning Agent.

Your job is to analyze user prompts and create a structured UI plan.
and always generate multiple pages based on the user request or user prompt

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
    Use this systematic approach to provide your response:
    1. Break down the prompt into smaller steps
    2. Address each step systematically
    3. Show your reasoning for each step
    4. Then provide your final conclusion
    """

    response = llm(planning_prompt, system_prompt=SYSTEM_PROMPT)

    try:
        plan = json.loads(response)
    except:
        plan = {
            "pages": ["home", "about", "features", "pricing", "contact"],
            "style": "modern",
            "layout": ["navbar", "hero", "footer"],
            "assets": ["icons"]
        }

    return plan
