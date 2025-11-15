"""
Simple test with just one aggregation method to verify Static MAS works.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from static_mas.run_experiment import run_static_experiment


def test_simple():
    """Run a simple test with one problem and one aggregation method."""
    print("="*80)
    print("SIMPLE STATIC MAS TEST")
    print("="*80)
    
    # Simple math problem
    problem = "What is 2 + 2?"
    ground_truth = "4"
    
    print(f"\nProblem: {problem}")
    print(f"Ground Truth: {ground_truth}")
    print("\nRunning Static MAS with majority_vote aggregation...")
    print("-"*80)
    
    try:
        result = run_static_experiment(
            problem=problem,
            ground_truth=ground_truth,
            aggregation_method="majority_vote",
            enable_logging=True
        )
        
        print("\n" + "="*80)
        print("RESULTS")
        print("="*80)
        print(f"Final Answer: {result.get('final_answer', 'N/A')}")
        print(f"Ground Truth: {ground_truth}")
        print(f"Correct: {result.get('correct', False)}")
        print(f"Total Tokens: {result.get('total_tokens', 0)}")
        print(f"Execution Time: {result.get('execution_time', 0):.2f} seconds")
        print(f"Number of Agents: {len(result.get('agents', []))}")
        print("="*80)
        
        return result
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    test_simple()

