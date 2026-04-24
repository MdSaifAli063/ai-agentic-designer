from langgraph.graph import StateGraph

from ai_agentic_designer.node.nodes import page_node, ui_node, design_node, planner_node, code_node
from ai_agentic_designer.agents.state import AgentState




def create_agent_graph():

  workflow = StateGraph(AgentState)

  workflow.add_node("plan", planner_node)
  workflow.add_node("page", page_node)
  workflow.add_node("ui", ui_node)
  workflow.add_node("design", design_node)
  workflow.add_node("code", code_node)


  workflow.set_entry_point("plan")

  workflow.add_edge("plan", "page")
  workflow.add_edge("page", "design")
  workflow.add_edge("design", "ui")
  workflow.add_edge("ui","code")

  workflow.set_finish_point("code")

  return workflow.compile()




def run_graph(prompt):
  graph = create_agent_graph()
  final_state = graph.invoke(
      {"prompt": prompt},
      config={"recursion_limit": 100}
  )
  return final_state

if __name__ == "__main__":
    result = run_graph("Create futuristic AI startup website")
    print(result)


