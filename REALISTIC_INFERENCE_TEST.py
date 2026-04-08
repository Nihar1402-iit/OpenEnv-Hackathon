#!/usr/bin/env python3
"""Test realistic inference flows that match actual validator scenarios"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.grader import GRADERS, TaskGrader
from app.tasks import get_tasks
from app.env import CRMQueryEnv

print("="*80)
print("REALISTIC INFERENCE FLOW TESTS")
print("="*80)

# Test 1: Cold start (validator scenario)
print("\n[TEST 1] Cold Start - No submission yet")
print("-"*80)
tasks = get_tasks()
scores = {}
for task in tasks:
    score = TaskGrader.grade_task(task, {})
    scores[task.task_id] = score
    print(f"  {task.task_id}: {score} (valid: {0.0 < score < 1.0})")

if len(scores) >= 3 and all(0.0 < s < 1.0 for s in scores.values()):
    print("✅ PASS: Cold start works")
else:
    print("❌ FAIL: Cold start issue")

# Test 2: Full task execution
print("\n[TEST 2] Full Task Execution (Sanitized Actions)")
print("-"*80)
results = {}
for task in tasks:
    try:
        env = CRMQueryEnv()
        obs = env.reset()
        env.current_task_id = task.task_id
        
        # Sanitize action (like inference.py does)
        action = {
            "tool": "submit_answer",
            "arguments": {"customer_ids": []}
        }
        
        # Ensure valid format
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
        
        # Execute
        obs, reward, done, info = env.step(action)
        
        # Grade
        final_answer = {"customer_ids": []}
        score = TaskGrader.grade_task(task, final_answer)
        
        is_valid = 0.0 < score < 1.0
        results[task.task_id] = {
            "score": score,
            "valid": is_valid,
            "done": done
        }
        
        status = "✅" if is_valid else "❌"
        print(f"  {status} {task.task_id}: score={score}, done={done}")
    except Exception as e:
        print(f"  ❌ {task.task_id}: {type(e).__name__}: {str(e)[:50]}")
        results[task.task_id] = {"error": str(e)}

all_valid = all("valid" in r and r["valid"] for r in results.values())
if all_valid and len(results) >= 3:
    print("✅ PASS: Full execution works")
else:
    print("❌ FAIL: Execution issue")

# Test 3: Multi-step flow
print("\n[TEST 3] Multi-Step Flow (Search + Submit)")
print("-"*80)
multi_results = {}
for task in tasks:
    try:
        env = CRMQueryEnv()
        obs = env.reset()
        env.current_task_id = task.task_id
        
        # Step 1: Search
        action1 = {
            "tool": "search_customers",
            "arguments": {"customer_id": 1}
        }
        obs, reward, done, info = env.step(action1)
        
        if not done:
            # Step 2: Submit
            action2 = {
                "tool": "submit_answer",
                "arguments": {"customer_ids": []}
            }
            obs, reward, done, info = env.step(action2)
        
        # Grade
        score = TaskGrader.grade_task(task, {"customer_ids": []})
        is_valid = 0.0 < score < 1.0
        
        multi_results[task.task_id] = {
            "score": score,
            "valid": is_valid,
            "done": done
        }
        
        status = "✅" if is_valid else "❌"
        print(f"  {status} {task.task_id}: score={score}")
    except Exception as e:
        print(f"  ❌ {task.task_id}: {type(e).__name__}")
        multi_results[task.task_id] = {"error": str(e)}

all_valid_multi = all("valid" in r and r["valid"] for r in multi_results.values())
if all_valid_multi and len(multi_results) >= 3:
    print("✅ PASS: Multi-step flow works")
else:
    print("❌ FAIL: Multi-step issue")

# Test 4: Grader registry access (validator access)
print("\n[TEST 4] Grader Registry Access (Validator Scenario)")
print("-"*80)
registry_results = []
try:
    from app.grader import GRADERS
    print(f"  ✅ GRADERS imported successfully")
    print(f"  ✅ Graders count: {len(GRADERS)}")
    
    for grader_name in GRADERS.keys():
        grader_func = GRADERS[grader_name]
        score = grader_func({"customer_ids": []})
        is_valid = isinstance(score, (int, float)) and 0.0 < score < 1.0
        registry_results.append((grader_name, is_valid))
        status = "✅" if is_valid else "❌"
        print(f"  {status} {grader_name}: {score}")
    
    if all(valid for _, valid in registry_results):
        print("✅ PASS: Grader registry works")
    else:
        print("❌ FAIL: Some graders invalid")
except Exception as e:
    print(f"  ❌ Failed to import GRADERS: {e}")

# Test 5: Score clamping verification
print("\n[TEST 5] Score Clamping - Edge Cases")
print("-"*80)
clamp_results = {"pass": 0, "fail": 0}

test_cases = [
    ({}, "empty submission"),
    ({"customer_ids": []}, "empty IDs"),
    ({"customer_ids": ["C005"]}, "correct answer"),
    ({"customer_ids": ["X1", "X2"]}, "wrong answer"),
    (None, "None"),
]

for task in tasks[:1]:  # Just test first task
    for answer, desc in test_cases:
        try:
            score = TaskGrader.grade_task(task, answer)
            
            # Check clamping
            is_valid = 0.0 < score < 1.0
            is_not_0_or_1 = score != 0.0 and score != 1.0
            
            if is_valid and is_not_0_or_1:
                clamp_results["pass"] += 1
                print(f"  ✅ {desc}: {score}")
            else:
                clamp_results["fail"] += 1
                print(f"  ❌ {desc}: {score} (invalid)")
        except Exception as e:
            clamp_results["fail"] += 1
            print(f"  ⚠️  {desc}: {type(e).__name__}")

if clamp_results["fail"] == 0:
    print("✅ PASS: All scores properly clamped")
else:
    print(f"❌ FAIL: {clamp_results['fail']} clamping issues")

# Final summary
print("\n" + "="*80)
print("REALISTIC TESTS SUMMARY")
print("="*80)
tests_passed = sum([
    all_valid and len(results) >= 3,
    all_valid_multi and len(multi_results) >= 3,
    len(registry_results) > 0 and all(v for _, v in registry_results),
    clamp_results["fail"] == 0
])

if tests_passed == 4:
    print("✅ ALL REALISTIC TESTS PASSED - READY FOR SUBMISSION")
else:
    print(f"⚠️  {4-tests_passed} tests failed")

print("="*80)
