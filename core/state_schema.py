import sys
from pathlib import Path

# Dynamic path resolution
root_path = str(Path(__file__).parent.parent.absolute())
if root_path not in sys.path:
    sys.path.append(root_path)

from typing import Annotated, List, Dict, TypedDict
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    The unified state for the Agent Orchestration Bench.
    This schema ensures all RQs are measurable during graph execution.
    """
    # --- core Communication & Logic ---
    # add_messages ensures new messages are appended rather than overwritten
    messages: Annotated[List[Dict], add_messages] 
    
    # --- RQ 2: Performance & Resources ---
    # Tracks { "input_tokens": 0, "output_tokens": 0, "total_cost": 0.0 }
    usage_metadata: Dict[str, float] 
    
    # Start and end timestamps to calculate Time-to-Completion
    start_time: float
    end_time: float
    
    # --- RQ 3: Coordination Overhead ---
    # Incremented at every node transition
    turn_count: int
    
    # Tracks agent assignments to identify redundant work patterns
    # e.g., {"file_path": ["agent_name", "agent_name"]}
    edit_history: Dict[str, List[str]]
    
    # --- Context & Grounding ---
    # The original task specification from FullStack-Bench
    task_description: str
    
    # The current state of the workspace (file tree and critical content)
    workspace_snapshot: Dict[str, str]

    # Final result status for RQ 1 (Orchestration Fidelity)
    execution_status: str # "SUCCESS", "FAILED", or "PENDING"