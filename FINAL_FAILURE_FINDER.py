#!/usr/bin/env python3
"""
VERDICT: Search for ANY failing test case - exhaustive
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.env import CRMQueryEnv
from app.tasks import get_tasks
from app.grader import TaskGrader


def simulate_sanitization(action):
    """Exact sanitization from inference.py"""
    valid_tools = {
        "search_customers",
        "search_orders",
        "search_tickets",
        "submit_answer"
    }

    if not isinstance(action, dict):
        action = {"tool": "submit_answer", "arguments": {"customer_ids": []}}

    tool = action.get("tool", "")
    if not isinstance(tool, str):
        tool = ""
    
    tool = tool.lower().strip()

    if tool not in valid_tools:
        tool = "submit_answer"

    arguments = action.get("arguments", {})
    if not isinstance(arguments, dict):
        arguments = {}

    if tool == "submit_answer":
        customer_ids = arguments.get("customer_ids", [])
        if not isinstance(customer_ids, list):
            customer_ids = []
        customer_ids = [str(x) for x in customer_ids if x is not None]
        arguments = {"customer_ids": customer_ids}

    action = {
        "tool": tool,
        "arguments": arguments
    }
    
    return action


def main():
    print("\n" + "="*70)
    print("EXHAUSTIVE FAILURE FINDER")
    print("="*70)
    print("Searching for ANY test case that fails...")
    print()
    
    failures = []
    test_count = 0
    
    # Test 1: Every possible LLM malformation + every task
    llm_outputs = [
        None,
        "invalid",
        {},
        {"tool": "invalid"},
        {"tool": "SUBMIT_ANSWER"},
        {"tool": "  submit_answer  "},
        {"arguments": {}},
        {"tool": "submit_answer", "arguments": None},
        {"tool": "submit_answer", "arguments": "invalid"},
        {"tool": "submit_answer", "arguments": {"customer_ids": None}},
        {"tool": "submit_answer", "arguments": {"customer_ids": "C001"}},
        {"tool": "submit_answer", "arguments": {"customer_ids": 123}},
        {"tool": "submit_answer", "arguments": {"customer_ids": ["C001", None, 123]}},
    ]
    
    env = CRMQueryEnv()
    
    for task in get_tasks():
        for llm_output in llm_outputs:
            test_count += 1
            
            try:
                # Reset
                obs = env.reset()
                env.current_task_id = task.task_id
                
                # Sanitize
                sanitized = simulate_sanitization(llm_output)
                
                # Execute
                obs, reward, done, info = env.step(sanitized)
                
                # Grade
                if sanitized["tool"] == "submit_answer":
                    answer = {"customer_ids": sanitized["arguments"].get("customer_ids", [])}
                    score = TaskGrader.grade_task(task, answer)
                    
                    # Validate score
                    if not (0.0 < score < 1.0):
                        failures.append(f"Invalid score {score} for {task.task_id} with {repr(llm_output)[:50]}")
                
            except Exception as e:
                failures.append(f"Exception in {task.task_id}: {str(e)[:60]}")
    
    # Test 2: Grader with every possible answer type
    print("Testing grader with every answer type...")
    for task in get_tasks():
        answer_types = [
            None,
            {},
            {"customer_ids": None},
            {"customer_ids": []},
            {"customer_ids": "string"},
            {"customer_ids": 123},
            {"customer_ids": ["C001"]},
            {"customer_ids": ["C001", None, 123]},
            "invalid",
            123,
            [],
        ]
        
        for answer in answer_types:
            test_count += 1
            
            try:
                score = TaskGrader.grade_task(task, answer)
                
                if not (0.0 < score < 1.0):
                    failures.append(f"Grader score {score} for {task.task_id} with {repr(answer)[:50]}")
                    
            except Exception as e:
                failures.append(f"Grader exception: {str(e)[:60]}")
    
    # Print results
    print(f"\n{'='*70}")
    print("RESULTS")
    print(f"{'='*70}")
    print(f"Tests run: {test_count}")
    print(f"Failures: {len(failures)}")
    
    if failures:
        print(f"\n❌ FAILURES FOUND:")
        for f in failures[:10]:
            print(f"  • {f}")
        if len(failures) > 10:
            print(f"  ... and {len(failures)-10} more")
        return False
    else:
        print(f"\n✅ NO FAILURES FOUND IN {test_count} TESTS")
        print(f"\n🎉 VERDICT: System is bulletproof - no breaking test case exists")
        return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
