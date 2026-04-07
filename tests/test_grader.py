"""
Tests for task grader.
"""

import pytest
import sys
import os

# Add parent directory to path for app module import
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.grader import TaskGrader
from app.models import Task


class TestTaskGrader:
    """Test suite for TaskGrader."""

    @staticmethod
    def create_test_task(ground_truth: list) -> Task:
        """Create a test task."""
        return Task(
            task_id="test_task",
            difficulty="easy",
            description="Test task",
            ground_truth={"customer_ids": ground_truth},
            max_steps=10,
            action_schema={}
        )

    def test_perfect_match(self) -> None:
        """Test perfect answer match."""
        task = self.create_test_task(["C001", "C002", "C003"])
        answer = {"customer_ids": ["C001", "C002", "C003"]}

        score = TaskGrader.grade_task(task, answer)

        # Perfect match should clamp to 0.95 (strictly less than 1.0)
        assert score == 0.95

    def test_partial_match(self) -> None:
        """Test partial answer match."""
        task = self.create_test_task(["C001", "C002", "C003"])
        answer = {"customer_ids": ["C001", "C002"]}

        score = TaskGrader.grade_task(task, answer)

        assert score == pytest.approx(2.0 / 3.0)

    def test_no_match(self) -> None:
        """Test no answer match."""
        task = self.create_test_task(["C001", "C002", "C003"])
        answer = {"customer_ids": ["C004", "C005"]}

        score = TaskGrader.grade_task(task, answer)

        # No match should clamp to 0.05 (strictly greater than 0.0)
        assert score == 0.05

    def test_empty_ground_truth(self) -> None:
        """Test empty ground truth."""
        task = self.create_test_task([])
        answer = {"customer_ids": []}

        score = TaskGrader.grade_task(task, answer)

        # Empty ground truth with empty answer should clamp to 0.95 (strictly less than 1.0)
        assert score == 0.95

    def test_empty_answer_with_ground_truth(self) -> None:
        """Test empty answer with ground truth."""
        task = self.create_test_task(["C001", "C002"])
        answer = {"customer_ids": []}

        score = TaskGrader.grade_task(task, answer)

        # Empty answer should clamp to 0.05 (strictly greater than 0.0)
        assert score == 0.05

    def test_superset_answer(self) -> None:
        """Test answer with extra items (penalized for false positives)."""
        task = self.create_test_task(["C001", "C002"])
        answer = {"customer_ids": ["C001", "C002", "C003", "C004"]}

        score = TaskGrader.grade_task(task, answer)

        # 2 correct, 2 false positives = 1.0 - (2 * 0.1) = 0.8
        assert score == 0.8

    def test_score_clamped(self) -> None:
        """Test score is properly clamped."""
        task = self.create_test_task(["C001"])
        answer = {"customer_ids": ["C001", "C002"]}

        score = TaskGrader.grade_task(task, answer)

        # Score should be strictly between 0.05 and 0.95
        assert 0.05 <= score <= 0.95

    def test_invalid_answer_format(self) -> None:
        """Test invalid answer format."""
        task = self.create_test_task(["C001"])
        answer = {"customer_ids": "not_a_list"}

        score = TaskGrader.grade_task(task, answer)

        # Invalid format should clamp to 0.05 (strictly greater than 0.0)
        assert score == 0.05

    def test_missing_customer_ids_key(self) -> None:
        """Test missing customer_ids key."""
        task = self.create_test_task(["C001"])
        answer = {"other_key": ["C001"]}

        score = TaskGrader.grade_task(task, answer)

        # Missing key should clamp to 0.05 (strictly greater than 0.0)
        assert score == 0.05

    def test_grade_multiple_tasks(self) -> None:
        """Test grading multiple tasks."""
        task1 = self.create_test_task(["C001", "C002"])
        task2 = self.create_test_task(["C003", "C004"])
        task3 = self.create_test_task(["C005"])

        tasks = [task1, task2, task3]
        answers = {
            "test_task": {"customer_ids": ["C001", "C002"]},
        }

        # This should handle partial task dict
        task1_score = TaskGrader.grade_task(task1, answers.get("test_task", {}))
        # Perfect match should clamp to 0.95 (strictly less than 1.0)
        assert task1_score == 0.95

    def test_compute_average_score(self) -> None:
        """Test average score computation."""
        scores = {
            "task1": 1.0,
            "task2": 0.5,
            "task3": 0.0,
        }

        average = TaskGrader.compute_average_score(scores)

        assert average == pytest.approx(0.5)

    def test_compute_average_empty(self) -> None:
        """Test average with empty scores."""
        scores: dict = {}

        average = TaskGrader.compute_average_score(scores)

        assert average == 0.0

    def test_deterministic_grading(self) -> None:
        """Test grading is deterministic."""
        task = self.create_test_task(["C001", "C002", "C003"])
        answer = {"customer_ids": ["C001", "C002"]}

        score1 = TaskGrader.grade_task(task, answer)
        score2 = TaskGrader.grade_task(task, answer)
        score3 = TaskGrader.grade_task(task, answer)

        assert score1 == score2 == score3
