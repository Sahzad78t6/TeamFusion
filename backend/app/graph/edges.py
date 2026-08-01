from app.graph.state import GraphState
from app.graph.router import determine_entry_node

def route_edge(state: GraphState) -> str:
    return determine_entry_node(state)
