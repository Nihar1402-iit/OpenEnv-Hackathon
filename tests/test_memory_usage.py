"""
Tests for memory system and temporal reasoning.
"""

import pytest
from app.env import CRMQueryEnv
from app.tasks import get_task_by_id
from app.models import Observation


class TestMemoryInitialization:
    """Test memory system initialization."""

    def test_memory_fields_in_state(self):
        """Test that environment state has memory fields."""
        env = CRMQueryEnv()
        obs = env.reset()
        
        assert hasattr(obs, 'memory_cache')
        assert hasattr(obs, 'step_summaries')
        assert isinstance(obs.memory_cache, dict)
        assert isinstance(obs.step_summaries, list)

    def test_retrieved_entities_initialization(self):
        """Test that retrieved entities are initialized."""
        env = CRMQueryEnv()
        env.reset()
        
        assert 'customers' in env.retrieved_entities
        assert 'orders' in env.retrieved_entities
        assert 'tickets' in env.retrieved_entities
        assert len(env.retrieved_entities['customers']) == 0
        assert len(env.retrieved_entities['orders']) == 0
        assert len(env.retrieved_entities['tickets']) == 0

    def test_step_summaries_initialization(self):
        """Test that step summaries are initialized."""
        env = CRMQueryEnv()
        env.reset()
        
        assert isinstance(env.step_summaries, list)
        assert len(env.step_summaries) == 0


class TestEntityCaching:
    """Test entity caching and retrieval."""

    def test_customers_cached_on_search(self):
        """Test that customers are cached when searched."""
        env = CRMQueryEnv()
        env.reset()
        
        action = {
            "tool": "search_customers",
            "arguments": {"tier": "Gold"}
        }
        
        obs, reward, done, info = env.step(action)
        
        assert len(env.retrieved_entities['customers']) > 0
        assert len(obs.memory_cache['customers']) > 0

    def test_orders_cached_on_search(self):
        """Test that orders are cached when searched."""
        env = CRMQueryEnv()
        env.reset()
        
        action = {
            "tool": "search_orders",
            "arguments": {"status": "Completed"}
        }
        
        obs, reward, done, info = env.step(action)
        
        assert len(env.retrieved_entities['orders']) > 0
        assert len(obs.memory_cache['orders']) > 0

    def test_tickets_cached_on_search(self):
        """Test that tickets are cached when searched."""
        env = CRMQueryEnv()
        env.reset()
        
        action = {
            "tool": "search_tickets",
            "arguments": {"priority": "High"}
        }
        
        obs, reward, done, info = env.step(action)
        
        assert len(env.retrieved_entities['tickets']) > 0
        assert len(obs.memory_cache['tickets']) > 0

    def test_multiple_queries_accumulate(self):
        """Test that multiple queries accumulate cached entities."""
        env = CRMQueryEnv()
        env.reset()
        
        # First query
        action1 = {"tool": "search_customers", "arguments": {"tier": "Gold"}}
        env.step(action1)
        count1 = len(env.retrieved_entities['customers'])
        
        # Second query
        action2 = {"tool": "search_customers", "arguments": {"tier": "Silver"}}
        env.step(action2)
        count2 = len(env.retrieved_entities['customers'])
        
        assert count2 >= count1
        assert count2 > 0


class TestStepSummaries:
    """Test step summary generation."""

    def test_summary_created_per_step(self):
        """Test that summary is created for each step."""
        env = CRMQueryEnv()
        env.reset()
        
        assert len(env.step_summaries) == 0
        
        action = {
            "tool": "search_customers",
            "arguments": {"tier": "Gold"}
        }
        env.step(action)
        
        assert len(env.step_summaries) == 1
        assert isinstance(env.step_summaries[0], str)
        assert "search_customers" in env.step_summaries[0]

    def test_summary_format(self):
        """Test that summaries have expected format."""
        env = CRMQueryEnv()
        env.reset()
        
        action = {
            "tool": "search_orders",
            "arguments": {"product": "Laptop"}
        }
        env.step(action)
        
        summary = env.step_summaries[0]
        assert "Step" in summary
        assert "search_orders" in summary
        assert "results" in summary

    def test_multiple_summaries_preserved(self):
        """Test that multiple step summaries are preserved."""
        env = CRMQueryEnv()
        env.reset()
        
        actions = [
            {"tool": "search_customers", "arguments": {"tier": "Gold"}},
            {"tool": "search_tickets", "arguments": {"priority": "High"}},
            {"tool": "search_orders", "arguments": {"status": "Completed"}},
        ]
        
        for action in actions:
            env.step(action)
        
        assert len(env.step_summaries) == 3
        assert "search_customers" in env.step_summaries[0]
        assert "search_tickets" in env.step_summaries[1]
        assert "search_orders" in env.step_summaries[2]


class TestMemoryReuseRewards:
    """Test memory reuse reward components."""

    def test_memory_reuse_bonus(self):
        """Test that memory reuse is tracked and rewarded."""
        env = CRMQueryEnv()
        env.reset()
        
        # First query
        action1 = {
            "tool": "search_customers",
            "arguments": {"tier": "Gold"}
        }
        obs1, reward1, done1, info1 = env.step(action1)
        
        # Second query (different filter)
        action2 = {
            "tool": "search_customers",
            "arguments": {"tier": "Silver"}
        }
        obs2, reward2, done2, info2 = env.step(action2)
        
        # Both should have valid rewards
        assert reward1.value > -10
        assert reward2.value > -10

    def test_cache_maintained_component(self):
        """Test cache maintained reward component."""
        env = CRMQueryEnv()
        env.reset()
        
        # Multiple searches build cache
        action1 = {"tool": "search_customers", "arguments": {"tier": "Gold"}}
        obs1, reward1, done1, info1 = env.step(action1)
        
        action2 = {"tool": "search_tickets", "arguments": {"priority": "High"}}
        obs2, reward2, done2, info2 = env.step(action2)
        
        # Verify cache is growing
        assert len(env.retrieved_entities['customers']) > 0
        assert len(env.retrieved_entities['tickets']) > 0

    def test_memory_hit_tracking(self):
        """Test that memory hits are tracked in history."""
        env = CRMQueryEnv()
        env.reset()
        
        action = {"tool": "search_customers", "arguments": {"tier": "Gold"}}
        env.step(action)
        
        # Check history tracks memory hit
        assert len(env.history) == 1
        assert "memory_hit" in env.history[0]


class TestRedundantQueryPenalties:
    """Test penalties for redundant queries."""

    def test_repeated_query_penalty(self):
        """Test that repeated queries receive penalties."""
        env = CRMQueryEnv()
        env.reset()
        
        action = {
            "tool": "search_customers",
            "arguments": {"tier": "Gold"}
        }
        
        # First query
        obs1, reward1, done1, info1 = env.step(action)
        base_reward = reward1.value
        
        # Repeated query
        obs2, reward2, done2, info2 = env.step(action)
        
        # Repeated query should have penalty
        assert "repeated_query" in reward2.components
        assert reward2.components["repeated_query"] < 0

    def test_different_queries_no_penalty(self):
        """Test that different queries don't trigger repeated penalty."""
        env = CRMQueryEnv()
        env.reset()
        
        action1 = {"tool": "search_customers", "arguments": {"tier": "Gold"}}
        action2 = {"tool": "search_customers", "arguments": {"tier": "Silver"}}
        
        obs1, reward1, done1, info1 = env.step(action1)
        obs2, reward2, done2, info2 = env.step(action2)
        
        # Second query is different, no repeated_query penalty
        assert "repeated_query" not in reward2.components or reward2.components.get("repeated_query") >= 0


class TestMemoryResetOnEpisode:
    """Test that memory resets properly between episodes."""

    def test_memory_reset_on_new_episode(self):
        """Test that memory clears on environment reset."""
        env = CRMQueryEnv()
        
        # First episode
        env.reset()
        action = {"tool": "search_customers", "arguments": {"tier": "Gold"}}
        env.step(action)
        
        entities_after_step = len(env.retrieved_entities['customers'])
        assert entities_after_step > 0
        
        # Reset environment
        env.reset()
        
        # Memory should be cleared
        assert len(env.retrieved_entities['customers']) == 0
        assert len(env.retrieved_entities['orders']) == 0
        assert len(env.retrieved_entities['tickets']) == 0
        assert len(env.step_summaries) == 0

    def test_query_history_reset(self):
        """Test that query history resets on environment reset."""
        env = CRMQueryEnv()
        
        env.reset()
        action = {"tool": "search_customers", "arguments": {"tier": "Gold"}}
        obs1, reward1, done1, info1 = env.step(action)
        
        # First repeat has penalty
        obs2, reward2, done2, info2 = env.step(action)
        assert reward2.components.get("repeated_query", 0) < 0
        
        # Reset
        env.reset()
        
        # After reset, query should not be in history
        obs3, reward3, done3, info3 = env.step(action)
        # No penalty for first occurrence in new episode
        assert reward3.components.get("repeated_query", 0) >= 0


class TestMemoryObservation:
    """Test memory information in observations."""

    def test_observation_includes_memory_cache(self):
        """Test that observations include memory cache."""
        env = CRMQueryEnv()
        obs = env.reset()
        
        assert hasattr(obs, 'memory_cache')
        assert isinstance(obs.memory_cache, dict)

    def test_observation_includes_step_summaries(self):
        """Test that observations include step summaries."""
        env = CRMQueryEnv()
        obs = env.reset()
        
        assert hasattr(obs, 'step_summaries')
        assert isinstance(obs.step_summaries, list)

    def test_memory_info_updated_in_observation(self):
        """Test that memory info is updated in subsequent observations."""
        env = CRMQueryEnv()
        obs1 = env.reset()
        
        initial_summaries = len(obs1.step_summaries)
        
        action = {"tool": "search_customers", "arguments": {"tier": "Gold"}}
        obs2, reward, done, info = env.step(action)
        
        assert len(obs2.step_summaries) > initial_summaries
        assert len(obs2.memory_cache['customers']) > 0
