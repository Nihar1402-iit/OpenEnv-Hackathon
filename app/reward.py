"""
Reward function for OpenEnv CRM environment.
"""

from typing import Dict, Any, Set, List
from .models import Reward


class RewardCalculator:
    """Dense reward calculator."""

    def __init__(self) -> None:
        """Initialize reward calculator."""
        self.query_history: List[str] = []
        self.last_action_result_size: int = 0

    def reset(self) -> None:
        """Reset reward calculator state."""
        self.query_history = []
        self.last_action_result_size = 0

    def calculate(
        self,
        action: Dict[str, Any],
        action_result: Dict[str, Any],
        done: bool,
        task_ground_truth: Dict[str, Any],
        step_count: int,
        max_steps: int,
        memory_hit: bool = False,
        retrieved_entities: Dict[str, List[Dict]] = None,
    ) -> Reward:
        """
        Calculate dense reward with shape.
        
        Args:
            action: The action taken
            action_result: Result of the action
            done: Whether episode ended
            task_ground_truth: Ground truth answer
            step_count: Current step count
            max_steps: Maximum steps allowed
            memory_hit: Whether action used cached results
            retrieved_entities: Dict of cached retrieved entities
        
        Returns:
            Reward object with value and components
        """
        components: Dict[str, float] = {}
        base_reward = 0.0

        tool = action.get("tool", "")
        arguments = action.get("arguments", {})

        # Schema validation reward
        if tool in ["search_customers", "search_orders", "search_tickets", "submit_answer"]:
            components["valid_schema"] = 0.5
            base_reward += 0.5
        else:
            components["invalid_schema"] = -2.0
            return Reward(
                value=-2.0,
                components=components,
                message="Invalid tool"
            )

        # Check for repeated queries
        query_key = f"{tool}:{str(sorted(arguments.items()))}"
        if query_key in self.query_history:
            components["repeated_query"] = -0.5
            base_reward -= 0.5
        else:
            self.query_history.append(query_key)

        # Intermediate result reward
        result_data = action_result.get("data", [])
        if isinstance(result_data, list):
            result_size = len(result_data)
        else:
            result_size = 0

        if result_size > 0 and result_size < 50:  # Reasonable result size
            components["narrowing_search"] = 0.3
            base_reward += 0.3
        elif result_size == 0:
            components["empty_result"] = -0.2
            base_reward -= 0.2

        self.last_action_result_size = result_size

        # Memory reuse reward
        if memory_hit and tool != "submit_answer":
            components["memory_reuse"] = 0.4
            base_reward += 0.4

        # Query efficiency reward
        if retrieved_entities:
            total_cached = sum(len(v) for v in retrieved_entities.values())
            if total_cached > 0 and tool in ["search_customers", "search_orders", "search_tickets"]:
                # Reward for maintaining cache without redundancy
                components["cache_maintained"] = 0.2
                base_reward += 0.2

        # Submit answer reward
        if tool == "submit_answer":
            submitted = action.get("arguments", {}).get("customer_ids", [])
            ground_truth = task_ground_truth.get("customer_ids", [])

            if isinstance(submitted, list) and isinstance(ground_truth, list):
                submitted_set = set(submitted)
                ground_truth_set = set(ground_truth)

                if len(ground_truth_set) > 0:
                    intersection = submitted_set & ground_truth_set
                    overlap_ratio = len(intersection) / len(ground_truth_set)
                else:
                    overlap_ratio = 0.0

                components["answer_accuracy"] = overlap_ratio * 3.0
                base_reward += overlap_ratio * 3.0

                # Penalize incorrect items
                false_positives = len(submitted_set - ground_truth_set)
                components["false_positives"] = -false_positives * 0.2
                base_reward -= false_positives * 0.2

                done = True

        # Step efficiency penalty
        if step_count > max_steps * 0.8:
            components["step_inefficiency"] = -0.5
            base_reward -= 0.5

        # Clamp reward
        final_reward = max(-10.0, min(10.0, base_reward))

        message = f"Reward: {final_reward:.2f} | Components: {components}"

        return Reward(
            value=final_reward,
            components=components,
            message=message
        )
