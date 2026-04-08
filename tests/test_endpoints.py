"""
Tests for FastAPI endpoints.
"""

import pytest
import sys
import os
import json

# Add parent directory to path for app module import
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestEndpoints:
    """Test suite for FastAPI endpoints."""

    def test_health_check(self, client) -> None:
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_get_tasks(self, client) -> None:
        """Test get tasks endpoint."""
        response = client.get("/tasks")

        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "action_schema" in data
        assert "tools" in data
        assert len(data["tasks"]) == 4  # 4 tasks: easy, medium, hard, extreme

    def test_reset_environment(self, client) -> None:
        """Test reset endpoint."""
        response = client.post("/reset")

        assert response.status_code == 200
        data = response.json()
        assert "observation" in data
        assert data["observation"]["step_count"] == 0

    def test_step_environment(self, client) -> None:
        """Test step endpoint."""
        # Reset first
        client.post("/reset")

        # Step with action
        action = {
            "tool": "search_customers",
            "arguments": {"tier": "Gold"}
        }

        response = client.post("/step", json=action)

        assert response.status_code == 200
        data = response.json()
        assert "observation" in data
        assert "reward" in data
        assert "done" in data
        assert "info" in data
        assert data["observation"]["step_count"] == 1

    def test_get_state(self, client) -> None:
        """Test get state endpoint."""
        client.post("/reset")

        response = client.get("/state")

        assert response.status_code == 200
        data = response.json()
        assert "observation" in data
        assert "step_count" in data
        assert "done" in data
        assert "episode_reward" in data

    def test_grader_no_answer(self, client) -> None:
        """Test grader with no answer - should return default scores."""
        client.post("/reset")

        response = client.post("/grader")

        # Should return 200 with default scores (0.05 for each task)
        assert response.status_code == 200
        data = response.json()
        assert "scores" in data
        assert len(data["scores"]) == 4
        # All scores should be valid (strictly between 0 and 1)
        for task_id, score in data["scores"].items():
            assert 0.0 < score < 1.0
            assert score == 0.01  # Default score when no answer

    def test_grader_with_answer(self, client) -> None:
        """Test grader with answer."""
        client.post("/reset")

        # Submit answer
        action = {
            "tool": "submit_answer",
            "arguments": {"customer_ids": ["C001", "C002"]}
        }
        client.post("/step", json=action)

        # Grade
        response = client.post("/grader")

        assert response.status_code == 200
        data = response.json()
        assert "scores" in data
        assert len(data["scores"]) == 4
        # All scores should be valid (strictly between 0 and 1)
        for score in data["scores"].values():
            assert 0.0 < score < 1.0

    def test_step_sequence(self, client) -> None:
        """Test sequence of steps."""
        client.post("/reset")

        # Step 1
        action1 = {"tool": "search_customers", "arguments": {"tier": "Gold"}}
        response1 = client.post("/step", json=action1)
        assert response1.status_code == 200
        assert response1.json()["observation"]["step_count"] == 1

        # Step 2
        action2 = {"tool": "search_orders", "arguments": {"product": "Laptop"}}
        response2 = client.post("/step", json=action2)
        assert response2.status_code == 200
        assert response2.json()["observation"]["step_count"] == 2

        # Step 3 - submit answer
        action3 = {
            "tool": "submit_answer",
            "arguments": {"customer_ids": ["C001"]}
        }
        response3 = client.post("/step", json=action3)
        assert response3.status_code == 200
        assert response3.json()["done"] is True

    def test_invalid_tool(self, client) -> None:
        """Test invalid tool handling."""
        client.post("/reset")

        action = {
            "tool": "invalid_tool",
            "arguments": {}
        }

        response = client.post("/step", json=action)

        assert response.status_code == 200
        data = response.json()
        assert "reward" in data
        assert data["reward"]["value"] < 0

    def test_reward_structure(self, client) -> None:
        """Test reward response structure."""
        client.post("/reset")

        action = {"tool": "search_customers", "arguments": {"tier": "Gold"}}
        response = client.post("/step", json=action)

        data = response.json()
        reward = data["reward"]

        assert "value" in reward
        assert "components" in reward
        assert "message" in reward
        assert isinstance(reward["value"], float)
        assert isinstance(reward["components"], dict)

    def test_observation_structure(self, client) -> None:
        """Test observation response structure."""
        response = client.post("/reset")

        data = response.json()
        obs = data["observation"]

        assert "task_id" in obs
        assert "task_description" in obs
        assert "step_count" in obs
        assert "max_steps" in obs
        assert "available_tools" in obs
        assert "tables_summary" in obs
        assert "done" in obs
        assert "message" in obs

    def test_multiple_resets(self, client) -> None:
        """Test multiple resets."""
        response1 = client.post("/reset")
        assert response1.status_code == 200

        response2 = client.post("/reset")
        assert response2.status_code == 200

        assert response1.json()["observation"]["step_count"] == 0
        assert response2.json()["observation"]["step_count"] == 0
