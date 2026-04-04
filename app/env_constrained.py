"""
Enhanced CRM Environment with real-world constraints.

Adds realistic business constraints to the CRM environment:
1. Query Budget - Limited number of database queries allowed
2. Response Latency - Some queries take multiple steps to complete
3. Data Quality - Incomplete/missing data (85% quality by default)
4. Cost Per Query - Each query has a monetary cost
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import random
from .models import Observation, Action, Reward, State


@dataclass
class EnvironmentConstraints:
    """Configuration for environment constraints."""
    query_budget: int = 10  # Max queries allowed
    data_quality_score: float = 0.85  # Percentage of data available (0.0-1.0)
    latency_probability: float = 0.2  # 20% chance query takes 2 steps
    cost_per_query: float = 10.0  # Cost in virtual $ per query
    response_delay_steps: int = 1  # Extra steps if latency triggered


class ConstrainedCRMEnvironment:
    """
    CRM environment with business constraints.
    
    Realistic challenges:
    - Limited budget forces efficient querying
    - Latency forces planning ahead
    - Data quality forces robustness
    - Cost awareness forces optimization
    """
    
    def __init__(self, constraints: Optional[EnvironmentConstraints] = None):
        """
        Initialize constrained environment.
        
        Args:
            constraints: EnvironmentConstraints configuration
        """
        self.constraints = constraints or EnvironmentConstraints()
        self.reset_state()
    
    def reset_state(self) -> None:
        """Reset environment state for new episode."""
        self.queries_used = 0
        self.budget_remaining = self.constraints.query_budget
        self.total_cost_incurred = 0.0
        self.query_delays_pending = 0
        self.query_log: List[Dict[str, Any]] = []
    
    def check_query_budget(self) -> bool:
        """
        Check if agent has remaining query budget.
        
        Returns:
            True if budget available, False if exceeded
        """
        return self.budget_remaining > 0
    
    def attempt_query(self, tool: str, arguments: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Attempt to execute a query with constraints.
        
        Args:
            tool: Tool name (e.g., "search_customers")
            arguments: Query arguments
            
        Returns:
            (success: bool, metadata: dict)
        """
        # Check budget
        if not self.check_query_budget():
            return False, {
                "error": "Query budget exceeded",
                "budget_remaining": self.budget_remaining,
                "queries_used": self.queries_used
            }
        
        # Check for pending delays
        if self.query_delays_pending > 0:
            self.query_delays_pending -= 1
            return False, {
                "error": "Query still processing from previous latency",
                "delays_remaining": self.query_delays_pending
            }
        
        # Deduct budget and cost
        self.budget_remaining -= 1
        self.total_cost_incurred += self.constraints.cost_per_query
        self.queries_used += 1
        
        # Check for latency
        latency_triggered = random.random() < self.constraints.latency_probability
        if latency_triggered:
            self.query_delays_pending = self.constraints.response_delay_steps
        
        metadata = {
            "success": True,
            "queries_used": self.queries_used,
            "budget_remaining": self.budget_remaining,
            "total_cost": self.total_cost_incurred,
            "latency_triggered": latency_triggered,
            "delays_pending": self.query_delays_pending
        }
        
        self.query_log.append({
            "tool": tool,
            "arguments": arguments,
            "latency_triggered": latency_triggered,
            "cost": self.constraints.cost_per_query
        })
        
        return True, metadata
    
    def apply_data_quality_filter(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply data quality degradation to results.
        
        Simulates incomplete data (e.g., 85% quality = 15% of fields missing).
        
        Args:
            results: Query results
            
        Returns:
            Results with some data missing
        """
        if not results or self.constraints.data_quality_score >= 1.0:
            return results
        
        filtered_results = []
        quality = self.constraints.data_quality_score
        
        for result in results:
            if isinstance(result, dict):
                # Randomly remove fields based on data quality
                filtered_result = {}
                for key, value in result.items():
                    if random.random() < quality:
                        filtered_result[key] = value
                    # Field is missing (30% chance depends on quality)
                
                # Keep at least ID for identification
                if "id" in result:
                    filtered_result["id"] = result["id"]
                
                filtered_results.append(filtered_result)
            else:
                filtered_results.append(result)
        
        return filtered_results
    
    def get_remaining_budget_reward(self) -> float:
        """
        Get reward bonus for careful budget management.
        
        Args:
            Returns: Bonus for having budget remaining
        """
        budget_ratio = self.budget_remaining / self.constraints.query_budget
        
        # Reward conservative querying
        if budget_ratio > 0.5:
            bonus = 0.3  # 50%+ budget remaining
        elif budget_ratio > 0.2:
            bonus = 0.15  # 20-50% remaining
        else:
            bonus = 0.0  # <20% or exceeded
        
        return bonus
    
    def get_cost_efficiency_reward(self, accuracy: float) -> float:
        """
        Calculate reward for cost-efficient solution.
        
        High accuracy with low cost = high reward
        
        Args:
            accuracy: Task accuracy (0.0-1.0)
            
        Returns:
            Cost efficiency reward
        """
        # Cost per correct answer
        if accuracy == 0.0:
            return -0.5  # Penalty for wasted budget
        
        cost_per_accuracy = self.total_cost_incurred / accuracy
        baseline_cost = self.constraints.query_budget * self.constraints.cost_per_query
        
        efficiency_ratio = baseline_cost / cost_per_accuracy if cost_per_accuracy > 0 else 0.0
        
        # Scale 0.0-0.3
        reward = min(0.3, efficiency_ratio * 0.1)
        
        return reward
    
    def get_constraint_penalty(self) -> float:
        """
        Get penalty if constraints were violated.
        
        Args:
            Returns: Penalty value
        """
        penalty = 0.0
        
        # Budget exceeded
        if self.budget_remaining < 0:
            penalty -= 1.0
        
        # Pending delays at episode end
        if self.query_delays_pending > 0:
            penalty -= 0.2 * self.query_delays_pending
        
        return penalty
    
    def get_episode_summary(self) -> Dict[str, Any]:
        """
        Get summary of constraint performance for this episode.
        
        Returns:
            Summary dictionary
        """
        return {
            "queries_used": self.queries_used,
            "budget_remaining": self.budget_remaining,
            "budget_exceeded": self.budget_remaining < 0,
            "total_cost": self.total_cost_incurred,
            "cost_per_query": self.constraints.cost_per_query,
            "latency_events": sum(1 for log in self.query_log if log["latency_triggered"]),
            "query_log": self.query_log
        }


class ConstrainedObservation:
    """Enhanced observation that includes constraint status."""
    
    @staticmethod
    def from_base_observation(
        base_obs: Observation,
        constraints_env: ConstrainedCRMEnvironment
    ) -> Dict[str, Any]:
        """
        Augment base observation with constraint information.
        
        Args:
            base_obs: Base observation from CRMQueryEnv
            constraints_env: ConstrainedCRMEnvironment instance
            
        Returns:
            Enhanced observation dictionary
        """
        obs_dict = base_obs.dict()
        
        # Add constraint information to message
        constraint_msg = (
            f"Budget: {constraints_env.budget_remaining}/{constraints_env.constraints.query_budget} queries | "
            f"Cost: ${constraints_env.total_cost_incurred:.2f} | "
            f"Delays pending: {constraints_env.query_delays_pending}"
        )
        
        obs_dict["message"] = f"{base_obs.message} | {constraint_msg}"
        
        # Add constraint status
        obs_dict["constraints"] = {
            "budget_remaining": constraints_env.budget_remaining,
            "budget_exceeded": not constraints_env.check_query_budget(),
            "total_cost": constraints_env.total_cost_incurred,
            "delays_pending": constraints_env.query_delays_pending,
            "data_quality": constraints_env.constraints.data_quality_score
        }
        
        return obs_dict


# Example usage
if __name__ == "__main__":
    # Create constrained environment
    constraints = EnvironmentConstraints(
        query_budget=10,
        data_quality_score=0.85,
        latency_probability=0.2
    )
    
    env = ConstrainedCRMEnvironment(constraints)
    
    # Simulate episode
    print("Simulating constrained episode...")
    
    for step in range(12):
        # Attempt a query
        tool = "search_customers"
        args = {"tier": "Gold"}
        
        success, metadata = env.attempt_query(tool, args)
        
        print(f"\nStep {step + 1}:")
        print(f"  Success: {success}")
        print(f"  Budget remaining: {metadata.get('budget_remaining', 'N/A')}")
        print(f"  Total cost: ${metadata.get('total_cost', 0):.2f}")
        print(f"  Latency triggered: {metadata.get('latency_triggered', False)}")
        
        if not success:
            print(f"  Error: {metadata.get('error', 'Unknown')}")
            break
    
    # Episode summary
    print("\n" + "="*60)
    print("Episode Summary:")
    summary = env.get_episode_summary()
    for key, value in summary.items():
        if key != "query_log":
            print(f"  {key}: {value}")
