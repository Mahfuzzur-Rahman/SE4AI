import sys
from pathlib import Path

# Dynamic path resolution to project root
root_path = str(Path(__file__).parent.parent.absolute())
if root_path not in sys.path:
    sys.path.append(root_path)

from langgraph.graph import StateGraph, START, END
from core.state_schema import AgentState
from core.agent_wrapper import call_model

# --- Node 1 & 2: The Peer Specialists (Decentralized Layer) ---
def frontend_specialist(state: AgentState):
    """Explores UI solutions and communicates peer-to-peer."""
    system_prompt = (
        "You are the Frontend Specialist. Coordinate with the Backend peer "
        "to implement the UI. Once ready for integration, submit your "
        "changes to the Gatekeeper for review."
    )
    return call_model(state, system_prompt)

def backend_specialist(state: AgentState):
    """Explores server logic and communicates peer-to-peer."""
    system_prompt = (
        "You are the Backend Specialist. Coordinate with the Frontend peer "
        "on API design. Once ready for integration, submit your changes "
        "to the Gatekeeper for review."
    )
    return call_model(state, system_prompt)

# --- Node 3: The Gatekeeper/Reviewer (Centralized Layer) ---
def gatekeeper_node(state: AgentState):
    """Acts as the final review authority for all code merges."""
    system_prompt = (
        "You are the Gatekeeper (Reviewer). Analyze the integrated solution "
        "from the peers. If it meets all requirements and passes logic checks, "
        "say 'APPROVE_MERGE'. If not, send it back with specific feedback."
    )
    return call_model(state, system_prompt)

# --- Hybrid Routing Logic ---
def hybrid_router(state: AgentState):
    """Manages the transition from peer exploration to centralized gating."""
    messages = state["messages"]
    last_msg = messages[-1].content.upper()
    
    # Check if the Centralized Gatekeeper approves
    if "APPROVE_MERGE" in last_msg:
        return END
    
    # Logic: If specialists are talking, they can loop among themselves.
    # We will trigger the Gatekeeper once a 'SUBMIT' keyword is detected.
    if "SUBMIT" in last_msg:
        return "gatekeeper"
    
    # Peer-to-peer switching
    return "backend" if "frontend" in last_msg.lower() else "frontend"

# --- Building the Graph ---
builder = StateGraph(AgentState)

builder.add_node("frontend", frontend_specialist)
builder.add_node("backend", backend_specialist)
builder.add_node("gatekeeper", gatekeeper_node)

# Flow: Start -> Peer Exploration <-> Peer Exploration -> Gatekeeper -> END/Loop
builder.add_edge(START, "frontend")
builder.add_conditional_edges("frontend", hybrid_router)
builder.add_conditional_edges("backend", hybrid_router)
builder.add_conditional_edges("gatekeeper", hybrid_router)

hybrid_graph = builder.compile()