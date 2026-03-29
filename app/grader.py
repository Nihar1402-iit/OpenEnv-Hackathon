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
            Score in [0.0, 1.0]
        """
        ground_truth = task.ground_truth.get("customer_ids", [])
        predicted = submitted_answer.get("customer_ids", [])

        if not isinstance(ground_truth, list) or not isinstance(predicted, list):
            return 0.0

        ground_truth_set: Set[str] = set(ground_truth)
        predicted_set: Set[str] = set(predicted)

        if len(ground_truth_set) == 0:
            return 1.0 if len(predicted_set) == 0 else 0.0

        intersection = ground_truth_set & predicted_set
        score = len(intersection) / len(ground_truth_set)

        # Penalize false positives
        false_positives = len(predicted_set - ground_truth_set)
        if false_positives > 0:
            score = max(0.0, score - false_positives * 0.1)

        return max(0.0, min(1.0, score))

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
        Compute average score across tasks.
        
        Args:
            scores: Dict mapping task_id to score
        
        Returns:
            Average score
        """
        if not scores:
            return 0.0
        return sum(scores.values()) / len(scores)

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
