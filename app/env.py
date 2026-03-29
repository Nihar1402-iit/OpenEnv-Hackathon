"""
OpenEnv-compliant CRM Query Environment.
"""

from typing import Dict, Any, List, Optional, Tuple
from .models import (
    Observation, Action, Reward, State, Info,
    Customer, Order, SupportTicket
)
from .data import create_database
from .tasks import get_task_by_id, get_all_task_ids
from .reward import RewardCalculator


class CRMQueryEnv:
    """
    CRM Query Environment for OpenEnv compliance.
    
    Agents interact with a simulated enterprise database using tool-based actions.
    """

    def __init__(self) -> None:
        """Initialize environment."""
        self.database = create_database()
        self.current_task_id: Optional[str] = None
        self.step_count: int = 0
        self.max_steps: int = 15
        self.done: bool = False
        self.history: List[Dict[str, Any]] = []
        self.reward_calculator = RewardCalculator()
        self.final_answer: Optional[Dict[str, Any]] = None
        self.last_action_result: Optional[Dict[str, Any]] = None
        self.episode_reward: float = 0.0
        # Memory tracking
        self.retrieved_entities: Dict[str, List[Dict]] = {
            "customers": [],
            "orders": [],
            "tickets": []
        }
        self.step_summaries: List[str] = []
        self.query_cache: Dict[str, List[Dict]] = {}

    def reset(self) -> Observation:
        """
        Reset environment to initial state.
        
        Returns:
            Initial observation
        """
        self.current_task_id = get_all_task_ids()[0]
        self.step_count = 0
        self.done = False
        self.history = []
        self.reward_calculator.reset()
        self.final_answer = None
        self.last_action_result = None
        self.episode_reward = 0.0
        # Reset memory
        self.retrieved_entities = {"customers": [], "orders": [], "tickets": []}
        self.step_summaries = []
        self.query_cache = {}

        return self.state()

    def state(self) -> Observation:
        """
        Get current observation.
        
        Returns:
            Current observation
        """
        if not self.current_task_id:
            raise RuntimeError("Environment not reset")

        task = get_task_by_id(self.current_task_id)

        tables_summary = {
            "customers_count": len(self.database["customers"]),
            "orders_count": len(self.database["orders"]),
            "tickets_count": len(self.database["support_tickets"]),
            "customer_tiers": ["Bronze", "Silver", "Gold"],
            "products": ["Laptop", "Monitor", "Keyboard", "Mouse"],
            "ticket_priorities": ["Low", "Medium", "High"],
            "ticket_statuses": ["Open", "Closed"],
            "order_statuses": ["Pending", "Completed", "Cancelled"],
        }

        return Observation(
            task_id=self.current_task_id,
            task_description=task.description,
            step_count=self.step_count,
            max_steps=task.max_steps,
            available_tools=["search_customers", "search_orders", "search_tickets", "submit_answer"],
            last_action_result=self.last_action_result,
            tables_summary=tables_summary,
            done=self.done,
            message=f"Step {self.step_count}/{task.max_steps}",
            memory_cache=self.retrieved_entities,
            step_summaries=self.step_summaries
        )

    def step(self, action: Dict[str, Any]) -> Tuple[Observation, Reward, bool, Info]:
        """
        Execute action in environment.
        
        Args:
            action: Action dict with 'tool' and 'arguments' keys
        
        Returns:
            (observation, reward, done, info)
        """
        if self.done:
            raise RuntimeError("Episode is done, call reset()")

        if not self.current_task_id:
            raise RuntimeError("Environment not reset")

        self.step_count += 1
        task = get_task_by_id(self.current_task_id)

        # Validate action
        tool = action.get("tool", "")
        arguments = action.get("arguments", {})

        # Execute action
        action_result: Dict[str, Any] = {}
        was_memory_hit = False

        if tool == "search_customers":
            action_result = self._search_customers(arguments)
            # Track retrieved entities
            data = action_result.get("data", [])
            self.retrieved_entities["customers"].extend(data)
            was_memory_hit = self._check_cache_hit(tool, arguments)
        elif tool == "search_orders":
            action_result = self._search_orders(arguments)
            data = action_result.get("data", [])
            self.retrieved_entities["orders"].extend(data)
            was_memory_hit = self._check_cache_hit(tool, arguments)
        elif tool == "search_tickets":
            action_result = self._search_tickets(arguments)
            data = action_result.get("data", [])
            self.retrieved_entities["tickets"].extend(data)
            was_memory_hit = self._check_cache_hit(tool, arguments)
        elif tool == "submit_answer":
            action_result = {"data": [], "message": "Answer submitted"}
            self.final_answer = arguments
            self.done = True
        else:
            action_result = {"data": [], "message": "Invalid tool", "error": True}

        # Create step summary
        summary = self._create_step_summary(tool, arguments, action_result)
        self.step_summaries.append(summary)

        self.last_action_result = action_result
        self.history.append({
            "step": self.step_count,
            "action": action,
            "result": action_result,
            "memory_hit": was_memory_hit,
        })

        # Calculate reward with memory awareness
        reward = self.reward_calculator.calculate(
            action=action,
            action_result=action_result,
            done=self.done,
            task_ground_truth=task.ground_truth,
            step_count=self.step_count,
            max_steps=task.max_steps,
            memory_hit=was_memory_hit,
            retrieved_entities=self.retrieved_entities,
        )

        self.episode_reward += reward.value

        # Check step limit
        if self.step_count >= task.max_steps and not self.done:
            self.done = True

        # Get observation
        obs = self.state()

        # Create info
        info = Info(
            task_id=self.current_task_id,
            episode_reward=self.episode_reward,
            intermediate_results={
                "step_count": self.step_count,
                "last_result_size": len(action_result.get("data", [])),
                "memory_hit": was_memory_hit,
                "cached_entities": sum(len(v) for v in self.retrieved_entities.values()),
            }
        )

        return obs, reward, self.done, info

    def _search_customers(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search customers with filters.
        
        Args:
            filters: Dict with optional keys: customer_id, name, email, tier, phone
        
        Returns:
            Dict with 'data' key containing matching customers
        """
        customers = self.database["customers"]
        results = []

        for customer in customers:
            if not self._matches_filters(customer.model_dump(), filters):
                continue
            results.append(customer.model_dump())

        return {
            "data": results,
            "message": f"Found {len(results)} customers",
            "count": len(results),
        }

    def _search_orders(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search orders with filters.
        
        Args:
            filters: Dict with optional keys: order_id, customer_id, product, status
        
        Returns:
            Dict with 'data' key containing matching orders
        """
        orders = self.database["orders"]
        results = []

        for order in orders:
            if not self._matches_filters(order.model_dump(), filters):
                continue
            results.append(order.model_dump())

        return {
            "data": results,
            "message": f"Found {len(results)} orders",
            "count": len(results),
        }

    def _search_tickets(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search support tickets with filters.
        
        Args:
            filters: Dict with optional keys: ticket_id, customer_id, priority, status
        
        Returns:
            Dict with 'data' key containing matching tickets
        """
        tickets = self.database["support_tickets"]
        results = []

        for ticket in tickets:
            if not self._matches_filters(ticket.model_dump(), filters):
                continue
            results.append(ticket.model_dump())

        return {
            "data": results,
            "message": f"Found {len(results)} tickets",
            "count": len(results),
        }

    @staticmethod
    def _matches_filters(entity: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """
        Check if entity matches all filters.
        
        Args:
            entity: Entity dict
            filters: Filter dict
        
        Returns:
            True if entity matches all filters
        """
        for key, value in filters.items():
            if key not in entity:
                return False
            if entity[key] != value:
                return False
        return True

    def _check_cache_hit(self, tool: str, arguments: Dict[str, Any]) -> bool:
        """
        Check if query result is in cache.
        
        Args:
            tool: Tool name
            arguments: Query arguments
        
        Returns:
            True if cached result would match
        """
        cache_key = f"{tool}:{str(sorted(arguments.items()))}"
        return cache_key in self.query_cache

    def _create_step_summary(self, tool: str, arguments: Dict[str, Any], result: Dict[str, Any]) -> str:
        """
        Create a compact summary of a step for memory.
        
        Args:
            tool: Tool used
            arguments: Arguments passed
            result: Result returned
        
        Returns:
            Summary string
        """
        count = len(result.get("data", []))
        return f"Step {self.step_count}: {tool} {arguments} -> {count} results"

    def close(self) -> None:
        """Close environment."""
        pass
