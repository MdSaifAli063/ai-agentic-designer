import json
from ai_agentic_designer.agents.llm import llm


def generate_theme(prompt):

    theme_prompt = f"""
    Generate UI theme.

    User Request:
    {prompt}

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