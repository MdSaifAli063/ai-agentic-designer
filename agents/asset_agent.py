import json
from ai_agentic_designer.agents.llm import llm


def generate_assets(prompt, plan):

    asset_prompt = f"""
    Generate UI assets for website.

    User Request:
    {prompt}

    Planner Output:
    {json.dumps(plan, indent=2)}
    
    STRICT RULES:
    - Use assets from planner
    - Do NOT add extra assets
    
    Return JSON:
    {{
      "assets": ["hero image", "icons", "background"]
    }}
    """

    response = llm(asset_prompt)

    try:
        assets = json.loads(response)
    except:
        assets = {"assets": ["hero image"]}

    return assets