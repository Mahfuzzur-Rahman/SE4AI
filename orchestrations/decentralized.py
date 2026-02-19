import sys
from pathlib import Path

# Dynamic path resolution to project root
root_path = str(Path(__file__).parent.parent.absolute())
if root_path not in sys.path:
    sys.path.append(root_path)

from langgraph.graph import StateGraph, START, END
from core.state_schema import AgentState
from core.agent_wrapper import call_model

# --- Node 1: Frontend Peer ---
def frontend_peer(state: AgentState):
    """Peer responsible for UI/UX and client-side logic."""
    system_prompt = (
        "You are the Frontend Peer. You work directly with the Backend Peer. "
        "Coordinate API contracts and state management. When you both agree "
        "the task is done, include 'CONSENSUS_REACHED' in your message."
    )
    return call_model(state, system_prompt)

# --- Node 2: Backend Peer ---
def backend_peer(state: AgentState):
    """Peer responsible for server logic, database, and API endpoints."""
    system_prompt = (
        "You are the Backend Peer. You work directly with the Frontend Peer. "
        "Define endpoints and database schemas. When you both agree the "
        "task is done, include 'CONSENSUS_REACHED' in your message."
    )
    return call_model(state, system_prompt)

# --- Peer-to-Peer Routing Logic ---
def peer_router(state: AgentState):
    """Determines which peer needs to speak next based on dialogue history."""
    messages = state["messages"]
    last_msg = messages[-1].content.upper()
    
    # Check for termination condition
    if "CONSENSUS_REACHED" in last_msg:
        return END
    
    # Simple alternating logic or keyword-based handoff
    last_sender = messages[-1].name if hasattr(messages[-1], 'name') else None
    if last_sender == "frontend":
        return "backend"
    return "frontend"

# --- Building the Graph ---
builder = StateGraph(AgentState)

builder.add_node("frontend", frontend_peer)
builder.add_node("backend", backend_peer)

# In Decentralized logic, Peers talk to each other directly
builder.add_edge(START, "frontend")
builder.add_conditional_edges("frontend", peer_router)
builder.add_conditional_edges("backend", peer_router)

decentralized_graph = builder.compile()