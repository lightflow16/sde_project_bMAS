"""
Data loading utilities for datasets.
"""
from typing import Dict, Any, List, Optional
import json
import os


def prepare_task(question: str, answer: Optional[str] = None, 
                dataset_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Prepare a task dictionary from question and optional answer.
    
    Args:
        question: The question/problem to solve
        answer: Optional ground truth answer
        dataset_name: Optional dataset identifier
        
    Returns:
        Task dictionary
    """
    return {
        "question": question,
        "answer": answer,
        "dataset": dataset_name,
        "task_id": None
    }


def load_dataset(dataset_path: str) -> List[Dict[str, Any]]:
    """
    Load dataset from JSON file.
    
    Args:
        dataset_path: Path to JSON file
        
    Returns:
        List of task dictionaries
    """
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset file not found: {dataset_path}")
    
    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle different JSON formats
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        # Try common keys
        for key in ['tasks', 'data', 'questions', 'items']:
            if key in data:
                return data[key]
        # If no standard key, return as single-item list
        return [data]
    else:
        raise ValueError(f"Unexpected dataset format in {dataset_path}")

