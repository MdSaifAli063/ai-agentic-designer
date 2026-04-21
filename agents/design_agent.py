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
        "style_family": "liquid_glass + aurora",
        "palette": {
            "primary": "#4f7cff",
            "accent": "#9b5cff"
        },
        "typography": {
            "heading": "Space Grotesk",
            "body": "Inter"
        },
        "spacing": [4,8,12,16,24,32],
        "radius": [8,12,20],
        "shadows": "soft glow",
        "assets": {
            "icons": "outline futuristic",
            "hero": "3d fintech dashboard",
            "background": "animated aurora gradient"
        }
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
