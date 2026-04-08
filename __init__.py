"""
OpenEnv CRM Query Environment - Root package init
Exports graders and task management functions for validator access.
"""

# Primary export from app module
try:
    from app import (
        GRADERS,
        get_grader,
        get_all_graders,
        get_tasks,
        get_task_by_id,
    )
except ImportError:
    # Fallback to standalone graders if app import fails
    from standalone_graders import GRADERS, get_grader, get_all_graders
    # get_tasks and get_task_by_id still from app
    from app.tasks import get_tasks, get_task_by_id

__all__ = [
    "GRADERS",
    "get_grader",
    "get_all_graders",
    "get_tasks",
    "get_task_by_id",
]
