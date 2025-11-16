# Benchmark Evaluation Report

Generated: N/A

## Performance Comparison (Table 1)

```
====================================================================================================
Table 1: Comparing MAS systems across benchmarks. Accuracy (%)
====================================================================================================

Method               MMLU            ARC-Challenge   GPQA-Diamond    BBH             MATH            GSM8K           Avg.      
----------------------------------------------------------------------------------------------------
CoT                           80.00%          40.00%            N/A            N/A            N/A          20.00%     46.67%
Static MAS                    25.00%           0.00%            N/A            N/A            N/A            N/A     12.50%
orig_impl_bMAS                60.00%           0.00%            N/A            N/A            N/A           0.00%     20.00%
LbMAS                         75.00%           0.00%            N/A            N/A            N/A           0.00%     25.00%

====================================================================================================
```

## Detailed Results by Benchmark

### MMLU

| System | Accuracy | Total Tokens | Avg Time | Avg Rounds |
|--------|----------|--------------|----------|------------|
| bMAS (LbMAS) | 75.00% | 30,290 | 111.70s | 3.50 |
| orig_impl_bMAS | 60.00% | 46,750 | 105.45s | 3.60 |
| Static MAS | 25.00% | 17,217 | 37.37s | 1.00 |
| Chain-of-Thought (CoT) | 80.00% | 4,216 | 13.21s | 1.00 |

### ARC_CHALLENGE

| System | Accuracy | Total Tokens | Avg Time | Avg Rounds |
|--------|----------|--------------|----------|------------|
| bMAS (LbMAS) | 0.00% | 60,221 | 112.44s | 3.40 |
| orig_impl_bMAS | 0.00% | 32,743 | 102.57s | 3.40 |
| Static MAS | 0.00% | 17,220 | 42.91s | 1.00 |
| Chain-of-Thought (CoT) | 40.00% | 8,106 | 18.45s | 1.00 |

### GSM8K

| System | Accuracy | Total Tokens | Avg Time | Avg Rounds |
|--------|----------|--------------|----------|------------|
| bMAS (LbMAS) | 0.00% | 23,870 | 72.65s | 2.20 |
| orig_impl_bMAS | 0.00% | 24,058 | 88.01s | 3.40 |
| Chain-of-Thought (CoT) | 20.00% | 2,789 | 12.07s | 1.00 |
