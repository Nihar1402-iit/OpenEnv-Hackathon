"""
FastAPI server for CRM Query Environment.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List
from .env import CRMQueryEnv
from .models import Task, Observation, Reward
from .tasks import get_tasks, get_task_by_id
from .grader import TaskGrader
import json


# Global environment instance
env = CRMQueryEnv()
app = FastAPI(
    title="CRM Query Environment",
    description="OpenEnv-compliant CRM query environment for agent training",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/tasks")
def get_available_tasks() -> Dict[str, Any]:
    """
    Get all available tasks and action schema.
    
    Returns:
        Dict with tasks and action schema
    """
    tasks = get_tasks()
    return {
        "tasks": [
            {
                "task_id": task.task_id,
                "difficulty": task.difficulty,
                "description": task.description,
                "max_steps": task.max_steps,
            }
            for task in tasks
        ],
        "action_schema": {
            "type": "object",
            "properties": {
                "tool": {
                    "type": "string",
                    "enum": ["search_customers", "search_orders", "search_tickets", "submit_answer"]
                },
                "arguments": {
                    "type": "object",
                    "description": "Arguments specific to the tool"
                }
            },
            "required": ["tool", "arguments"]
        },
        "tools": {
            "search_customers": {
                "description": "Search customers by filters",
                "parameters": {
                    "customer_id": "string (optional)",
                    "name": "string (optional)",
                    "email": "string (optional)",
                    "tier": "string - Bronze|Silver|Gold (optional)",
                    "phone": "string (optional)"
                }
            },
            "search_orders": {
                "description": "Search orders by filters",
                "parameters": {
                    "order_id": "string (optional)",
                    "customer_id": "string (optional)",
                    "product": "string (optional)",
                    "status": "string - Pending|Completed|Cancelled (optional)"
                }
            },
            "search_tickets": {
                "description": "Search support tickets by filters",
                "parameters": {
                    "ticket_id": "string (optional)",
                    "customer_id": "string (optional)",
                    "priority": "string - Low|Medium|High (optional)",
                    "status": "string - Open|Closed (optional)"
                }
            },
            "submit_answer": {
                "description": "Submit final answer with list of customer_ids",
                "parameters": {
                    "customer_ids": "list of strings"
                }
            }
        }
    }


@app.post("/reset")
def reset_environment() -> Dict[str, Any]:
    """
    Reset environment to initial state.
    
    Returns:
        Initial observation
    """
    obs = env.reset()
    return {
        "observation": obs.model_dump(),
        "message": "Environment reset successfully"
    }


@app.post("/step")
def step_environment(action: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute action in environment.
    
    Args:
        action: Action dict with 'tool' and 'arguments'
    
    Returns:
        Dict with observation, reward, done, and info
    """
    try:
        obs, reward, done, info = env.step(action)
        return {
            "observation": obs.model_dump(),
            "reward": reward.model_dump(),
            "done": done,
            "info": info.model_dump()
        }
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/state")
def get_current_state() -> Dict[str, Any]:
    """
    Get current environment state.
    
    Returns:
        Current observation
    """
    obs = env.state()
    return {
        "observation": obs.model_dump(),
        "step_count": env.step_count,
        "done": env.done,
        "episode_reward": env.episode_reward
    }


@app.post("/grader")
def grade_episode(task_id: str = None) -> Dict[str, Any]:
    """
    Grade the current episode.
    
    Args:
        task_id: Optional task ID to grade (defaults to current task)
    
    Returns:
        Grade and analysis
    """
    if not env.final_answer:
        raise HTTPException(status_code=400, detail="No answer submitted yet")
    
    target_task_id = task_id or env.current_task_id
    if not target_task_id:
        raise HTTPException(status_code=400, detail="No task active")
    
    task = get_task_by_id(target_task_id)
    score = TaskGrader.grade_task(task, env.final_answer)
    
    return {
        "task_id": target_task_id,
        "score": score,
        "ground_truth": task.ground_truth,
        "submitted_answer": env.final_answer,
        "steps_taken": env.step_count,
        "episode_reward": env.episode_reward,
        "message": f"Task scored: {score:.2%}"
    }


@app.post("/plan")
def generate_plan() -> Dict[str, Any]:
    """
    Generate execution plan for current task using planner agent.
    
    Returns:
        Structured plan with steps
    """
    try:
        from .multi_agent import PlannerAgent
        
        if not env.current_task_id:
            raise HTTPException(status_code=400, detail="Environment not reset")
        
        task = get_task_by_id(env.current_task_id)
        planner = PlannerAgent()
        
        plan = planner.generate_plan(
            task_id=env.current_task_id,
            task_description=task.description,
            tables_summary=env.state().tables_summary,
            max_steps=task.max_steps
        )
        
        return {
            "plan": plan.model_dump(),
            "message": "Plan generated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plan generation failed: {str(e)}")


@app.post("/execute_plan")
def execute_full_pipeline() -> Dict[str, Any]:
    """
    Run full multi-agent pipeline: planner → executor.
    
    Returns:
        Complete execution results
    """
    try:
        from .multi_agent import Coordinator
        
        if not env.current_task_id:
            raise HTTPException(status_code=400, detail="Environment not reset")
        
        coordinator = Coordinator()
        results = coordinator.run_pipeline(env, max_iterations=1)
        
        return {
            "results": results,
            "message": "Multi-agent pipeline executed",
            "episode_reward": env.episode_reward,
            "steps_taken": env.step_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")


@app.get("/baseline")
def run_baseline_agent() -> Dict[str, Any]:
    """
    Run baseline agent on all tasks.
    
    Returns:
        Scores for each task and average
    """
    from .baseline import run_baseline
    
    try:
        results = run_baseline()
        return {
            "results": results,
            "message": "Baseline agent completed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Baseline failed: {str(e)}")


@app.get("/health")
def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "environment": "CRM Query Environment"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
