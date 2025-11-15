# Static MAS (Multi-Agent System)

A baseline multi-agent system implementation for comparison with the blackboard-based LbMAS system.

## Overview

Static MAS implements a simple parallel multi-agent system where:
- **Fixed roles**: All agents have predefined, static roles (no dynamic generation)
- **Parallel execution**: All agents receive the problem simultaneously and process it independently
- **Single pass**: No iteration, no blackboard updates - one round only
- **Aggregation**: Results are aggregated using voting, decider-based, or confidence-based methods

## Key Differences from LbMAS

| Feature | LbMAS | Static MAS |
|---------|-------|------------|
| Blackboard | ✅ Yes | ❌ No |
| Iteration | ✅ Yes (multi-round) | ❌ No (single pass) |
| Dynamic Roles | ✅ Yes | ❌ No (fixed roles) |
| Agent Selection | ✅ Dynamic (control unit) | ❌ All agents execute |
| Communication | ✅ Via blackboard | ❌ Independent |

## Structure

```
static_mas/
├── agents/
│   ├── base_agent.py          # Base agent class (no blackboard)
│   └── static_agents.py       # Static agent implementations
├── prompts.py                  # Static prompts (no blackboard references)
├── aggregation.py             # Aggregation mechanisms
├── run_experiment.py           # Main experiment runner
├── example.py                  # Example usage
└── README.md                   # This file
```

## Agents

The system includes the following fixed agents:
- **Mathematics Expert** (2 instances)
- **Physics Expert**
- **Logic Reasoning Expert**
- **Planner**
- **Decider**
- **General Expert**

Each agent is randomly assigned an LLM backend (Llama or Qwen) at initialization.

## Aggregation Methods

1. **majority_vote**: Selects the answer with the most votes
2. **decider_based**: Uses the decider agent's answer
3. **most_confident**: Selects the answer from the agent with highest confidence
4. **weighted_average**: Weighted aggregation based on confidence scores

## Usage

### Single Experiment

```python
from static_mas.run_experiment import run_static_experiment

result = run_static_experiment(
    problem="What is 15 * 23?",
    ground_truth="345",
    aggregation_method="majority_vote"
)

print(f"Final Answer: {result['final_answer']}")
print(f"Total Tokens: {result['total_tokens']}")
```

### Batch Experiments

```python
from static_mas.run_experiment import run_batch_experiments

tasks = [
    {"question": "What is 2+2?", "answer": "4"},
    {"question": "What is the capital of France?", "answer": "Paris"},
]

results = run_batch_experiments(
    tasks=tasks,
    aggregation_method="majority_vote"
)
```

### Run Example

```bash
python static_mas/example.py
```

## Output

The system generates:
- **JSON trace files**: Detailed logs in `static_mas/outputs/`
- **Text reports**: Human-readable reports in `static_mas/outputs/`
- **Results**: Batch experiment summaries in `static_mas/results/`

## Comparison with LbMAS

This Static MAS serves as a baseline to evaluate:
- **Accuracy**: How does parallel independent reasoning compare to iterative blackboard-based reasoning?
- **Cost**: Token usage comparison (single pass vs multi-round)
- **Speed**: Execution time comparison
- **Quality**: Answer quality and reasoning depth

## Configuration

The system uses the same LLM configuration as bMAS (from `config.py`):
- Supports Ollama (local) and API models (remote)
- Random model assignment per agent
- Configurable temperature and other parameters

## Logging

All experiments log:
- Agent roles and LLM backends
- Individual agent answers and confidence scores
- Token usage per agent
- Aggregation method and final answer
- Execution time
- Evaluation results (if ground truth provided)

