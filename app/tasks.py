"""
Task definitions for OpenEnv CRM environment.
"""

from typing import Dict, Any, List
from .models import Task


def get_tasks() -> List[Task]:
    """Return all task definitions."""
    return [
        Task(
            task_id="task_easy_001",
            difficulty="easy",
            description="Find the customer with ID C005 and return their customer_id.",
            ground_truth={"customer_ids": ["C005"]},
            max_steps=5,
            action_schema={
                "search_customers": {
                    "type": "object",
                    "properties": {
                        "customer_id": {"type": "string"}
                    }
                }
            }
        ),
        Task(
            task_id="task_medium_001",
            difficulty="medium",
            description="Find all customers who are either Gold tier OR have purchased a Laptop. Return their customer_ids.",
            ground_truth={"customer_ids": ["C001", "C004", "C006", "C009", "C011", "C014", "C016", "C019"]},
            max_steps=10,
            action_schema={
                "search_customers": {
                    "type": "object",
                    "properties": {
                        "tier": {"type": "string"}
                    }
                },
                "search_orders": {
                    "type": "object",
                    "properties": {
                        "product": {"type": "string"}
                    }
                }
            }
        ),
        Task(
            task_id="task_hard_001",
            difficulty="hard",
            description="Find all Gold-tier customers who have at least one HIGH priority OPEN support ticket. Return their customer_ids.",
            ground_truth={"customer_ids": ["C001", "C004", "C006", "C009", "C011", "C014", "C016", "C019"]},
            max_steps=15,
            action_schema={
                "search_customers": {
                    "type": "object",
                    "properties": {
                        "tier": {"type": "string"}
                    }
                },
                "search_tickets": {
                    "type": "object",
                    "properties": {
                        "priority": {"type": "string"},
                        "status": {"type": "string"}
                    }
                }
            }
        ),
        Task(
            task_id="task_extreme_001",
            difficulty="extreme",
            description="Find all customers who appeared in previous Gold-tier queries AND have at least one HIGH priority OPEN support ticket. This requires memory reuse: use results from Gold-tier customer search AND match with high-priority open tickets.",
            ground_truth={"customer_ids": ["C001", "C004", "C006", "C009", "C011", "C014", "C016", "C019"]},
            max_steps=20,
            action_schema={
                "search_customers": {
                    "type": "object",
                    "properties": {
                        "tier": {"type": "string"},
                        "customer_id": {"type": "string"}
                    }
                },
                "search_tickets": {
                    "type": "object",
                    "properties": {
                        "priority": {"type": "string"},
                        "status": {"type": "string"},
                        "customer_id": {"type": "string"}
                    }
                }
            }
        ),
    ]


def get_task_by_id(task_id: str) -> Task:
    """Get task by ID."""
    tasks = get_tasks()
    for task in tasks:
        if task.task_id == task_id:
            return task
    raise ValueError(f"Task {task_id} not found")


def get_all_task_ids() -> List[str]:
    """Get all task IDs."""
    return [task.task_id for task in get_tasks()]
