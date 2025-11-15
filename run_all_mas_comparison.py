"""
Run the easy test case (Case A) across all MAS setups and compare results.
"""
import sys
import os
import time

# Add paths for imports
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

# Import test functions from each MAS setup
from bMAS.experiment_runner.run_experiment import run_single_experiment as run_bmas
from bMAS.utils.logger import ExperimentLogger
from orig_impl_bMAS.experiment_runner.run_experiment import run_single_experiment as run_orig_bmas
from orig_impl_bMAS.utils.logger import ExperimentLogger as OrigExperimentLogger
from static_mas.run_experiment import run_static_experiment
from cot.run_experiment import run_cot_experiment

# Test case definition
PROBLEM = "In the land of Ink, the money system is unique. One Trinket is equal to 4 Blinkets, and 3 Blinkets are equal to 7 Drinkets. In Trinkets, what is the value of 56 Drinkets?"
GROUND_TRUTH = "6 Trinkets"


def run_orig_bmas_test():
    """Run Case A with orig_impl_bMAS (Original Implementation Prompts)."""
    print("\n" + "="*80)
    print("RUNNING orig_impl_bMAS (Original Prompts) - TEST CASE A")
    print("="*80)
    
    logger = OrigExperimentLogger(experiment_id="comparison_case_a_orig_bmas")
    
    start_time = time.time()
    result = run_orig_bmas(
        problem=PROBLEM,
        max_rounds=4,
        ground_truth=GROUND_TRUTH,
        enable_logging=True,
        logger=logger
    )
    execution_time = time.time() - start_time
    
    # Extract metrics
    metrics = {
        'system': 'orig_impl_bMAS (Original Prompts)',
        'final_answer': result.get('final_answer', 'N/A'),
        'correct': result.get('correct', False),
        'total_tokens': result.get('total_tokens', 0),
        'execution_time': execution_time,
        'rounds': len(result.get('rounds', [])),
        'solution_ready': result.get('is_solution_ready', False),
        'trace_json': result.get('trace_json', 'N/A'),
        'trace_txt': result.get('trace_txt', 'N/A')
    }
    
    print(f"\nFinal Answer: {metrics['final_answer']}")
    print(f"Correct: {metrics['correct']}")
    print(f"Total Tokens: {metrics['total_tokens']}")
    print(f"Execution Time: {metrics['execution_time']:.2f} seconds")
    print(f"Rounds: {metrics['rounds']}")
    
    return metrics


def run_bmas_test():
    """Run Case A with bMAS (LbMAS - Paper style prompts)."""
    print("\n" + "="*80)
    print("RUNNING bMAS (LbMAS - Paper Prompts) - TEST CASE A")
    print("="*80)
    
    logger = ExperimentLogger(experiment_id="comparison_case_a_bmas")
    
    start_time = time.time()
    result = run_bmas(
        problem=PROBLEM,
        max_rounds=4,
        ground_truth=GROUND_TRUTH,
        enable_logging=True,
        logger=logger
    )
    execution_time = time.time() - start_time
    
    # Extract metrics
    metrics = {
        'system': 'bMAS (Paper Prompts)',
        'final_answer': result.get('final_answer', 'N/A'),
        'correct': result.get('correct', False),
        'total_tokens': result.get('total_tokens', 0),
        'execution_time': execution_time,
        'rounds': len(result.get('rounds', [])),
        'solution_ready': result.get('is_solution_ready', False),
        'trace_json': result.get('trace_json', 'N/A'),
        'trace_txt': result.get('trace_txt', 'N/A')
    }
    
    print(f"\nFinal Answer: {metrics['final_answer']}")
    print(f"Correct: {metrics['correct']}")
    print(f"Total Tokens: {metrics['total_tokens']}")
    print(f"Execution Time: {metrics['execution_time']:.2f} seconds")
    print(f"Rounds: {metrics['rounds']}")
    
    return metrics


def run_static_mas_test():
    """Run Case A with Static MAS."""
    print("\n" + "="*80)
    print("RUNNING STATIC MAS - TEST CASE A")
    print("="*80)
    
    start_time = time.time()
    result = run_static_experiment(
        problem=PROBLEM,
        ground_truth=GROUND_TRUTH,
        aggregation_method="majority_vote",
        enable_logging=True
    )
    execution_time = time.time() - start_time
    
    # Extract metrics
    metrics = {
        'system': 'Static MAS',
        'final_answer': result.get('final_answer', 'N/A'),
        'correct': result.get('correct', False),
        'total_tokens': result.get('total_tokens', 0),
        'execution_time': execution_time,
        'rounds': 1,  # Static MAS is single-pass
        'num_agents': len(result.get('agents', [])),
        'aggregation_method': 'majority_vote'
    }
    
    print(f"\nFinal Answer: {metrics['final_answer']}")
    print(f"Correct: {metrics['correct']}")
    print(f"Total Tokens: {metrics['total_tokens']}")
    print(f"Execution Time: {metrics['execution_time']:.2f} seconds")
    print(f"Number of Agents: {metrics['num_agents']}")
    
    return metrics


def run_cot_test():
    """Run Case A with Chain-of-Thought baseline."""
    print("\n" + "="*80)
    print("RUNNING CHAIN-OF-THOUGHT BASELINE - TEST CASE A")
    print("="*80)
    
    start_time = time.time()
    result = run_cot_experiment(
        problem=PROBLEM,
        ground_truth=GROUND_TRUTH,
        enable_logging=True
    )
    execution_time = time.time() - start_time
    
    # Extract metrics
    metrics = {
        'system': 'Chain-of-Thought (CoT)',
        'final_answer': result.get('final_answer', 'N/A'),
        'correct': result.get('correct', False),
        'total_tokens': result.get('tokens_used', 0),
        'execution_time': execution_time,
        'rounds': 1,  # CoT is single-pass
        'model_backend': result.get('model_backend', 'N/A')
    }
    
    print(f"\nFinal Answer: {metrics['final_answer']}")
    print(f"Correct: {metrics['correct']}")
    print(f"Total Tokens: {metrics['total_tokens']}")
    print(f"Execution Time: {metrics['execution_time']:.2f} seconds")
    print(f"Model Backend: {metrics['model_backend']}")
    
    return metrics


def compare_results(results):
    """Compare results from all MAS setups."""
    print("\n" + "="*80)
    print("COMPARISON RESULTS - TEST CASE A")
    print("="*80)
    print(f"\nProblem: {PROBLEM}")
    print(f"Ground Truth: {GROUND_TRUTH}\n")
    
    # Print comparison table
    print(f"{'System':<25} {'Answer':<20} {'Correct':<10} {'Tokens':<10} {'Time (s)':<12} {'Rounds':<10}")
    print("-" * 100)
    
    for result in results:
        answer_str = str(result['final_answer'])[:18]
        correct_str = "YES" if result['correct'] else "NO"
        print(f"{result['system']:<25} {answer_str:<20} {correct_str:<10} {result['total_tokens']:<10} {result['execution_time']:<12.2f} {result['rounds']:<10}")
    
    # Find best performers
    print("\n" + "="*80)
    print("PERFORMANCE ANALYSIS")
    print("="*80)
    
    # Accuracy
    correct_systems = [r['system'] for r in results if r['correct']]
    print(f"\nAccuracy:")
    print(f"  Correct: {', '.join(correct_systems) if correct_systems else 'None'}")
    print(f"  Incorrect: {', '.join([r['system'] for r in results if not r['correct']]) if any(not r['correct'] for r in results) else 'None'}")
    
    # Token efficiency
    min_tokens = min(r['total_tokens'] for r in results)
    most_efficient = [r['system'] for r in results if r['total_tokens'] == min_tokens]
    print(f"\nToken Efficiency (fewest tokens):")
    print(f"  Most Efficient: {', '.join(most_efficient)} ({min_tokens} tokens)")
    for r in results:
        if r['total_tokens'] != min_tokens:
            diff = r['total_tokens'] - min_tokens
            pct = (diff / min_tokens) * 100
            print(f"  {r['system']}: {r['total_tokens']} tokens (+{diff}, +{pct:.1f}%)")
    
    # Speed
    min_time = min(r['execution_time'] for r in results)
    fastest = [r['system'] for r in results if r['execution_time'] == min_time]
    print(f"\nSpeed (fastest execution):")
    print(f"  Fastest: {', '.join(fastest)} ({min_time:.2f}s)")
    for r in results:
        if r['execution_time'] != min_time:
            diff = r['execution_time'] - min_time
            pct = (diff / min_time) * 100
            print(f"  {r['system']}: {r['execution_time']:.2f}s (+{diff:.2f}s, +{pct:.1f}%)")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    print("\n" + "="*80)
    print("RUNNING EASY TEST CASE (CASE A) ACROSS ALL MAS SETUPS")
    print("="*80)
    print("\nThis script will run Test Case A (Mathematical Problem) with:")
    print("  1. orig_impl_bMAS - Original Implementation Prompts")
    print("  2. bMAS (LbMAS) - Paper Style Prompts")
    print("  3. Static MAS - Parallel single-pass MAS")
    print("  4. Chain-of-Thought (CoT) - Baseline single-agent approach")
    print("\nResults will be compared at the end.")
    print("="*80)
    
    all_results = []
    
    # Run each MAS setup
    try:
        result_orig_bmas = run_orig_bmas_test()
        all_results.append(result_orig_bmas)
    except Exception as e:
        print(f"\nERROR running orig_impl_bMAS: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        result_bmas = run_bmas_test()
        all_results.append(result_bmas)
    except Exception as e:
        print(f"\nERROR running bMAS: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        result_static = run_static_mas_test()
        all_results.append(result_static)
    except Exception as e:
        print(f"\nERROR running Static MAS: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        result_cot = run_cot_test()
        all_results.append(result_cot)
    except Exception as e:
        print(f"\nERROR running CoT: {e}")
        import traceback
        traceback.print_exc()
    
    # Compare results
    if all_results:
        compare_results(all_results)
        
        print("\n" + "="*80)
        print("ALL TESTS COMPLETE")
        print("="*80)
        print("\nDetailed trace files are available in:")
        for result in all_results:
            if 'trace_txt' in result:
                print(f"  {result['system']}: {result['trace_txt']}")
        print("="*80)
    else:
        print("\nERROR: No results were collected. Check errors above.")

