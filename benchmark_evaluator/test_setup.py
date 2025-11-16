"""
Quick test script to verify benchmark evaluator setup.
"""
import sys
import os

# Add parent directory to path
_current_dir = os.path.dirname(os.path.abspath(__file__))
_root_dir = os.path.dirname(_current_dir)
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")
    
    try:
        from datasets import load_dataset
        print("[OK] datasets library available")
    except ImportError:
        print("[X] datasets library not found. Install with: pip install datasets")
        return False
    
    try:
        from benchmark_evaluator.benchmark_loader import BenchmarkLoader
        print("[OK] BenchmarkLoader imported")
    except ImportError as e:
        print(f"[X] Failed to import BenchmarkLoader: {e}")
        return False
    
    try:
        from benchmark_evaluator.answer_evaluator import AnswerEvaluator
        print("[OK] AnswerEvaluator imported")
    except ImportError as e:
        print(f"[X] Failed to import AnswerEvaluator: {e}")
        return False
    
    try:
        from benchmark_evaluator.benchmark_runner import BenchmarkRunner
        print("[OK] BenchmarkRunner imported")
    except ImportError as e:
        print(f"[X] Failed to import BenchmarkRunner: {e}")
        return False
    
    try:
        from benchmark_evaluator.results_aggregator import ResultsAggregator
        print("[OK] ResultsAggregator imported")
    except ImportError as e:
        print(f"[X] Failed to import ResultsAggregator: {e}")
        return False
    
    return True

def test_mas_systems():
    """Test if MAS systems can be imported."""
    print("\nTesting MAS system imports...")
    
    try:
        from bMAS.experiment_runner.run_experiment import run_single_experiment as run_bmas
        print("[OK] bMAS system available")
    except ImportError as e:
        print(f"[X] bMAS system not available: {e}")
        return False
    
    try:
        from orig_impl_bMAS.experiment_runner.run_experiment import run_single_experiment as run_orig_bmas
        print("[OK] orig_impl_bMAS system available")
    except ImportError as e:
        print(f"[X] orig_impl_bMAS system not available: {e}")
        return False
    
    try:
        from static_mas.run_experiment import run_static_experiment
        print("[OK] Static MAS system available")
    except ImportError as e:
        print(f"[X] Static MAS system not available: {e}")
        return False
    
    try:
        from cot.run_experiment import run_cot_experiment
        print("[OK] CoT system available")
    except ImportError as e:
        print(f"[X] CoT system not available: {e}")
        return False
    
    return True

def test_benchmark_loader():
    """Test benchmark loader functionality."""
    print("\nTesting benchmark loader...")
    
    try:
        loader = BenchmarkLoader()
        benchmarks = loader.list_benchmarks()
        print(f"[OK] Available benchmarks: {', '.join(benchmarks)}")
        return True
    except Exception as e:
        print(f"[X] Benchmark loader test failed: {e}")
        return False

def test_answer_evaluator():
    """Test answer evaluator functionality."""
    print("\nTesting answer evaluator...")
    
    try:
        from benchmark_evaluator.answer_evaluator import AnswerEvaluator
        evaluator = AnswerEvaluator()
        
        # Test multiple choice
        is_correct, reason = evaluator.evaluate_answer("A", "A", "multiple_choice")
        assert is_correct, "Multiple choice evaluation failed"
        print("[OK] Multiple-choice evaluation works")
        
        # Test free-form
        is_correct, reason = evaluator.evaluate_answer("42", "42", "free_form")
        assert is_correct, "Free-form evaluation failed"
        print("[OK] Free-form evaluation works")
        
        return True
    except Exception as e:
        print(f"[X] Answer evaluator test failed: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("Benchmark Evaluator Setup Test")
    print("="*60)
    
    all_passed = True
    
    all_passed &= test_imports()
    all_passed &= test_mas_systems()
    all_passed &= test_benchmark_loader()
    all_passed &= test_answer_evaluator()
    
    print("\n" + "="*60)
    if all_passed:
        print("[OK] All tests passed! Setup is correct.")
        print("\nYou can now run benchmark evaluations:")
        print("  python run_benchmark_evaluation.py --benchmark math --max-problems 5")
    else:
        print("[X] Some tests failed. Please fix the issues above.")
    print("="*60)

