#!/bin/bash
# cagent Multi-Pattern Benchmark Visualization with Logging

# 1. Load API Key from the parent directory's .env file
if [ -f "../.env" ]; then
    export ANTHROPIC_API_KEY=$(grep ANTHROPIC_API_KEY ../.env | cut -d '=' -f2)
else
    echo "Error: .env file not found in parent directory."
    exit 1
fi

# 2. Path to the customized churn data
TASK_FILE="test_task.json"
INSTRUCTION=$(python3 -c "import json; print(json.load(open('$TASK_FILE'))['instruction'])")

# Create a results folder if it doesn't exist
mkdir -p results

echo "===================================================="
echo "STARTING FULLSTACK ORCHESTRATION BENCHMARK"
echo "===================================================="

for PATTERN in centralized hierarchical decentralized hybrid; do
    UPPER_PATTERN=$(echo "$PATTERN" | tr '[:lower:]' '[:upper:]')
    echo -e "\n--- RUNNING PATTERN: $UPPER_PATTERN ---"
    
    # 3. Use --log-file to capture the agent's internal reasoning
    # Use --debug to see every file read/write and tool call
    LOG_FILE="results/${PATTERN}_debug.log"
    
    cagent exec "${PATTERN}.yaml" "$INSTRUCTION" --debug --log-file "$LOG_FILE"
    
    echo -e "\n--- $UPPER_PATTERN COMPLETED ---"
    
    # 4. Display usage summary from the session
    echo "Extracted Session Metrics:"
    grep -E "input_tokens|output_tokens|total_cost" "$LOG_FILE" | tail -n 3
    
    echo "Wait 10s for API rate limits..."
    sleep 10
done

echo -e "\n===================================================="
echo "BENCHMARK COMPLETE. ALL LOGS SAVED IN /cagent/results/"
echo "===================================================="