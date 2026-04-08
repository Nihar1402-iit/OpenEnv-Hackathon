#!/usr/bin/env python3
"""
Inference script for OpenEnv Business CRM Query Environment.

This script serves as the baseline agent for the hackathon submission.
It uses OpenAI's API to interact with the CRM Query environment.

Environment Variables:
    HF_TOKEN (required): OpenAI-compatible API key (used as api_key)
    API_BASE_URL (optional): Custom API base URL (defaults to OpenAI official)
    MODEL_NAME (optional): Model identifier (defaults to gpt-3.5-turbo)

Usage:
    python inference.py
    
    With custom configuration:
    export OPENAI_API_KEY="sk-..."
    export API_BASE_URL="https://custom-api.example.com/v1"
    export MODEL_NAME="gpt-4"
    python inference.py
"""

import os
import json
import sys
import time
from typing import Dict, Any, List
from pathlib import Path

# Add app directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.env import CRMQueryEnv
from app.tasks import get_tasks, get_task_by_id
from app.grader import TaskGrader
from app.utils import extract_customer_ids


def get_api_config() -> Dict[str, str]:
    """Load API configuration from environment variables.

    Required env vars:
        HF_TOKEN: OpenAI-compatible API key (or OPENAI_API_KEY)
    
    Optional env vars (with defaults):
        API_BASE_URL (default: "https://api.openai.com/v1")
        MODEL_NAME (default: "gpt-3.5-turbo")
    
    Optional for docker deployments:
        LOCAL_IMAGE_NAME: Docker image name (when using from_docker_image())
    """
    # HF_TOKEN is required - no default
    api_key = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "HF_TOKEN or OPENAI_API_KEY environment variable is required. "
            "Please set: export HF_TOKEN='your-api-key'"
        )
    
    # API_BASE_URL has default
    api_base = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
    
    # MODEL_NAME has default
    model_name = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
    
    # LOCAL_IMAGE_NAME is optional (for docker deployments)
    local_image_name = os.getenv("LOCAL_IMAGE_NAME")

    return {
        "api_key": api_key,
        "api_base": api_base,
        "model_name": model_name,
        "local_image_name": local_image_name,
    }
def initialize_openai_client(config: Dict[str, str]) -> Any:
    """Initialize OpenAI Client (required by rules)."""
    try:
        from openai import OpenAI
    except ImportError as e:
        raise ImportError("openai package not installed. Install with: pip install openai") from e

    return OpenAI(api_key=config["api_key"], base_url=config["api_base"])


def _log_start(run_id: str, api_base_url: str, model_name: str, task_ids: list[str]) -> None:
    """Log session start in structured format for Phase 2 checker."""
    print(f"[START] task=all env=CRMQueryEnv model={model_name}", flush=True)


def _log_step(task_id: str, step_idx: int, tool: str, arguments: Dict[str, Any], reward: float, done: bool, error: str = None) -> None:
    """Log step in structured format for Phase 2 checker."""
    error_val = error if error is not None else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step_idx} action={tool} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True
    )


def _log_task_end(task_id: str, success: bool, steps: int, rewards: List[float], score: float) -> None:
    """Log task end in structured format for Phase 2 checker."""
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] task_id={task_id} success={str(success).lower()} steps={steps} rewards={rewards_str} score={score:.3f}",
        flush=True
    )


def _log_final_end(run_id: str, average_score: float, total_time_sec: float, task_scores: Dict[str, float]) -> None:
    """Log final session end."""
    success = average_score >= 0.50
    score_str = ",".join(f"{v:.3f}" for v in task_scores.values())
    print(
        f"[END] task_id=multi success={str(success).lower()} steps=0 rewards={score_str} score={average_score:.3f}",
        flush=True
    )


def run_inference_on_task(
    env: CRMQueryEnv,
    task: Any,
    openai_client: Any,
    model_name: str,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Run inference on a single task using the OpenAI API.
    
    Args:
        env: CRM Query environment instance
        task: Task object with description and metadata
        openai_client: Configured OpenAI client
        model_name: Name of the model to use
        verbose: Whether to print step-by-step output
        
    Returns:
        Dictionary with task results (score, steps, reward, answer)
    """
    task_id = task.task_id
    if verbose:
        print(f"\n{'='*60}")
        print(f"Task: {task_id}")
        print(f"Difficulty: {task.difficulty}")
        print(f"Description: {task.description}")
        print(f"{'='*60}")

    # Reset environment and set task
    obs = env.reset()
    env.current_task_id = task_id

    # Initialize conversation with system prompt
    messages = [
        {
            "role": "system",
            "content": """You are an expert database analyst. Your task is to query a CRM database to find specific customers based on criteria.

Available tools:
1. search_customers: Search customers by filters (customer_id, name, email, tier, phone)
2. search_orders: Search orders by filters (order_id, customer_id, product, status)
3. search_tickets: Search support tickets by filters (ticket_id, customer_id, priority, status)
4. submit_answer: Submit final answer with list of customer_ids

Always respond with valid JSON containing 'tool' and 'arguments' keys.
Analyze the task carefully, make multiple queries if needed, and submit your final answer."""
        },
        {
            "role": "user",
            "content": f"Task: {task.description}\n\nCRM Database Summary:\n{json.dumps(obs.tables_summary, indent=2)}"
        }
    ]

    step = 0
    max_steps = task.max_steps
    done = False
    final_answer = None
    step_times = []
    task_rewards = []  # 🔥 Track rewards for each step

    while step < max_steps and not done:
        step += 1
        step_start = time.time()

        try:
            # Call OpenAI API
            response = openai_client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.1,
                max_tokens=500
            )

            assistant_message = response.choices[0].message.content
            messages.append({
                "role": "assistant",
                "content": assistant_message
            })

            # Parse action from response
            try:
                action = json.loads(assistant_message)
            except json.JSONDecodeError:
                # Try to extract JSON from response if it's wrapped in text
                import re
                json_match = re.search(r'\{.*\}', assistant_message, re.DOTALL)
                if json_match:
                    action = json.loads(json_match.group())
                else:
                    if verbose:
                        print(f"Step {step}: Failed to parse action from response")
                    continue

            if verbose:
                print(f"\nStep {step}:")
                print(f"  Tool: {action.get('tool')}")
                print(f"  Arguments: {action.get('arguments')}")

            # 🔥 FIX 1: SANITIZE ACTION BEFORE EXECUTION
            if not isinstance(action, dict):
                action = {"tool": "submit_answer", "arguments": {"customer_ids": []}}

            if "tool" not in action:
                action["tool"] = "submit_answer"

            if "arguments" not in action or not isinstance(action["arguments"], dict):
                action["arguments"] = {}

            # Ensure submit_answer always valid
            if action["tool"] == "submit_answer":
                ids = action["arguments"].get("customer_ids", [])
                if not isinstance(ids, list):
                    ids = []
                action["arguments"]["customer_ids"] = [str(x) for x in ids]

            # Execute action in environment
            obs, reward, done, info = env.step(action)

            # Clamp reward to valid range
            reward_value = float(reward.value)
            reward_value = max(0.0, min(1.0, reward_value))
            task_rewards.append(reward_value)  # 🔥 Track rewards

            # Log structured STEP marker
            _log_step(
                task_id=task_id,
                step_idx=step,
                tool=action.get('tool', ''),
                arguments=action.get('arguments', {}),
                reward=reward_value,
                done=bool(done),
                error=None
            )

            if verbose:
                print(f"  Reward: {reward.value:.2f}")
                print(f"  Result: {obs.last_action_result}")

            # Add result to conversation for next step
            result_message = {
                "role": "user",
                "content": f"Action result: {json.dumps(obs.last_action_result, indent=2)}"
            }
            messages.append(result_message)

            # Check if final answer was submitted
            if action.get("tool") == "submit_answer":
                args = action.get("arguments", {})

                # 🔥 HARD VALIDATION - Ensure format is correct
                if not isinstance(args, dict):
                    args = {}

                customer_ids = args.get("customer_ids", [])

                if not isinstance(customer_ids, list):
                    customer_ids = []

                # Ensure all are strings
                customer_ids = [str(x) for x in customer_ids]

                final_answer = {"customer_ids": customer_ids}
                done = True

        except Exception as e:
            if verbose:
                print(f"Step {step}: Error - {str(e)}")
            # Log error step with empty action
            _log_step(
                task_id=task_id,
                step_idx=step,
                tool="error",
                arguments={"error": str(e)},
                reward=0.01,
                done=False,
                error=str(e)
            )
            # Continue to next step even on error (🔥 NOT break)
            continue
        
        finally:
            step_time = time.time() - step_start
            step_times.append(step_time)

    # 🔥 FIX 2: FORCE FINAL SUBMISSION AT MAX STEPS
    if step == max_steps and not done:
        if verbose:
            print(f"\n⚠️  Max steps reached, forcing final submission...")
        
        fallback_action = {
            "tool": "submit_answer",
            "arguments": {"customer_ids": []}
        }
        
        try:
            obs, reward, done, info = env.step(fallback_action)
            final_answer = {"customer_ids": []}
        except Exception as e:
            if verbose:
                print(f"Forced submission failed: {str(e)}")
            final_answer = {"customer_ids": []}

    # 🔥 FIX 3: FORCE FINAL SUBMISSION VIA ENV IF NOT ALREADY SUBMITTED
    if not final_answer:
        if verbose:
            print(f"\n⚠️  No submission detected, forcing final submission through env...")
        
        fallback_action = {
            "tool": "submit_answer",
            "arguments": {"customer_ids": []}
        }

        try:
            obs, reward, done, info = env.step(fallback_action)
            final_answer = {"customer_ids": []}
        except Exception as e:
            if verbose:
                print(f"Fallback submission failed: {str(e)}")
            final_answer = {"customer_ids": []}

    score = TaskGrader.grade_task(task, final_answer)

    if verbose:
        print(f"\nTask Score: {score:.2%}")
        print(f"Steps Taken: {step}")
        print(f"Episode Reward: {env.episode_reward:.2f}")
        if step_times:
            print(f"Avg Step Time: {sum(step_times)/len(step_times):.2f}s")

    return {
        "score": score,
        "steps": step,
        "episode_reward": env.episode_reward,
        "final_answer": final_answer,
        "ground_truth": task.ground_truth,
        "step_times": step_times,
        "task_rewards": task_rewards  # 🔥 Return actual tracked rewards
    }


def run_inference(verbose: bool = True) -> Dict[str, Any]:
    """
    Run complete inference on all available tasks.
    
    Args:
        verbose: Whether to print detailed output
        
    Returns:
        Dictionary with aggregated results across all tasks
    """
    # Get API configuration
    try:
        config = get_api_config()
    except ValueError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        return {
            "error": "Configuration Error",
            "message": str(e)
        }

    # Initialize OpenAI client
    try:
        openai_client = initialize_openai_client(config)
    except ImportError as e:
        print(f"Import Error: {e}", file=sys.stderr)
        return {
            "error": "Import Error",
            "message": str(e)
        }

    if verbose:
        print("\n" + "="*60)
        print("OpenEnv Business CRM Query Environment - Inference")
        print("="*60)
        print(f"API Base: {config['api_base']}")
        print(f"Model: {config['model_name']}")
        print("="*60)

    # Get all tasks
    tasks = get_tasks()
    run_id = str(int(time.time()))
    print(f"Total tasks loaded: {len(tasks)}")  # 🔥 Debug output
    _log_start(run_id, config["api_base"], config["model_name"], [t.task_id for t in tasks])
    results = {}
    scores = {}
    total_time = time.time()

    # Run inference on each task
    for task in tasks:
        task_id = task.task_id
        try:
            env = CRMQueryEnv()
            task_result = run_inference_on_task(
                env,
                task,
                openai_client,
                config["model_name"],
                verbose=verbose
            )
            results[task_id] = task_result
            scores[task_id] = task_result["score"]
            
            # Log task end with proper structure
            task_success = task_result["score"] >= 0.50
            task_rewards = task_result.get("task_rewards", [])  # 🔥 Use actual tracked rewards
            _log_task_end(
                task_id=task_id,
                success=task_success,
                steps=task_result["steps"],
                rewards=task_rewards,
                score=task_result["score"]
            )
        except Exception as e:
            if verbose:
                print(f"\nFailed to run task {task_id}: {str(e)}")
            results[task_id] = {
                "error": str(e),
                "score": 0.01  # Minimum non-zero score for error cases
            }
            scores[task_id] = 0.01
            _log_task_end(
                task_id=task_id,
                success=False,
                steps=0,
                rewards=[],
                score=0.01
            )

    total_time = time.time() - total_time

    # Compute aggregate statistics and clamp scores
    average_score = TaskGrader.compute_average_score(scores)
    # Ensure score is in (0.001, 0.999) range
    average_score = max(0.001, min(0.999, average_score))

    # Log structured END marker
    _log_final_end(run_id, average_score, total_time, scores)

    if verbose:
        print(f"\n{'='*60}")
        print("INFERENCE RESULTS SUMMARY")
        print(f"{'='*60}")
        print(f"Total Time: {total_time:.2f}s")
        print(f"Average Score: {average_score:.2%}")
        print(f"{'='*60}")
        for task_id, score in scores.items():
            status = "✅" if score > 0 else "❌"
            print(f"  {status} {task_id}: {score:.2%}")

    return {
        "results": results,
        "average_score": average_score,
        "task_scores": scores,
        "total_time": total_time,
        "config": {
            "api_base": config["api_base"],
            "model_name": config["model_name"]
        }
    }


def main():
    """Main entry point for the inference script."""
    try:
        results = run_inference(verbose=True)
        
        # Print final results as JSON
        print("\n" + json.dumps(results, indent=2, default=str))
        
        # Exit with appropriate code
        if results.get("error"):
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n\nInference interrupted by user.", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"\n\nFatal Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
