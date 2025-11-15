"""
Fast version: Run easy cases with Chain-of-Thought baseline.

This script runs the two easy test cases from the paper using a single-agent
Chain-of-Thought approach with "Let's think step by step." prompting.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cot.run_experiment import run_cot_experiment


def test_case_a_fast():
    """Case A: Mathematical Problem - CoT baseline."""
    print("="*80)
    print("CHAIN-OF-THOUGHT BASELINE - TEST CASE A: Mathematical Problem")
    print("="*80)
    
    problem = "In the land of Ink, the money system is unique. One Trinket is equal to 4 Blinkets, and 3 Blinkets are equal to 7 Drinkets. In Trinkets, what is the value of 56 Drinkets?"
    ground_truth = "6 Trinkets"
    
    print(f"\nProblem: {problem}")
    print(f"Ground Truth: {ground_truth}")
    print("\nRunning Chain-of-Thought baseline...")
    print("-"*80)
    
    result = run_cot_experiment(
        problem=problem,
        ground_truth=ground_truth,
        enable_logging=True
    )
    
    print("\n" + "="*80)
    print("CASE A RESULTS - CHAIN-OF-THOUGHT BASELINE")
    print("="*80)
    print(f"Final Answer: {result.get('final_answer', 'N/A')}")
    print(f"Ground Truth: {ground_truth}")
    print(f"Correct: {result.get('correct', False)}")
    print(f"Model Backend: {result.get('model_backend', 'N/A')}")
    print(f"Total Tokens: {result.get('tokens_used', 0)}")
    print(f"Execution Time: {result.get('execution_time', 0):.2f} seconds")
    
    if result.get('reasoning'):
        reasoning_preview = result['reasoning'][:200]
        print(f"\nReasoning Preview: {reasoning_preview}...")
    
    print("\n" + "="*80)
    return result


def test_case_b_fast():
    """Case B: Common Knowledge Question - CoT baseline."""
    print("\n" + "="*80)
    print("CHAIN-OF-THOUGHT BASELINE - TEST CASE B: Common Knowledge Question")
    print("="*80)
    
    problem = "Why is the sky blue? A) Because the molecules that compose the Earth's atmosphere have a blue-ish color. B) Because the sky reflects the color of the Earth's oceans. C) Because the atmosphere preferentially scatters short wavelengths. D) Because the Earth's atmosphere preferentially absorbs all other colors."
    ground_truth = "C"
    
    print(f"\nProblem: {problem}")
    print(f"Ground Truth: {ground_truth}")
    print("\nRunning Chain-of-Thought baseline...")
    print("-"*80)
    
    result = run_cot_experiment(
        problem=problem,
        ground_truth=ground_truth,
        enable_logging=True
    )
    
    print("\n" + "="*80)
    print("CASE B RESULTS - CHAIN-OF-THOUGHT BASELINE")
    print("="*80)
    print(f"Final Answer: {result.get('final_answer', 'N/A')}")
    print(f"Ground Truth: {ground_truth}")
    print(f"Correct: {result.get('correct', False)}")
    print(f"Model Backend: {result.get('model_backend', 'N/A')}")
    print(f"Total Tokens: {result.get('tokens_used', 0)}")
    print(f"Execution Time: {result.get('execution_time', 0):.2f} seconds")
    
    if result.get('reasoning'):
        reasoning_preview = result['reasoning'][:200]
        print(f"\nReasoning Preview: {reasoning_preview}...")
    
    print("\n" + "="*80)
    return result


if __name__ == "__main__":
    print("\n" + "="*80)
    print("CHAIN-OF-THOUGHT (CoT) BASELINE - EASY CASES")
    print("="*80)
    print("\nThis script runs the two easy test cases using a single-agent")
    print("Chain-of-Thought approach with 'Let's think step by step.' prompting.")
    print("="*80 + "\n")
    
    result_a = test_case_a_fast()
    result_b = test_case_b_fast()
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Case A - Correct: {result_a.get('correct', False)}, Tokens: {result_a.get('tokens_used', 0)}, Time: {result_a.get('execution_time', 0):.2f}s, Model: {result_a.get('model_backend', 'N/A')}")
    print(f"Case B - Correct: {result_b.get('correct', False)}, Tokens: {result_b.get('tokens_used', 0)}, Time: {result_b.get('execution_time', 0):.2f}s, Model: {result_b.get('model_backend', 'N/A')}")
    print("\nTrace files saved in: cot/outputs/")
    print("="*80)

