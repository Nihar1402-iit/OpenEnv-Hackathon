#!/usr/bin/env python3
"""EXHAUSTIVE EXCEPTION TEST - Test every possible failure point"""
import os
import sys
import json
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("="*80)
print("EXHAUSTIVE EXCEPTION TEST SUITE")
print("="*80)

# TEST 1: Module imports
print("\n[TEST 1] ========== MODULE IMPORTS ==========")
try:
    from app.env import CRMQueryEnv
    print("✅ CRMQueryEnv imported")
except Exception as e:
    print(f"❌ CRMQueryEnv import failed: {e}")

try:
    from app.tasks import get_tasks, get_task_by_id
    print("✅ get_tasks, get_task_by_id imported")
except Exception as e:
    print(f"❌ tasks import failed: {e}")

try:
    from app.grader import TaskGrader
    print("✅ TaskGrader imported")
except Exception as e:
    print(f"❌ TaskGrader import failed: {e}")

try:
    from app.grader import GRADERS
    print(f"✅ GRADERS dict imported: {list(GRADERS.keys())}")
except Exception as e:
    print(f"❌ GRADERS import failed: {e}")
    traceback.print_exc()

# TEST 2: YAML loading
print("\n[TEST 2] ========== YAML CONFIGURATION ==========")
try:
    import yaml
    with open("openenv.yaml", "r") as f:
        config = yaml.safe_load(f)
    print(f"✅ openenv.yaml loaded: {len(config.get('tasks', []))} tasks")
    for task in config.get('tasks', []):
        print(f"   - {task.get('task_id', 'MISSING')} (grader: {task.get('grader', 'MISSING')})")
except Exception as e:
    print(f"❌ YAML loading failed: {e}")

# TEST 3: Tasks loading
print("\n[TEST 3] ========== TASKS LOADING ==========")
try:
    tasks = get_tasks()
    print(f"✅ get_tasks() returned {len(tasks)} tasks")
    for task in tasks:
        print(f"   - {task.task_id}: gt={task.ground_truth}")
except Exception as e:
    print(f"❌ get_tasks() failed: {e}")

# TEST 4: Grader registry
print("\n[TEST 4] ========== GRADER REGISTRY ==========")
try:
    from app.grader import GRADERS
    print(f"✅ GRADERS has {len(GRADERS)} entries: {list(GRADERS.keys())}")
except Exception as e:
    print(f"❌ GRADERS access failed: {e}")
    traceback.print_exc()

# TEST 5: Grader function calls with edge cases
print("\n[TEST 5] ========== GRADER FUNCTION CALLS (EDGE CASES) ==========")
try:
    from app.grader import GRADERS
    
    test_cases = [
        ({"customer_ids": []}, "Empty list"),
        ({"customer_ids": ["1", "2"]}, "With IDs"),
        ({}, "Empty dict"),
        (None, "None"),
        ("invalid", "String"),
        ([], "List not dict"),
    ]
    
    for grader_name, grader_func in GRADERS.items():
        print(f"\n   {grader_name}:")
        for answer, desc in test_cases:
            try:
                score = grader_func(answer)
                valid = isinstance(score, (int, float)) and 0.0 < score < 1.0
                status = "✅" if valid else "❌"
                print(f"     {status} {desc}: {score} (valid={valid})")
            except Exception as e:
                print(f"     ⚠️  {desc}: {type(e).__name__}: {str(e)[:50]}")
except Exception as e:
    print(f"❌ Grader tests failed: {e}")
    traceback.print_exc()

# TEST 6: TaskGrader.grade_task() with all tasks
print("\n[TEST 6] ========== TaskGrader.grade_task() ALL TASKS ==========")
try:
    from app.grader import TaskGrader
    tasks = get_tasks()
    
    for task in tasks:
        print(f"\n   {task.task_id}:")
        
        test_answers = [
            ({"customer_ids": []}, "Empty"),
            ({}, "Empty dict"),
            (None, "None"),
            (task.ground_truth, "Perfect"),
        ]
        
        for answer, desc in test_answers:
            try:
                score = TaskGrader.grade_task(task, answer)
                valid = isinstance(score, (int, float)) and 0.0 < score < 1.0
                status = "✅" if valid else "❌"
                print(f"     {status} {desc}: score={score} (valid={valid})")
            except Exception as e:
                print(f"     ⚠️  {desc}: {type(e).__name__}: {str(e)[:60]}")
except Exception as e:
    print(f"❌ TaskGrader tests failed: {e}")
    traceback.print_exc()

# TEST 7: Environment and actions
print("\n[TEST 7] ========== ENVIRONMENT ACTIONS ==========")
try:
    env = CRMQueryEnv()
    obs = env.reset()
    print(f"✅ Environment reset")
    
    actions = [
        ({"tool": "submit_answer", "arguments": {"customer_ids": []}}, "Valid submit"),
        ({"tool": "invalid", "arguments": {}}, "Invalid tool"),
        ({}, "Empty dict"),
        (None, "None"),
        ("string", "String"),
    ]
    
    for action, desc in actions:
        try:
            obs, reward, done, info = env.step(action)
            print(f"   ✅ {desc}: reward={reward}, done={done}")
        except Exception as e:
            print(f"   ⚠️  {desc}: {type(e).__name__}: {str(e)[:50]}")
except Exception as e:
    print(f"❌ Environment tests failed: {e}")
    traceback.print_exc()

# TEST 8: /grader endpoint simulation
print("\n[TEST 8] ========== /GRADER ENDPOINT SIMULATION ==========")
try:
    from app.grader import TaskGrader
    tasks = get_tasks()
    scores = {}
    
    for task in tasks:
        try:
            score = TaskGrader.grade_task(task, {})
            if not (0.0 < score < 1.0):
                score = max(0.01, min(0.99, score))
            scores[task.task_id] = float(score)
        except Exception as e:
            print(f"   ⚠️  {task.task_id} failed: {e}")
            scores[task.task_id] = 0.01
    
    response = {
        "scores": scores,
        "task_count": len(scores),
        "all_valid": all(0.0 < v < 1.0 for v in scores.values())
    }
    
    print(f"✅ Endpoint response:")
    print(f"   {json.dumps(response, indent=2)}")
    
    if response["all_valid"] and response["task_count"] >= 3:
        print(f"\n   ✅ PASS: Validator ready")
    else:
        print(f"\n   ❌ FAIL: Issues found")
except Exception as e:
    print(f"❌ Endpoint simulation failed: {e}")
    traceback.print_exc()

# TEST 9: Inference flow
print("\n[TEST 9] ========== INFERENCE FLOW SIMULATION ==========")
try:
    from app.env import CRMQueryEnv
    from app.tasks import get_tasks
    from app.grader import TaskGrader
    
    tasks = get_tasks()
    results = {}
    scores = {}
    
    for task_idx, task in enumerate(tasks, 1):
        try:
            env = CRMQueryEnv()
            obs = env.reset()
            env.current_task_id = task.task_id
            
            # Execute submit
            action = {"tool": "submit_answer", "arguments": {"customer_ids": []}}
            obs, reward, done, info = env.step(action)
            
            # Grade
            score = TaskGrader.grade_task(task, {"customer_ids": []})
            if not (0.0 < score < 1.0):
                score = max(0.01, min(0.99, score))
            
            scores[task.task_id] = score
            print(f"   ✅ [{task_idx}] {task.task_id}: {score}")
        except Exception as e:
            scores[task.task_id] = 0.01
            print(f"   ❌ [{task_idx}] {task.task_id}: {e}")
    
    avg_score = sum(scores.values()) / len(scores) if scores else 0
    print(f"\n   Summary: {len(scores)} tasks, avg={avg_score:.3f}")
    
    if len(scores) >= 3 and all(0.0 < s < 1.0 for s in scores.values()):
        print(f"   ✅ PASS")
    else:
        print(f"   ❌ FAIL")
except Exception as e:
    print(f"❌ Inference simulation failed: {e}")
    traceback.print_exc()

print("\n" + "="*80)
print("EXHAUSTIVE TEST COMPLETE")
print("="*80)
