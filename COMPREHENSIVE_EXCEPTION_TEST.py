#!/usr/bin/env python3
"""
COMPREHENSIVE EXCEPTION TEST FOR INFERENCE.PY
Tests every possible exception that could cause validator failure.
"""

import sys
import json
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.tasks import get_tasks
from app.grader import TaskGrader
from app.env import CRMQueryEnv

print("\n" + "="*80)
print("COMPREHENSIVE EXCEPTION DIAGNOSTIC FOR 'Not enough tasks with graders'")
print("="*80)

# ============================================================================
# TEST 1: Load tasks and verify structure
# ============================================================================
print("\n[TEST 1] Task Loading and Structure")
print("-" * 80)

try:
    tasks = get_tasks()
    print(f"✅ Tasks loaded: {len(tasks)} tasks")
    
    for i, task in enumerate(tasks):
        print(f"\n  Task {i+1}: {task.task_id}")
        print(f"    - task_id: {getattr(task, 'task_id', '❌ MISSING')}")
        print(f"    - difficulty: {getattr(task, 'difficulty', '❌ MISSING')}")
        print(f"    - description: {getattr(task, 'description', '❌ MISSING')[:50]}...")
        print(f"    - ground_truth: {getattr(task, 'ground_truth', '❌ MISSING')}")
        print(f"    - max_steps: {getattr(task, 'max_steps', '❌ MISSING')}")
        
except Exception as e:
    print(f"❌ FAILED TO LOAD TASKS: {type(e).__name__}: {e}")
    sys.exit(1)

# ============================================================================
# TEST 2: Verify grader registry
# ============================================================================
print("\n\n[TEST 2] Grader Registry")
print("-" * 80)

try:
    # This is what the validator checks
    from app.grader import GRADERS
    print(f"✅ GRADERS dict found: {len(GRADERS)} graders")
    print(f"   Grader keys: {list(GRADERS.keys())}")
    
    for task_id, grader_func in GRADERS.items():
        print(f"\n  {task_id}:")
        print(f"    - callable: {callable(grader_func)}")
        print(f"    - type: {type(grader_func)}")
        
except Exception as e:
    print(f"❌ FAILED TO ACCESS GRADERS: {type(e).__name__}: {e}")

# ============================================================================
# TEST 3: Cold start grading (empty submission)
# ============================================================================
print("\n\n[TEST 3] Cold Start Grading (Empty Submission)")
print("-" * 80)

try:
    cold_start_answer = {"customer_ids": []}
    scores = {}
    
    for task in tasks:
        try:
            score = TaskGrader.grade_task(task, cold_start_answer)
            scores[task.task_id] = score
            
            # Check score validity
            if score <= 0.0:
                print(f"  ❌ {task.task_id}: score={score} (≤ 0.0 - INVALID)")
            elif score >= 1.0:
                print(f"  ❌ {task.task_id}: score={score} (≥ 1.0 - INVALID)")
            elif not (0.0 < score < 1.0):
                print(f"  ❌ {task.task_id}: score={score} (not in (0,1) - INVALID)")
            else:
                print(f"  ✅ {task.task_id}: score={score:.4f} (valid)")
                
        except Exception as e:
            print(f"  ❌ {task.task_id}: {type(e).__name__}: {e}")
            
    print(f"\n  Valid scores: {sum(1 for s in scores.values() if 0.0 < s < 1.0)}/{len(tasks)}")
    
except Exception as e:
    print(f"❌ COLD START GRADING FAILED: {type(e).__name__}: {e}")

# ============================================================================
# TEST 4: Perfect answer grading
# ============================================================================
print("\n\n[TEST 4] Perfect Answer Grading")
print("-" * 80)

try:
    perfect_scores = {}
    
    for task in tasks:
        try:
            # Perfect answer for task_easy_001 is customer_id=1
            perfect_answer = {"customer_ids": [str(task.ground_truth.get("customer_ids", [1])[0])]}
            score = TaskGrader.grade_task(task, perfect_answer)
            perfect_scores[task.task_id] = score
            
            if score <= 0.0:
                print(f"  ❌ {task.task_id}: score={score} (≤ 0.0 - INVALID)")
            elif score >= 1.0:
                print(f"  ❌ {task.task_id}: score={score} (≥ 1.0 - INVALID)")
            elif not (0.0 < score < 1.0):
                print(f"  ❌ {task.task_id}: score={score} (not in (0,1) - INVALID)")
            else:
                print(f"  ✅ {task.task_id}: score={score:.4f} (valid)")
                
        except Exception as e:
            print(f"  ❌ {task.task_id}: {type(e).__name__}: {e}")

    print(f"\n  Valid scores: {sum(1 for s in perfect_scores.values() if 0.0 < s < 1.0)}/{len(tasks)}")
            
except Exception as e:
    print(f"❌ PERFECT ANSWER GRADING FAILED: {type(e).__name__}: {e}")

# ============================================================================
# TEST 5: TaskGrader.compute_average_score()
# ============================================================================
print("\n\n[TEST 5] Average Score Computation")
print("-" * 80)

try:
    test_scores = {
        "task_easy_001": 0.5,
        "task_medium_001": 0.6,
        "task_hard_001": 0.7,
        "task_extreme_001": 0.4
    }
    
    avg = TaskGrader.compute_average_score(test_scores)
    print(f"  Input scores: {test_scores}")
    print(f"  Average: {avg:.4f}")
    
    if avg <= 0.0:
        print(f"  ❌ Average score is ≤ 0.0 (INVALID)")
    elif avg >= 1.0:
        print(f"  ❌ Average score is ≥ 1.0 (INVALID)")
    elif 0.0 < avg < 1.0:
        print(f"  ✅ Average score is valid")
    else:
        print(f"  ❌ Average score is NaN or invalid")
        
except Exception as e:
    print(f"❌ AVERAGE COMPUTATION FAILED: {type(e).__name__}: {e}")

# ============================================================================
# TEST 6: Environment step with submit_answer
# ============================================================================
print("\n\n[TEST 6] Environment Step with submit_answer")
print("-" * 80)

try:
    env = CRMQueryEnv()
    obs = env.reset()
    env.current_task_id = "task_easy_001"
    
    # Test submit_answer action
    action = {
        "tool": "submit_answer",
        "arguments": {"customer_ids": ["1"]}
    }
    
    try:
        obs, reward, done, info = env.step(action)
        print(f"  ✅ submit_answer executed")
        print(f"     - reward: {reward.value}")
        print(f"     - done: {done}")
        print(f"     - info: {info}")
    except Exception as e:
        print(f"  ❌ submit_answer failed: {type(e).__name__}: {e}")
        
except Exception as e:
    print(f"❌ ENVIRONMENT INITIALIZATION FAILED: {type(e).__name__}: {e}")

# ============================================================================
# TEST 7: Simulate /grader endpoint
# ============================================================================
print("\n\n[TEST 7] Simulate /grader Endpoint")
print("-" * 80)

try:
    # This is what the validator calls
    all_tasks = get_tasks()
    scores = {}
    answer = {"customer_ids": []}  # Cold start
    
    for task in all_tasks:
        try:
            score = TaskGrader.grade_task(task, answer)
            
            # Apply clamping like grader.py does
            if not (0.0 < score < 1.0):
                score = 0.01
                
            scores[task.task_id] = float(score)
            
        except Exception as e:
            print(f"  ❌ Failed to grade {task.task_id}: {e}")
            scores[task.task_id] = 0.01
    
    # Simulate response
    response = {
        "scores": scores,
        "task_count": len(scores),
        "all_valid": all(0.0 < s < 1.0 for s in scores.values())
    }
    
    print(f"  Response: {json.dumps(response, indent=2)}")
    
    if response["all_valid"]:
        print(f"  ✅ All scores valid")
    else:
        print(f"  ❌ Some scores invalid: {[v for v in scores.values() if not (0.0 < v < 1.0)]}")
        
    if len(scores) >= 3:
        print(f"  ✅ Enough tasks: {len(scores)} >= 3")
    else:
        print(f"  ❌ Not enough tasks: {len(scores)} < 3")
        
except Exception as e:
    print(f"❌ /grader ENDPOINT SIMULATION FAILED: {type(e).__name__}: {e}")

# ============================================================================
# TEST 8: Check inference.py can be imported
# ============================================================================
print("\n\n[TEST 8] Inference.py Import Check")
print("-" * 80)

try:
    import inference
    print(f"  ✅ inference.py imported successfully")
    
    # Check key functions exist
    functions = [
        "get_api_config",
        "initialize_openai_client",
        "_log_start",
        "_log_step",
        "_log_task_end",
        "_log_final_end",
        "run_inference_on_task",
        "run_inference",
        "main"
    ]
    
    for func_name in functions:
        if hasattr(inference, func_name):
            print(f"    ✅ {func_name}")
        else:
            print(f"    ❌ {func_name} - MISSING")
            
except Exception as e:
    print(f"❌ INFERENCE.PY IMPORT FAILED: {type(e).__name__}: {e}")

# ============================================================================
# TEST 9: Sanitization logic check
# ============================================================================
print("\n\n[TEST 9] Action Sanitization Logic")
print("-" * 80)

test_cases = [
    ("Valid action", {"tool": "submit_answer", "arguments": {"customer_ids": ["1"]}}),
    ("Missing tool", {"arguments": {"customer_ids": ["1"]}}),
    ("Missing arguments", {"tool": "submit_answer"}),
    ("Non-dict action", "not a dict"),
    ("Empty dict", {}),
    ("Bad customer_ids", {"tool": "submit_answer", "arguments": {"customer_ids": "not a list"}}),
    ("None action", None),
]

for test_name, action in test_cases:
    print(f"\n  Test: {test_name}")
    print(f"    Input: {action}")
    
    try:
        # Apply sanitization logic from inference.py
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
        
        print(f"    Output: {action}")
        print(f"    ✅ Sanitization succeeded")
        
    except Exception as e:
        print(f"    ❌ Sanitization failed: {type(e).__name__}: {e}")

# ============================================================================
# TEST 10: Verify all fixes are in place
# ============================================================================
print("\n\n[TEST 10] Verify All Fixes Are In Place")
print("-" * 80)

try:
    with open("/Users/niharshah/Desktop/Meta Hackathon/inference.py", "r") as f:
        content = f.read()
    
    fixes = [
        ("FIX 1: Action sanitization", "if not isinstance(action, dict):"),
        ("FIX 2: Force submission at max steps", "if step == max_steps and not done:"),
        ("FIX 3: Force submission if not already", "if not final_answer:"),
        ("FIX 3: Fallback via env.step()", "obs, reward, done, info = env.step(fallback_action)"),
        ("Continue on error", "except Exception as e:" in content and "continue" in content),
        ("Structured logging START", '[START] task=all env=CRMQueryEnv'),
        ("Structured logging STEP", '[STEP] step=' in content),
        ("Structured logging END", '[END] task_id=' in content),
        ("Score clamping", "max(0.001, min(0.999," in content),
    ]
    
    for fix_name, check in fixes:
        if isinstance(check, bool):
            if check:
                print(f"  ✅ {fix_name}")
            else:
                print(f"  ❌ {fix_name} - NOT FOUND")
        else:
            if check in content:
                print(f"  ✅ {fix_name}")
            else:
                print(f"  ❌ {fix_name} - NOT FOUND")
                
except Exception as e:
    print(f"❌ FAILED TO CHECK FIXES: {type(e).__name__}: {e}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n\n" + "="*80)
print("DIAGNOSTIC COMPLETE")
print("="*80)
print("\nIf any tests above show ❌, that's a potential cause of validator failure.")
print("\nMost likely issues:")
print("  1. Not enough valid scores returned")
print("  2. Scores outside (0, 1) range")
print("  3. Missing task_id in YAML")
print("  4. Grader not registered")
print("  5. env.step() not called for submission")
print("="*80 + "\n")
