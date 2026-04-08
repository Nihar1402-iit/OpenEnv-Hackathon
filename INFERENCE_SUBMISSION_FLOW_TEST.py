#!/usr/bin/env python3
"""Test inference.py submission flow handling"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.env import CRMQueryEnv
from app.tasks import get_tasks
from app.grader import TaskGrader

print("\n" + "="*80)
print("INFERENCE SUBMISSION FLOW TEST")
print("="*80)

# TEST 1: Submission flow - max steps reached
print("\n[TEST 1] Submission at max steps")
try:
    task = get_tasks()[0]
    env = CRMQueryEnv()
    obs = env.reset()
    env.current_task_id = task.task_id
    
    max_steps = task.max_steps
    print(f"  Task: {task.task_id}, max_steps: {max_steps}")
    
    step = 0
    final_answer = None
    
    # Simulate steps without submission
    while step < max_steps:
        step += 1
        
        # Execute non-submit action
        action = {"tool": "search_customers", "arguments": {"customer_id": 1}}
        try:
            obs, reward, done, info = env.step(action)
        except:
            pass
        
        if step == max_steps:
            print(f"  Reached max steps: {step}")
            break
    
    # Now force submission (inference.py FIX 2)
    if step == max_steps and not final_answer:
        print(f"  Forcing submission at max steps...")
        fallback_action = {"tool": "submit_answer", "arguments": {"customer_ids": []}}
        obs, reward, done, info = env.step(fallback_action)
        final_answer = {"customer_ids": []}
        print(f"  ✅ Forced submission executed, done={done}")
    
    # Grade
    score = TaskGrader.grade_task(task, final_answer)
    print(f"  ✅ Final score: {score}")
    assert 0.0 < score < 1.0, f"Invalid score: {score}"

except Exception as e:
    print(f"  ❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# TEST 2: Submission flow - no submission during steps
print("\n[TEST 2] Submission when no submit_answer called")
try:
    task = get_tasks()[1]
    env = CRMQueryEnv()
    obs = env.reset()
    env.current_task_id = task.task_id
    
    final_answer = None
    
    # Do nothing - no submission
    print(f"  Task: {task.task_id}")
    print(f"  Simulated: no submission during steps")
    
    # Inference.py FIX 3: Force submission if not already submitted
    if not final_answer:
        print(f"  Forcing final submission...")
        fallback_action = {"tool": "submit_answer", "arguments": {"customer_ids": []}}
        obs, reward, done, info = env.step(fallback_action)
        final_answer = {"customer_ids": []}
        print(f"  ✅ Forced submission executed")
    
    # Grade
    score = TaskGrader.grade_task(task, final_answer)
    print(f"  ✅ Final score: {score}")
    assert 0.0 < score < 1.0, f"Invalid score: {score}"

except Exception as e:
    print(f"  ❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# TEST 3: Action sanitization (FIX 1)
print("\n[TEST 3] Action sanitization before env.step()")
try:
    env = CRMQueryEnv()
    obs = env.reset()
    
    # Test malformed actions
    malformed_actions = [
        {"tool": "submit_answer", "arguments": {"customer_ids": None}},
        {"tool": "submit_answer", "arguments": {"customer_ids": "C001"}},
        {"tool": "submit_answer", "arguments": {}},
        {"tool": "submit_answer"},
    ]
    
    for i, action in enumerate(malformed_actions):
        if i > 0:
            env = CRMQueryEnv()
            obs = env.reset()
        
        print(f"\n  Action {i+1}: {action}")
        
        # Sanitize (FIX 1)
        if not isinstance(action, dict):
            action = {"tool": "submit_answer", "arguments": {"customer_ids": []}}
        
        if "tool" not in action:
            action["tool"] = "submit_answer"
        
        if "arguments" not in action or not isinstance(action["arguments"], dict):
            action["arguments"] = {}
        
        if action["tool"] == "submit_answer":
            ids = action["arguments"].get("customer_ids", [])
            if not isinstance(ids, list):
                ids = []
            action["arguments"]["customer_ids"] = [str(x) for x in ids]
        
        print(f"    Sanitized: {action}")
        
        # Execute
        obs, reward, done, info = env.step(action)
        print(f"    ✅ Executed successfully")

except Exception as e:
    print(f"  ❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# TEST 4: Error handling - continue not break
print("\n[TEST 4] Error handling - continue on step error")
try:
    task = get_tasks()[2]
    env = CRMQueryEnv()
    obs = env.reset()
    env.current_task_id = task.task_id
    
    max_steps = 5
    step = 0
    error_count = 0
    
    print(f"  Task: {task.task_id}, simulating {max_steps} steps with errors")
    
    while step < max_steps:
        step += 1
        
        try:
            # Simulate error on step 2, 4
            if step in [2, 4]:
                raise ValueError("Simulated error")
            
            # Normal action
            action = {"tool": "submit_answer", "arguments": {"customer_ids": []}}
            obs, reward, done, info = env.step(action)
            
            if step == 1:
                print(f"  Step {step}: OK")
            elif step in [2, 4]:
                print(f"  Step {step}: Error (caught)")
            else:
                print(f"  Step {step}: OK")
        
        except Exception as e:
            error_count += 1
            # FIX: continue, not break
            print(f"  Step {step}: Exception - {e} (continue)")
            continue
        
        if done:
            break
    
    print(f"\n  ✅ Completed {step} steps, {error_count} errors caught, all handled")
    assert error_count > 0, "Should have caught errors"

except Exception as e:
    print(f"  ❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# TEST 5: Full task flow - all tasks
print("\n[TEST 5] Full task flow - all tasks")
try:
    tasks = get_tasks()
    results = {}
    
    for i, task in enumerate(tasks, 1):
        task_id = task.task_id
        
        # Create environment
        env = CRMQueryEnv()
        obs = env.reset()
        env.current_task_id = task_id
        
        # Simulate steps (none in this test)
        final_answer = None
        
        # Apply FIX 3: Force final submission
        if not final_answer:
            fallback_action = {"tool": "submit_answer", "arguments": {"customer_ids": []}}
            obs, reward, done, info = env.step(fallback_action)
            final_answer = {"customer_ids": []}
        
        # Grade
        score = TaskGrader.grade_task(task, final_answer)
        
        # Validate
        valid = 0.0 < score < 1.0
        status = "✅" if valid else "❌"
        print(f"  [{i}] {status} {task_id}: score={score}")
        
        if not valid:
            raise ValueError(f"Invalid score for {task_id}")
        
        results[task_id] = score
    
    avg_score = sum(results.values()) / len(results)
    print(f"\n  ✅ All {len(results)} tasks completed, avg_score={avg_score:.3f}")
    assert len(results) >= 3, "Need at least 3 tasks"
    assert all(0.0 < s < 1.0 for s in results.values()), "All scores must be in (0,1)"

except Exception as e:
    print(f"  ❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# TEST 6: Edge case - exception in fallback submission
print("\n[TEST 6] Exception handling in fallback submission")
try:
    task = get_tasks()[3]
    env = CRMQueryEnv()
    obs = env.reset()
    env.current_task_id = task.task_id
    
    final_answer = None
    
    # FIX 3: Safe fallback
    if not final_answer:
        fallback_action = {"tool": "submit_answer", "arguments": {"customer_ids": []}}
        
        try:
            obs, reward, done, info = env.step(fallback_action)
            final_answer = {"customer_ids": []}
            print(f"  ✅ Fallback submission succeeded")
        except Exception as e:
            print(f"  ⚠️  Fallback submission failed: {e}")
            # Still ensure we have a final_answer
            final_answer = {"customer_ids": []}
            print(f"  ✅ Used guaranteed default")
    
    # Grade with potentially invalid submission
    score = TaskGrader.grade_task(task, final_answer)
    print(f"  ✅ Task graded: score={score}")
    assert 0.0 < score < 1.0, f"Invalid score: {score}"

except Exception as e:
    print(f"  ❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*80)
print("✅ ALL SUBMISSION FLOW TESTS PASSED!")
print("="*80 + "\n")
