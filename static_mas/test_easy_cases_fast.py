"""
Fast version: Run easy cases with just one aggregation method (majority_vote).
This is faster than running all 4 aggregation methods.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from static_mas.run_experiment import run_static_experiment


def test_case_a_fast():
    """Case A: Mathematical Problem - Fast version with one aggregation method."""
    print("="*80)
    print("STATIC MAS - TEST CASE A: Mathematical Problem (FAST)")
    print("="*80)
    
    problem = "In the land of Ink, the money system is unique. One Trinket is equal to 4 Blinkets, and 3 Blinkets are equal to 7 Drinkets. In Trinkets, what is the value of 56 Drinkets?"
    ground_truth = "6 Trinkets"
    
    print(f"\nProblem: {problem}")
    print(f"Ground Truth: {ground_truth}")
    print("\nRunning Static MAS with majority_vote aggregation...")
    print("-"*80)
    
    result = run_static_experiment(
        problem=problem,
        ground_truth=ground_truth,
        aggregation_method="majority_vote",
        enable_logging=True
    )
    
    print("\n" + "="*80)
    print("CASE A RESULTS - STATIC MAS")
    print("="*80)
    print(f"Final Answer: {result.get('final_answer', 'N/A')}")
    print(f"Ground Truth: {ground_truth}")
    print(f"Correct: {result.get('correct', False)}")
    print(f"Total Tokens: {result.get('total_tokens', 0)}")
    print(f"Execution Time: {result.get('execution_time', 0):.2f} seconds")
    print(f"Number of Agents: {len(result.get('agents', []))}")
    
    print(f"\nAgent Answers:")
    for agent_result in result.get('agent_results', []):
        if not agent_result.get('error'):
            answer_preview = str(agent_result.get('answer', 'N/A'))[:60]
            print(f"  - {agent_result.get('agent', 'N/A')} ({agent_result.get('role', 'N/A')}): {answer_preview}... [Conf: {agent_result.get('confidence', 0.0):.2f}]")
    
    print("\n" + "="*80)
    return result


def test_case_b_fast():
    """Case B: Common Knowledge Question - Fast version."""
    print("\n" + "="*80)
    print("STATIC MAS - TEST CASE B: Common Knowledge Question (FAST)")
    print("="*80)
    
    problem = "Why is the sky blue? A) Because the molecules that compose the Earth's atmosphere have a blue-ish color. B) Because the sky reflects the color of the Earth's oceans. C) Because the atmosphere preferentially scatters short wavelengths. D) Because the Earth's atmosphere preferentially absorbs all other colors."
    ground_truth = "C"
    
    print(f"\nProblem: {problem}")
    print(f"Ground Truth: {ground_truth}")
    print("\nRunning Static MAS with majority_vote aggregation...")
    print("-"*80)
    
    result = run_static_experiment(
        problem=problem,
        ground_truth=ground_truth,
        aggregation_method="majority_vote",
        enable_logging=True
    )
    
    print("\n" + "="*80)
    print("CASE B RESULTS - STATIC MAS")
    print("="*80)
    print(f"Final Answer: {result.get('final_answer', 'N/A')}")
    print(f"Ground Truth: {ground_truth}")
    print(f"Correct: {result.get('correct', False)}")
    print(f"Total Tokens: {result.get('total_tokens', 0)}")
    print(f"Execution Time: {result.get('execution_time', 0):.2f} seconds")
    print(f"Number of Agents: {len(result.get('agents', []))}")
    
    print(f"\nAgent Answers:")
    for agent_result in result.get('agent_results', []):
        if not agent_result.get('error'):
            answer_preview = str(agent_result.get('answer', 'N/A'))[:60]
            print(f"  - {agent_result.get('agent', 'N/A')} ({agent_result.get('role', 'N/A')}): {answer_preview}... [Conf: {agent_result.get('confidence', 0.0):.2f}]")
    
    print("\n" + "="*80)
    return result


if __name__ == "__main__":
    print("\n" + "="*80)
    print("STATIC MAS - EASY CASES (FAST VERSION)")
    print("="*80)
    print("\nRunning with majority_vote aggregation only (faster).")
    print("For full comparison with all methods, use: python static_mas/test_easy_cases.py")
    print("="*80 + "\n")
    
    result_a = test_case_a_fast()
    result_b = test_case_b_fast()
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Case A - Correct: {result_a.get('correct', False)}, Tokens: {result_a.get('total_tokens', 0)}, Time: {result_a.get('execution_time', 0):.2f}s")
    print(f"Case B - Correct: {result_b.get('correct', False)}, Tokens: {result_b.get('total_tokens', 0)}, Time: {result_b.get('execution_time', 0):.2f}s")
    print("\nTrace files saved in: static_mas/outputs/")
    print("="*80)

