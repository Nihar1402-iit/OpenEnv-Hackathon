#!/usr/bin/env python3
"""
STANDALONE GRADERS - Completely independent from circular imports
This module can be imported safely from anywhere
"""

from typing import Dict, Any, Set


def _grade_answer(ground_truth_ids: list, submitted_ids: list) -> float:
    """
    Core grading function - completely standalone
    """
    # Validate inputs
    if not isinstance(ground_truth_ids, list):
        ground_truth_ids = []
    if not isinstance(submitted_ids, list):
        submitted_ids = []
    
    ground_truth_set: Set[str] = set(ground_truth_ids)
    submitted_set: Set[str] = set(submitted_ids)
    
    # Empty ground truth case
    if len(ground_truth_set) == 0:
        return 0.95 if len(submitted_set) == 0 else 0.05
    
    # Calculate set overlap
    intersection = ground_truth_set & submitted_set
    score = len(intersection) / len(ground_truth_set)
    
    # Penalize false positives
    false_positives = len(submitted_set - ground_truth_set)
    if false_positives > 0:
        score = max(0.05, score - false_positives * 0.1)
    
    # Clamp strictly between 0 and 1
    clamped = max(0.05, min(0.95, score))
    return clamped


# Task ground truths
TASK_GROUND_TRUTHS = {
    "task_easy_001": ["C005"],
    "task_medium_001": ["C001", "C004", "C006", "C009", "C011", "C014", "C016", "C019"],
    "task_hard_001": ["C001", "C004", "C006", "C009", "C011", "C014", "C016", "C019"],
    "task_extreme_001": ["C001", "C004", "C006", "C009", "C011", "C014", "C016", "C019"],
}


def grade_task_task_easy_001(submitted_answer: Dict[str, Any]) -> float:
    """Grade task_easy_001 - STANDALONE"""
    submitted_ids = submitted_answer.get("customer_ids", [])
    return _grade_answer(TASK_GROUND_TRUTHS["task_easy_001"], submitted_ids)


def grade_task_task_medium_001(submitted_answer: Dict[str, Any]) -> float:
    """Grade task_medium_001 - STANDALONE"""
    submitted_ids = submitted_answer.get("customer_ids", [])
    return _grade_answer(TASK_GROUND_TRUTHS["task_medium_001"], submitted_ids)


def grade_task_task_hard_001(submitted_answer: Dict[str, Any]) -> float:
    """Grade task_hard_001 - STANDALONE"""
    submitted_ids = submitted_answer.get("customer_ids", [])
    return _grade_answer(TASK_GROUND_TRUTHS["task_hard_001"], submitted_ids)


def grade_task_task_extreme_001(submitted_answer: Dict[str, Any]) -> float:
    """Grade task_extreme_001 - STANDALONE"""
    submitted_ids = submitted_answer.get("customer_ids", [])
    return _grade_answer(TASK_GROUND_TRUTHS["task_extreme_001"], submitted_ids)


# GRADERS registry - completely standalone
GRADERS = {
    "task_easy_001": grade_task_task_easy_001,
    "task_medium_001": grade_task_task_medium_001,
    "task_hard_001": grade_task_task_hard_001,
    "task_extreme_001": grade_task_task_extreme_001,
}


def get_grader(task_id: str):
    """Get grader for a task"""
    if task_id not in GRADERS:
        raise ValueError(f"No grader for {task_id}")
    return GRADERS[task_id]


def get_all_graders():
    """Get all graders"""
    return GRADERS.copy()


if __name__ == "__main__":
    # Test
    print("Testing standalone graders...")
    for task_id, grader in GRADERS.items():
        score = grader({})
        print(f"  {task_id}: {score} (valid: {0 < score < 1})")
