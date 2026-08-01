from app.graph.state import GraphState

def determine_entry_node(state: GraphState) -> str:
    text = state["input_text"].lower()
    if "learn" in text or "resource" in text:
        return "learning_curator_node"
    elif "opportunity" in text or "job" in text:
        return "opportunity_node"
    elif "reflect" in text or "mood" in text:
        return "reflection_node"
    return "planner_node"
