"""
Tests for multi-agent planning and execution system.
"""

import pytest
import os
import json
from app.env import CRMQueryEnv
from app.tasks import get_task_by_id, get_all_task_ids
from app.multi_agent import (
    PlannerAgent, ExecutorAgent, Coordinator,
    Plan, PlanStep
)


class TestPlannerAgentInitialization:
    """Test planner agent initialization."""

    def test_planner_initialization(self):
        """Test planner agent can be initialized."""
        planner = PlannerAgent()
        assert planner.model == "gpt-3.5-turbo"
        assert planner.temperature == 0.0

    def test_planner_with_custom_api_key(self):
        """Test planner with custom API key."""
        api_key = "test-key"
        planner = PlannerAgent(api_key=api_key)
        assert planner.api_key == api_key

    def test_planner_uses_deterministic_temperature(self):
        """Test planner uses temperature=0 for determinism."""
        planner = PlannerAgent()
        assert planner.temperature == 0.0


class TestPlannerFallback:
    """Test planner fallback behavior."""

    def test_fallback_plan_generation(self):
        """Test that fallback plan is generated correctly."""
        planner = PlannerAgent()
        
        plan = planner._generate_fallback_plan(
            task_id="test_task",
            task_description="Test task description"
        )
        
        assert plan.task_id == "test_task"
        assert plan.description == "Test task description"
        assert len(plan.steps) > 0
        assert isinstance(plan.steps[0], PlanStep)

    def test_fallback_plan_structure(self):
        """Test fallback plan has correct structure."""
        planner = PlannerAgent()
        
        plan = planner._generate_fallback_plan("task_1", "Description")
        
        assert plan.total_steps > 0
        assert all(step.tool in ["search_customers", "search_orders", "search_tickets", "submit_answer"] 
                   for step in plan.steps)
        assert all(hasattr(step, 'rationale') for step in plan.steps)
        assert all(hasattr(step, 'expected_output') for step in plan.steps)


class TestExecutorAgentInitialization:
    """Test executor agent initialization."""

    def test_executor_initialization(self):
        """Test executor agent can be initialized."""
        executor = ExecutorAgent()
        assert executor.memory_hits == 0
        assert executor.memory_misses == 0
        assert isinstance(executor.execution_history, list)
        assert len(executor.execution_history) == 0

    def test_executor_has_memory_tracking(self):
        """Test executor has memory tracking fields."""
        executor = ExecutorAgent()
        
        assert hasattr(executor, 'retrieved_entities')
        assert hasattr(executor, 'memory_hits')
        assert hasattr(executor, 'memory_misses')

    def test_executor_reset(self):
        """Test executor reset method."""
        executor = ExecutorAgent()
        executor.memory_hits = 5
        executor.memory_misses = 3
        
        executor.reset()
        
        assert executor.memory_hits == 0
        assert executor.memory_misses == 0
        assert len(executor.execution_history) == 0


class TestPlanExecution:
    """Test plan execution against environment."""

    def test_execute_simple_plan(self):
        """Test executing a simple plan."""
        env = CRMQueryEnv()
        env.reset()
        
        executor = ExecutorAgent()
        
        plan = Plan(
            task_id=env.current_task_id,
            description="Test plan",
            total_steps=2,
            reasoning="Test reasoning",
            steps=[
                PlanStep(
                    step_number=1,
                    tool="search_customers",
                    arguments={"tier": "Gold"},
                    rationale="Find gold tier customers",
                    expected_output="List of customers"
                ),
                PlanStep(
                    step_number=2,
                    tool="submit_answer",
                    arguments={"customer_ids": []},
                    rationale="Submit answer",
                    expected_output="Task completed"
                )
            ]
        )
        
        result = executor.execute_plan(plan, env)
        
        assert result["plan_id"] == env.current_task_id
        assert result["steps_executed"] > 0
        assert env.done

    def test_execution_tracks_memory(self):
        """Test that execution tracks retrieved entities."""
        env = CRMQueryEnv()
        env.reset()
        
        executor = ExecutorAgent()
        
        plan = Plan(
            task_id=env.current_task_id,
            description="Memory tracking test",
            total_steps=1,
            reasoning="Test",
            steps=[
                PlanStep(
                    step_number=1,
                    tool="search_customers",
                    arguments={"tier": "Gold"},
                    rationale="Search",
                    expected_output="Results"
                )
            ]
        )
        
        result = executor.execute_plan(plan, env)
        
        assert len(executor.retrieved_entities['customers']) > 0
        assert result["memory_efficiency"] > 0

    def test_execution_stops_on_done(self):
        """Test execution stops when environment marks done."""
        env = CRMQueryEnv()
        env.reset()
        
        executor = ExecutorAgent()
        
        plan = Plan(
            task_id=env.current_task_id,
            description="Stop early test",
            total_steps=3,
            reasoning="Test",
            steps=[
                PlanStep(
                    step_number=1,
                    tool="submit_answer",
                    arguments={"customer_ids": ["C001"]},
                    rationale="Early submit",
                    expected_output="Done"
                ),
                PlanStep(
                    step_number=2,
                    tool="search_customers",
                    arguments={"tier": "Gold"},
                    rationale="Should not execute",
                    expected_output="Should not reach"
                ),
                PlanStep(
                    step_number=3,
                    tool="submit_answer",
                    arguments={"customer_ids": ["C002"]},
                    rationale="Also should not execute",
                    expected_output="Should not reach"
                )
            ]
        )
        
        result = executor.execute_plan(plan, env)
        
        # Should stop after first submit_answer
        assert result["steps_executed"] == 1
        assert env.done


class TestCoordinatorInitialization:
    """Test coordinator initialization."""

    def test_coordinator_initialization(self):
        """Test coordinator can be initialized."""
        coordinator = Coordinator()
        assert hasattr(coordinator, 'planner')
        assert hasattr(coordinator, 'executor')
        assert isinstance(coordinator.planner, PlannerAgent)
        assert isinstance(coordinator.executor, ExecutorAgent)

    def test_coordinator_with_api_key(self):
        """Test coordinator with custom API key."""
        api_key = "test-key"
        coordinator = Coordinator(api_key=api_key)
        assert coordinator.planner.api_key == api_key


class TestCoordinatorPipeline:
    """Test full pipeline execution."""

    def test_pipeline_with_fallback(self):
        """Test pipeline with fallback plan."""
        env = CRMQueryEnv()
        env.reset()
        
        coordinator = Coordinator(api_key="invalid-key-for-fallback")
        
        # Pipeline should use fallback
        result = coordinator.run_pipeline(env, max_iterations=1)
        
        assert result["task_id"] == env.current_task_id
        assert result["iterations"] == 1
        assert len(result["plans"]) > 0 or "plan_error" in result

    def test_pipeline_executes_plans(self):
        """Test that pipeline executes generated plans."""
        env = CRMQueryEnv()
        env.reset()
        
        coordinator = Coordinator(api_key="invalid-key")
        
        result = coordinator.run_pipeline(env, max_iterations=1)
        
        # Even with errors, should attempt execution
        assert "task_id" in result
        assert "steps_taken" in result

    def test_pipeline_requires_reset(self):
        """Test that pipeline requires environment reset."""
        env = CRMQueryEnv()
        # Don't reset
        
        coordinator = Coordinator()
        
        with pytest.raises(ValueError):
            coordinator.run_pipeline(env)

    def test_pipeline_result_structure(self):
        """Test pipeline result has expected structure."""
        env = CRMQueryEnv()
        env.reset()
        
        coordinator = Coordinator(api_key="invalid-key")
        
        result = coordinator.run_pipeline(env, max_iterations=1)
        
        assert "task_id" in result
        assert "iterations" in result
        assert "execution_results" in result
        assert "episode_reward" in result
        assert "steps_taken" in result


class TestPlanStructure:
    """Test plan data structure."""

    def test_plan_creation(self):
        """Test creating a plan object."""
        plan = Plan(
            task_id="test_task",
            description="Test description",
            total_steps=2,
            reasoning="Test reasoning",
            steps=[
                PlanStep(
                    step_number=1,
                    tool="search_customers",
                    arguments={"tier": "Gold"},
                    rationale="Find gold customers",
                    expected_output="List of customers"
                )
            ]
        )
        
        assert plan.task_id == "test_task"
        assert plan.total_steps == 2
        assert len(plan.steps) == 1

    def test_plan_model_dump(self):
        """Test plan can be serialized."""
        plan = Plan(
            task_id="test",
            description="Test",
            total_steps=1,
            reasoning="Test",
            steps=[
                PlanStep(
                    step_number=1,
                    tool="search_customers",
                    arguments={},
                    rationale="Test",
                    expected_output="Test"
                )
            ]
        )
        
        dumped = plan.model_dump()
        assert isinstance(dumped, dict)
        assert "task_id" in dumped
        assert "steps" in dumped
        assert len(dumped["steps"]) == 1

    def test_plan_step_validation(self):
        """Test plan step has required fields."""
        step = PlanStep(
            step_number=1,
            tool="search_customers",
            arguments={"tier": "Gold"},
            rationale="Test",
            expected_output="Test output"
        )
        
        assert step.step_number == 1
        assert step.tool == "search_customers"
        assert isinstance(step.arguments, dict)


class TestMultiAgentMemory:
    """Test multi-agent memory tracking."""

    def test_executor_tracks_retrieved_entities(self):
        """Test executor tracks retrieved entities."""
        env = CRMQueryEnv()
        env.reset()
        
        executor = ExecutorAgent()
        
        plan = Plan(
            task_id=env.current_task_id,
            description="Memory test",
            total_steps=1,
            reasoning="Test",
            steps=[
                PlanStep(
                    step_number=1,
                    tool="search_customers",
                    arguments={"tier": "Gold"},
                    rationale="Get customers",
                    expected_output="Customers"
                )
            ]
        )
        
        executor.execute_plan(plan, env)
        
        assert len(executor.retrieved_entities['customers']) > 0

    def test_executor_memory_efficiency_calculation(self):
        """Test executor calculates memory efficiency."""
        env = CRMQueryEnv()
        env.reset()
        
        executor = ExecutorAgent()
        
        # Plan with multiple same queries
        plan = Plan(
            task_id=env.current_task_id,
            description="Efficiency test",
            total_steps=2,
            reasoning="Test",
            steps=[
                PlanStep(
                    step_number=1,
                    tool="search_customers",
                    arguments={"tier": "Gold"},
                    rationale="Query 1",
                    expected_output="Result 1"
                ),
                PlanStep(
                    step_number=2,
                    tool="search_orders",
                    arguments={"status": "Completed"},
                    rationale="Query 2",
                    expected_output="Result 2"
                )
            ]
        )
        
        result = executor.execute_plan(plan, env)
        
        assert "memory_efficiency" in result
        assert result["memory_efficiency"] >= 0.0


class TestMultiAgentErrorHandling:
    """Test error handling in multi-agent system."""

    def test_executor_handles_invalid_action(self):
        """Test executor handles invalid actions gracefully."""
        env = CRMQueryEnv()
        env.reset()
        
        executor = ExecutorAgent()
        
        plan = Plan(
            task_id=env.current_task_id,
            description="Error test",
            total_steps=1,
            reasoning="Test",
            steps=[
                PlanStep(
                    step_number=1,
                    tool="invalid_tool",
                    arguments={},
                    rationale="Invalid",
                    expected_output="Error"
                )
            ]
        )
        
        result = executor.execute_plan(plan, env)
        
        # Should handle gracefully
        assert isinstance(result, dict)

    def test_plan_missing_api_key(self):
        """Test plan generation handles missing API key gracefully."""
        planner = PlannerAgent(api_key=None)
        
        # Should use fallback when API key missing
        plan = planner._generate_fallback_plan("task", "description")
        
        assert isinstance(plan, Plan)
        assert len(plan.steps) > 0
