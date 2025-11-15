"""
Test script to run the same easy cases with Static MAS.
Compares Static MAS performance with LbMAS on the same problems.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from static_mas.run_experiment import run_static_experiment


def test_case_a():
    """
    Case a) Mathematical Problem: Converting Drinkets to Trinkets
    Static MAS: All agents process in parallel, then aggregate
    """
    print("="*80)
    print("STATIC MAS - TEST CASE A: Mathematical Problem")
    print("="*80)
    
    problem = "In the land of Ink, the money system is unique. One Trinket is equal to 4 Blinkets, and 3 Blinkets are equal to 7 Drinkets. In Trinkets, what is the value of 56 Drinkets?"
    ground_truth = "6 Trinkets"
    
    print(f"\nProblem: {problem}")
    print(f"Ground Truth: {ground_truth}")
    print("\nRunning Static MAS with all agents in parallel...")
    print("-"*80)
    
    # Test with different aggregation methods
    aggregation_methods = ["majority_vote", "decider_based", "most_confident", "weighted_average"]
    
    results = {}
    for method in aggregation_methods:
        print(f"\n[{method}] Running experiment...")
        result = run_static_experiment(
            problem=problem,
            ground_truth=ground_truth,
            aggregation_method=method,
            enable_logging=True
        )
        results[method] = result
    
    # Print summary
    print("\n" + "="*80)
    print("CASE A RESULTS - STATIC MAS")
    print("="*80)
    print(f"Problem: {problem}")
    print(f"Ground Truth: {ground_truth}\n")
    
    for method, result in results.items():
        print(f"\nAggregation Method: {method}")
        print(f"  Final Answer: {result.get('final_answer', 'N/A')}")
        print(f"  Correct: {result.get('correct', False)}")
        print(f"  Total Tokens: {result.get('total_tokens', 0)}")
        print(f"  Execution Time: {result.get('execution_time', 0):.2f} seconds")
        print(f"  Number of Agents: {len(result.get('agents', []))}")
        
        # Show agent answers
        print(f"  Agent Answers:")
        for agent_result in result.get('agent_results', []):
            answer_preview = str(agent_result.get('answer', 'N/A'))[:50]
            print(f"    - {agent_result.get('agent', 'N/A')} ({agent_result.get('role', 'N/A')}): {answer_preview}... [Conf: {agent_result.get('confidence', 0.0):.2f}]")
    
    print("\n" + "="*80)
    print(f"Trace files saved in: static_mas/outputs/")
    print("="*80)
    
    return results


def test_case_b():
    """
    Case b) Common Knowledge Question: Why is the sky blue?
    Static MAS: All agents process in parallel, then aggregate
    """
    print("\n" + "="*80)
    print("STATIC MAS - TEST CASE B: Common Knowledge Question")
    print("="*80)
    
    problem = "Why is the sky blue? A) Because the molecules that compose the Earth's atmosphere have a blue-ish color. B) Because the sky reflects the color of the Earth's oceans. C) Because the atmosphere preferentially scatters short wavelengths. D) Because the Earth's atmosphere preferentially absorbs all other colors."
    ground_truth = "C"
    
    print(f"\nProblem: {problem}")
    print(f"Ground Truth: {ground_truth}")
    print("\nRunning Static MAS with all agents in parallel...")
    print("-"*80)
    
    # Test with different aggregation methods
    aggregation_methods = ["majority_vote", "decider_based", "most_confident", "weighted_average"]
    
    results = {}
    for method in aggregation_methods:
        print(f"\n[{method}] Running experiment...")
        result = run_static_experiment(
            problem=problem,
            ground_truth=ground_truth,
            aggregation_method=method,
            enable_logging=True
        )
        results[method] = result
    
    # Print summary
    print("\n" + "="*80)
    print("CASE B RESULTS - STATIC MAS")
    print("="*80)
    print(f"Problem: {problem}")
    print(f"Ground Truth: {ground_truth}\n")
    
    for method, result in results.items():
        print(f"\nAggregation Method: {method}")
        print(f"  Final Answer: {result.get('final_answer', 'N/A')}")
        print(f"  Correct: {result.get('correct', False)}")
        print(f"  Total Tokens: {result.get('total_tokens', 0)}")
        print(f"  Execution Time: {result.get('execution_time', 0):.2f} seconds")
        print(f"  Number of Agents: {len(result.get('agents', []))}")
        
        # Show agent answers
        print(f"  Agent Answers:")
        for agent_result in result.get('agent_results', []):
            answer_preview = str(agent_result.get('answer', 'N/A'))[:50]
            print(f"    - {agent_result.get('agent', 'N/A')} ({agent_result.get('role', 'N/A')}): {answer_preview}... [Conf: {agent_result.get('confidence', 0.0):.2f}]")
    
    print("\n" + "="*80)
    print(f"Trace files saved in: static_mas/outputs/")
    print("="*80)
    
    return results


def compare_with_lbmas():
    """Compare Static MAS results with LbMAS if available."""
    print("\n" + "="*80)
    print("COMPARISON SUMMARY")
    print("="*80)
    print("\nTo compare with LbMAS results:")
    print("1. Run: python test_easy_cases.py  (for LbMAS)")
    print("2. Compare token usage, accuracy, and execution time")
    print("3. Check trace files in outputs/ and static_mas/outputs/")
    print("="*80)


if __name__ == "__main__":
    print("\n" + "="*80)
    print("STATIC MAS - EASY CASES DEMONSTRATION")
    print("="*80)
    print("\nThis script runs the same test cases as LbMAS:")
    print("  Case A: Mathematical problem (Drinkets to Trinkets conversion)")
    print("  Case B: Common knowledge question (Why is the sky blue?)")
    print("\nStatic MAS processes all agents in parallel (single pass).")
    print("Results will be compared across different aggregation methods.")
    print("="*80 + "\n")
    
    # Run both test cases
    results_a = test_case_a()
    results_b = test_case_b()
    
    # Print comparison info
    compare_with_lbmas()
    
    print("\n" + "="*80)
    print("ALL STATIC MAS TESTS COMPLETE")
    print("="*80)
    print("\nKey Differences from LbMAS:")
    print("  - Single pass (no iteration)")
    print("  - All agents execute in parallel")
    print("  - No blackboard communication")
    print("  - Fixed agent roles")
    print("  - Multiple aggregation methods tested")
    print("\nCheck the output files for detailed logs:")
    print("  - static_mas/outputs/static_mas_trace_*.json")
    print("  - static_mas/outputs/static_mas_report_*.txt")
    print("="*80)

