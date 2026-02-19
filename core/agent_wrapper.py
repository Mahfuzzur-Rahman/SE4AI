import sys
import time
import anthropic
from pathlib import Path
from langchain_anthropic import ChatAnthropic
from core.state_schema import AgentState

# Dynamic path resolution to project root
root_path = str(Path(__file__).parent.parent.absolute())
if root_path not in sys.path:
    sys.path.append(root_path)

def get_model():
    """Returns a standardized Claude 4.6 Sonnet instance."""
    # max_retries=0 because we handle retries manually
    return ChatAnthropic(model="claude-sonnet-4-6", temperature=0, max_retries=0)

def call_model(state: AgentState, system_prompt: str):
    """
    Standardized wrapper with Prompt Caching and Exponential Backoff.
    """
    model = get_model()
    messages = state["messages"]

    # 1. Safety Guard: Ensure turn ends with user message
    if messages and (getattr(messages[-1], "type", None) == "ai" or 
                    getattr(messages[-1], "role", None) == "assistant"):
        messages.append({"role": "user", "content": "Please proceed."})

    # 2. Setup Prompt Caching for the System Prompt
    # We pass system as a list of content blocks to enable cache_control
    cached_system = [
        {"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}
    ]

    # 3. Rate Limit Handling Loop (Exponential Backoff)
    max_retries = 5
    delay = 5 
    
    for attempt in range(max_retries):
        try:
            start_call = time.time()
            
            # Pass system as a cached block list
            response = model.invoke(messages, system=cached_system)
            
            duration = time.time() - start_call
            
            # Update state metrics (Cost reflects 2026 Sonnet 4.6 pricing)
            usage = response.usage_metadata
            new_usage = {
                "input_tokens": state["usage_metadata"].get("input_tokens", 0) + usage["input_tokens"],
                "output_tokens": state["usage_metadata"].get("output_tokens", 0) + usage["output_tokens"],
                "total_cost": state["usage_metadata"].get("total_cost", 0) + 
                              (usage["input_tokens"] * 0.000003) + 
                              (usage["output_tokens"] * 0.000015)
            }
            
            return {
                "messages": messages + [response],
                "usage_metadata": new_usage,
                "turn_count": state["turn_count"] + 1
            }

        except Exception as e:
            # Handle Rate Limits (429)
            if "429" in str(e) or "rate_limit_error" in str(e).lower():
                print(f"--- Rate Limit Hit! Sleeping {delay}s (Attempt {attempt+1}/{max_retries}) ---")
                time.sleep(delay)
                delay *= 2 
            else:
                raise e

    raise Exception("Benchmark failed due to sustained Rate Limits.")