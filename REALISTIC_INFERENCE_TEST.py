#!/usr/bin/env python3
"""Realistic inference.py test - how it actually works"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.env import CRMQueryEnv
from app.tasks import get_tasks
from app.grader import TaskGrader

print("\n" + "="*80)
print("REALISTIC INFERENCE TEST - Simulate actual inference.py flow")
print("="*80)

# TEST 1: Normal flow - LLM calls submit_answer during steps
print("\n[TEST 1] Normal flow: LLM submits during steps")
try:
    task = get_tasks()[0]
    env = CRMQueryEnv()
    obs = env.reset()
    env.current_task_id = task.task_id
    
    max_steps = task.max_steps
    step = 0
    done = False
    final_answer = None
    
    print(f"  Task: {task.task_id}, max_steps: {max_steps}")
    
    # Simulate loop
    while step < max_steps and not done:
        step += 1
        
        # LLM decides to submit early
        if step == 2:
            action = {"tool": "submit_answer", "arguments": {"customer_ids": []}}
            obs, reward, done, info = env.step(action)
            final_answer = {"customer_ids": []}
            print(f"  Step {step}: LLM submitted, done={done}")
            break
    
    if not final_answer:
        final_answer = {"customer_ids": []}
    
    score = TaskGrader.grade_task(task, final_answer)
    print(f"  ✅ Score: {score}")
    assert 0.0 < score < 1.0

except Exception as e:
    print(f"  ❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# TEST 2: Edge case - LLM never submits, reaches max steps
print("\n[TEST 2] Edge case: LLM doesn't submit, reaches max steps")
try:
    task = get_tasks()[1]
    env = CRMQueryEnv()
    obs = env.reset()
    env.current_task_id = task.task_id
    
    max_steps = task.max_steps
    step = 0
    done = False
    final_answer = None
    
    print(f"  Task: {task.task_id}, max_steps: {max_steps}")
    
    # Simulate loop - LLM never submits
    while step < max_steps and not done:
        step += 1
        
        # Only search actions, never submit
        action = {"tool": "search_customers", "arguments": {"customer_id": 1}}
        try:
            obs, reward, done, info = env.step(action)
        except:
            # Might fail for various reasons
            pass
    
    print(f"  Loop ended: step={step}, done={done}")
    
    # 🔥 FIX 2: Check if max steps reached and not done
    if step == max_steps and not done:
        print(f"  Forcing submission at max steps...")
        fallback_action = {"tool": "submit_answer", "arguments": {"customer_ids": []}}
        obs, reward, done, info = env.step(fallback_action)
        final_answer = {"customer_ids": []}
        print(f"  ✅ Forced submission executed")
    
    # 🔥 FIX 3: Check if still no answer after loop
    if not final_answer and not done:
        print(f"  ⚠️  Still no answer, forcing again...")
        fallback_action = {"tool": "submit_answer", "arguments": {"customer_ids": []}}
        obs, reward, done, info = env.step(fallback_action)
        final_answer = {"customer_ids": []}
    
    # 🔥 FIX 4: Guarantee answer
    if not final_answer:
        final_answer = {"customer_ids": []}
        print(f"  Used guaranteed default")
    
    score = TaskGrader.grade_task(task, final_answer)
    print(f"  ✅ Score: {score}")
    assert 0.0 < score < 1.0

except Exception as e:
    print(f"  ❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# TEST 3: Sanitization - malformed LLM actions
print("\n[TEST 3] Action sanitization on malformed LLM output")
try:
    task = get_tasks()[2]
    env = CRMQueryEnv()
    obs = env.reset()
    env.current_task_id = task.task_id
    
    step = 0
    done = False
    final_answer = None
    
    print(f"  Task: {task.task_id}")
    
    # Simulate LLM outputting malformed action
    while step < 3 and not done:
        step += 1
        
        # Malformed action from LLM
        if step == 1:
            action = {"tool": "submit_answer", "arguments": {"customer_ids": None}}
        else:
            action = {"tool": "submit_answer", "arguments": {"customer_ids": []}}
        
        # 🔥 FIX 1: Sanitize before env.step()
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
        
        print(f"  Step {step}: Sanitized action executed")
        obs, reward, done, info = env.step(action)
        
        if action.get("tool") == "submit_answer":
            final_answer = {"customer_ids": action["arguments"]["customer_ids"]}
            break
    
    if not final_answer:
        final_answer = {"customer_ids": []}
    
    score = TaskGrader.grade_task(task, final_answer)
    print(f"  ✅ Score: {score}")
    assert 0.0 < score < 1.0

except Exception as e:
    print(f"  ❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# TEST 4: Error handling - continue on exception
print("\n[TEST 4] Error handling - continue on exception")
try:
    task = get_tasks()[3]
    env = CRMQueryEnv()
    obs = env.reset()
    env.current_task_id = task.task_id
    
    step = 0
    done = False
    final_answer = None
    errors_caught = 0
    
    print(f"  Task: {task.task_id}")
    
    while step < 5 and not done:
        step += 1
        
        try:
            # Simulate error on odd steps
            if step % 2 == 1:
                raise ValueError("Simulated LLM error")
            
            action = {"tool": "submit_answer", "arguments": {"customer_ids": []}}
            obs, reward, done, info = env.step(action)
            final_answer = {"customer_ids": []}
            
            if done:
                print(f"  Step {step}: Submitted successfully")
                break
        
        except Exception as e:
            errors_caught += 1
            # 🔥 FIX: continue, NOT break
            print(f"  Step {step}: Error caught, continue")
            continue
    
    if not final_answer:
        final_answer = {"customer_ids": []}
    
    score = TaskGrader.grade_task(task, final_answer)
    print(f"  ✅ Score: {score}, errors_caught: {errors_caught}")
    assert 0.0 < score < 1.0
    assert errors_caught > 0

except Exception as e:
    print(f"  ❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# TEST 5: Full realistic flow - all tasks
print("\n[TEST 5] Full realistic flow - all tasks")
try:
    tasks = get_tasks()
    results = {}
    
    for i, task in enumerate(tasks, 1):
        task_id = task.task_id
        env = CRMQueryEnv()
        obs = env.reset()
        env.current_task_id = task_id
        
        step = 0
        max_steps = task.max_steps
        done = False
        final_answer = None
        
        # Simulate loop with immediate submission
        while step < max_steps and not done:
            step += 1
            
            # LLM decides to submit immediately (simplified)
            action = {"tool": "submit_answer", "arguments": {"customer_ids": []}}
            
            # Sanitize
            if action["tool"] == "submit_answer":
                ids = action["arguments"].get("customer_ids", [])
                if not isinstance(ids, list):
                    ids = []
                action["arguments"]["customer_ids"] = [str(x) for x in ids]
            
            obs, reward, done, info = env.step(action)
            final_answer = {"customer_ids": action["arguments"]["customer_ids"]}
            break
        
        # Apply FIX 4 guarantee
        if not final_answer:
            final_answer = {"customer_ids": []}
        
        # Grade
        score = TaskGrader.grade_task(task, final_answer)
        valid = 0.0 < score < 1.0
        status = "✅" if valid else "❌"
        print(f"  [{i}] {status} {task_id}: score={score}")
        
        if not valid:
            raise ValueError(f"Invalid score: {score}")
        
        results[task_id] = score
    
    avg = sum(results.values()) / len(results)
    print(f"\n  ✅ All {len(results)} tasks completed, avg={avg:.3f}")
    assert len(results) >= 3
    assert all(0.0 < s < 1.0 for s in results.values())

except Exception as e:
    print(f"  ❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*80)
print("✅ ALL REALISTIC INFERENCE TESTS PASSED!")
print("="*80 + "\n")
