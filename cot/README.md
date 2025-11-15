# Chain-of-Thought (CoT) Baseline

This directory contains the Chain-of-Thought baseline implementation for MAS-style benchmarking.

## Overview

The CoT baseline provides a single-agent comparison point using the standard "Let's think step by step." prompting technique. This allows for fair comparison with multi-agent systems (LbMAS and Static MAS).

## Features

- **Single-agent reasoning**: Uses one LLM call with CoT prompting
- **Random model selection**: Randomly selects between Llama and Qwen (per paper protocol)
- **Answer extraction**: Automatically extracts final answers from reasoning text
- **Comprehensive logging**: Saves detailed traces and reports
- **Same test cases**: Uses the same easy test cases as Static MAS and LbMAS

## Usage

### Quick Start

Run the easy test cases:

```bash
python cot/test_easy_cases_fast.py
```

### Programmatic Usage

```python
from cot.run_experiment import run_cot_experiment

result = run_cot_experiment(
    problem="Your problem here",
    ground_truth="Expected answer",  # Optional
    enable_logging=True
)

print(f"Final Answer: {result['final_answer']}")
print(f"Correct: {result.get('correct', None)}")
print(f"Tokens Used: {result['tokens_used']}")
```

## Test Cases

The baseline runs on the same two easy test cases:

1. **Case A**: Mathematical Problem (Trinkets/Blinkets/Drinkets conversion)
   - Ground Truth: "6 Trinkets"

2. **Case B**: Common Knowledge Question (Why is the sky blue?)
   - Ground Truth: "C"

## Output Structure

Results are saved in `cot/outputs/`:

- `cot_trace_YYYYMMDD_HHMMSS.json`: Full trace with all details
- `cot_report_YYYYMMDD_HHMMSS.txt`: Human-readable report

Each trace includes:
- Problem and ground truth
- Model backend used
- Full CoT prompt
- Complete reasoning response
- Extracted final answer
- Token usage (prompt, completion, total)
- Execution time
- Correctness evaluation (if ground truth provided)

## Answer Extraction

The system automatically extracts final answers from reasoning text using:

1. Explicit answer markers ("The answer is...", "Final answer:", etc.)
2. Problem-type specific extraction:
   - Multiple choice: Extracts letter (A-D)
   - Math problems: Extracts numbers with units
3. Fallback: Uses last sentence or end of reasoning

## Model Selection

Per paper protocol, the system randomly selects between:
- `llama`: Meta Llama-3.1-70B-Instruct
- `qwen`: Qwen/Qwen2.5-72B-Instruct

(When using API models; falls back to available Ollama models if configured)

## Comparison with Other Baselines

This CoT baseline provides:
- **Baseline comparison**: Single-agent performance vs. multi-agent systems
- **Token efficiency**: Typically uses fewer tokens than multi-agent systems
- **Simplicity**: No agent coordination or aggregation needed
- **Speed**: Single LLM call, faster execution

Use this alongside Static MAS and LbMAS results to demonstrate:
- When multi-agent systems provide value
- Trade-offs between token usage and accuracy
- Benefits of agent specialization and coordination

## Files

- `run_experiment.py`: Main experiment runner with CoT logic
- `test_easy_cases_fast.py`: Test script for easy cases
- `__init__.py`: Package initialization
- `outputs/`: Directory for trace files and reports

