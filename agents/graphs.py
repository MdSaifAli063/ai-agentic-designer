from langgraph.graph import StateGraph

from ai_agentic_designer.node.nodes import page_node, ui_node, theme_node, asset_node, planner_node
from ai_agentic_designer.agents.state import AgentState




def create_agent_graph():

  workflow = StateGraph(AgentState)

  workflow.add_node("plan", planner_node)
  workflow.add_node("page", page_node)
  workflow.add_node("ui", ui_node)
  workflow.add_node("theme", theme_node)
  workflow.add_node("assets", asset_node)

  workflow.set_entry_point("plan")

  workflow.add_edge("plan", "page")
  workflow.add_edge("page", "ui")
  workflow.add_edge("ui", "theme")
  workflow.add_edge("theme", "assets")

  workflow.set_finish_point("assets")

  return workflow.compile()




def main():
  graph = create_agent_graph()
  final_state = graph.invoke(
      {"prompt": "Create AI startup website"},
      config={"recursion_limit": 100}
  )
  print(final_state)

if __name__ == "__main__":
    main()




