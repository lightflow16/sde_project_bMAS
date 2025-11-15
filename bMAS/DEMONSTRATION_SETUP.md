# Demonstration Setup for Easy Cases

This document explains how to demonstrate the two easy cases from the paper with full logging and tracing.

## What Was Added

### 1. Enhanced Logging System (`utils/logger.py`)
- Captures all prompts sent to agents
- Records all agent responses
- Tracks agent selection reasoning
- Stores blackboard state snapshots
- Generates human-readable reports

### 2. Updated Experiment Runner
- Integrated logging into `run_single_experiment()`
- Captures execution flow at each step
- Saves traces in JSON and text formats

### 3. Test Script (`test_easy_cases.py`)
- Implements both easy cases from the paper
- Case A: Mathematical problem (Drinkets to Trinkets)
- Case B: Common knowledge (Why is the sky blue?)

### 4. Visualization Tools (`visualize_trace.py`)
- Creates flow diagrams
- Generates ASCII art visualizations
- Shows agent execution paths

## Quick Demonstration

### Step 1: Run the Easy Cases

```bash
python test_easy_cases.py
```

This will:
- Execute both test cases
- Generate detailed traces
- Save JSON and text reports
- Print execution summaries

### Step 2: View the Traces

**JSON Trace** (complete data):
```bash
# View in any JSON viewer or text editor
cat outputs/trace_case_a_mathematical.json
```

**Text Report** (human-readable):
```bash
cat outputs/report_case_a_mathematical.txt
```

### Step 3: Visualize the Flow

```bash
python visualize_trace.py outputs/trace_case_a_mathematical.json
```

## What Gets Logged

### For Each Round:
1. **Agent Selection**
   - Which agents were selected
   - Control unit's reasoning
   - Raw selection response

2. **Agent Actions**
   - Full prompts sent to each agent
   - Complete agent responses
   - Parsed responses (JSON)
   - Token usage
   - Blackboard updates

3. **Blackboard State**
   - All public messages
   - All private spaces (debate/reflection)
   - Message metadata (agent, type, timestamp)

### For the Entire Experiment:
- Problem/question
- Ground truth (if provided)
- Agent pool (all available agents)
- Final answer and source
- Total token usage
- Execution timeline

## Expected Outputs

### Case A: Mathematical Problem

**Expected Flow:**
```
Round 1: Planner → creates 3-step plan
Round 2: Mathematician/Data Analyst → solve conversion
Round 3: Cleaner → identify redundancy
Round 4: Decider → confirm "6 Trinkets"
```

**Key Evidence in Trace:**
- Planner's plan with 3 steps
- Expert calculations showing conversion
- Cleaner identifying redundant information
- Decider confirming final answer

### Case B: Common Knowledge

**Expected Flow:**
```
Round 1: Expert Agents → domain analysis
Round 2: Decider → consensus on answer C
```

**Key Evidence in Trace:**
- Multiple expert agents (Atmospheric Physicist, etc.)
- Expert analyses of each option
- Consensus on answer C
- Decider's final confirmation

## File Structure

```
outputs/
├── trace_case_a_mathematical.json    # Complete trace (JSON)
├── report_case_a_mathematical.txt     # Human-readable report
├── trace_case_b_common_knowledge.json
└── report_case_b_common_knowledge.txt
```

## Demonstrating to Others

### 1. Show the Problem
- Display the question
- Explain what type of problem it is

### 2. Show Agent Selection
- Point out which agents were selected
- Explain the control unit's reasoning
- Show why these agents are appropriate

### 3. Show Agent Execution
- Display agent responses
- Show how information flows
- Highlight key contributions

### 4. Show Blackboard Evolution
- Compare blackboard state across rounds
- Show how information accumulates
- Point out cleaning/refinement steps

### 5. Show Final Answer
- Display the final answer
- Show how it was derived
- Compare with ground truth

## Customization

### Change Output Directory

```python
logger = ExperimentLogger(
    experiment_id="my_test",
    output_dir="custom_outputs"
)
```

### Disable Logging

```python
result = run_single_experiment(
    problem="...",
    enable_logging=False  # Disable detailed logging
)
```

### Add Custom Logging

```python
logger.log_prompt("agent_name", "custom_type", "prompt text")
logger.log_agent_response("agent_name", response_dict)
```

## Troubleshooting

**No output files?**
- Check that `outputs/` directory exists
- Verify write permissions
- Check for errors in execution

**Incomplete traces?**
- Ensure agents are executing successfully
- Check Ollama/API connectivity
- Review error messages in console

**Missing prompts?**
- Prompts are logged when agents act
- Check that agents are being called
- Verify logger is initialized correctly

## Next Steps

1. Run `test_easy_cases.py` to generate traces
2. Review the generated reports
3. Use `visualize_trace.py` for visualizations
4. Customize for your own test cases
5. Share traces to demonstrate the system's behavior

