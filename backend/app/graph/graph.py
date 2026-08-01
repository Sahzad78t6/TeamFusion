from app.graph.workflow import workflow_engine

def run_growthos_graph(user_id: str, prompt: str) -> dict:
    state = workflow_engine.execute(user_id, prompt)
    return {
        "user_id": state["user_id"],
        "executed_nodes": state["history"],
        "response": state["output"]
    }
