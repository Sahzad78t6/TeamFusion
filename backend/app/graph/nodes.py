from app.graph.state import GraphState
from app.agents.planner.agent import planner_agent
from app.agents.learning_curator.agent import learning_curator_agent
from app.agents.opportunity.agent import opportunity_agent
from app.agents.reflection.agent import reflection_agent

def supervisor_node(state: GraphState) -> GraphState:
    state["history"].append("supervisor_node")
    state["current_node"] = "supervisor_node"
    return state

def planner_node(state: GraphState) -> GraphState:
    state["history"].append("planner_node")
    result = planner_agent.create_plan(state["user_id"], [state["input_text"]])
    state["output"] = result.get("ai_feedback")
    return state

def learning_curator_node(state: GraphState) -> GraphState:
    state["history"].append("learning_curator_node")
    res = learning_curator_agent.curate(state["user_id"], state["input_text"])
    state["output"] = f"Curated {len(res)} learning recommendations."
    return state

def opportunity_node(state: GraphState) -> GraphState:
    state["history"].append("opportunity_node")
    res = opportunity_agent.match(state["user_id"], state["input_text"])
    state["output"] = f"Matched {len(res)} career opportunities."
    return state

def reflection_node(state: GraphState) -> GraphState:
    state["history"].append("reflection_node")
    res = reflection_agent.process(state["user_id"], 4, 4, state["input_text"])
    state["output"] = res.get("ai_insight")
    return state
