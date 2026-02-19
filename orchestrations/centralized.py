import sys
from pathlib import Path

# Dynamic path resolution to project root
root_path = str(Path(__file__).parent.parent.absolute())
if root_path not in sys.path:
    sys.path.append(root_path)

from langgraph.graph import StateGraph, START, END
from core.state_schema import AgentState
from core.agent_wrapper import call_model

# --- Node 1: The Manager (Supervisor) ---
def manager_node(state: AgentState):
    """
    Acts as the Root/Orchestrator. Analyzes the task and delegates to the Developer.
    """
    system_prompt = (
        "You are the Project Manager (Manager). Your job is to break down full-stack "
        "requirements and instruct the Developer. When the task is complete, say 'FINISH'."
    )
    # Reusing our call_model to track RQ2/RQ3 metrics
    return call_model(state, system_prompt)

# --- Node 2: The Developer (Specialist) ---
def developer_node(state: AgentState):
    """
    Executes the technical implementation based on Manager instructions.
    """
    system_prompt = (
        "You are a Full-Stack Developer. Implement the requested features, "
        "run tests, and report back to the Manager with your progress."
    )
    return call_model(state, system_prompt)

# --- Routing Logic ---
def router(state: AgentState):
    """
    Conditional logic to determine if we should continue or end.
    """
    last_message = state["messages"][-1].content
    if "FINISH" in last_message.upper():
        return END
    return "developer"

# --- Building the Graph ---
builder = StateGraph(AgentState)

# 1. Add Nodes
builder.add_node("manager", manager_node)
builder.add_node("developer", developer_node)

# 2. Add Edges (Centralized Flow)
builder.add_edge(START, "manager") # Start at the Root/Manager
builder.add_conditional_edges("manager", router) # Manager decides: Developer or END
builder.add_edge("developer", "manager") # Developer must always report back to Manager

# 3. Compile
centralized_graph = builder.compile()