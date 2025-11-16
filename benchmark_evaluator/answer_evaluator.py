"""
Answer evaluation utilities for different benchmark formats.

Handles:
- Multiple-choice answers (exact letter match)
- Free-form answers (normalization, boxed format, number extraction)
"""
import re
from typing import Optional, Tuple


class AnswerEvaluator:
    """Evaluator for different answer formats."""
    
    @staticmethod
    def normalize_answer(answer: str, answer_type: str = "general") -> str:
        """
        Normalize an answer for comparison.
        
        Args:
            answer: Answer string to normalize
            answer_type: Type of answer ("multiple_choice", "free_form", "math", "general")
            
        Returns:
            Normalized answer string
        """
        if not answer:
            return ""
        
        answer = str(answer).strip()
        
        if answer_type == "multiple_choice":
            # Extract single letter (A, B, C, D)
            answer = answer.upper()
            match = re.search(r'([A-D])', answer)
            if match:
                return match.group(1)
            return answer[:1] if answer else ""
        
        elif answer_type in ["free_form", "math"]:
            # For math problems, extract number (possibly with units)
            # Remove common prefixes
            answer = re.sub(r'^(the\s+)?(answer|final\s+answer|solution|result)\s+is\s*:?\s*', '', answer, flags=re.IGNORECASE)
            
            # Look for boxed format: \boxed{42} or $\\boxed{42}$
            boxed_match = re.search(r'\\boxed\{([^}]+)\}', answer)
            if boxed_match:
                return boxed_match.group(1).strip()
            
            # Extract number (with optional decimal)
            number_match = re.search(r'(\d+(?:\.\d+)?)', answer)
            if number_match:
                return number_match.group(1)
            
            # Return cleaned answer
            return answer.strip()
        
        else:
            # General normalization
            answer = answer.lower().strip()
            # Remove common prefixes
            answer = re.sub(r'^(the\s+)?(answer|final\s+answer|solution|result)\s+is\s*:?\s*', '', answer)
            return answer.strip()
    
    @staticmethod
    def evaluate_answer(predicted: str, ground_truth: str, answer_type: str = "general") -> Tuple[bool, str]:
        """
        Evaluate if predicted answer matches ground truth.
        
        Args:
            predicted: Predicted answer
            ground_truth: Ground truth answer
            answer_type: Type of answer
            
        Returns:
            Tuple of (is_correct, reason)
        """
        if not predicted and not ground_truth:
            return False, "Both answers empty"
        
        # Normalize both answers
        norm_pred = AnswerEvaluator.normalize_answer(predicted, answer_type)
        norm_gt = AnswerEvaluator.normalize_answer(ground_truth, answer_type)
        
        # Exact match
        if norm_pred == norm_gt:
            return True, "Exact match"
        
        # For multiple choice, exact match is required
        if answer_type == "multiple_choice":
            return False, f"Mismatch: predicted '{norm_pred}' vs ground truth '{norm_gt}'"
        
        # For free-form, try fuzzy matching
        if answer_type in ["free_form", "math"]:
            # Check if ground truth is contained in prediction
            if norm_gt in norm_pred:
                return True, "Ground truth contained in prediction"
            
            # Check if prediction is contained in ground truth
            if norm_pred in norm_gt:
                return True, "Prediction contained in ground truth"
            
            # Extract numbers and compare
            pred_numbers = re.findall(r'\d+(?:\.\d+)?', norm_pred)
            gt_numbers = re.findall(r'\d+(?:\.\d+)?', norm_gt)
            
            if pred_numbers and gt_numbers:
                # Compare last numbers (usually the final answer)
                if pred_numbers[-1] == gt_numbers[-1]:
                    return True, "Number match"
                
                # Try to match any number
                if any(p == g for p in pred_numbers for g in gt_numbers):
                    return True, "Partial number match"
            
            # Check if answers are very similar (for text answers)
            if len(norm_pred) > 0 and len(norm_gt) > 0:
                # Calculate simple similarity (check if significant portion matches)
                if len(norm_gt) <= len(norm_pred):
                    if norm_gt in norm_pred[:len(norm_gt) + 10]:  # Allow small prefix
                        return True, "Prefix match"
        
        return False, f"Mismatch: predicted '{norm_pred}' vs ground truth '{norm_gt}'"
    
    @staticmethod
    def extract_answer_from_response(response: str, answer_type: str = "general") -> Optional[str]:
        """
        Extract answer from LLM response text.
        
        Args:
            response: LLM response text
            answer_type: Type of answer expected
            
        Returns:
            Extracted answer or None
        """
        if not response:
            return None
        
        # Look for explicit answer markers
        patterns = [
            r'(?:the\s+)?(?:correct\s+)?(?:final\s+)?answer\s+is\s*:?\s*([^\n\.]+)',
            r'answer\s*:?\s*([A-Z]|[\d\.]+(?:\s+\w+)?)',
            r'final\s+answer\s*:?\s*([^\n\.]+)',
            r'solution\s*:?\s*([^\n\.]+)',
            r'result\s*:?\s*([^\n\.]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                answer = match.group(1).strip()
                # Clean up common suffixes
                answer = re.sub(r'[\.\,\;]$', '', answer)
                return answer
        
        # For multiple choice, extract letter
        if answer_type == "multiple_choice":
            letters = re.findall(r'\b([A-D])\b', response.upper())
            if letters:
                return letters[-1]  # Return last letter found
        
        # For math problems, extract number
        if answer_type in ["free_form", "math"]:
            # Look for boxed format
            boxed_match = re.search(r'\\boxed\{([^}]+)\}', response)
            if boxed_match:
                return boxed_match.group(1).strip()
            
            # Extract last significant number
            numbers = re.findall(r'\d+(?:\.\d+)?', response)
            if numbers:
                return numbers[-1]
        
        return None

