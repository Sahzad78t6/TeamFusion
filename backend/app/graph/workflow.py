from app.graph.state import GraphState
from app.graph.nodes import (
    supervisor_node,
    planner_node,
    learning_curator_node,
    opportunity_node,
    reflection_node
)
from app.graph.router import determine_entry_node

class LangGraphWorkflow:
    def execute(self, user_id: str, input_text: str) -> GraphState:
        state: GraphState = {
            "user_id": user_id,
            "input_text": input_text,
            "current_node": "supervisor_node",
            "context": {},
            "output": None,
            "history": []
        }
        state = supervisor_node(state)
        target_node = determine_entry_node(state)
        
        if target_node == "planner_node":
            state = planner_node(state)
        elif target_node == "learning_curator_node":
            state = learning_curator_node(state)
        elif target_node == "opportunity_node":
            state = opportunity_node(state)
        elif target_node == "reflection_node":
            state = reflection_node(state)
        else:
            state = planner_node(state)

        return state

workflow_engine = LangGraphWorkflow()
