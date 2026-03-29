"""
Tests for CRM Query Environment.
"""

import pytest
import sys
import os

# Add parent directory to path for app module import
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.env import CRMQueryEnv
from app.models import Observation, Reward


class TestCRMEnv:
    """Test suite for CRMQueryEnv."""

    def test_reset(self) -> None:
        """Test environment reset."""
        env = CRMQueryEnv()
        obs = env.reset()

        assert isinstance(obs, Observation)
        assert obs.task_id is not None
        assert obs.step_count == 0
        assert env.done is False
        assert env.step_count == 0

    def test_state(self) -> None:
        """Test environment state."""
        env = CRMQueryEnv()
        env.reset()
        obs = env.state()

        assert isinstance(obs, Observation)
        assert obs.step_count == 0
        assert obs.max_steps > 0
        assert "search_customers" in obs.available_tools
        assert "search_orders" in obs.available_tools
        assert "search_tickets" in obs.available_tools
        assert "submit_answer" in obs.available_tools

    def test_search_customers(self) -> None:
        """Test customer search."""
        env = CRMQueryEnv()
        env.reset()

        action = {
            "tool": "search_customers",
            "arguments": {"tier": "Gold"}
        }

        obs, reward, done, info = env.step(action)

        assert isinstance(obs, Observation)
        assert isinstance(reward, Reward)
        assert isinstance(done, bool)
        assert reward.value >= -10.0
        assert reward.value <= 10.0
        assert obs.last_action_result is not None
        assert "data" in obs.last_action_result
        assert len(obs.last_action_result["data"]) > 0

    def test_search_orders(self) -> None:
        """Test order search."""
        env = CRMQueryEnv()
        env.reset()

        action = {
            "tool": "search_orders",
            "arguments": {"product": "Laptop"}
        }

        obs, reward, done, info = env.step(action)

        assert isinstance(obs, Observation)
        assert obs.last_action_result is not None
        assert len(obs.last_action_result["data"]) > 0

    def test_search_tickets(self) -> None:
        """Test ticket search."""
        env = CRMQueryEnv()
        env.reset()

        action = {
            "tool": "search_tickets",
            "arguments": {"priority": "High"}
        }

        obs, reward, done, info = env.step(action)

        assert isinstance(obs, Observation)
        assert obs.last_action_result is not None
        assert len(obs.last_action_result["data"]) > 0

    def test_submit_answer(self) -> None:
        """Test answer submission."""
        env = CRMQueryEnv()
        env.reset()

        action = {
            "tool": "submit_answer",
            "arguments": {"customer_ids": ["C001", "C002"]}
        }

        obs, reward, done, info = env.step(action)

        assert done is True
        assert env.final_answer is not None
        assert env.final_answer["customer_ids"] == ["C001", "C002"]

    def test_step_count_increments(self) -> None:
        """Test that step count increments."""
        env = CRMQueryEnv()
        env.reset()

        assert env.step_count == 0

        action = {"tool": "search_customers", "arguments": {}}
        env.step(action)

        assert env.step_count == 1

        env.step(action)

        assert env.step_count == 2

    def test_reward_components(self) -> None:
        """Test reward has proper components."""
        env = CRMQueryEnv()
        env.reset()

        action = {"tool": "search_customers", "arguments": {"tier": "Gold"}}
        obs, reward, done, info = env.step(action)

        assert isinstance(reward.value, float)
        assert isinstance(reward.components, dict)
        assert isinstance(reward.message, str)
        assert "valid_schema" in reward.components or "invalid_schema" in reward.components

    def test_invalid_tool_penalty(self) -> None:
        """Test penalty for invalid tool."""
        env = CRMQueryEnv()
        env.reset()

        action = {
            "tool": "invalid_tool",
            "arguments": {}
        }

        obs, reward, done, info = env.step(action)

        assert reward.value < 0
        assert "invalid_schema" in reward.components

    def test_max_steps_limit(self) -> None:
        """Test max steps enforcement."""
        env = CRMQueryEnv()
        obs = env.reset()
        max_steps = obs.max_steps

        for _ in range(max_steps):
            if env.done:
                break
            action = {"tool": "search_customers", "arguments": {}}
            obs, reward, done, info = env.step(action)

        assert env.done is True
        assert env.step_count <= max_steps

    def test_deterministic_database(self) -> None:
        """Test database is deterministic."""
        env1 = CRMQueryEnv()
        env2 = CRMQueryEnv()

        env1.reset()
        env2.reset()

        action = {"tool": "search_customers", "arguments": {"tier": "Gold"}}

        obs1, _, _, _ = env1.step(action)
        obs2, _, _, _ = env2.step(action)

        result1 = obs1.last_action_result["data"]
        result2 = obs2.last_action_result["data"]

        assert len(result1) == len(result2)
        assert result1 == result2

    def test_episode_reward_accumulation(self) -> None:
        """Test episode reward accumulates."""
        env = CRMQueryEnv()
        env.reset()

        initial_reward = env.episode_reward
        assert initial_reward == 0.0

        action = {"tool": "search_customers", "arguments": {"tier": "Gold"}}
        obs, reward, done, info = env.step(action)

        assert env.episode_reward == initial_reward + reward.value

    def test_history_tracking(self) -> None:
        """Test action history is tracked."""
        env = CRMQueryEnv()
        env.reset()

        action = {"tool": "search_customers", "arguments": {"tier": "Gold"}}
        env.step(action)

        assert len(env.history) == 1
        assert env.history[0]["step"] == 1
        assert env.history[0]["action"] == action
