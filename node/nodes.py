from ai_agentic_designer.agents.page_agent import generate_pages
from ai_agentic_designer.agents.theme_agent import generate_theme
from ai_agentic_designer.agents.ui_agent import generate_ui
from ai_agentic_designer.agents.asset_agent import generate_assets
from ai_agentic_designer.agents.planner_agent import planner
from ai_agentic_designer.agents.state import AgentState
from ai_agentic_designer.mcp_server.tools.figma_tool import create_ui_frames



def planner_node(state: AgentState):
    plan = planner(state['prompt'])
    print("Planner running")
    return {"plan": plan}

def page_node(state: AgentState):
    pages = generate_pages(state['prompt'], state['plan'])
    print("Page running")
    return {"pages": pages}


def ui_node(state: AgentState):
    ui_layout = generate_ui(state["pages"]["pages"],state["plan"])
    print("ui running")
    return {"ui": ui_layout}

def theme_node(state: AgentState):
    theme = generate_theme(state["ui"], state['plan'])
    print("theme running")
    return {"theme": theme}

def asset_node(state: AgentState):  
    assets = generate_assets(state['plan'])
    print("assets running")
    return {"assets": assets}

def figma_node(state: AgentState):
    figma = create_ui_frames.invoke({
    "layout": state['ui']['layout']})
    print(state["ui"]["layout"])
    print("figma toold runnning ")
    if "layout" not in state["ui"]:
        return {"figma": {}}
    return {"figma": figma}


