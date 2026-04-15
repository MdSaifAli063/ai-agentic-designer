import json
from ai_agentic_designer.agents.llm import llm
from ai_agentic_designer.mcp_server.tools.figma_tool import create_ui_frames


def generate_ui(prompt, plan):

    ui_prompt = f"""
    Generate UI layout sections.

    User Request:
    {prompt}

    Planner Output:
    {json.dumps(plan, indent=2)}
  

    Return JSON:
    {{
      "layout": ["navbar", "hero", "features", "footer"]
    }}
    """

    response = llm(ui_prompt)

    try:
        layout = json.loads(response)
    except:
        layout = {"layout": ["navbar", "hero"]}

    return layout