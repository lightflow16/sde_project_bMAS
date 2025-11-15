# Static MAS vs LbMAS Comparison Guide

This document outlines how to compare Static MAS (baseline) with LbMAS (blackboard-based system).

## Key Differences

### Architecture

**Static MAS:**
- Fixed agent roles (no dynamic generation)
- All agents execute in parallel
- Single pass (no iteration)
- No blackboard (agents work independently)
- Simple aggregation (voting/decider/confidence-based)

**LbMAS:**
- Dynamic agent generation based on problem
- Iterative execution (up to 4 rounds)
- Blackboard for agent communication
- Control unit selects agents per round
- Decider determines solution readiness

### Execution Flow

**Static MAS:**
```
Problem → All Agents (Parallel) → Aggregation → Final Answer
```

**LbMAS:**
```
Problem → Agent Generation → Round 1 → Blackboard Update → 
Control Unit Selection → Round 2 → ... → Decider Check → Final Answer
```

## Comparison Metrics

### 1. Accuracy
Compare final answers against ground truth:
- Static MAS: `result['correct']`
- LbMAS: `execution_log['correct']`

### 2. Token Usage
Compare total tokens consumed:
- Static MAS: `result['total_tokens']` (single pass)
- LbMAS: `execution_log['total_tokens']` (multi-round)

### 3. Execution Time
Compare time to solution:
- Static MAS: `result['execution_time']`
- LbMAS: `execution_log` (check timestamps)

### 4. Answer Quality
Compare:
- Explanation depth
- Reasoning steps
- Confidence scores

## Running Comparisons

### Example Comparison Script

```python
from static_mas.run_experiment import run_static_experiment
from experiment_runner.run_experiment import run_single_experiment

problem = "What is 15 * 23?"
ground_truth = "345"

# Run Static MAS
static_result = run_static_experiment(
    problem=problem,
    ground_truth=ground_truth,
    aggregation_method="majority_vote"
)

# Run LbMAS
lbmas_result = run_single_experiment(
    problem=problem,
    ground_truth=ground_truth
)

# Compare
print(f"Static MAS: {static_result['final_answer']} (Tokens: {static_result['total_tokens']})")
print(f"LbMAS: {lbmas_result['final_answer']} (Tokens: {lbmas_result['total_tokens']})")
```

## Expected Findings

### Advantages of Static MAS
- **Faster**: Single pass execution
- **Lower cost**: No iteration overhead
- **Simpler**: Easier to understand and debug
- **Parallel**: All agents work simultaneously

### Advantages of LbMAS
- **Better accuracy**: Iterative refinement
- **Deeper reasoning**: Blackboard enables collaboration
- **Adaptive**: Dynamic agent selection
- **Context-aware**: Agents build on each other's work

## Logging Comparison

Both systems log:
- Agent roles and backends
- Individual agent outputs
- Token usage
- Final answers
- Execution times

**Static MAS logs:**
- `static_mas/outputs/static_mas_trace_*.json`
- `static_mas/outputs/static_mas_report_*.txt`

**LbMAS logs:**
- `outputs/trace_*.json`
- `outputs/report_*.txt`

## Batch Comparison

Run both systems on the same dataset:

```python
from static_mas.run_experiment import run_batch_experiments
from experiment_runner.run_experiment import run_batch_experiments as run_lbmas_batch

tasks = [
    {"question": "What is 2+2?", "answer": "4"},
    # ... more tasks
]

# Static MAS
static_results = run_batch_experiments(tasks, aggregation_method="majority_vote")

# LbMAS
lbmas_results = run_lbmas_batch(tasks)

# Compare summaries
print(f"Static MAS Accuracy: {static_results['accuracy']:.2%}")
print(f"LbMAS Accuracy: {lbmas_results['accuracy']:.2%}")
```

## Aggregation Methods

Static MAS supports multiple aggregation methods:
- `majority_vote`: Most common answer wins
- `decider_based`: Use decider agent's answer
- `most_confident`: Highest confidence answer
- `weighted_average`: Confidence-weighted aggregation

Compare which method works best for different problem types.

