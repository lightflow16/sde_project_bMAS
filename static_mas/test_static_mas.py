"""
Simple test script to verify Static MAS implementation.
Can be run directly: python static_mas/test_static_mas.py
"""
import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from static_mas.agents.static_agents import create_static_agent_pool
from static_mas.aggregation import aggregate_results


def test_agent_creation():
    """Test that agents can be created."""
    print("Testing agent creation...")
    agents = create_static_agent_pool()
    print(f"[OK] Created {len(agents)} agents")
    for agent in agents:
        print(f"  - {agent.name} ({agent.role}) - Backend: {agent.llm_backend}")
    return agents


def test_aggregation():
    """Test aggregation mechanisms."""
    print("\nTesting aggregation...")
    
    # Mock agent results
    mock_results = [
        {"agent": "agent1", "role": "mathematics_expert", "answer": "345", "confidence": 0.9, "tokens": 100},
        {"agent": "agent2", "role": "mathematics_expert", "answer": "345", "confidence": 0.8, "tokens": 110},
        {"agent": "agent3", "role": "planner", "answer": "345", "confidence": 0.7, "tokens": 120},
        {"agent": "agent4", "role": "decider", "answer": "346", "confidence": 0.6, "tokens": 95},
    ]
    
    # Test majority vote
    result = aggregate_results(mock_results, method="majority_vote")
    print(f"[OK] Majority vote: {result['final_answer']} (confidence: {result['confidence']:.2f})")
    
    # Test decider based
    result = aggregate_results(mock_results, method="decider_based")
    print(f"[OK] Decider based: {result['final_answer']} (confidence: {result['confidence']:.2f})")
    
    # Test most confident
    result = aggregate_results(mock_results, method="most_confident")
    print(f"[OK] Most confident: {result['final_answer']} (confidence: {result['confidence']:.2f})")
    
    # Test weighted average
    result = aggregate_results(mock_results, method="weighted_average")
    print(f"[OK] Weighted average: {result['final_answer']} (confidence: {result['confidence']:.2f})")


def main():
    """Run all tests."""
    print("=" * 80)
    print("Static MAS Test Suite")
    print("=" * 80)
    
    try:
        agents = test_agent_creation()
        test_aggregation()
        
        print("\n" + "=" * 80)
        print("All tests passed! [OK]")
        print("=" * 80)
        print("\nTo run a full experiment, use:")
        print("  python -m static_mas.example")
        print("  or")
        print("  from static_mas.run_experiment import run_static_experiment")
        
    except Exception as e:
        print(f"\n[FAILED] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

