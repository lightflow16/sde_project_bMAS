# Benchmark Evaluation Framework

A comprehensive framework for evaluating Multi-Agent Systems (MAS) against standard LLM benchmarks, aligned with the paper's evaluation methodology.

## Overview

This framework validates 4 MAS systems against 6 standard benchmarks:
- **MMLU** (Massive Multitask Language Understanding) - 1,140 problems
- **ARC-Challenge** - 1,172 problems  
- **GPQA-Diamond** - 198 problems
- **BBH** (BIG-Bench Hard) - 250 problems
- **MATH** - 500 problems
- **GSM8K** - 1,319 problems

## Systems Evaluated

1. **bMAS (LbMAS)** - Blackboard-based MAS with paper-style prompts
2. **orig_impl_bMAS** - Original implementation with original prompts
3. **Static MAS** - Parallel single-pass MAS with majority voting
4. **Chain-of-Thought (CoT)** - Single-agent baseline

## Features

- **Automatic dataset loading** from Hugging Face
- **Answer normalization** for multiple-choice and free-form formats
- **Comprehensive metrics tracking**: accuracy, token cost, execution time, rounds to consensus
- **Comparison tables** similar to paper format (Table 1 and Table 3)
- **Markdown reports** with detailed results

## Installation

Ensure you have the required dependencies:

```bash
pip install datasets huggingface_hub
```

The framework will automatically download datasets from Hugging Face on first use.

## Usage

### Basic Usage

Run a single benchmark:

```bash
# Run MMLU with 10 problems
python run_benchmark_evaluation.py --benchmark mmlu --max-problems 10

# Run MATH benchmark
python run_benchmark_evaluation.py --benchmark math --max-problems 50
```

### Run All Benchmarks

```bash
# Run all benchmarks with 50 problems each
python run_benchmark_evaluation.py --all --max-problems 50
```

### Run Specific Systems

```bash
# Run only bMAS and Static MAS on MATH
python run_benchmark_evaluation.py --benchmark math --systems bMAS static_mas --max-problems 20
```

### Generate Tables from Existing Results

```bash
# Generate comparison tables from previously run evaluations
python run_benchmark_evaluation.py --generate-tables
```

## Output Files

Results are saved in `benchmark_evaluator/results/`:

- `{benchmark}_{system}_results.json` - Detailed results per system
- `{benchmark}_summary.json` - Aggregated summary per benchmark
- `{benchmark}_summary.txt` - Human-readable summary
- `table1_performance.txt` - Performance comparison table (Table 1 format)
- `table3_token_cost.txt` - Token cost comparison (Table 3 format)
- `benchmark_report.md` - Comprehensive markdown report

## Metrics Tracked

For each system and benchmark:

- **Accuracy**: Percentage of correct answers
- **Token Usage**: Total prompt tokens, completion tokens, and total tokens
- **Execution Time**: Total and average time per problem
- **Rounds to Consensus**: Average rounds needed (for iterative systems)
- **Consensus Rate**: Percentage of problems reaching consensus

## Answer Evaluation

The framework handles different answer formats:

- **Multiple-choice** (MMLU, ARC-Challenge, GPQA-Diamond): Exact letter match (A, B, C, D)
- **Free-form** (MATH, GSM8K, BBH): Normalized number extraction, boxed format support

## Example Output

### Performance Table (Table 1)

```
Method              MMLU            ARC-Challenge   GPQA-Diamond   BBH             MATH            GSM8K           Avg.
CoT                 81.31           92.74          35.35          81.20           62.20           94.84           74.60%
Static MAS          81.84           90.35          44.44          85.60           65.80           93.85           76.98%
LbMAS               85.35           93.43          54.04          90.00           72.60           94.46           81.68%
```

### Token Cost Table (Table 3)

```
Method              Prompt Token    Completion Token Total Token      Performance
CoT                     5,475,154        2,853,618     8,328,772        60.40%
Static MAS              1,351,821          820,069     2,171,890        65.80%
LbMAS                   3,352,594        1,013,015     4,721,489        72.60% **
```

## Configuration

### Adjusting Max Rounds

For iterative systems (bMAS, orig_bMAS), you can adjust the maximum rounds:

```bash
python run_benchmark_evaluation.py --benchmark math --max-rounds 6
```

### Custom Output Directory

```bash
python run_benchmark_evaluation.py --benchmark mmlu --output-dir custom_results/
```

## Troubleshooting

### Dataset Loading Issues

If Hugging Face datasets fail to load:

1. Check internet connection
2. Verify `datasets` library is installed: `pip install datasets`
3. Datasets will be cached locally after first download

### Memory Issues

For large benchmarks, use `--max-problems` to limit evaluation:

```bash
# Evaluate only 10 problems per benchmark
python run_benchmark_evaluation.py --all --max-problems 10
```

### System-Specific Errors

If a specific system fails:

1. Check system logs in `benchmark_evaluator/results/`
2. Verify the system is properly configured (see main README)
3. Run individual systems to isolate issues:
   ```bash
   python run_benchmark_evaluation.py --benchmark math --systems bMAS
   ```

## Integration with Paper Methodology

This framework aligns with the paper's evaluation protocol:

- **Temperature**: 0.7 (set in `config.py`)
- **Max Rounds**: 4 (configurable via `--max-rounds`)
- **Random Model Assignment**: Per-agent LLM backend assignment
- **Answer Formats**: Supports both multiple-choice and free-form evaluation
- **Metrics**: Accuracy, token cost, throughput, consensus rate

## Next Steps

1. Run initial evaluation with small sample sizes to verify setup
2. Scale up to full benchmarks for final results
3. Generate comparison tables for paper inclusion
4. Analyze results for insights on system performance

## Notes

- First run will download datasets (may take time)
- Results are saved incrementally (every 10 problems)
- Can resume interrupted evaluations by checking existing results
- Token costs are tracked per-system for cost analysis

