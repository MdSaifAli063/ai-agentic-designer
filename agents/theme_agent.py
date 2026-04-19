import json
from ai_agentic_designer.agents.llm import llm


def generate_theme(prompt, plan):

    theme_prompt = f"""
    Generate UI theme.

    User Request:
    {prompt}
   
    Planner Output:
    {json.dumps(plan, indent=2)}
    
    STRICT RULES:
    - Style must match planner style
    - Return ONLY JSON

    Return JSON:
    {{
      "theme": {{
        "primary": "#6366f1",
        "background": "#0f172a"
      }}
    }}
    """

    response = llm(theme_prompt)

    try:
        theme = json.loads(response)
    except:
        theme = {
            "theme": {
                "primary": "#6366f1"
            }
        }

    return theme
