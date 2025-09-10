from langgraph.graph import END, StateGraph, START
from state import retrieve,web_search
from graph import GraphState
from edges import route_question


workflow = StateGraph(GraphState)
# Define the nodes
workflow.add_node("web_search", web_search)  # web search
workflow.add_node("retrieve", retrieve)  # retrieve

# Build graph
workflow.add_conditional_edges(
    START,
    route_question,
    {
        "web_search": "web_search",
        "vectorstore": "retrieve",
    },
)
workflow.add_edge( "retrieve", END)
workflow.add_edge( "web_search", END)
# Compile
app = workflow.compile()