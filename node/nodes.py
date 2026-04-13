from ai_agentic_designer.agents.page_agent import generate_pages
from ai_agentic_designer.agents.theme_agent import generate_theme
from ai_agentic_designer.agents.ui_agent import generate_ui
from ai_agentic_designer.agents.asset_agent import generate_assets
from ai_agentic_designer.agents.planner_agent import planner
from ai_agentic_designer.agents.state import AgentState



def planner_node(state: AgentState):
    plan = planner(state['prompt'])
    print("Planner running")
    return {"plan": plan}

def page_node(state: AgentState):
    pages = generate_pages(state['prompt'])
    print("Page running")
    return {"pages": pages}


def ui_node(state: AgentState):
    ui_layout = generate_ui(state['prompt'])
    print("ui running")
    return {"ui_layout": ui_layout}

def theme_node(state: AgentState):
    theme = generate_theme(state['prompt'])
    return {"theme": theme}

def asset_node(state: AgentState):  
    assets = generate_assets(state['prompt'])
    return {"assets": assets}

