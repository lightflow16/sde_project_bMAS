# Benchmark Evaluation Guide

This guide explains how to validate your 4 MAS systems against the benchmarks suggested in the paper.

## Quick Start

### 1. Verify Setup

First, test that everything is configured correctly:

```bash
python benchmark_evaluator/test_setup.py
```

This will verify:
- Required libraries are installed
- All 4 MAS systems are available
- Benchmark loader works
- Answer evaluator functions correctly

### 2. Run a Small Test

Start with a small evaluation to verify everything works:

```bash
# Quick test script (5 problems from each benchmark)
python run_quick_benchmark_test.py

# Or test with MATH benchmark, 5 problems (default is 10)
python run_benchmark_evaluation.py --benchmark math --sample 5

# Default runs 10 problems (good for testing)
python run_benchmark_evaluation.py --benchmark math
```

This will:
- Load 5 problems from MATH dataset
- Run all 4 systems on each problem
- Generate results and summary

### 3. Run Full Benchmarks

Once verified, run full evaluations:

```bash
# Run all benchmarks with 50 problems each (for testing)
python run_benchmark_evaluation.py --all --max-problems 50

# Or run specific benchmarks with full dataset
python run_benchmark_evaluation.py --benchmark math
python run_benchmark_evaluation.py --benchmark mmlu
```

## Available Benchmarks

| Benchmark | Type | Problems | Description |
|-----------|------|----------|-------------|
| **MMLU** | Multiple-choice | 1,140 | General knowledge across 57 tasks |
| **ARC-Challenge** | Multiple-choice | 1,172 | Hard science reasoning |
| **GPQA-Diamond** | Multiple-choice | 198 | Graduate-level science QA |
| **BBH** | Free-form | 250 | Symbolic reasoning tasks |
| **MATH** | Free-form | 500 | Math word problems |
| **GSM8K** | Free-form | 1,319 | Grade-school math problems |

## Systems Evaluated

1. **bMAS (LbMAS)** - Your blackboard-based MAS with paper-style prompts
2. **orig_impl_bMAS** - Original implementation with original prompts  
3. **Static MAS** - Parallel single-pass MAS with majority voting
4. **Chain-of-Thought (CoT)** - Single-agent baseline

## Output Files

Results are saved in `benchmark_evaluator/results/`:

### Per-Benchmark Files
- `{benchmark}_{system}_results.json` - Detailed results for each system
- `{benchmark}_summary.json` - Aggregated summary
- `{benchmark}_summary.txt` - Human-readable summary

### Comparison Tables
- `table1_performance.txt` - Performance comparison (like paper Table 1)
- `table3_token_cost.txt` - Token cost comparison (like paper Table 3)
- `benchmark_report.md` - Comprehensive markdown report

## Metrics Tracked

For each system and benchmark:

- **Accuracy** (%): Percentage of correct answers
- **Token Usage**: 
  - Prompt tokens
  - Completion tokens
  - Total tokens
- **Execution Time**: Total and average per problem
- **Rounds to Consensus**: Average rounds (for iterative systems)
- **Consensus Rate**: % of problems reaching consensus

## Example Usage

### Run Single Benchmark

```bash
# MMLU with 5 sample problems (recommended for testing)
python run_benchmark_evaluation.py --benchmark mmlu --sample 5

# MATH with 10 problems (default)
python run_benchmark_evaluation.py --benchmark math

# MATH with all problems (WARNING: will take very long!)
python run_benchmark_evaluation.py --benchmark math --max-problems 999999
```

### Run Specific Systems

```bash
# Only test bMAS and Static MAS with 5 sample problems
python run_benchmark_evaluation.py --benchmark math --systems bMAS static_mas --sample 5
```

### Adjust Max Rounds

```bash
# Use 6 rounds instead of default 4
python run_benchmark_evaluation.py --benchmark math --max-rounds 6
```

### Generate Tables from Existing Results

```bash
# If you've already run evaluations, generate tables
python run_benchmark_evaluation.py --generate-tables
```

## Understanding Results

### Performance Table (Table 1)

Shows accuracy across all benchmarks:

```
Method              MMLU    ARC-Challenge   GPQA-Diamond   BBH    MATH    GSM8K   Avg.
CoT                 81.31   92.74          35.35          81.20  62.20   94.84   74.60%
Static MAS          81.84   90.35          44.44          85.60  65.80   93.85   76.98%
LbMAS               85.35   93.43          54.04          90.00  72.60   94.46   81.68%
```

### Token Cost Table (Table 3)

Shows token usage and performance for a specific benchmark:

```
Method              Prompt Token    Completion Token   Total Token    Performance
CoT                     5,475,154        2,853,618     8,328,772        60.40%
Static MAS              1,351,821          820,069     2,171,890        65.80%
LbMAS                   3,352,594        1,013,015     4,721,489        72.60% **
```

** = Best performance

## Paper Alignment

This framework aligns with the paper's evaluation protocol:

- ✅ **Temperature**: 0.7 (set in `config.py`)
- ✅ **Max Rounds**: 4 (configurable via `--max-rounds`)
- ✅ **Random Model Assignment**: Per-agent LLM backend assignment
- ✅ **Answer Formats**: Supports both multiple-choice and free-form
- ✅ **Metrics**: Accuracy, token cost, throughput, consensus rate
- ✅ **Table Formats**: Matches paper Table 1 and Table 3

## Troubleshooting

### Dataset Loading Issues

If datasets fail to load from Hugging Face:

1. Check internet connection
2. Verify `datasets` library: `pip install datasets`
3. Datasets are cached after first download

### Memory Issues

For large benchmarks, limit problems:

```bash
python run_benchmark_evaluation.py --all --max-problems 10
```

### System Errors

If a specific system fails:

1. Check logs in `benchmark_evaluator/results/`
2. Test system individually:
   ```bash
   python run_benchmark_evaluation.py --benchmark math --systems bMAS
   ```

### Slow Execution

- Start with small `--max-problems` values
- Use `--systems` to test one system at a time
- Results are saved incrementally (every 10 problems)

## Next Steps

1. **Initial Test**: Run with 5-10 problems per benchmark
2. **Scale Up**: Increase to 50-100 problems for meaningful results
3. **Full Evaluation**: Run complete benchmarks for final results
4. **Generate Tables**: Use `--generate-tables` to create comparison tables
5. **Analyze**: Review results in `benchmark_report.md`

## Tips

- **Start Small**: Test with `--max-problems 5` first
- **Save Progress**: Results are saved incrementally
- **Resume**: Can check existing results without re-running
- **Compare**: Use `--generate-tables` to compare across runs
- **Focus**: Use `--systems` to focus on specific systems

## Example Workflow

```bash
# 1. Test setup
python benchmark_evaluator/test_setup.py

# 2. Quick test (5 problems from each benchmark)
python run_quick_benchmark_test.py

# 3. Small test run on specific benchmark
python run_benchmark_evaluation.py --benchmark math --sample 5

# 4. Check results
cat benchmark_evaluator/results/math_summary.txt

# 5. Run with more samples (one benchmark at a time)
python run_benchmark_evaluation.py --benchmark math --sample 20

# 6. Generate comparison tables
python run_benchmark_evaluation.py --generate-tables

# 7. Review report
cat benchmark_evaluator/results/benchmark_report.md
```

## Quick Testing

For fastest testing, use the quick test script:

```bash
python run_quick_benchmark_test.py
```

This runs 5 problems from each benchmark across all systems - perfect for validating everything works before running larger evaluations.

## Support

For issues or questions:
1. Check `benchmark_evaluator/README.md` for detailed documentation
2. Review error logs in `benchmark_evaluator/results/`
3. Test individual components with `test_setup.py`

