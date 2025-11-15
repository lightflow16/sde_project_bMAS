"""
Main experiment runner for the LbMAS system (Original Implementation).
"""
from typing import Dict, Any, List, Optional
import json
import os
import sys
from datetime import datetime

# Add parent directories to path for imports
_current_dir = os.path.dirname(os.path.abspath(__file__))
_orig_dir = os.path.dirname(_current_dir)
_root_dir = os.path.dirname(_orig_dir)
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)
if _orig_dir not in sys.path:
    sys.path.insert(0, _orig_dir)

from blackboard.blackboard import Blackboard
from agents.predefined import (
    PlannerAgent, DeciderAgent, CriticAgent, 
    CleanerAgent, ConflictResolverAgent
)
from agents.generated_expert import GeneratedExpertAgent, generate_expert_agents
from control_unit.scheduler import ControlUnit
from llm_integration.api import random_model_choice
import config
from utils.logger import ExperimentLogger
from utils.answer_validation import cross_validate_decider_response, validate_answer_consistency

# Import metrics tracker
try:
    from metrics_tracker import MetricsTracker
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False
    MetricsTracker = None


def create_agent_pool(blackboard: Blackboard, problem: str) -> List:
    """
    Create the pool of agents (predefined + generated experts).
    
    Args:
        blackboard: Reference to blackboard
        problem: Problem to solve (for generating experts)
        
    Returns:
        List of agent objects
    """
    agents = []
    
    # Create predefined agents
    predefined_agents = [
        ("planner", PlannerAgent),
        ("decider", DeciderAgent),
        ("critic", CriticAgent),
        ("cleaner", CleanerAgent),
        ("conflict_resolver", ConflictResolverAgent)
    ]
    
    for name, agent_class in predefined_agents:
        llm_backend = random_model_choice()
        agent = agent_class(name, llm_backend, blackboard)
        agents.append(agent)
    
    # Generate expert agents based on problem
    try:
        expert_descriptions = generate_expert_agents(problem)
        for i, expert_desc in enumerate(expert_descriptions):
            expert_name = f"expert_{expert_desc.get('role', i)}"
            expert = GeneratedExpertAgent(
                name=expert_name,
                role=expert_desc.get('role', 'expert'),
                description=expert_desc.get('description', 'General expert'),
                blackboard=blackboard
            )
            agents.append(expert)
    except Exception as e:
        print(f"Warning: Failed to generate expert agents: {e}")
        # Continue with just predefined agents
    
    return agents


def run_single_experiment(problem: str, max_rounds: int = config.MAX_ROUNDS,
                         ground_truth: Optional[str] = None,
                         enable_logging: bool = True,
                         logger: Optional[ExperimentLogger] = None,
                         metrics_tracker: Optional[MetricsTracker] = None) -> Dict[str, Any]:
    """
    Run a single experiment on a problem.
    
    Args:
        problem: The problem/question to solve
        max_rounds: Maximum number of rounds
        ground_truth: Optional ground truth answer for evaluation
        enable_logging: Whether to enable detailed logging
        logger: Optional logger instance (creates new one if None and enable_logging=True)
        metrics_tracker: Optional metrics tracker instance
        
    Returns:
        Dictionary with results including final answer, token usage, etc.
    """
    # Initialize logger
    if enable_logging and logger is None:
        logger = ExperimentLogger(output_dir="orig_impl_bMAS/outputs")
    
    # Initialize metrics tracker
    if METRICS_AVAILABLE and metrics_tracker is None:
        metrics_tracker = MetricsTracker("orig_impl_bMAS")
    
    # Start metrics tracking
    if metrics_tracker:
        metrics_tracker.start_tracking(problem, ground_truth)
        metrics_tracker.track_quality_attribute("modularity", "Agent pool with predefined and generated agents (original prompts)", "architecture")
        metrics_tracker.track_quality_attribute("transparency", "Full blackboard trace with agent actions", "logging")
    
    # Log problem (always log if logger exists, even if passed in)
    if enable_logging and logger:
        logger.log_problem(problem, ground_truth)
    
    # Initialize blackboard
    blackboard = Blackboard()
    
    # Create agent pool
    agents = create_agent_pool(blackboard, problem)
    
    if metrics_tracker:
        metrics_tracker.track_agent_count(len(agents))
        metrics_tracker.track_reasoning_step(f"Created agent pool with {len(agents)} agents", None, "setup")
    
    if enable_logging and logger:
        logger.log_agent_pool(agents)
    
    # Initialize control unit
    control_unit = ControlUnit(agents, blackboard)
    
    # Track execution
    execution_log = {
        "problem": problem,
        "rounds": [],
        "total_tokens": 0,
        "final_answer": None,
        "is_solution_ready": False
    }
    
    # Main execution loop
    for round_num in range(max_rounds):
        blackboard.increment_round()
        print(f"\n=== Round {round_num + 1} ===")
        
        # Track round in metrics
        if metrics_tracker:
            metrics_tracker.track_round(round_num + 1)
            metrics_tracker.track_reasoning_step(f"Starting round {round_num + 1}", None, "round_start")
        
        # Log round start
        if enable_logging and logger:
            blackboard_state = blackboard.get_all_messages_summary()
            round_index = logger.log_round_start(round_num + 1, blackboard_state)
        
        # Check if we need critic validation
        need_critic_validation = execution_log.get("is_solution_ready", False) and not any(
            round_data.get("solution_ready", False) 
            for round_data in execution_log.get("rounds", [])
        )
        
        # Select agents for this round
        selected_agent_names = control_unit.choose_agents_for_round(problem, require_critic=need_critic_validation)
        selected_agents = control_unit.get_agents_by_names(selected_agent_names)
        
        print(f"Selected agents: {[a.name for a in selected_agents]}")
        
        # Track agent selection in metrics
        if metrics_tracker:
            metrics_tracker.track_reasoning_step(
                f"Control unit selected agents: {', '.join(selected_agent_names)}", 
                "control_unit", 
                "agent_selection"
            )
        
        # Log agent selection
        if enable_logging and logger:
            selection_history = control_unit.round_history[-1] if control_unit.round_history else {}
            logger.log_agent_selection(
                round_index,
                selected_agent_names,
                selection_history.get("reasoning", ""),
                selection_history.get("raw_response", "")
            )
        
        round_results = {
            "round": round_num + 1,
            "selected_agents": selected_agent_names,
            "agent_outputs": []
        }
        
        # Execute selected agents
        for agent in selected_agents:
            try:
                # Get blackboard state before action
                blackboard_before = blackboard.get_all_messages_summary()
                
                result = agent.act(problem)
                
                # Get blackboard state after action
                blackboard_after = blackboard.get_all_messages_summary()
                blackboard_update = blackboard_after[len(blackboard_before):] if len(blackboard_after) > len(blackboard_before) else ""
                
                # Track metrics
                if metrics_tracker:
                    # Track tokens
                    tokens = result.get("tokens", 0)
                    prompt_tokens = result.get("metadata", {}).get("prompt_tokens", 0)
                    completion_tokens = result.get("metadata", {}).get("completion_tokens", 0)
                    if prompt_tokens > 0 or completion_tokens > 0:
                        metrics_tracker.track_tokens(prompt_tokens, completion_tokens)
                    else:
                        metrics_tracker.track_tokens(0, tokens)
                    
                    # Track agent output
                    raw_response = result.get("raw_response", "")
                    if raw_response:
                        metrics_tracker.track_agent_output(agent.name, raw_response[:500])
                    
                    # Track reasoning step
                    response_type = result.get("response", {}).get("type", "unknown")
                    metrics_tracker.track_reasoning_step(
                        f"Agent {agent.name} ({agent.role}) produced {response_type} response",
                        agent.name,
                        "agent_action"
                    )
                
                # Log agent action
                if enable_logging and logger:
                    logger.log_agent_action(round_index, agent.name, result, blackboard_update)
                
                round_results["agent_outputs"].append({
                    "agent": agent.name,
                    "tokens": result.get("tokens", 0),
                    "response_type": result.get("response", {}).get("type", "unknown"),
                    "response": result.get("response", {}),
                    "raw_response": result.get("raw_response", "")
                })
                execution_log["total_tokens"] += result.get("tokens", 0)
                
                if enable_logging and logger:
                    logger.add_tokens(result.get("tokens", 0))
                
                # Check if decider says solution is ready
                if agent.name == "decider" and result.get("is_solution_ready"):
                    # Track decision step
                    if metrics_tracker:
                        metrics_tracker.track_decision_step(
                            f"Decider determined solution is ready: {result.get('final_answer', 'N/A')}",
                            "decider"
                        )
                    
                    # Cross-validate decider response
                    # Detect problem type for better validation
                    problem_type = "math" if any(word in problem.lower() for word in ["calculate", "equal", "value", "trinket", "blinket"]) else "general"
                    
                    validated_result = cross_validate_decider_response(result, problem_type)
                    
                    if validated_result.get("validation_applied"):
                        print(f"[VALIDATION] Inconsistency detected: {validated_result.get('validation_reason')}")
                        print(f"[VALIDATION] Original answer: {validated_result.get('response', {}).get('original_final_answer', 'N/A')}")
                        print(f"[VALIDATION] Corrected answer: {validated_result.get('final_answer', 'N/A')}")
                        
                        # Track error correction
                        if metrics_tracker:
                            metrics_tracker.track_agent_error(
                                "decider",
                                "answer_inconsistency",
                                validated_result.get('validation_reason', ''),
                                recovered=True,
                                recovery_method="validation"
                            )
                            metrics_tracker.track_error_recovery({
                                "event": "decider_validation_correction",
                                "original": validated_result.get('response', {}).get('original_final_answer', 'N/A'),
                                "corrected": validated_result.get('final_answer', 'N/A'),
                                "reason": validated_result.get('validation_reason', '')
                            })
                        
                        result = validated_result
                    
                    execution_log["is_solution_ready"] = True
                    execution_log["final_answer"] = result.get("final_answer")
                    execution_log["decider_validated"] = validated_result.get("validation_applied", False)
                    execution_log["validation_reason"] = validated_result.get("validation_reason", "")
                    round_results["solution_ready"] = True
                    print(f"Decider reports solution ready: {execution_log['final_answer']}")
                
                # Track critic activity
                if agent.name == "critic" and metrics_tracker:
                    metrics_tracker.track_critique(
                        agent.name,
                        result.get("response", {}).get("type", "general"),
                        led_to_correction=False
                    )
                    metrics_tracker.track_traceable_critique({
                        "critic": agent.name,
                        "round": round_num + 1,
                        "critique": result.get("raw_response", "")[:500]
                    })
            except Exception as e:
                print(f"Error executing agent {agent.name}: {e}")
                
                # Track agent error
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
                
                round_results["agent_outputs"].append({
                    "agent": agent.name,
                    "error": str(e)
                })
        
        # Log blackboard snapshot
        if enable_logging and logger:
            logger.log_blackboard_snapshot(round_index, blackboard)
            logger.log_round_end(round_index)
        
        execution_log["rounds"].append(round_results)
        
        # Track consensus event
        if metrics_tracker:
            consensus_agents = [output.get("agent") for output in round_results.get("agent_outputs", [])]
            if consensus_agents:
                metrics_tracker.track_consensus_event(
                    consensus_agents,
                    "blackboard_iterative",
                    round_num + 1,
                    confidence=None
                )
        
        # Require critic validation before early termination
        # Check termination condition with validation
        if execution_log["is_solution_ready"]:
            # Check if critic has run in this round
            critic_ran = any(
                output.get("agent") == "critic" 
                for output in round_results.get("agent_outputs", [])
            )
            
            if critic_ran:
                # Critic has reviewed, safe to terminate
                print("Solution ready and validated by critic, terminating.")
                if metrics_tracker:
                    metrics_tracker.track_reasoning_step("Solution validated by critic, terminating", "critic", "termination")
                break
            else:
                # Don't terminate until critic validates
                print("Decider says solution ready, but waiting for critic validation...")
                execution_log["is_solution_ready"] = False  # Reset to allow critic to run
                # Continue to next round where critic will be selected
    
    # If no solution from decider, try to extract from blackboard
    if not execution_log["final_answer"]:
        # First, check private spaces (reflection spaces may contain final solutions)
        for space_key, messages in blackboard.private_spaces.items():
            if "reflection" in space_key.lower() or "debate" in space_key.lower():
                # Look for solution-type messages in private spaces
                for msg in reversed(messages):  # Check most recent first
                    if "solution" in msg.get("type", "").lower() or "final" in msg.get("content", "").lower():
                        execution_log["final_answer"] = msg.get("content", "No answer found")
                        execution_log["answer_source"] = f"private_space_{space_key}"
                        break
                if execution_log["final_answer"]:
                    break
        
        # If still no answer, check public space
        if not execution_log["final_answer"]:
            # Look for decision messages
            decision_messages = blackboard.get_public_messages("decision")
            if decision_messages:
                last_decision = decision_messages[-1]
                execution_log["final_answer"] = last_decision.get("content", "No answer found")
                execution_log["answer_source"] = "public_decision"
            else:
                # Use last message as fallback
                if blackboard.public_space:
                    execution_log["final_answer"] = blackboard.public_space[-1].get("content", "No answer found")
                    execution_log["answer_source"] = "public_last_message"
    
    # Evaluate if ground truth provided
    if ground_truth:
        execution_log["correct"] = evaluate_answer(execution_log["final_answer"], ground_truth)
    
    execution_log["blackboard_summary"] = blackboard.get_all_messages_summary()
    
    # Finalize metrics tracking
    if metrics_tracker:
        final_answer = execution_log.get("final_answer", "")
        correct = execution_log.get("correct")
        metrics_tracker.finalize(final_answer, correct)
        
        # Track final consensus
        if execution_log.get("is_solution_ready"):
            consensus_agents = []
            for round_data in execution_log.get("rounds", []):
                for output in round_data.get("agent_outputs", []):
                    if output.get("agent") not in consensus_agents:
                        consensus_agents.append(output.get("agent"))
            if consensus_agents:
                metrics_tracker.track_consensus_event(
                    consensus_agents,
                    "decider_final",
                    len(execution_log.get("rounds", [])),
                    confidence=None
                )
        
        # Save metrics
        metrics_path = metrics_tracker.save()
        metrics_summary_path = metrics_tracker.save_summary_report()
        execution_log["metrics_json"] = str(metrics_path)
        execution_log["metrics_summary"] = str(metrics_summary_path)
        print(f"\nMetrics saved to: {metrics_path}")
        print(f"Metrics summary saved to: {metrics_summary_path}")
    
    # Log final answer and save
    if enable_logging and logger:
        logger.log_final_answer(
            execution_log.get("final_answer", ""),
            execution_log.get("answer_source", "unknown"),
            execution_log.get("is_solution_ready", False)
        )
        json_path = logger.save()
        txt_path = logger.save_text_report()
        execution_log["trace_json"] = str(json_path)
        execution_log["trace_txt"] = str(txt_path)
        print(f"\nTrace saved to: {json_path}")
        print(f"Report saved to: {txt_path}")
    
    return execution_log


def evaluate_answer(predicted: str, ground_truth: str) -> bool:
    """
    Simple answer evaluation (can be enhanced with more sophisticated matching).
    
    Args:
        predicted: Predicted answer
        ground_truth: Ground truth answer
        
    Returns:
        True if answers match (approximately)
    """
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
                         max_rounds: int = config.MAX_ROUNDS,
                         output_dir: str = config.RESULTS_DIR) -> Dict[str, Any]:
    """
    Run experiments on a batch of tasks.
    
    Args:
        tasks: List of task dictionaries with 'question' and optional 'answer'
        max_rounds: Maximum rounds per experiment
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
            experiment_result = run_single_experiment(
                problem=task.get("question", ""),
                max_rounds=max_rounds,
                ground_truth=task.get("answer")
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

