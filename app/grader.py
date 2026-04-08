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
            return 0.05

        ground_truth_set: Set[str] = set(ground_truth)
        predicted_set: Set[str] = set(predicted)

        if len(ground_truth_set) == 0:
            return 0.95 if len(predicted_set) == 0 else 0.05

        intersection = ground_truth_set & predicted_set
        score = len(intersection) / len(ground_truth_set)

        # Penalize false positives
        false_positives = len(predicted_set - ground_truth_set)
        if false_positives > 0:
            score = max(0.05, score - false_positives * 0.1)

        # Clamp to (0.0, 1.0) - strictly between
        # Map to range [0.05, 0.95] to ensure strictly between 0 and 1
        clamped = max(0.05, min(0.95, score))
        
        # Final validation: ensure strictly between 0 and 1 (defensive programming)
        if not (0.0 < clamped < 1.0):
            clamped = 0.05  # Fallback to minimum valid score
        
        # Ensure it's a Python float, not numpy or other type
        final_score = float(clamped)
        
        # Triple-check the range
        assert 0.0 < final_score < 1.0, f"Score {final_score} is not strictly between 0 and 1"
        
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
