"""
FastAPI server for CRM Query Environment.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
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


# Startup and shutdown events for debugging and HF Spaces compatibility
@app.on_event("startup")
async def startup_event():
    """Log startup information for debugging."""
    print("=" * 80)
    print("🚀 OpenEnv CRM Query Environment - STARTUP")
    print("=" * 80)
    print(f"✅ App Title: {app.title}")
    print(f"✅ App Version: {app.version}")
    print(f"✅ Total Routes: {len([r for r in app.routes if hasattr(r, 'path')])}")
    print(f"✅ Environment initialized: {type(env).__name__}")
    print("✅ Server ready to accept requests")
    print("=" * 80)

@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown information for debugging."""
    print("=" * 80)
    print("🛑 OpenEnv CRM Query Environment - SHUTDOWN")
    print("=" * 80)


# HTML Response for root path
@app.get("/", response_class=HTMLResponse)
def root():
    """Root endpoint with API documentation"""
    return """
    <html>
        <head>
            <title>OpenEnv CRM Query Environment</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 40px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }
                .container {
                    background: rgba(0, 0, 0, 0.7);
                    padding: 30px;
                    border-radius: 10px;
                    max-width: 800px;
                    margin: 0 auto;
                }
                h1 { color: #667eea; }
                h2 { margin-top: 20px; }
                .endpoint {
                    background: rgba(255, 255, 255, 0.1);
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 5px;
                    border-left: 4px solid #667eea;
                }
                code {
                    background: rgba(0, 0, 0, 0.5);
                    padding: 2px 6px;
                    border-radius: 3px;
                }
                .status {
                    color: #4ade80;
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🏢 OpenEnv Business CRM Query Environment</h1>
                <p>An OpenEnv-compliant environment for training AI agents to perform complex enterprise database queries.</p>
                
                <h2>📊 Status: <span class="status">✅ Running</span></h2>
                
                <h2>📚 Available Endpoints</h2>
                
                <div class="endpoint">
                    <strong>GET /health</strong><br>
                    Health check endpoint. Returns {"status": "healthy"}
                </div>
                
                <div class="endpoint">
                    <strong>GET /tasks</strong><br>
                    Get all available tasks and action schema
                </div>
                
                <div class="endpoint">
                    <strong>POST /reset</strong><br>
                    Reset environment to initial state. Returns initial observation
                </div>
                
                <div class="endpoint">
                    <strong>POST /step</strong><br>
                    Execute action in environment. Send: {"tool": "...", "arguments": {...}}
                </div>
                
                <div class="endpoint">
                    <strong>GET /state</strong><br>
                    Get current environment state
                </div>
                
                <div class="endpoint">
                    <strong>POST /grader</strong><br>
                    Grade the current episode (after submitting answer)
                </div>
                
                <div class="endpoint">
                    <strong>POST /plan</strong><br>
                    Generate execution plan using planner agent
                </div>
                
                <div class="endpoint">
                    <strong>POST /execute_plan</strong><br>
                    Execute a structured plan
                </div>
                
                <h2>🔗 Links</h2>
                <ul>
                    <li><a href="/docs" style="color: #667eea;">Interactive API Docs (Swagger UI)</a></li>
                    <li><a href="/redoc" style="color: #667eea;">API Documentation (ReDoc)</a></li>
                    <li><a href="https://github.com/Nihar1402-iit/OpenEnv-Hackathon" style="color: #667eea;">GitHub Repository</a></li>
                </ul>
                
                <h2>📖 Quick Start</h2>
                <p>Test the environment with curl:</p>
                <code>curl -X POST http://localhost:8000/reset -H "Content-Type: application/json" -d '{}'</code>
            </div>
        </body>
    </html>
    """


@app.get("/health")
def health_check() -> Dict[str, str]:
    """
    Health check endpoint.
    
    Returns:
        Status dict
    """
    return {"status": "healthy"}


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
def grade_episode() -> Dict[str, Any]:
    """
    Grade ALL tasks. Always returns scores for every task, even on cold start.
    
    The validator calls this endpoint without running an episode first.
    Never raise an error — always return scores for all 4 tasks.
    
    Returns:
        {"scores": {"task_id_1": score, "task_id_2": score, ...}}
    """
    from .tasks import get_tasks
    
    all_tasks = get_tasks()
    scores = {}
    
    # Use submitted answer if available, otherwise empty dict (scores 0.01)
    answer = env.final_answer if env.final_answer else {}
    
    for task in all_tasks:
        score = TaskGrader.grade_task(task, answer)
        # Belt-and-suspenders: enforce strictly (0, 1)
        score = max(0.01, min(0.99, float(score)))
        scores[task.task_id] = score
    
    return {"scores": scores}


@app.post("/plan")
def generate_plan() -> Dict[str, Any]:
    """
    Generate execution plan for current task using planner agent.
    
    Returns:
        Structured plan with steps
    """
    try:
        from .multi_agent import PlannerAgent
        
        api_key = None
        planner = PlannerAgent(api_key=api_key)
        task = get_task_by_id(env.current_task_id)
        plan = planner.plan(task.description)
        
        return {
            "task_id": env.current_task_id,
            "plan": plan.model_dump(),
            "message": "Plan generated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/execute_plan")
def execute_plan(plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a structured plan.
    
    Args:
        plan: Plan dict with steps
    
    Returns:
        Execution results
    """
    try:
        from .multi_agent import ExecutorAgent
        
        executor = ExecutorAgent(env)
        results = executor.execute_plan(plan)
        
        return {
            "results": results,
            "final_observation": env.state().model_dump(),
            "message": "Plan executed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
