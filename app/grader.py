"""
Deterministic graders for task evaluation.
"""

from typing import Dict, Any, List, Set
from .models import Task


class TaskGrader:
    """Deterministic task grader."""

    @staticmethod
    def grade_task(
        task: Task,
        submitted_answer: Dict[str, Any],
    ) -> float:
        """
        Grade a task based on set overlap.
        
        Score = |correct ∩ predicted| / |correct|
        
        Args:
            task: Task object with ground truth
            submitted_answer: Agent's submitted answer
        
        Returns:
            Score in (0.0, 1.0) - strictly between 0 and 1
        """
        ground_truth = task.ground_truth.get("customer_ids", [])
        predicted = submitted_answer.get("customer_ids", [])

        if not isinstance(ground_truth, list) or not isinstance(predicted, list):
            return 0.01

        ground_truth_set: Set[str] = set(ground_truth)
        predicted_set: Set[str] = set(predicted)

        if len(ground_truth_set) == 0:
            return 0.99 if len(predicted_set) == 0 else 0.01

        intersection = ground_truth_set & predicted_set
        # Raw score: fraction of correct answers found
        raw_score = len(intersection) / len(ground_truth_set)

        # CRITICAL: Clamp to (0.01, 0.99) — not (0.05, 0.95)
        # This prevents perfect matches from returning exactly 1.0
        clamped_score = max(0.01, min(0.99, raw_score))
        
        # Penalize false positives (extra items returned that shouldn't be)
        false_positives = len(predicted_set - ground_truth_set)
        if false_positives > 0:
            clamped_score = max(0.01, clamped_score - false_positives * 0.1)
        
        # Defensive check: if somehow clamping didn't work, use safe default
        if not (0.0 < clamped_score < 1.0):
            clamped_score = 0.01
        
        # Ensure it's a Python float (not numpy or other numeric type)
        final_score = float(clamped_score)
        
        # Final assertion: guarantee the invariant
        assert 0.0 < final_score < 1.0, (
            f"CRITICAL: Score {final_score} violates (0, 1) constraint. "
            f"raw_score={raw_score}, false_positives={false_positives}"
        )
        
        return final_score

    @staticmethod
    def grade_multiple_tasks(
        tasks: List[Task],
        submitted_answers: Dict[str, Dict[str, Any]],
    ) -> Dict[str, float]:
        """
        Grade multiple tasks.
        
        Args:
            tasks: List of Task objects
            submitted_answers: Dict mapping task_id to answer
        
        Returns:
            Dict mapping task_id to score
        """
        results = {}

        for task in tasks:
            task_id = task.task_id
            answer = submitted_answers.get(task_id, {})
            score = TaskGrader.grade_task(task, answer)
            results[task_id] = score

        return results

    @staticmethod
    def compute_average_score(scores: Dict[str, float]) -> float:
        """
        Compute average score across all tasks.
        
        Args:
            scores: Dict mapping task_id to score
        
        Returns:
            Average score
        """
        if not scores:
            return 0.0
        return sum(scores.values()) / len(scores)


# 🔥 CRITICAL: Export graders dict for validator
# Validator checks: from app.grader import GRADERS
def _create_graders_dict():
    """Create graders dict from task registry."""
    from .tasks import get_tasks
    
    graders = {}
    for task in get_tasks():
        # Each task has a grader_id (same as task_id in our case)
        graders[task.task_id] = lambda t=task, ans={}: TaskGrader.grade_task(t, ans)
    
    return graders


# Initialize GRADERS at module level
GRADERS = _create_graders_dict()
