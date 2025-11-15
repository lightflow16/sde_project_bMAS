"""
Aggregation mechanisms for Static MAS results.
Implements voting, decider-based, and confidence-based aggregation.
"""
from typing import Dict, Any, List
import re
from collections import Counter


def majority_vote(agent_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregate answers using majority voting.
    
    Args:
        agent_results: List of agent result dictionaries
        
    Returns:
        Aggregated result with final answer and metadata
    """
    answers = []
    for result in agent_results:
        answer = result.get("answer", "")
        # Skip error results
        if result.get("error"):
            continue
        if answer:
            try:
                # Normalize answer for comparison
                normalized = normalize_answer(answer)
                answers.append((normalized, result))
            except Exception as e:
                # Skip answers that can't be normalized
                continue
    
    if not answers:
        return {
            "final_answer": "No answers provided",
            "method": "majority_vote",
            "confidence": 0.0,
            "vote_counts": {},
            "winning_answer": None
        }
    
    # Count votes
    answer_counts = Counter([ans[0] for ans in answers])
    most_common = answer_counts.most_common(1)[0]
    winning_answer = most_common[0]
    vote_count = most_common[1]
    
    # Find the original answer from one of the agents
    original_answer = None
    for normalized, result in answers:
        if normalized == winning_answer:
            original_answer = result.get("answer", "")
            break
    
    return {
        "final_answer": original_answer or winning_answer,
        "method": "majority_vote",
        "confidence": vote_count / len(answers),
        "vote_counts": dict(answer_counts),
        "winning_answer": winning_answer,
        "total_votes": len(answers)
    }


def decider_based(agent_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Use the decider agent's answer as the final answer.
    If no decider, fall back to majority vote.
    
    Args:
        agent_results: List of agent result dictionaries
        
    Returns:
        Aggregated result with final answer
    """
    # Find decider agent (skip errors)
    decider_result = None
    for result in agent_results:
        if result.get("error"):
            continue
        if result.get("role") == "decider":
            decider_result = result
            break
    
    if decider_result:
        return {
            "final_answer": decider_result.get("answer", ""),
            "method": "decider_based",
            "confidence": decider_result.get("confidence", 0.5),
            "decider_agent": decider_result.get("agent", ""),
            "explanation": decider_result.get("explanation", "")
        }
    else:
        # Fallback to majority vote if no decider
        return majority_vote(agent_results)


def most_confident(agent_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Select the answer from the agent with highest confidence.
    
    Args:
        agent_results: List of agent result dictionaries
        
    Returns:
        Aggregated result with final answer
    """
    # Filter out error results
    valid_results = [r for r in agent_results if not r.get("error")]
    
    if not valid_results:
        return {
            "final_answer": "No answers provided",
            "method": "most_confident",
            "confidence": 0.0
        }
    
    # Find agent with highest confidence
    best_result = max(valid_results, key=lambda r: r.get("confidence", 0.0))
    
    return {
        "final_answer": best_result.get("answer", ""),
        "method": "most_confident",
        "confidence": best_result.get("confidence", 0.0),
        "selected_agent": best_result.get("agent", ""),
        "selected_role": best_result.get("role", ""),
        "explanation": best_result.get("explanation", "")
    }


def weighted_average(agent_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Weighted aggregation based on confidence scores.
    For numerical answers, compute weighted average.
    For text answers, use confidence-weighted voting.
    
    Args:
        agent_results: List of agent result dictionaries
        
    Returns:
        Aggregated result with final answer
    """
    # Filter out error results
    valid_results = [r for r in agent_results if not r.get("error")]
    
    if not valid_results:
        return {
            "final_answer": "No answers provided",
            "method": "weighted_average",
            "confidence": 0.0
        }
    
    # Try to extract numerical answers
    numerical_answers = []
    text_answers = []
    
    for result in valid_results:
        answer = result.get("answer", "")
        confidence = result.get("confidence", 0.5)
        
        # Try to extract number from answer
        numbers = re.findall(r'-?\d+\.?\d*', str(answer))
        if numbers:
            try:
                num_value = float(numbers[-1])  # Use last number found
                numerical_answers.append((num_value, confidence, result))
            except ValueError:
                text_answers.append((answer, confidence, result))
        else:
            text_answers.append((answer, confidence, result))
    
    # If we have numerical answers, compute weighted average
    if numerical_answers:
        total_weight = sum(conf for _, conf, _ in numerical_answers)
        if total_weight > 0:
            weighted_sum = sum(val * conf for val, conf, _ in numerical_answers)
            avg_answer = weighted_sum / total_weight
            
            # Find the result with closest numerical value
            closest_result = min(numerical_answers, 
                                key=lambda x: abs(x[0] - avg_answer))[2]
            
            return {
                "final_answer": str(avg_answer),
                "method": "weighted_average",
                "confidence": total_weight / len(numerical_answers),
                "numerical_average": avg_answer,
                "selected_agent": closest_result.get("agent", ""),
                "explanation": f"Weighted average of {len(numerical_answers)} numerical answers"
            }
    
    # Fallback to confidence-weighted text voting
    answer_weights = {}
    for answer, confidence, result in text_answers:
        normalized = normalize_answer(answer)
        if normalized not in answer_weights:
            answer_weights[normalized] = []
        answer_weights[normalized].append((confidence, result))
    
    # Compute weighted scores
    weighted_scores = {}
    for answer, weight_list in answer_weights.items():
        total_weight = sum(conf for conf, _ in weight_list)
        weighted_scores[answer] = total_weight
    
    if weighted_scores:
        best_answer = max(weighted_scores.items(), key=lambda x: x[1])
        # Get original answer from one of the results
        original_answer = None
        for answer, weight_list in answer_weights.items():
            if answer == best_answer[0]:
                original_answer = weight_list[0][1].get("answer", "")
                break
        
        return {
            "final_answer": original_answer or best_answer[0],
            "method": "weighted_average",
            "confidence": best_answer[1] / sum(weighted_scores.values()),
            "weighted_scores": weighted_scores
        }
    
    return {
        "final_answer": "No valid answers",
        "method": "weighted_average",
        "confidence": 0.0
    }


def normalize_answer(answer) -> str:
    """
    Normalize an answer for comparison (lowercase, remove extra whitespace, extract key info).
    
    Args:
        answer: Raw answer (can be string, int, float, etc.)
        
    Returns:
        Normalized answer string
    """
    if answer is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(answer, str):
        answer = str(answer)
    
    if not answer:
        return ""
    
    # Convert to lowercase
    normalized = answer.lower().strip()
    
    # Extract numbers if present (for numerical answers)
    numbers = re.findall(r'\d+\.?\d*', normalized)
    if numbers:
        # Use the last number found (often the final answer)
        return numbers[-1]
    
    # Remove common prefixes/suffixes
    normalized = re.sub(r'^(the answer is|answer:|solution:|result:)\s*', '', normalized)
    normalized = normalized.strip()
    
    # Limit length for comparison
    if len(normalized) > 100:
        normalized = normalized[:100]
    
    return normalized


def aggregate_results(agent_results: List[Dict[str, Any]], 
                     method: str = "majority_vote") -> Dict[str, Any]:
    """
    Aggregate agent results using the specified method.
    
    Args:
        agent_results: List of agent result dictionaries
        method: Aggregation method ("majority_vote", "decider_based", "most_confident", "weighted_average")
        
    Returns:
        Aggregated result dictionary
    """
    if method == "majority_vote":
        return majority_vote(agent_results)
    elif method == "decider_based":
        return decider_based(agent_results)
    elif method == "most_confident":
        return most_confident(agent_results)
    elif method == "weighted_average":
        return weighted_average(agent_results)
    else:
        raise ValueError(f"Unknown aggregation method: {method}")

