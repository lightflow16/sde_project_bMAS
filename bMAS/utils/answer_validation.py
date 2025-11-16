"""
Answer validation utilities for cross-checking LLM outputs.
Handles inconsistencies between structured JSON fields and natural language explanations.
"""
import re
from typing import Dict, Any, Optional, Tuple


def extract_answer_from_text(text: str, problem_type: str = "general") -> Optional[str]:
    """
    Extract the final answer from natural language text.
    
    Args:
        text: Natural language text containing an answer
        problem_type: Type of problem ("math", "multiple_choice", "general")
        
    Returns:
        Extracted answer string, or None if not found
    """
    if not text:
        return None
    
    text_lower = text.lower()
    
    # Look for explicit answer markers
    patterns = [
        r'(?:the\s+)?(?:correct\s+)?(?:final\s+)?answer\s+is\s*:?\s*([^\n\.]+)',
        r'answer\s*:?\s*([A-Z]|[\d\.]+(?:\s+\w+)?)',
        r'final\s+answer\s*:?\s*([^\n\.]+)',
        r'solution\s*:?\s*([^\n\.]+)',
        r'result\s*:?\s*([^\n\.]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            answer = match.group(1).strip()
            # Clean up common suffixes
            answer = re.sub(r'[\.\,\;]$', '', answer)
            return answer
    
    # For multiple choice questions, extract letter
    if problem_type == "multiple_choice":
        # First try to find boxed format: boxed[A] or boxed[A]
        boxed_match = re.search(r'boxed\[([A-D])\]', text, re.IGNORECASE)
        if boxed_match:
            return boxed_match.group(1).upper()
        
        # Look for explicit answer markers
        patterns = [
            r'(?:the\s+)?(?:final\s+)?answer\s+is\s*:?\s*([A-D])',
            r'answer\s*:?\s*([A-D])',
            r'choice\s*:?\s*([A-D])',
            r'option\s*:?\s*([A-D])',
            r'select\s*:?\s*([A-D])',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).upper()
        
        # Extract any standalone letter A-D
        letters = re.findall(r'\b([A-D])\b', text.upper())
        if letters:
            return letters[-1]  # Return last letter found
        
        # Try to convert numeric indices (0, 1, 2, 3) to letters
        numbers = re.findall(r'\b([0-3])\b', text)
        if numbers:
            idx = int(numbers[-1])
            return chr(65 + idx)  # 0->A, 1->B, 2->C, 3->D
    
    # For math problems, extract numbers
    if problem_type == "math":
        # Look for numbers followed by units
        numbers_with_units = re.findall(r'(\d+(?:\.\d+)?)\s*([A-Za-z]+)', text)
        if numbers_with_units:
            # Return the last one (usually the final answer)
            num, unit = numbers_with_units[-1]
            return f"{num} {unit}"
        
        # Or just extract the last significant number
        numbers = re.findall(r'\d+(?:\.\d+)?', text)
        if numbers:
            return numbers[-1]
    
    return None


def validate_answer_consistency(response: Dict[str, Any], 
                                problem_type: str = "general") -> Tuple[bool, Optional[str], str]:
    """
    Validate consistency between structured answer field and explanation text.
    
    Args:
        response: Agent response dictionary with 'final_answer' and 'explanation'
        problem_type: Type of problem for better extraction
        
    Returns:
        Tuple of (is_consistent, validated_answer, reason)
    """
    structured_answer = response.get("final_answer") or response.get("answer")
    explanation = response.get("explanation", "")
    
    if not structured_answer and not explanation:
        return False, None, "No answer found"
    
    # Extract answer from explanation
    extracted_answer = extract_answer_from_text(explanation, problem_type)
    
    # Normalize for comparison
    def normalize(s):
        if not s:
            return ""
        s = str(s).lower().strip()
        # Remove common prefixes
        s = re.sub(r'^(the\s+)?(answer|final\s+answer|solution|result)\s+is\s*:?\s*', '', s)
        # Extract key parts (numbers, letters, units)
        if problem_type == "multiple_choice":
            letters = re.findall(r'[A-D]', s.upper())
            return letters[-1] if letters else s
        elif problem_type == "math":
            # Extract number and unit
            match = re.search(r'(\d+(?:\.\d+)?)\s*([a-z]+)?', s)
            if match:
                num, unit = match.groups()
                return f"{num} {unit or ''}".strip()
        return s
    
    norm_structured = normalize(structured_answer) if structured_answer else ""
    norm_extracted = normalize(extracted_answer) if extracted_answer else ""
    
    # Check consistency
    if norm_structured and norm_extracted:
        # Exact match
        if norm_structured == norm_extracted:
            return True, structured_answer, "Consistent"
        
        # Check if one contains the other
        if norm_extracted in norm_structured or norm_structured in norm_extracted:
            # Prefer the more specific one
            if len(norm_extracted) > len(norm_structured):
                return False, extracted_answer, "Mismatch: using explanation (more specific)"
            else:
                return False, structured_answer, "Mismatch: using structured field"
        
        # Mismatch detected
        return False, extracted_answer, f"Mismatch detected: structured='{structured_answer}', explanation='{extracted_answer}'"
    
    # Fallback to available answer
    if extracted_answer and not structured_answer:
        return False, extracted_answer, "No structured answer, using explanation"
    
    if structured_answer and not extracted_answer:
        return True, structured_answer, "Only structured answer available"
    
    return False, None, "No answer found"


def cross_validate_decider_response(decider_result: Dict[str, Any], 
                                   problem_type: str = "general") -> Dict[str, Any]:
    """
    Cross-validate decider's response and fix inconsistencies.
    
    Args:
        decider_result: Decider agent result dictionary
        problem_type: Type of problem
        
    Returns:
        Validated result dictionary with corrected answer if needed
    """
    response = decider_result.get("response", {})
    
    is_consistent, validated_answer, reason = validate_answer_consistency(response, problem_type)
    
    # Create validated result
    validated_result = decider_result.copy()
    
    if not is_consistent and validated_answer:
        # Update with validated answer
        if "response" not in validated_result:
            validated_result["response"] = {}
        
        original_answer = response.get("final_answer") or response.get("answer")
        validated_result["response"]["final_answer"] = validated_answer
        validated_result["response"]["original_final_answer"] = original_answer
        validated_result["response"]["validation_note"] = reason
        validated_result["validation_applied"] = True
        validated_result["validation_reason"] = reason
        
        # Update main fields
        validated_result["final_answer"] = validated_answer
        if "is_solution_ready" in validated_result:
            # Lower confidence if inconsistency found
            if "confidence" in response:
                validated_result["response"]["original_confidence"] = response["confidence"]
                validated_result["response"]["confidence"] = max(0.5, response["confidence"] * 0.8)
    
    else:
        validated_result["validation_applied"] = False
        validated_result["validation_reason"] = reason
    
    return validated_result

