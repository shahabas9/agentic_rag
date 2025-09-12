from langgraph.graph import END, StateGraph, START
from state import retrieve,web_search,generate
from graph import GraphState
from edges import route_question
from grader import grade_answer
from human import human_escalation


def build_workflow():
    workflow = StateGraph(GraphState)

    # Nodes
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("web_search", web_search)
    workflow.add_node("generate", generate)
    workflow.add_node("grade", grade_answer)
    workflow.add_node("human", human_escalation)

    # Start → route
    workflow.add_conditional_edges(
        START,
        route_question,
        {"vectorstore": "retrieve","web_search": "web_search"},
    )

    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("web_search", "generate")

    # Answer → grade
    workflow.add_edge("generate", "grade")

    # Both routes → grade
    workflow.add_conditional_edges(
    "grade",
    lambda state: "END" if state.get("grade") == "good" else "human",
    {"END": END, "human": "human"},
)

    # Human → END
    workflow.add_edge("human", END)

    return workflow.compile()
