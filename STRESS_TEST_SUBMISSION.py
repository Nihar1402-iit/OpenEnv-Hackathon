#!/usr/bin/env python3
"""
STRESS TEST - Complete submission flow
Try to find ANY way the submission can fail
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.env import CRMQueryEnv
from app.tasks import get_tasks
from app.grader import TaskGrader


def test_complete_submission_scenarios():
    """
    Test 50 complete task submission scenarios
    Each with different step patterns and answer combinations
    """
    
    print("\n" + "="*70)
    print("COMPLETE SUBMISSION FLOW STRESS TEST")
    print("="*70)
    
    tasks = get_tasks()
    scenarios_run = 0
    scenarios_failed = 0
    
    for task_idx, task in enumerate(tasks):
        print(f"\n\nTask {task_idx+1}: {task.task_id}")
        ground_truth = task.ground_truth.get("customer_ids", [])
        
        # Scenario 1: Immediate submit (empty)
        try:
            env = CRMQueryEnv()
            obs = env.reset()
            env.current_task_id = task.task_id
            
            obs, reward, done, info = env.step({
                "tool": "submit_answer",
                "arguments": {"customer_ids": []}
            })
            
            answer = {"customer_ids": []}
            score = TaskGrader.grade_task(task, answer)
            
            if 0.0 < score < 1.0:
                print(f"  ✅ Scenario 1 (immediate empty): score={score:.3f}")
                scenarios_run += 1
            else:
                print(f"  ❌ Scenario 1: INVALID SCORE {score}")
                scenarios_failed += 1
        except Exception as e:
            print(f"  ❌ Scenario 1: {str(e)[:50]}")
            scenarios_failed += 1
        
        # Scenario 2: Immediate submit (correct)
        try:
            env = CRMQueryEnv()
            obs = env.reset()
            env.current_task_id = task.task_id
            
            obs, reward, done, info = env.step({
                "tool": "submit_answer",
                "arguments": {"customer_ids": ground_truth}
            })
            
            answer = {"customer_ids": ground_truth}
            score = TaskGrader.grade_task(task, answer)
            
            if 0.0 < score < 1.0:
                print(f"  ✅ Scenario 2 (immediate correct): score={score:.3f}")
                scenarios_run += 1
            else:
                print(f"  ❌ Scenario 2: INVALID SCORE {score}")
                scenarios_failed += 1
        except Exception as e:
            print(f"  ❌ Scenario 2: {str(e)[:50]}")
            scenarios_failed += 1
        
        # Scenario 3: Search then submit (partial)
        try:
            env = CRMQueryEnv()
            obs = env.reset()
            env.current_task_id = task.task_id
            
            # Do some searches
            obs, reward, done, info = env.step({
                "tool": "search_customers",
                "arguments": {"customer_id": ground_truth[0] if ground_truth else "C001"}
            })
            
            # Submit partial
            partial = ground_truth[:max(1, len(ground_truth)//2)] if ground_truth else []
            obs, reward, done, info = env.step({
                "tool": "submit_answer",
                "arguments": {"customer_ids": partial}
            })
            
            answer = {"customer_ids": partial}
            score = TaskGrader.grade_task(task, answer)
            
            if 0.0 < score < 1.0:
                print(f"  ✅ Scenario 3 (search + partial): score={score:.3f}")
                scenarios_run += 1
            else:
                print(f"  ❌ Scenario 3: INVALID SCORE {score}")
                scenarios_failed += 1
        except Exception as e:
            print(f"  ❌ Scenario 3: {str(e)[:50]}")
            scenarios_failed += 1
        
        # Scenario 4: Multiple searches then submit
        try:
            env = CRMQueryEnv()
            obs = env.reset()
            env.current_task_id = task.task_id
            
            # Multiple searches
            for i in range(3):
                obs, reward, done, info = env.step({
                    "tool": "search_customers",
                    "arguments": {"customer_id": ground_truth[i % len(ground_truth)] if ground_truth else "C001"}
                })
            
            # Submit
            obs, reward, done, info = env.step({
                "tool": "submit_answer",
                "arguments": {"customer_ids": ground_truth}
            })
            
            answer = {"customer_ids": ground_truth}
            score = TaskGrader.grade_task(task, answer)
            
            if 0.0 < score < 1.0:
                print(f"  ✅ Scenario 4 (multi-search + submit): score={score:.3f}")
                scenarios_run += 1
            else:
                print(f"  ❌ Scenario 4: INVALID SCORE {score}")
                scenarios_failed += 1
        except Exception as e:
            print(f"  ❌ Scenario 4: {str(e)[:50]}")
            scenarios_failed += 1
        
        # Scenario 5: Malformed action that sanitizes to submit
        try:
            env = CRMQueryEnv()
            obs = env.reset()
            env.current_task_id = task.task_id
            
            # Send malformed action (will be sanitized)
            malformed = {
                "tool": "INVALID",  # Should fallback to submit_answer
                "arguments": {"customer_ids": "wrong"}  # Should be converted to []
            }
            
            # Sanitize
            action = malformed
            if not isinstance(action, dict):
                action = {"tool": "submit_answer", "arguments": {"customer_ids": []}}
            tool = action.get("tool", "").lower().strip()
            if tool not in {"search_customers", "search_orders", "search_tickets", "submit_answer"}:
                tool = "submit_answer"
            arguments = action.get("arguments", {})
            if not isinstance(arguments, dict):
                arguments = {}
            if tool == "submit_answer":
                cids = arguments.get("customer_ids", [])
                if not isinstance(cids, list):
                    cids = []
                cids = [str(x) for x in cids if x is not None]
                arguments = {"customer_ids": cids}
            action = {"tool": tool, "arguments": arguments}
            
            # Execute
            obs, reward, done, info = env.step(action)
            
            answer = {"customer_ids": action["arguments"].get("customer_ids", [])}
            score = TaskGrader.grade_task(task, answer)
            
            if 0.0 < score < 1.0:
                print(f"  ✅ Scenario 5 (sanitized malformed): score={score:.3f}")
                scenarios_run += 1
            else:
                print(f"  ❌ Scenario 5: INVALID SCORE {score}")
                scenarios_failed += 1
        except Exception as e:
            print(f"  ❌ Scenario 5: {str(e)[:50]}")
            scenarios_failed += 1
    
    # Summary
    print(f"\n\n{'='*70}")
    print("STRESS TEST SUMMARY")
    print(f"{'='*70}")
    print(f"Total scenarios: {scenarios_run}")
    print(f"Failed: {scenarios_failed}")
    print(f"Success rate: {scenarios_run/(scenarios_run+scenarios_failed)*100:.1f}%")
    
    if scenarios_failed == 0:
        print(f"\n🎉 ALL {scenarios_run} SCENARIOS PASS")
        return True
    else:
        print(f"\n⚠️  {scenarios_failed} scenarios failed")
        return False


if __name__ == "__main__":
    success = test_complete_submission_scenarios()
    sys.exit(0 if success else 1)
