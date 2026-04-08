"""
Grader functions for OpenEnv compliance.
This module exports grader functions that can be used by validators.
"""

from typing import Callable, Dict, Any
from .grader import TaskGrader
from .tasks import get_tasks, get_task_by_id


def grade_task_task_easy_001(submitted_answer: Dict[str, Any]) -> float:
    """Grade task_easy_001."""
    task = get_task_by_id("task_easy_001")
    return TaskGrader.grade_task(task, submitted_answer)


def grade_task_task_medium_001(submitted_answer: Dict[str, Any]) -> float:
    """Grade task_medium_001."""
    task = get_task_by_id("task_medium_001")
    return TaskGrader.grade_task(task, submitted_answer)


def grade_task_task_hard_001(submitted_answer: Dict[str, Any]) -> float:
    """Grade task_hard_001."""
    task = get_task_by_id("task_hard_001")
    return TaskGrader.grade_task(task, submitted_answer)


def grade_task_task_extreme_001(submitted_answer: Dict[str, Any]) -> float:
    """Grade task_extreme_001."""
    task = get_task_by_id("task_extreme_001")
    return TaskGrader.grade_task(task, submitted_answer)


# Grader registry for OpenEnv validation
GRADERS = {
    "task_easy_001": grade_task_task_easy_001,
    "task_medium_001": grade_task_task_medium_001,
    "task_hard_001": grade_task_task_hard_001,
    "task_extreme_001": grade_task_task_extreme_001,
}


def get_grader(task_id: str):
    """Get grader function for a specific task."""
    if task_id not in GRADERS:
        raise ValueError(f"No grader found for task {task_id}")
    return GRADERS[task_id]


def get_all_graders() -> Dict[str, Callable[[Dict[str, Any]], float]]:
    """Get all graders."""
    return GRADERS.copy()
