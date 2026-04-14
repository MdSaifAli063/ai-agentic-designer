import json
from ai_agentic_designer.agents.llm import llm


def generate_assets(prompt):

    asset_prompt = f"""
    Generate UI assets for website.

    User Request:
    {prompt}
    

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