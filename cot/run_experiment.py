"""
Chain-of-Thought (CoT) experiment runner.

Single-agent baseline using "Let's think step by step." prompting.
"""
import random
import re
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_integration.api import call_llm, get_available_models
import config

# Import metrics tracker
try:
    from metrics_tracker import MetricsTracker
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False
    MetricsTracker = None


class CoTLogger:
    """Logger for Chain-of-Thought experiments."""
    
    def __init__(self, output_dir: str = "cot/outputs"):
        """Initialize logger."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.log_data = {
            "experiment_type": "chain_of_thought",
            "timestamp": datetime.now().isoformat(),
            "problem": None,
            "ground_truth": None,
            "model_backend": None,
            "cot_prompt": None,
            "reasoning": None,
            "extracted_answer": None,
            "final_answer": None,
            "tokens_used": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "execution_time": None
        }
        self.start_time = None
    
    def log_problem(self, problem: str, ground_truth: Optional[str] = None):
        """Log the problem and ground truth."""
        self.log_data["problem"] = problem
        self.log_data["ground_truth"] = ground_truth
        self.start_time = datetime.now()
    
    def log_model(self, model_backend: str):
        """Log the model backend used."""
        self.log_data["model_backend"] = model_backend
    
    def log_prompt(self, cot_prompt: str):
        """Log the CoT prompt."""
        self.log_data["cot_prompt"] = cot_prompt
    
    def log_response(self, response: Dict[str, Any]):
        """Log the LLM response."""
        self.log_data["reasoning"] = response.get("content", "")
        metadata = response.get("metadata", {})
        self.log_data["tokens_used"] = metadata.get("tokens_used", 0)
        self.log_data["prompt_tokens"] = metadata.get("prompt_tokens", 0)
        self.log_data["completion_tokens"] = metadata.get("completion_tokens", 0)
    
    def log_extracted_answer(self, extracted_answer: str):
        """Log the extracted final answer."""
        self.log_data["extracted_answer"] = extracted_answer
        self.log_data["final_answer"] = extracted_answer
    
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
        filename = f"cot_trace_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.log_data, f, indent=2)
        
        return filepath
    
    def save_text_report(self) -> str:
        """Save human-readable text report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cot_report_{timestamp}.txt"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8', errors='replace') as f:
            f.write("=" * 80 + "\n")
            f.write("Chain-of-Thought (CoT) Baseline Experiment Report\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Timestamp: {self.log_data.get('timestamp', 'N/A')}\n")
            f.write(f"Execution Time: {self.log_data.get('execution_time', 'N/A')} seconds\n\n")
            
            f.write("Problem:\n")
            f.write("-" * 80 + "\n")
            problem_text = str(self.log_data.get('problem', 'N/A'))
            f.write(f"{problem_text}\n\n")
            
            if self.log_data.get('ground_truth'):
                f.write(f"Ground Truth: {self.log_data['ground_truth']}\n\n")
            
            f.write(f"Model Backend: {self.log_data.get('model_backend', 'N/A')}\n\n")
            
            f.write("CoT Prompt:\n")
            f.write("-" * 80 + "\n")
            prompt_text = str(self.log_data.get('cot_prompt', 'N/A'))
            f.write(f"{prompt_text}\n\n")
            
            f.write("Reasoning (Full Response):\n")
            f.write("-" * 80 + "\n")
            reasoning = str(self.log_data.get('reasoning', 'N/A'))
            f.write(f"{reasoning}\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("Extracted Final Answer:\n")
            f.write("-" * 80 + "\n")
            answer_text = str(self.log_data.get('final_answer', 'N/A'))
            f.write(f"{answer_text}\n\n")
            
            if self.log_data.get('ground_truth'):
                correct = self.evaluate()
                f.write(f"Ground Truth: {self.log_data['ground_truth']}\n")
                f.write(f"Correct: {correct}\n\n")
            
            f.write(f"Token Usage:\n")
            f.write(f"  Total Tokens: {self.log_data.get('tokens_used', 0)}\n")
            f.write(f"  Prompt Tokens: {self.log_data.get('prompt_tokens', 0)}\n")
            f.write(f"  Completion Tokens: {self.log_data.get('completion_tokens', 0)}\n")
            f.write("=" * 80 + "\n")
        
        return filepath


def extract_final_answer(reasoning_text: str, problem: str) -> str:
    """
    Extract the final answer from CoT reasoning text.
    
    Args:
        reasoning_text: Full reasoning text from LLM
        problem: Original problem/question
        
    Returns:
        Extracted final answer string
    """
    if not reasoning_text:
        return "No answer found"
    
    # Detect problem type
    problem_lower = problem.lower()
    is_multiple_choice = bool(re.search(r'\b[A-D]\)', problem))
    is_math = any(word in problem_lower for word in ["calculate", "equal", "value", "trinket", "blinket", "drinket"])
    
    # Look for explicit answer markers
    patterns = [
        r'(?:the\s+)?(?:correct\s+)?(?:final\s+)?answer\s+is\s*:?\s*([^\n\.]+)',
        r'answer\s*:?\s*([A-Z]|[\d\.]+(?:\s+\w+)?)',
        r'final\s+answer\s*:?\s*([^\n\.]+)',
        r'solution\s*:?\s*([^\n\.]+)',
        r'result\s*:?\s*([^\n\.]+)',
        r'therefore[,\s]+(?:the\s+)?(?:answer\s+is\s+)?([^\n\.]+)',
        r'so[,\s]+(?:the\s+)?(?:answer\s+is\s+)?([^\n\.]+)',
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, reasoning_text, re.IGNORECASE)
        for match in matches:
            answer = match.group(1).strip()
            # Clean up common suffixes
            answer = re.sub(r'[\.\,\;\:]$', '', answer)
            if answer:
                return answer
    
    # For multiple choice questions, extract letter
    if is_multiple_choice:
        # Look for explicit letter answers
        letter_patterns = [
            r'(?:answer|choice|option|select)\s+([A-D])',
            r'([A-D])\s+(?:is\s+)?(?:the\s+)?(?:correct|right|answer)',
            r'\b([A-D])\b(?:\s+is\s+correct)?',
        ]
        for pattern in letter_patterns:
            matches = re.finditer(pattern, reasoning_text, re.IGNORECASE)
            for match in matches:
                letter = match.group(1).upper()
                return letter
        
        # Fallback: find last occurrence of A-D in context
        letters = re.findall(r'\b([A-D])\b', reasoning_text.upper())
        if letters:
            return letters[-1]
    
    # For math problems, extract numbers with units
    if is_math:
        # Look for numbers followed by units (e.g., "6 Trinkets")
        numbers_with_units = re.findall(r'(\d+(?:\.\d+)?)\s*([A-Z][a-z]+)', reasoning_text)
        if numbers_with_units:
            # Return the last one (usually the final answer)
            num, unit = numbers_with_units[-1]
            return f"{num} {unit}"
        
        # Or just extract the last significant number
        numbers = re.findall(r'\d+(?:\.\d+)?', reasoning_text)
        if numbers:
            return numbers[-1]
    
    # Fallback: try to extract from last sentence
    sentences = re.split(r'[\.\!\?]\s+', reasoning_text)
    if sentences:
        last_sentence = sentences[-1]
        # Try to extract answer from last sentence
        for pattern in patterns:
            match = re.search(pattern, last_sentence, re.IGNORECASE)
            if match:
                answer = match.group(1).strip()
                answer = re.sub(r'[\.\,\;\:]$', '', answer)
                if answer:
                    return answer
    
    # Last resort: return a snippet from the end
    return reasoning_text[-100:].strip() if len(reasoning_text) > 100 else reasoning_text.strip()


def select_model_for_cot() -> str:
    """
    Randomly select a model for CoT baseline (Llama or Qwen per paper protocol).
    
    Returns:
        Model identifier string
    """
    # Per paper protocol: randomly select between Llama and Qwen
    # Check if we're using API models (which have llama and qwen)
    if not config.USE_OLLAMA and "llama" in config.API_MODELS and "qwen" in config.API_MODELS:
        return random.choice(["llama", "qwen"])
    
    # If using Ollama or other models, randomly select from available
    available_models = get_available_models()
    if available_models:
        return random.choice(available_models)
    
    # Fallback
    return "llama" if "llama" in config.API_MODELS else get_available_models()[0] if get_available_models() else "llama"


def run_cot_experiment(problem: str,
                      ground_truth: Optional[str] = None,
                      model_name: Optional[str] = None,
                      enable_logging: bool = True,
                      logger: Optional[CoTLogger] = None,
                      metrics_tracker: Optional[MetricsTracker] = None) -> Dict[str, Any]:
    """
    Run a single Chain-of-Thought experiment.
    
    Args:
        problem: The problem/question to solve
        ground_truth: Optional ground truth answer for evaluation
        model_name: Optional model name (randomly selected if None)
        enable_logging: Whether to enable detailed logging
        logger: Optional logger instance
        metrics_tracker: Optional metrics tracker instance
        
    Returns:
        Dictionary with results including final answer, token usage, etc.
    """
    start_time = datetime.now()
    
    # Initialize logger
    if enable_logging and logger is None:
        logger = CoTLogger()
    
    # Initialize metrics tracker
    if METRICS_AVAILABLE and metrics_tracker is None:
        metrics_tracker = MetricsTracker("CoT")
    
    # Start metrics tracking
    if metrics_tracker:
        metrics_tracker.start_tracking(problem, ground_truth)
        metrics_tracker.track_agent_count(1)  # Single agent
        metrics_tracker.track_round(1)  # Single pass
        metrics_tracker.track_quality_attribute("transparency", "Single-agent CoT with step-by-step reasoning", "architecture")
    
    if enable_logging and logger:
        logger.log_problem(problem, ground_truth)
    
    # Select model (randomly choose Llama or Qwen per paper protocol)
    if model_name is None:
        model_name = select_model_for_cot()
    
    if enable_logging and logger:
        logger.log_model(model_name)
    
    # Create CoT prompt
    cot_prompt = f"{problem}\n\nLet's think step by step."
    
    if enable_logging and logger:
        logger.log_prompt(cot_prompt)
    
    print(f"\n{'='*80}")
    print("Chain-of-Thought (CoT) Baseline Experiment")
    print(f"{'='*80}")
    print(f"Problem: {problem[:100]}...")
    print(f"Model: {model_name}")
    print(f"{'='*80}\n")
    
    # Call LLM with CoT prompt
    print("Calling LLM with CoT prompt...")
    try:
        response = call_llm(cot_prompt, model_name=model_name)
        
        # Track metrics
        if metrics_tracker:
            # Track tokens
            metadata = response.get("metadata", {})
            prompt_tokens = metadata.get("prompt_tokens", 0)
            completion_tokens = metadata.get("completion_tokens", 0)
            tokens_used = metadata.get("tokens_used", 0)
            if prompt_tokens > 0 or completion_tokens > 0:
                metrics_tracker.track_tokens(prompt_tokens, completion_tokens)
            else:
                metrics_tracker.track_tokens(0, tokens_used)
            
            # Track reasoning step
            metrics_tracker.track_reasoning_step("CoT prompt sent to LLM", "cot_agent", "prompt")
        
        if enable_logging and logger:
            logger.log_response(response)
        
        reasoning = response.get("content", "")
        print(f"Received response ({len(reasoning)} characters)")
        
        # Track reasoning in metrics
        if metrics_tracker:
            metrics_tracker.track_agent_output("cot_agent", reasoning[:1000])
            metrics_tracker.track_reasoning_step(f"Received reasoning response ({len(reasoning)} chars)", "cot_agent", "reasoning")
        
        # Extract final answer
        extracted_answer = extract_final_answer(reasoning, problem)
        
        # Track answer extraction
        if metrics_tracker:
            metrics_tracker.track_decision_step(f"Extracted final answer: {extracted_answer}", "extraction")
            
            # Check for extraction issues
            if extracted_answer == "No answer found" or len(extracted_answer) < 2:
                metrics_tracker.track_error_type("answer_extraction", "Failed to extract clear answer from reasoning", "extraction")
                metrics_tracker.track_agent_error("extraction", "answer_extraction", "Could not extract final answer", recovered=False)
        
        if enable_logging and logger:
            logger.log_extracted_answer(extracted_answer)
        
        # Safely print extracted answer (handle Unicode)
        try:
            print(f"\nExtracted Final Answer: {extracted_answer}")
        except UnicodeEncodeError:
            safe_answer = extracted_answer.encode('ascii', errors='replace').decode('ascii')
            print(f"\nExtracted Final Answer: {safe_answer}")
        
        # Prepare result
        execution_time = (datetime.now() - start_time).total_seconds()
        
        final_result = {
            "problem": problem,
            "ground_truth": ground_truth,
            "model_backend": model_name,
            "cot_prompt": cot_prompt,
            "reasoning": reasoning,
            "extracted_answer": extracted_answer,
            "final_answer": extracted_answer,
            "tokens_used": response.get("metadata", {}).get("tokens_used", 0),
            "prompt_tokens": response.get("metadata", {}).get("prompt_tokens", 0),
            "completion_tokens": response.get("metadata", {}).get("completion_tokens", 0),
            "execution_time": execution_time
        }
        
        # Evaluate if ground truth provided
        if ground_truth:
            correct = evaluate_answer(final_result["final_answer"], ground_truth)
            final_result["correct"] = correct
            print(f"Ground Truth: {ground_truth}")
            print(f"Correct: {correct}")
        else:
            correct = None
        
        print(f"Total Tokens: {final_result['tokens_used']}")
        print(f"Execution Time: {execution_time:.2f} seconds")
        
        # Finalize metrics tracking
        if metrics_tracker:
            metrics_tracker.finalize(final_result["final_answer"], correct)
            
            # Track consensus (single agent)
            metrics_tracker.track_consensus_event(
                ["cot_agent"],
                "single_agent",
                1,
                confidence=None
            )
            
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
        
    except Exception as e:
        error_msg = str(e).encode('ascii', errors='replace').decode('ascii')
        print(f"Error running CoT experiment: {error_msg}")
        
        # Track error in metrics
        if metrics_tracker:
            metrics_tracker.track_agent_error("cot_agent", "execution_error", str(e), recovered=False)
            metrics_tracker.track_agent_failure("cot_agent", "system_exception", "error")
            metrics_tracker.track_error_type("llm_inconsistency", f"CoT execution error: {str(e)}", "cot_agent")
            metrics_tracker.finalize("Error", False)
        
        error_result = {
            "problem": problem,
            "ground_truth": ground_truth,
            "model_backend": model_name,
            "error": str(e),
            "execution_time": (datetime.now() - start_time).total_seconds()
        }
        return error_result


def evaluate_answer(predicted: str, ground_truth: str) -> bool:
    """
    Simple answer evaluation.
    
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
    pred_numbers = re.findall(r'\d+\.?\d*', pred_norm)
    gt_numbers = re.findall(r'\d+\.?\d*', gt_norm)
    
    if pred_numbers and gt_numbers:
        return pred_numbers[-1] == gt_numbers[-1]
    
    return False

