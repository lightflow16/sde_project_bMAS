"""
Example script demonstrating Static MAS usage.
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from static_mas.run_experiment import run_static_experiment


def main():
    """Run example Static MAS experiments."""
    
    # Example 1: Simple math problem
    print("\n" + "="*80)
    print("Example 1: Mathematics Problem")
    print("="*80)
    problem1 = "What is 15 * 23?"
    result1 = run_static_experiment(
        problem=problem1,
        ground_truth="345",
        aggregation_method="majority_vote"
    )
    
    # Example 2: Logic problem
    print("\n" + "="*80)
    print("Example 2: Logic Problem")
    print("="*80)
    problem2 = "If all roses are flowers, and some flowers are red, can we conclude that some roses are red?"
    result2 = run_static_experiment(
        problem=problem2,
        aggregation_method="decider_based"
    )
    
    # Example 3: Physics problem
    print("\n" + "="*80)
    print("Example 3: Physics Problem")
    print("="*80)
    problem3 = "A ball is dropped from a height of 100 meters. How long does it take to hit the ground? (Assume g = 9.8 m/s²)"
    result3 = run_static_experiment(
        problem=problem3,
        aggregation_method="most_confident"
    )
    
    print("\n" + "="*80)
    print("All experiments completed!")
    print("="*80)


if __name__ == "__main__":
    main()

