"""
OpenEnv CRM Query Environment - Root package init
Exports graders and task management functions for validator access.
"""

# Export graders and related functions for easy access by validators
from app import (
    GRADERS,
    get_grader,
    get_all_graders,
    get_tasks,
    get_task_by_id,
)

__all__ = [
    "GRADERS",
    "get_grader",
    "get_all_graders",
    "get_tasks",
    "get_task_by_id",
]
