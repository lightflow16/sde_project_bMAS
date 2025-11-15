"""
Test script to demonstrate the two easy cases from the paper.
"""
import sys
import os

# Add current directory to path for imports
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from experiment_runner.run_experiment import run_single_experiment
from utils.logger import ExperimentLogger


def test_case_a():
    """
    Case a) Mathematical Problem: Converting Drinkets to Trinkets
    Expected flow: Planner -> Mathematician/Data Analyst -> Cleaner -> Decider
    """
    print("="*80)
    print("TEST CASE A: Mathematical Problem")
    print("="*80)
    
    problem = "In the land of Ink, the money system is unique. One Trinket is equal to 4 Blinkets, and 3 Blinkets are equal to 7 Drinkets. In Trinkets, what is the value of 56 Drinkets?"
    ground_truth = "6 Trinkets"
    
    logger = ExperimentLogger(experiment_id="case_a_mathematical")
    
    result = run_single_experiment(
        problem=problem,
        max_rounds=4,
        ground_truth=ground_truth,
        enable_logging=True,
        logger=logger
    )
    
    print("\n" + "="*80)
    print("CASE A RESULTS")
    print("="*80)
    print(f"Problem: {problem}")
    print(f"Final Answer: {result.get('final_answer', 'N/A')}")
    print(f"Ground Truth: {ground_truth}")
    print(f"Correct: {result.get('correct', False)}")
    print(f"Solution Ready: {result.get('is_solution_ready', False)}")
    print(f"Total Tokens: {result.get('total_tokens', 0)}")
    print(f"Rounds: {len(result.get('rounds', []))}")
    print(f"\nTrace JSON: {result.get('trace_json', 'N/A')}")
    print(f"Trace Report: {result.get('trace_txt', 'N/A')}")
    print("="*80)
    
    return result


def test_case_b():
    """
    Case b) Common Knowledge Question: Why is the sky blue?
    Expected flow: Expert agents (Atmospheric Physicist, Optics Scientist, Meteorologist) -> Decider
    """
    print("\n" + "="*80)
    print("TEST CASE B: Common Knowledge Question")
    print("="*80)
    
    problem = "Why is the sky blue? A) Because the molecules that compose the Earth's atmosphere have a blue-ish color. B) Because the sky reflects the color of the Earth's oceans. C) Because the atmosphere preferentially scatters short wavelengths. D) Because the Earth's atmosphere preferentially absorbs all other colors."
    ground_truth = "C"
    
    logger = ExperimentLogger(experiment_id="case_b_common_knowledge")
    
    result = run_single_experiment(
        problem=problem,
        max_rounds=4,
        ground_truth=ground_truth,
        enable_logging=True,
        logger=logger
    )
    
    print("\n" + "="*80)
    print("CASE B RESULTS")
    print("="*80)
    print(f"Problem: {problem}")
    print(f"Final Answer: {result.get('final_answer', 'N/A')}")
    print(f"Ground Truth: {ground_truth}")
    print(f"Correct: {result.get('correct', False)}")
    print(f"Solution Ready: {result.get('is_solution_ready', False)}")
    print(f"Total Tokens: {result.get('total_tokens', 0)}")
    print(f"Rounds: {len(result.get('rounds', []))}")
    print(f"\nTrace JSON: {result.get('trace_json', 'N/A')}")
    print(f"Trace Report: {result.get('trace_txt', 'N/A')}")
    print("="*80)
    
    return result


def print_agent_flow(result):
    """Print a visual representation of the agent flow."""
    import sys
    import io
    
    # Set UTF-8 encoding for output
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print("\n" + "="*80)
    print("AGENT EXECUTION FLOW")
    print("="*80)
    
    for round_entry in result.get('rounds', []):
        print(f"\nRound {round_entry['round']}:")
        print(f"  Selected Agents: {', '.join(round_entry['selected_agents'])}")
        
        for output in round_entry.get('agent_outputs', []):
            agent_name = output.get('agent', 'unknown')
            response_preview = str(output.get('raw_response', ''))[:150]
            # Replace problematic characters
            response_preview = response_preview.encode('ascii', errors='replace').decode('ascii')
            print(f"    -> {agent_name}: {response_preview}...")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    print("\n" + "="*80)
    print("LbMAS EASY CASES DEMONSTRATION")
    print("="*80)
    print("\nThis script demonstrates the two easy cases from the paper:")
    print("  Case A: Mathematical problem (Drinkets to Trinkets conversion)")
    print("  Case B: Common knowledge question (Why is the sky blue?)")
    print("\nFull traces with prompts, responses, and agent flows will be saved.")
    print("="*80 + "\n")
    
    # Run both test cases
    result_a = test_case_a()
    print_agent_flow(result_a)
    
    result_b = test_case_b()
    print_agent_flow(result_b)
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETE")
    print("="*80)
    print(f"\nCase A Trace: {result_a.get('trace_txt', 'N/A')}")
    print(f"Case B Trace: {result_b.get('trace_txt', 'N/A')}")
    print("\nCheck the output files for detailed logs including:")
    print("  - All prompts sent to agents")
    print("  - All agent responses")
    print("  - Agent selection reasoning")
    print("  - Blackboard state at each round")
    print("  - Complete execution trace")
    print("="*80)

