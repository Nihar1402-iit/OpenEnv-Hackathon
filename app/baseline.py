"""
Baseline agent using OpenAI API for CRM Query Environment.
"""

import os
import json
from typing import Dict, Any, List
from .env import CRMQueryEnv
from .tasks import get_tasks, get_task_by_id
from .grader import TaskGrader
from .utils import extract_customer_ids


def run_baseline() -> Dict[str, Any]:
    """
    Run baseline agent on all tasks.
    
    Returns:
        Results dict with scores for each task
    """
    try:
        import openai
    except ImportError:
        return {
            "error": "openai not installed",
            "message": "Install with: pip install openai"
        }

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "error": "OPENAI_API_KEY not set",
            "message": "Set environment variable OPENAI_API_KEY"
        }

    openai.api_key = api_key

    tasks = get_tasks()
    results = {}
    scores = {}

    for task in tasks:
        task_id = task.task_id
        print(f"\n{'='*60}")
        print(f"Task: {task_id}")
        print(f"Difficulty: {task.difficulty}")
        print(f"Description: {task.description}")
        print(f"{'='*60}")

        env = CRMQueryEnv()
        obs = env.reset()

        # Set specific task
        env.current_task_id = task_id

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

        while step < max_steps and not done:
            step += 1

            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.1,
                    max_tokens=500
                )

                assistant_message = response.choices[0].message.content
                messages.append({
                    "role": "assistant",
                    "content": assistant_message
                })

                # Parse action
                try:
                    action = json.loads(assistant_message)
                except json.JSONDecodeError:
                    # Try to extract JSON from response
                    import re
                    json_match = re.search(r'\{.*\}', assistant_message, re.DOTALL)
                    if json_match:
                        action = json.loads(json_match.group())
                    else:
                        print(f"Step {step}: Failed to parse action")
                        continue

                print(f"\nStep {step}:")
                print(f"  Tool: {action.get('tool')}")
                print(f"  Arguments: {action.get('arguments')}")

                # Execute action
                obs, reward, done, info = env.step(action)

                print(f"  Reward: {reward.value:.2f}")
                print(f"  Result: {obs.last_action_result}")

                # Add result to conversation
                result_message = {
                    "role": "user",
                    "content": f"Action result: {json.dumps(obs.last_action_result, indent=2)}"
                }
                messages.append(result_message)

                if action.get("tool") == "submit_answer":
                    final_answer = action.get("arguments", {})
                    done = True

            except Exception as e:
                print(f"Step {step}: Error - {str(e)}")
                break

        # Grade task
        if final_answer:
            score = TaskGrader.grade_task(task, final_answer)
        else:
            score = 0.0

        print(f"\nTask Score: {score:.2%}")
        print(f"Steps Taken: {step}")
        print(f"Episode Reward: {env.episode_reward:.2f}")

        results[task_id] = {
            "score": score,
            "steps": step,
            "episode_reward": env.episode_reward,
            "final_answer": final_answer,
            "ground_truth": task.ground_truth
        }
        scores[task_id] = score

    # Compute average
    average_score = TaskGrader.compute_average_score(scores)

    print(f"\n{'='*60}")
    print(f"BASELINE RESULTS")
    print(f"{'='*60}")
    print(f"Average Score: {average_score:.2%}")
    for task_id, score in scores.items():
        print(f"  {task_id}: {score:.2%}")

    return {
        "results": results,
        "average_score": average_score,
        "task_scores": scores
    }


if __name__ == "__main__":
    results = run_baseline()
    print("\n" + json.dumps(results, indent=2, default=str))
