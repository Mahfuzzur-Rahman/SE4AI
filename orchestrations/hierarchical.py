import sys
from pathlib import Path

# Dynamic path resolution to project root
root_path = str(Path(__file__).parent.parent.absolute())
if root_path not in sys.path:
    sys.path.append(root_path)

from langgraph.graph import StateGraph, START, END
from core.state_schema import AgentState
from core.agent_wrapper import call_model

# --- Node 1: The Director (Strategic Leadership) ---
def director_node(state: AgentState):
    """Provides high-level project oversight and strategic technical decisions."""
    system_prompt = (
        "You are the Director. Your job is to define the project scope and "
        "delegate technical management to the Lead Developer. Review final "
        "deliverables against requirements. If satisfied, say 'PROJECT_COMPLETE'."
    )
    return call_model(state, system_prompt)

# --- Node 2: The Lead Developer (Technical Management) ---
def lead_dev_node(state: AgentState):
    """Breaks down work into specific tasks and manages implementation specialists."""
    system_prompt = (
        "You are the Lead Developer. You receive direction from the Director. "
        "Your role is to coordinate between Frontend and Backend implementation. "
        "Instruct your specialists and review their integrated code."
    )
    return call_model(state, system_prompt)

# --- Node 3: Specialist Implementation (Full-Stack Specialists) ---
def specialist_node(state: AgentState):
    """Executes technical implementation (Frontend, Backend, DB)."""
    system_prompt = (
        "You are a Senior Full-Stack Specialist. Implement the technical tasks "
        "assigned by the Lead Developer. Focus on production-quality code "
        "and pass all unit tests."
    )
    return call_model(state, system_prompt)

# --- Hierarchical Logic ---
def hierarchy_router(state: AgentState):
    """Determines the flow of authority and reporting."""
    last_msg = state["messages"][-1].content.upper()
    
    # Director decides when the entire project is finished
    if "PROJECT_COMPLETE" in last_msg:
        return END
    
    # If Director just spoke, go to Lead Dev
    # If Specialist just spoke, go back to Lead Dev for review
    # If Lead Dev just spoke, they decide to call Specialist or report to Director
    return "lead_dev"

# --- Building the Graph ---
builder = StateGraph(AgentState)

builder.add_node("director", director_node)
builder.add_node("lead_dev", lead_dev_node)
builder.add_node("specialist", specialist_node)

# Flow: Director -> Lead Dev -> Specialist -> Lead Dev -> Director
builder.add_edge(START, "director")
builder.add_edge("director", "lead_dev")
builder.add_edge("lead_dev", "specialist")
builder.add_edge("specialist", "lead_dev")
builder.add_conditional_edges("lead_dev", hierarchy_router)

hierarchical_graph = builder.compile()