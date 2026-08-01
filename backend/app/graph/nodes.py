from app.graph.state import GraphState
from app.agents.planner.tools import generate_ai_roadmap
from app.agents.learning_curator.tools import generate_ai_recommendations
from app.agents.opportunity.agent import opportunity_agent
from app.agents.reflection.tools import compute_burnout_risk_indicator
from app.llm.groq_client import groq_llm

def supervisor_node(state: GraphState) -> GraphState:
    state["history"].append("supervisor_node")
    state["current_node"] = "supervisor_node"
    return state

def planner_node(state: GraphState) -> GraphState:
    state["history"].append("planner_node")
    roadmap = generate_ai_roadmap(goals=[state["input_text"]])
    state["output"] = roadmap.get("ai_feedback")
    return state

def learning_curator_node(state: GraphState) -> GraphState:
    state["history"].append("learning_curator_node")
    recs = generate_ai_recommendations(target_role=state["input_text"])
    state["output"] = f"Curated {len(recs)} learning recommendations for {state['input_text']}."
    return state

def opportunity_node(state: GraphState) -> GraphState:
    state["history"].append("opportunity_node")
    res = opportunity_agent.match(state["user_id"], {"goal": state["input_text"]})
    state["output"] = f"Matched {len(res)} career opportunities."
    return state

def reflection_node(state: GraphState) -> GraphState:
    state["history"].append("reflection_node")
    risk = compute_burnout_risk_indicator(4, 4)
    insight = groq_llm.generate(prompt=f"Reflection notes: {state['input_text']}. Risk: {risk}")
    state["output"] = insight
    return state
