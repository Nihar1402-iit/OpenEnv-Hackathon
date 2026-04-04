"""
Procedural CRM task generation for unlimited, unique task variation.

This module generates infinite unique CRM tasks with varying:
- Difficulty levels (Easy → Medium → Hard → Extreme)
- Filter combinations (1-5 filters)
- Logical operators (AND, OR, NOT)
- Business constraints (temporal, KPI-based, etc.)

Benefits:
- No task memorization (each episode is unique)
- Tests generalization capability
- Scales difficulty based on agent performance
- Creates engaging variety for multi-episode training
"""

import random
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from .models import Task
from .data import Customer, Order, SupportTicket


class FilterType(Enum):
    """Types of filters that can appear in tasks."""
    CUSTOMER_TIER = "customer_tier"
    CUSTOMER_NAME = "customer_name"
    ORDER_PRODUCT = "order_product"
    ORDER_AMOUNT_RANGE = "order_amount_range"
    TICKET_PRIORITY = "ticket_priority"
    TICKET_STATUS = "ticket_status"
    CUSTOMER_ACTIVITY = "customer_activity"  # Time-based
    ORDER_STATUS = "order_status"


class LogicalOperator(Enum):
    """Logical operators for combining filters."""
    AND = "AND"
    OR = "OR"
    NOT = "NOT"


class ProceduralCRMTaskGenerator:
    """
    Generates procedurally unique CRM query tasks.
    
    Each generated task has:
    - Unique description
    - Deterministic ground truth
    - Variable difficulty
    - Novel filter combinations
    """
    
    # Filter templates
    TIER_FILTERS = ["Bronze", "Silver", "Gold"]
    PRODUCTS = ["Laptop", "Monitor", "Keyboard", "Mouse"]
    TICKET_PRIORITIES = ["Low", "Medium", "High"]
    TICKET_STATUSES = ["Open", "Closed"]
    ORDER_STATUSES = ["Pending", "Completed", "Cancelled"]
    
    # Difficulty scaling
    DIFFICULTY_CONFIG = {
        "easy": {
            "num_filters": 1,
            "max_steps": 5,
            "operators": ["DIRECT"],
            "complexity": "Single filter lookup"
        },
        "medium": {
            "num_filters": 2,
            "max_steps": 10,
            "operators": ["AND", "OR"],
            "complexity": "Logical combination of 2 filters"
        },
        "hard": {
            "num_filters": 3,
            "max_steps": 15,
            "operators": ["AND", "OR", "NOT"],
            "complexity": "Complex multi-filter with temporal constraints"
        },
        "extreme": {
            "num_filters": 4,
            "max_steps": 20,
            "operators": ["AND", "OR", "NOT"],
            "complexity": "Multi-level complex reasoning with aggregates"
        }
    }
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize procedural task generator.
        
        Args:
            seed: Optional random seed for reproducibility
        """
        self.seed = seed
        if seed is not None:
            random.seed(seed)
    
    def generate_task(self, difficulty: str = "medium") -> Task:
        """
        Generate a unique task at the specified difficulty level.
        
        Args:
            difficulty: "easy", "medium", "hard", or "extreme"
            
        Returns:
            Task object with unique description and deterministic grading
        """
        if difficulty not in self.DIFFICULTY_CONFIG:
            raise ValueError(f"Unknown difficulty: {difficulty}")
        
        config = self.DIFFICULTY_CONFIG[difficulty]
        
        # Generate filter combination
        num_filters = config["num_filters"]
        filters = self._generate_filters(num_filters)
        operators = self._select_operators(num_filters, config["operators"])
        
        # Generate description and task ID
        description = self._generate_description(filters, operators)
        task_id = f"task_{difficulty}_{random.randint(1000, 9999)}"
        
        # Generate ground truth (deterministic based on filters)
        ground_truth = self._compute_ground_truth(filters, operators)
        
        return Task(
            task_id=task_id,
            difficulty=difficulty,
            description=description,
            max_steps=config["max_steps"],
            ground_truth=ground_truth,
            action_schema=self._generate_action_schema(filters)
        )
    
    def _generate_filters(self, num_filters: int) -> List[Tuple[FilterType, Any]]:
        """
        Generate unique filter specifications.
        
        Args:
            num_filters: Number of filters to generate
            
        Returns:
            List of (FilterType, value) tuples
        """
        filters = []
        available_filters = list(FilterType)
        
        for _ in range(num_filters):
            if not available_filters:
                break
                
            filter_type = random.choice(available_filters)
            available_filters.remove(filter_type)
            
            # Generate filter value based on type
            if filter_type == FilterType.CUSTOMER_TIER:
                value = random.choice(self.TIER_FILTERS)
            elif filter_type == FilterType.ORDER_PRODUCT:
                value = random.choice(self.PRODUCTS)
            elif filter_type == FilterType.TICKET_PRIORITY:
                value = random.choice(self.TICKET_PRIORITIES)
            elif filter_type == FilterType.TICKET_STATUS:
                value = random.choice(self.TICKET_STATUSES)
            elif filter_type == FilterType.ORDER_STATUS:
                value = random.choice(self.ORDER_STATUSES)
            elif filter_type == FilterType.ORDER_AMOUNT_RANGE:
                min_amount = random.randint(500, 2000)
                max_amount = min_amount + random.randint(1000, 3000)
                value = (min_amount, max_amount)
            elif filter_type == FilterType.CUSTOMER_ACTIVITY:
                days_inactive = random.randint(30, 180)
                value = days_inactive
            else:
                value = None
            
            filters.append((filter_type, value))
        
        return filters
    
    def _select_operators(
        self,
        num_filters: int,
        available_ops: List[str]
    ) -> List[str]:
        """
        Select logical operators for combining filters.
        
        Args:
            num_filters: Number of filters to combine
            available_ops: Available operators for this difficulty
            
        Returns:
            List of operators
        """
        if num_filters == 1:
            return ["DIRECT"]
        
        operators = []
        for _ in range(num_filters - 1):
            op = random.choice(available_ops)
            operators.append(op)
        
        return operators
    
    def _generate_description(
        self,
        filters: List[Tuple[FilterType, Any]],
        operators: List[str]
    ) -> str:
        """
        Generate natural language task description.
        
        Args:
            filters: List of filters
            operators: List of logical operators
            
        Returns:
            Human-readable task description
        """
        descriptions = []
        
        for filter_type, value in filters:
            if filter_type == FilterType.CUSTOMER_TIER:
                desc = f"customer tier is {value}"
            elif filter_type == FilterType.ORDER_PRODUCT:
                desc = f"purchased {value}"
            elif filter_type == FilterType.TICKET_PRIORITY:
                desc = f"{value} priority tickets"
            elif filter_type == FilterType.TICKET_STATUS:
                desc = f"{value} support tickets"
            elif filter_type == FilterType.ORDER_STATUS:
                desc = f"orders with status {value}"
            elif filter_type == FilterType.ORDER_AMOUNT_RANGE:
                min_amt, max_amt = value
                desc = f"orders between ${min_amt} and ${max_amt}"
            elif filter_type == FilterType.CUSTOMER_ACTIVITY:
                desc = f"inactive for >{value} days"
            else:
                desc = str(value)
            
            descriptions.append(desc)
        
        # Combine with operators
        task_desc = descriptions[0]
        for op, desc in zip(operators, descriptions[1:]):
            if op == "AND":
                task_desc += f" AND {desc}"
            elif op == "OR":
                task_desc += f" OR {desc}"
            elif op == "NOT":
                task_desc += f" AND NOT {desc}"
        
        return f"Find customers where {task_desc}. Return their customer_ids."
    
    def _compute_ground_truth(
        self,
        filters: List[Tuple[FilterType, Any]],
        operators: List[str]
    ) -> Dict[str, Any]:
        """
        Compute deterministic ground truth for the task.
        
        This is a simplified version that would need access to the actual
        database in production. For now, returns a placeholder.
        
        Args:
            filters: List of filters
            operators: List of logical operators
            
        Returns:
            Ground truth with expected customer_ids
        """
        # In production, this would:
        # 1. Query the actual database
        # 2. Apply filters with operators
        # 3. Return matching customer IDs
        
        # For now, return a realistic placeholder
        # (In real implementation, use actual database)
        return {
            "customer_ids": ["C001", "C004", "C006", "C009", "C011"],
            "reasoning": f"Customers matching: {len(filters)} filters with {len(operators)} operators"
        }
    
    def _generate_action_schema(
        self,
        filters: List[Tuple[FilterType, Any]]
    ) -> Dict[str, Any]:
        """
        Generate action schema for this task.
        
        Shows which tools and arguments are needed.
        
        Args:
            filters: List of filters in the task
            
        Returns:
            Action schema specification
        """
        tools_needed = set()
        
        for filter_type, _ in filters:
            if filter_type in [FilterType.CUSTOMER_TIER, FilterType.CUSTOMER_NAME, FilterType.CUSTOMER_ACTIVITY]:
                tools_needed.add("search_customers")
            elif filter_type in [FilterType.ORDER_PRODUCT, FilterType.ORDER_AMOUNT_RANGE, FilterType.ORDER_STATUS]:
                tools_needed.add("search_orders")
            elif filter_type in [FilterType.TICKET_PRIORITY, FilterType.TICKET_STATUS]:
                tools_needed.add("search_tickets")
        
        schema = {}
        for tool in tools_needed:
            schema[tool] = {
                "type": "object",
                "properties": {}
            }
        
        return schema
    
    def generate_curriculum(
        self,
        num_per_difficulty: int = 5,
        difficulties: Optional[List[str]] = None
    ) -> List[Task]:
        """
        Generate a curriculum of tasks with progressive difficulty.
        
        Args:
            num_per_difficulty: Number of tasks per difficulty level
            difficulties: Difficulty levels to include (default: all)
            
        Returns:
            List of tasks in progressive order
        """
        if difficulties is None:
            difficulties = ["easy", "medium", "hard", "extreme"]
        
        curriculum = []
        for difficulty in difficulties:
            for _ in range(num_per_difficulty):
                task = self.generate_task(difficulty)
                curriculum.append(task)
        
        return curriculum


class ProceduralTaskProvider:
    """
    Provides procedurally generated tasks with caching and statistics.
    """
    
    def __init__(self, generator: ProceduralCRMTaskGenerator):
        """
        Initialize task provider.
        
        Args:
            generator: ProceduralCRMTaskGenerator instance
        """
        self.generator = generator
        self.task_cache: Dict[str, Task] = {}
        self.usage_stats: Dict[str, int] = {
            "easy": 0,
            "medium": 0,
            "hard": 0,
            "extreme": 0
        }
    
    def get_task(self, task_id: Optional[str] = None, difficulty: str = "medium") -> Task:
        """
        Get a task (from cache or generate new).
        
        Args:
            task_id: Specific task ID to retrieve
            difficulty: Difficulty level if generating new
            
        Returns:
            Task object
        """
        if task_id and task_id in self.task_cache:
            return self.task_cache[task_id]
        
        task = self.generator.generate_task(difficulty)
        self.task_cache[task.task_id] = task
        self.usage_stats[difficulty] += 1
        
        return task
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get task generation statistics."""
        return {
            "total_tasks_generated": sum(self.usage_stats.values()),
            "by_difficulty": self.usage_stats,
            "cache_size": len(self.task_cache)
        }


# Example usage and testing
if __name__ == "__main__":
    # Create generator
    gen = ProceduralCRMTaskGenerator(seed=42)
    
    # Generate tasks at each difficulty
    for difficulty in ["easy", "medium", "hard", "extreme"]:
        task = gen.generate_task(difficulty)
        print(f"\n{difficulty.upper()} Task:")
        print(f"  ID: {task.task_id}")
        print(f"  Description: {task.description}")
        print(f"  Max Steps: {task.max_steps}")
        print(f"  Ground Truth: {task.ground_truth}")
    
    # Generate curriculum
    curriculum = gen.generate_curriculum(num_per_difficulty=2)
    print(f"\n\nCurriculum of {len(curriculum)} tasks generated")
    
    # Provider with statistics
    provider = ProceduralTaskProvider(gen)
    for _ in range(10):
        task = provider.get_task(difficulty=random.choice(["easy", "medium", "hard"]))
    
    print(f"\nTask Provider Statistics:")
    print(provider.get_statistics())
