# Logging and Tracing Guide

This guide explains how to use the detailed logging and tracing system to demonstrate the LbMAS execution flow, as shown in the paper's easy cases.

## Overview

The logging system captures:
- **All prompts** sent to agents and the control unit
- **All responses** from agents with full content
- **Agent selection** reasoning from the control unit
- **Blackboard state** at each round (public and private spaces)
- **Complete execution trace** showing the flow of information
- **Token usage** for cost tracking

## Quick Start

### Run the Easy Cases Test

```bash
python test_easy_cases.py
```

This will:
1. Run Case A (Mathematical problem: Drinkets to Trinkets)
2. Run Case B (Common knowledge: Why is the sky blue?)
3. Generate detailed traces for both cases
4. Save JSON traces and text reports

### Output Files

For each test case, you'll get:
- `trace_<experiment_id>.json` - Complete trace in JSON format
- `report_<experiment_id>.txt` - Human-readable text report

## Understanding the Trace Structure

### JSON Trace Format

```json
{
  "experiment_id": "case_a_mathematical",
  "problem": "In the land of Ink...",
  "ground_truth": "6 Trinkets",
  "agent_pool": [
    {
      "name": "planner",
      "role": "planner",
      "type": "predefined",
      "llm_backend": "llama3.1"
    },
    ...
  ],
  "rounds": [
    {
      "round": 1,
      "selected_agents": ["planner"],
      "selection_reasoning": "...",
      "agent_actions": [
        {
          "agent": "planner",
          "result": {
            "response": {...},
            "raw_response": "...",
            "tokens": 152
          },
          "blackboard_update": "..."
        }
      ],
      "blackboard_snapshot": {
        "public_messages": [...],
        "private_spaces": {...}
      }
    }
  ],
  "final_answer": "6 Trinkets",
  "total_tokens": 1234
}
```

### Text Report Format

The text report shows:
1. **Problem** - The question being solved
2. **Agent Pool** - All available agents with their types
3. **Execution Trace** - Round-by-round breakdown:
   - Selected agents and reasoning
   - Agent actions with responses
   - Blackboard state
4. **Final Answer** - Solution and source

## Visualizing Traces

### Generate Flow Visualization

```bash
python visualize_trace.py outputs/trace_case_a_mathematical.json
```

This creates:
- Detailed flow visualization
- ASCII diagram of agent execution

### Custom Visualization

```python
from visualize_trace import visualize_flow, create_ascii_diagram

# Load and visualize
visualize_flow("outputs/trace_case_a_mathematical.json", "flow_diagram.txt")
create_ascii_diagram("outputs/trace_case_a_mathematical.json")
```

## Demonstrating the Easy Cases

### Case A: Mathematical Problem

**Expected Flow:**
```
Planner → Mathematician/Data Analyst → Cleaner → Decider
```

**What to Look For:**
1. Planner creates a 3-step plan
2. Mathematician/Data Analyst solve the conversion
3. Cleaner identifies redundancy
4. Decider confirms final answer: "6 Trinkets"

**Key Evidence:**
- Planner's plan in Round 1
- Expert agents' calculations in Round 2
- Cleaner's redundancy detection
- Decider's final confirmation

### Case B: Common Knowledge Question

**Expected Flow:**
```
Expert Agents (Atmospheric Physicist, Optics Scientist, Meteorologist) → Decider
```

**What to Look For:**
1. Multiple expert agents provide analysis
2. Consensus on answer C
3. Decider confirms based on expert consensus

**Key Evidence:**
- Expert agents' domain-specific analysis
- Agreement on answer C
- Decider's consensus-based decision

## Analyzing Traces

### Check Agent Selection

Look at `rounds[].selection_reasoning` to see why the control unit selected specific agents.

### Check Agent Responses

Look at `rounds[].agent_actions[].result.raw_response` for full agent outputs.

### Check Blackboard Evolution

Look at `rounds[].blackboard_snapshot` to see how information accumulates.

### Check Prompts

Look at `prompts[]` array to see all prompts sent to agents.

## Example: Extracting Key Information

```python
import json

# Load trace
with open('outputs/trace_case_a_mathematical.json') as f:
    trace = json.load(f)

# Get agent flow
for round_entry in trace['rounds']:
    print(f"Round {round_entry['round']}:")
    print(f"  Selected: {round_entry['selected_agents']}")
    for action in round_entry['agent_actions']:
        agent = action['agent']
        response = action['result'].get('raw_response', '')[:100]
        print(f"    {agent}: {response}...")
```

## Tips for Demonstrations

1. **Show the Flow**: Use `visualize_trace.py` to create clear diagrams
2. **Highlight Key Agents**: Point out which agents were triggered and why
3. **Show Reasoning**: Display the control unit's selection reasoning
4. **Show Evolution**: Compare blackboard state across rounds
5. **Show Final Answer**: Highlight how the decider reached the conclusion

## Integration with Your Own Experiments

```python
from experiment_runner.run_experiment import run_single_experiment
from utils.logger import ExperimentLogger

# Create logger
logger = ExperimentLogger(experiment_id="my_experiment")

# Run experiment with logging
result = run_single_experiment(
    problem="Your problem here",
    ground_truth="Expected answer",
    enable_logging=True,
    logger=logger
)

# Traces are automatically saved
print(f"Trace: {result['trace_json']}")
print(f"Report: {result['trace_txt']}")
```

## Troubleshooting

**No traces generated?**
- Check that `enable_logging=True` (default)
- Verify `outputs/` directory exists and is writable

**Missing prompts?**
- Prompts are logged when agents are called
- Check that agents are actually executing

**Incomplete traces?**
- Check for errors in agent execution
- Verify Ollama/API is working correctly

