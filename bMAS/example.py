"""
Simple example script to test the LbMAS system.
"""
import os
import sys

# Add current directory to path for imports
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from experiment_runner.run_experiment import run_single_experiment

if __name__ == "__main__":
    # Test with a simple problem
    problem = "What is 2 + 2? Explain your reasoning."
    
    print("Running LbMAS experiment...")
    print(f"Problem: {problem}\n")
    
    result = run_single_experiment(problem, max_rounds=3)
    
    print("\n" + "="*60)
    print("FINAL RESULT")
    print("="*60)
    print(f"Final Answer: {result.get('final_answer', 'N/A')}")
    print(f"Solution Ready: {result.get('is_solution_ready', False)}")
    print(f"Total Tokens: {result.get('total_tokens', 0)}")
    print(f"Rounds: {len(result.get('rounds', []))}")
    print("="*60)

