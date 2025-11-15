# Test Case A Comparison Results - All MAS Setups

**Date:** November 15, 2025  
**Test Case:** Case A - Mathematical Problem (Drinkets to Trinkets conversion)

## Problem
"In the land of Ink, the money system is unique. One Trinket is equal to 4 Blinkets, and 3 Blinkets are equal to 7 Drinkets. In Trinkets, what is the value of 56 Drinkets?"

**Ground Truth:** 6 Trinkets

---

## Results Summary

| System | Final Answer | Correct | Tokens | Time (s) | Rounds |
|--------|-------------|---------|--------|----------|--------|
| **bMAS (LbMAS)** | Solution ready: False, Final answer: N/A | ❌ NO | 6,289 | 124.31 | 4 |
| **Static MAS** | 6 Trinkets (extracted from JSON) | ✅ YES | 6,481 | 65.82 | 1 |
| **Chain-of-Thought (CoT)** | $\boxed{6}$ | ✅ YES | 681 | 10.16 | 1 |

---

## Detailed Analysis

### 1. Accuracy
- **Correct:** Static MAS, Chain-of-Thought (CoT)
- **Incorrect:** bMAS (LbMAS) - Failed to produce a final answer

**Analysis:**
- bMAS went through 4 rounds but did not reach a solution-ready state
- Static MAS successfully aggregated agent responses and extracted the correct answer
- CoT baseline solved the problem correctly in a single pass

### 2. Token Efficiency

**Most Efficient:** Chain-of-Thought (CoT) - **681 tokens**

| System | Tokens | Difference | Percentage Increase |
|--------|--------|-------------|---------------------|
| CoT | 681 | Baseline | - |
| bMAS | 6,289 | +5,608 | +823.5% |
| Static MAS | 6,481 | +5,800 | +851.7% |

**Analysis:**
- CoT uses **9.2x fewer tokens** than bMAS
- CoT uses **9.5x fewer tokens** than Static MAS
- Multi-agent systems require significantly more tokens due to:
  - Multiple agent prompts and responses
  - Inter-agent communication (bMAS)
  - Aggregation overhead (Static MAS)

### 3. Execution Speed

**Fastest:** Chain-of-Thought (CoT) - **10.16 seconds**

| System | Time (s) | Difference | Percentage Increase |
|--------|----------|------------|---------------------|
| CoT | 10.16 | Baseline | - |
| Static MAS | 65.82 | +55.66 | +547.7% |
| bMAS | 124.31 | +114.14 | +1123.1% |

**Analysis:**
- CoT is **6.5x faster** than Static MAS
- CoT is **12.2x faster** than bMAS
- Static MAS is **1.9x faster** than bMAS (parallel execution vs iterative)

### 4. Architecture Comparison

| Aspect | bMAS (LbMAS) | Static MAS | CoT |
|--------|--------------|------------|-----|
| **Execution Model** | Iterative (4 rounds) | Single-pass parallel | Single-pass |
| **Communication** | Blackboard-based | None (independent) | N/A |
| **Agent Selection** | Dynamic (control unit) | All agents execute | Single agent |
| **Number of Agents** | Variable (multiple per round) | 7 fixed agents | 1 |
| **Solution Status** | Failed to converge | Successfully aggregated | Solved directly |

---

## Key Observations

### bMAS (LbMAS) Issues
1. **Failed to converge:** Despite 4 rounds of execution, the system did not produce a final answer
2. **High overhead:** Most expensive in both tokens and time
3. **Complexity:** Multi-round iterative process with blackboard communication may have led to confusion

### Static MAS Performance
1. **Correct answer:** Successfully aggregated responses from 7 agents
2. **Efficiency:** Faster than bMAS due to parallel execution
3. **Answer extraction:** Final answer includes JSON formatting that should be cleaned

### Chain-of-Thought Baseline
1. **Best performance:** Most efficient and fastest
2. **Correct answer:** Solved the problem correctly
3. **Simplicity:** Single-agent approach works well for straightforward mathematical problems

---

## Conclusions

1. **For this test case (mathematical problem):**
   - CoT baseline performs best in terms of efficiency and speed
   - Static MAS achieves correct answer but with significant overhead
   - bMAS failed to produce a solution

2. **Trade-offs:**
   - **CoT:** Best for simple, well-defined problems
   - **Static MAS:** Good for problems requiring multiple perspectives, but with overhead
   - **bMAS:** May be better for complex problems requiring iterative refinement, but failed here

3. **Recommendations:**
   - Investigate why bMAS failed to converge
   - Improve answer extraction in Static MAS to remove JSON formatting
   - Consider when multi-agent overhead is justified vs. simple CoT

---

## Trace Files

Detailed execution traces are available in:
- **bMAS:** `outputs/trace_comparison_case_a_bmas.json` and `outputs/report_comparison_case_a_bmas.txt`
- **Static MAS:** `static_mas/outputs/static_mas_trace_*.json` and `static_mas/outputs/static_mas_report_*.txt`
- **CoT:** `cot/outputs/cot_trace_*.json` and `cot/outputs/cot_report_*.txt`

