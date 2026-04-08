"""
Grader functions for OpenEnv compliance.
This module exports grader functions that can be used by validators.
"""

from typing import Callable, Dict, Any
from .grader import TaskGrader
from .tasks import get_tasks, get_task_by_id


def _validate_score(score: float, task_id: str) -> float:
    """
    Validate that a score is strictly between 0 and 1.
    Returns score clamped to [0.05, 0.95] if needed.
    """
    try:
        score = float(score)
    except (TypeError, ValueError):
        return 0.05
    
    # Ensure strictly between 0 and 1
    if not (0.0 < score < 1.0):
        clamped = max(0.05, min(0.95, score))
        return clamped
    
    return score


def grade_task_task_easy_001(submitted_answer: Dict[str, Any]) -> float:
    """Grade task_easy_001."""
    try:
        task = get_task_by_id("task_easy_001")
        score = TaskGrader.grade_task(task, submitted_answer)
        return _validate_score(score, "task_easy_001")
    except Exception:
        return 0.05


def grade_task_task_medium_001(submitted_answer: Dict[str, Any]) -> float:
    """Grade task_medium_001."""
    try:
        task = get_task_by_id("task_medium_001")
        score = TaskGrader.grade_task(task, submitted_answer)
        return _validate_score(score, "task_medium_001")
    except Exception:
        return 0.05


def grade_task_task_hard_001(submitted_answer: Dict[str, Any]) -> float:
    """Grade task_hard_001."""
    try:
        task = get_task_by_id("task_hard_001")
        score = TaskGrader.grade_task(task, submitted_answer)
        return _validate_score(score, "task_hard_001")
    except Exception:
        return 0.05


def grade_task_task_extreme_001(submitted_answer: Dict[str, Any]) -> float:
    """Grade task_extreme_001."""
    try:
        task = get_task_by_id("task_extreme_001")
        score = TaskGrader.grade_task(task, submitted_answer)
        return _validate_score(score, "task_extreme_001")
    except Exception:
        return 0.05


# Grader registry for OpenEnv validation
_RAW_GRADERS = {
    "task_easy_001": grade_task_task_easy_001,
    "task_medium_001": grade_task_task_medium_001,
    "task_hard_001": grade_task_task_hard_001,
    "task_extreme_001": grade_task_task_extreme_001,
}


class SafeGraderWrapper:
    """Wrapper that ensures grader always returns valid score"""
    
    def __init__(self, grader: Callable, task_id: str):
        self.grader = grader
        self.task_id = task_id
    
    def __call__(self, submitted_answer: Dict[str, Any]) -> float:
        try:
            score = self.grader(submitted_answer)
            # Triple-check the score is valid
            score = float(score)
            if 0.0 < score < 1.0:
                return score
            else:
                # Clamp to valid range
                return max(0.05, min(0.95, score))
        except Exception:
            # Ultimate fallback
            return 0.05


# Wrap all graders with safety wrapper
GRADERS = {
    task_id: SafeGraderWrapper(grader, task_id)
    for task_id, grader in _RAW_GRADERS.items()
}


def get_grader(task_id: str):
    """Get grader function for a specific task."""
    if task_id not in GRADERS:
        raise ValueError(f"No grader found for task {task_id}")
    return GRADERS[task_id]


def get_all_graders() -> Dict[str, Callable[[Dict[str, Any]], float]]:
    """Get all graders."""
    return GRADERS.copy()
