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


def create_sample_dataset(output_path: str = "bMAS/datasets/sample.json"):
    """
    Create a sample dataset file for testing.
    
    Args:
        output_path: Path to save sample dataset
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    sample_tasks = [
        {
            "question": "What is 2 + 2?",
            "answer": "4",
            "dataset": "sample",
            "task_id": "sample_1"
        },
        {
            "question": "Explain the concept of photosynthesis.",
            "answer": "Photosynthesis is the process by which plants convert light energy into chemical energy.",
            "dataset": "sample",
            "task_id": "sample_2"
        },
        {
            "question": "Solve: If a train travels 60 miles per hour, how far will it travel in 3 hours?",
            "answer": "180 miles",
            "dataset": "sample",
            "task_id": "sample_3"
        }
    ]
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sample_tasks, f, indent=2)
    
    print(f"Sample dataset created at {output_path}")

