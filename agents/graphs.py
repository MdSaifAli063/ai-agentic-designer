from langgraph.graph import StateGraph

from ai_agentic_designer.agents.state import AgentState
from ai_agentic_designer.node.nodes import code_node, planner_node


def create_agent_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("plan", planner_node)
    workflow.add_node("code", code_node)

    workflow.set_entry_point("plan")
    workflow.add_edge("plan", "code")
    workflow.set_finish_point("code")

    return workflow.compile


def run_graph(prompt: str):
    graph = create_agent_graph()
    final_state = graph.invoke(
        {"prompt": prompt, "errors": []},
        config={"recursion_limit": 50},
    )
    return final_state


# if __name__ == "__main__":
#     result = run_graph("Create futuristic AI startup website")
#     print(result)
