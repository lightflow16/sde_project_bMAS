"""
Chain-of-Thought (CoT) baseline for MAS-style benchmarking.

This module provides a single-agent Chain-of-Thought baseline that uses
"Let's think step by step." prompting for comparison with multi-agent systems.
"""

from .run_experiment import run_cot_experiment

__all__ = ['run_cot_experiment']

