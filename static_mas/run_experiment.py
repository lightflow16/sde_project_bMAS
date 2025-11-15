"""
Main experiment runner for Static MAS.
All agents process problems in parallel, then results are aggregated.
"""
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
from datetime import datetime
from .agents.static_agents import create_static_agent_pool
from .aggregation import aggregate_results
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import metrics tracker
try:
    from metrics_tracker import MetricsTracker
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False
    MetricsTracker = None


class StaticMASLogger:
    """Logger for Static MAS experiments."""
    
    def __init__(self, output_dir: str = "static_mas/outputs"):
        """Initialize logger."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.log_data = {
            "experiment_type": "static_mas",
            "timestamp": datetime.now().isoformat(),
            "problem": None,
            "ground_truth": None,
            "agents": [],
            "agent_results": [],
            "aggregation": {},
            "final_answer": None,
            "total_tokens": 0,
            "execution_time": None
        }
        self.start_time = None
    
    def log_problem(self, problem: str, ground_truth: Optional[str] = None):
        """Log the problem and ground truth."""
        self.log_data["problem"] = problem
        self.log_data["ground_truth"] = ground_truth
        self.start_time = datetime.now()
    
    def log_agents(self, agents: List):
        """Log agent information."""
        self.log_data["agents"] = [
            {
                "name": agent.name,
                "role": agent.role,
                "llm_backend": agent.llm_backend
            }
            for agent in agents
        ]
    
    def log_agent_result(self, result: Dict[str, Any]):
        """Log an agent's result."""
        self.log_data["agent_results"].append(result)
        self.log_data["total_tokens"] += result.get("tokens", 0)
    
    def log_aggregation(self, aggregation_result: Dict[str, Any]):
        """Log aggregation result."""
        self.log_data["aggregation"] = aggregation_result
        self.log_data["final_answer"] = aggregation_result.get("final_answer", "")
    
    def evaluate(self) -> Optional[bool]:
        """Evaluate if final answer matches ground truth."""
        if not self.log_data.get("ground_truth"):
            return None
        
        predicted = str(self.log_data.get("final_answer", "")).lower().strip()
        ground_truth = str(self.log_data["ground_truth"]).lower().strip()
        
        # Simple evaluation
        if predicted == ground_truth:
            return True
        
        # Check if ground truth is contained in prediction
        if ground_truth in predicted:
            return True
        
        # Extract numbers and compare
        import re
        pred_numbers = re.findall(r'\d+\.?\d*', predicted)
        gt_numbers = re.findall(r'\d+\.?\d*', ground_truth)
        
        if pred_numbers and gt_numbers:
            return pred_numbers[-1] == gt_numbers[-1]
        
        return False
    
    def save(self) -> str:
        """Save log to JSON file."""
        if self.start_time:
            self.log_data["execution_time"] = (datetime.now() - self.start_time).total_seconds()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"static_mas_trace_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.log_data, f, indent=2)
        
        return filepath
    
    def save_text_report(self) -> str:
        """Save human-readable text report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"static_mas_report_{timestamp}.txt"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("Static MAS Experiment Report\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Timestamp: {self.log_data.get('timestamp', 'N/A')}\n")
            f.write(f"Execution Time: {self.log_data.get('execution_time', 'N/A')} seconds\n\n")
            
            f.write("Problem:\n")
            f.write("-" * 80 + "\n")
            f.write(f"{self.log_data.get('problem', 'N/A')}\n\n")
            
            if self.log_data.get('ground_truth'):
                f.write(f"Ground Truth: {self.log_data['ground_truth']}\n\n")
            
            f.write("Agents:\n")
            f.write("-" * 80 + "\n")
            for agent in self.log_data.get('agents', []):
                f.write(f"  - {agent['name']} ({agent['role']}) - Backend: {agent['llm_backend']}\n")
            f.write("\n")
            
            f.write("Agent Results:\n")
            f.write("-" * 80 + "\n")
            for i, result in enumerate(self.log_data.get('agent_results', []), 1):
                f.write(f"\nAgent {i}: {result.get('agent', 'N/A')} ({result.get('role', 'N/A')})\n")
                f.write(f"  Answer: {result.get('answer', 'N/A')}\n")
                f.write(f"  Confidence: {result.get('confidence', 0.0):.2f}\n")
                f.write(f"  Tokens: {result.get('tokens', 0)}\n")
                if result.get('explanation'):
                    f.write(f"  Explanation: {result.get('explanation', '')[:200]}...\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("Aggregation Result:\n")
            f.write("-" * 80 + "\n")
            agg = self.log_data.get('aggregation', {})
            f.write(f"Method: {agg.get('method', 'N/A')}\n")
            f.write(f"Final Answer: {agg.get('final_answer', 'N/A')}\n")
            f.write(f"Confidence: {agg.get('confidence', 0.0):.2f}\n")
            
            if self.log_data.get('ground_truth'):
                correct = self.evaluate()
                f.write(f"\nCorrect: {correct}\n")
            
            f.write(f"\nTotal Tokens: {self.log_data.get('total_tokens', 0)}\n")
            f.write("=" * 80 + "\n")
        
        return filepath


def run_static_experiment(problem: str,
                         ground_truth: Optional[str] = None,
                         aggregation_method: str = "majority_vote",
                         enable_logging: bool = True,
                         logger: Optional[StaticMASLogger] = None,
                         metrics_tracker: Optional[MetricsTracker] = None) -> Dict[str, Any]:
    """
    Run a single Static MAS experiment.
    
    All agents process the problem independently in parallel, then results are aggregated.
    
    Args:
        problem: The problem/question to solve
        ground_truth: Optional ground truth answer for evaluation
        aggregation_method: Method to aggregate results ("majority_vote", "decider_based", "most_confident", "weighted_average")
        enable_logging: Whether to enable detailed logging
        logger: Optional logger instance
        metrics_tracker: Optional metrics tracker instance
        
    Returns:
        Dictionary with results including final answer, token usage, etc.
    """
    start_time = datetime.now()
    
    # Initialize logger
    if enable_logging and logger is None:
        logger = StaticMASLogger()
    
    # Initialize metrics tracker
    if METRICS_AVAILABLE and metrics_tracker is None:
        metrics_tracker = MetricsTracker("Static_MAS")
    
    # Start metrics tracking
    if metrics_tracker:
        metrics_tracker.start_tracking(problem, ground_truth)
        metrics_tracker.track_quality_attribute("modularity", "Fixed-role agents with parallel execution", "architecture")
        metrics_tracker.track_quality_attribute("scalability", "Parallel execution with ThreadPoolExecutor", "execution")
    
    if enable_logging and logger:
        logger.log_problem(problem, ground_truth)
    
    # Create agent pool
    agents = create_static_agent_pool()
    
    if metrics_tracker:
        metrics_tracker.track_agent_count(len(agents))
        metrics_tracker.track_reasoning_step(f"Created static agent pool with {len(agents)} agents", None, "setup")
        metrics_tracker.track_round(1)  # Static MAS is single-pass
    
    if enable_logging and logger:
        logger.log_agents(agents)
    
    print(f"\n{'='*80}")
    print("Static MAS Experiment")
    print(f"{'='*80}")
    print(f"Problem: {problem[:100]}...")
    print(f"Agents: {len(agents)}")
    print(f"Aggregation Method: {aggregation_method}")
    print(f"{'='*80}\n")
    
    # Execute all agents in parallel
    agent_results = []
    
    def solve_with_agent(agent):
        """Wrapper to solve problem with an agent."""
        try:
            result = agent.solve(problem)
            return result
        except Exception as e:
            print(f"Error with agent {agent.name}: {e}")
            error_result = {
                "agent": agent.name,
                "role": agent.role,
                "answer": f"Error: {str(e)}",
                "confidence": 0.0,
                "tokens": 0,
                "error": str(e)
            }
            # Track error in metrics (if available in this context)
            # Note: This is called in parallel, so we'll track errors in the main loop
            return error_result
    
    # Use ThreadPoolExecutor for parallel execution
    print("Executing agents in parallel...")
    with ThreadPoolExecutor(max_workers=len(agents)) as executor:
        future_to_agent = {executor.submit(solve_with_agent, agent): agent for agent in agents}
        
        for future in as_completed(future_to_agent):
            agent = future_to_agent[future]
            try:
                result = future.result()
                agent_results.append(result)
                
                # Track metrics
                if metrics_tracker:
                    # Track tokens
                    tokens = result.get("tokens", 0)
                    metrics_tracker.track_tokens(0, tokens)  # Approximate split
                    
                    # Track agent output
                    answer = result.get("answer", "")
                    if answer:
                        metrics_tracker.track_agent_output(agent.name, answer[:500])
                    
                    # Track reasoning step
                    metrics_tracker.track_reasoning_step(
                        f"Agent {agent.name} ({agent.role}) produced answer: {answer[:100]}...",
                        agent.name,
                        "agent_action"
                    )
                    
                    # Check for outliers (answers that differ significantly)
                    if result.get("error"):
                        metrics_tracker.track_agent_error(
                            agent.name,
                            "execution_error",
                            result.get("error", ""),
                            recovered=False
                        )
                
                # Log result
                if enable_logging and logger:
                    logger.log_agent_result(result)
                
                print(f"  [OK] {agent.name} ({agent.role}): {result.get('answer', 'N/A')[:50]}... "
                      f"[Confidence: {result.get('confidence', 0.0):.2f}, Tokens: {result.get('tokens', 0)}]")
            except Exception as e:
                print(f"  [ERROR] {agent.name}: Error - {e}")
                error_result = {
                    "agent": agent.name,
                    "role": agent.role,
                    "answer": f"Error: {str(e)}",
                    "confidence": 0.0,
                    "tokens": 0,
                    "error": str(e)
                }
                agent_results.append(error_result)
                
                # Track error in metrics
                if metrics_tracker:
                    metrics_tracker.track_agent_error(
                        agent.name,
                        "execution_error",
                        str(e),
                        recovered=False
                    )
                    metrics_tracker.track_agent_failure(
                        agent.name,
                        "execution_exception",
                        "error"
                    )
                    metrics_tracker.track_error_type("parsing", f"Agent {agent.name} execution error: {str(e)}", agent.name)
                
                if enable_logging and logger:
                    logger.log_agent_result(error_result)
    
    # Aggregate results
    print(f"\nAggregating results using {aggregation_method}...")
    aggregation_result = aggregate_results(agent_results, method=aggregation_method)
    
    # Track consensus and aggregation
    if metrics_tracker:
        # Track consensus event
        contributing_agents = []
        final_answer = aggregation_result.get("final_answer", "")
        
        # Find agents that contributed to the final answer
        if aggregation_method == "majority_vote":
            # Find agents with matching answers
            for result in agent_results:
                if result.get("answer", "").strip().lower() == final_answer.strip().lower():
                    contributing_agents.append(result.get("agent", ""))
            metrics_tracker.track_consensus_event(
                contributing_agents,
                "majority_vote",
                1,
                confidence=aggregation_result.get("confidence", None)
            )
            metrics_tracker.metrics["robustness"]["majority_vote_effectiveness"] = len(contributing_agents) / len(agent_results) if agent_results else 0
        elif aggregation_method == "decider_based":
            # Find decider agent
            for result in agent_results:
                if "decider" in result.get("role", "").lower():
                    contributing_agents.append(result.get("agent", ""))
            metrics_tracker.track_consensus_event(
                contributing_agents,
                "decider_based",
                1,
                confidence=aggregation_result.get("confidence", None)
            )
        elif aggregation_method == "most_confident":
            # Find agent with highest confidence
            max_confidence = max((r.get("confidence", 0.0) for r in agent_results), default=0.0)
            for result in agent_results:
                if result.get("confidence", 0.0) == max_confidence:
                    contributing_agents.append(result.get("agent", ""))
            metrics_tracker.track_consensus_event(
                contributing_agents,
                "most_confident",
                1,
                confidence=max_confidence
            )
        
        # Track decision step
        metrics_tracker.track_decision_step(
            f"Aggregation method {aggregation_method} selected final answer: {final_answer}",
            "aggregation"
        )
        
        # Check for error recovery through voting
        if aggregation_method == "majority_vote" and len(contributing_agents) > 0:
            # Check if there were errors that were corrected by voting
            error_count = sum(1 for r in agent_results if r.get("error"))
            if error_count > 0 and len(contributing_agents) > error_count:
                metrics_tracker.track_agent_error(
                    "multiple_agents",
                    "voting_correction",
                    f"{error_count} agents had errors, but majority vote recovered",
                    recovered=True,
                    recovery_method="voting"
                )
                metrics_tracker.metrics["robustness"]["voting_recoveries"] += 1
    
    if enable_logging and logger:
        logger.log_aggregation(aggregation_result)
    
    # Prepare final result
    execution_time = (datetime.now() - start_time).total_seconds()
    
    final_result = {
        "problem": problem,
        "ground_truth": ground_truth,
        "agents": [{"name": a.name, "role": a.role, "backend": a.llm_backend} for a in agents],
        "agent_results": agent_results,
        "aggregation_method": aggregation_method,
        "aggregation_result": aggregation_result,
        "final_answer": aggregation_result.get("final_answer", ""),
        "total_tokens": sum(r.get("tokens", 0) for r in agent_results),
        "execution_time": execution_time
    }
    
    # Evaluate if ground truth provided
    if ground_truth:
        correct = evaluate_answer(final_result["final_answer"], ground_truth)
        final_result["correct"] = correct
        print(f"\nFinal Answer: {final_result['final_answer']}")
        print(f"Ground Truth: {ground_truth}")
        print(f"Correct: {correct}")
    else:
        print(f"\nFinal Answer: {final_result['final_answer']}")
        correct = None
    
    print(f"Total Tokens: {final_result['total_tokens']}")
    print(f"Execution Time: {execution_time:.2f} seconds")
    
    # Finalize metrics tracking
    if metrics_tracker:
        metrics_tracker.finalize(final_result["final_answer"], correct)
        
        # Save metrics
        metrics_path = metrics_tracker.save()
        metrics_summary_path = metrics_tracker.save_summary_report()
        final_result["metrics_json"] = str(metrics_path)
        final_result["metrics_summary"] = str(metrics_summary_path)
        print(f"\nMetrics saved to: {metrics_path}")
        print(f"Metrics summary saved to: {metrics_summary_path}")
    
    # Save logs
    if enable_logging and logger:
        json_path = logger.save()
        txt_path = logger.save_text_report()
        final_result["trace_json"] = str(json_path)
        final_result["trace_txt"] = str(txt_path)
        print(f"\nTrace saved to: {json_path}")
        print(f"Report saved to: {txt_path}")
    
    return final_result


def evaluate_answer(predicted: str, ground_truth: str) -> bool:
    """
    Simple answer evaluation.
    
    Args:
        predicted: Predicted answer
        ground_truth: Ground truth answer
        
    Returns:
        True if answers match (approximately)
    """
    # Convert to string if needed
    if not isinstance(predicted, str):
        predicted = str(predicted)
    if not isinstance(ground_truth, str):
        ground_truth = str(ground_truth)
    
    # Normalize answers
    pred_norm = predicted.lower().strip()
    gt_norm = ground_truth.lower().strip()
    
    # Exact match
    if pred_norm == gt_norm:
        return True
    
    # Check if ground truth is contained in prediction
    if gt_norm in pred_norm:
        return True
    
    # Extract numbers and compare
    import re
    pred_numbers = re.findall(r'\d+\.?\d*', pred_norm)
    gt_numbers = re.findall(r'\d+\.?\d*', gt_norm)
    
    if pred_numbers and gt_numbers:
        return pred_numbers[-1] == gt_numbers[-1]
    
    return False


def run_batch_experiments(tasks: List[Dict[str, Any]],
                         aggregation_method: str = "majority_vote",
                         output_dir: str = "static_mas/results") -> Dict[str, Any]:
    """
    Run Static MAS experiments on a batch of tasks.
    
    Args:
        tasks: List of task dictionaries with 'question' and optional 'answer'
        aggregation_method: Aggregation method to use
        output_dir: Directory to save results
        
    Returns:
        Summary dictionary with results
    """
    os.makedirs(output_dir, exist_ok=True)
    
    results = {
        "total_tasks": len(tasks),
        "completed": 0,
        "correct": 0,
        "total_tokens": 0,
        "experiments": []
    }
    
    for i, task in enumerate(tasks):
        print(f"\n{'='*60}")
        print(f"Task {i+1}/{len(tasks)}")
        print(f"Question: {task.get('question', 'N/A')[:100]}...")
        print(f"{'='*60}")
        
        try:
            experiment_result = run_static_experiment(
                problem=task.get("question", ""),
                ground_truth=task.get("answer"),
                aggregation_method=aggregation_method
            )
            
            experiment_result["task_id"] = task.get("task_id", i)
            experiment_result["dataset"] = task.get("dataset", "unknown")
            
            results["experiments"].append(experiment_result)
            results["completed"] += 1
            results["total_tokens"] += experiment_result.get("total_tokens", 0)
            
            if experiment_result.get("correct"):
                results["correct"] += 1
            
            # Save individual result
            result_file = os.path.join(output_dir, f"result_{i+1}.json")
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(experiment_result, f, indent=2)
        
        except Exception as e:
            print(f"Error running experiment {i+1}: {e}")
            results["experiments"].append({
                "task_id": task.get("task_id", i),
                "error": str(e)
            })
    
    # Calculate accuracy
    if results["completed"] > 0:
        results["accuracy"] = results["correct"] / results["completed"]
    
    # Save summary
    summary_file = os.path.join(output_dir, "summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*60}")
    print("Batch Experiment Summary")
    print(f"{'='*60}")
    print(f"Total tasks: {results['total_tasks']}")
    print(f"Completed: {results['completed']}")
    print(f"Correct: {results['correct']}")
    print(f"Accuracy: {results.get('accuracy', 0):.2%}")
    print(f"Total tokens: {results['total_tokens']}")
    print(f"{'='*60}")
    
    return results

