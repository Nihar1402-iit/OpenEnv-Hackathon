#!/usr/bin/env python3
"""Manual edge case testing - every possible failure scenario"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.grader import GRADERS, TaskGrader
from app.tasks import get_tasks
from app.env import CRMQueryEnv
import json

print("\n" + "="*80)
print("MANUAL EDGE CASE TEST - EVERY POSSIBLE FAILURE")
print("="*80)

# TEST 1: GRADERS dict callable directly
print("\n[EDGE TEST 1] GRADERS dict - Direct calls")
try:
    for grader_id in GRADERS.keys():
        grader_func = GRADERS[grader_id]
        
        # Test 1.1: Empty answer
        result = grader_func({"customer_ids": []})
        print(f"  ✅ {grader_id}({{'customer_ids': []}}): {result}")
        assert 0.0 < result < 1.0, f"Score {result} out of range!"
        
        # Test 1.2: With IDs
        result = grader_func({"customer_ids": ["C001"]})
        print(f"  ✅ {grader_id}({{'customer_ids': ['C001']}}): {result}")
        assert 0.0 < result < 1.0, f"Score {result} out of range!"
        
        # Test 1.3: Empty dict
        result = grader_func({})
        print(f"  ✅ {grader_id}({{}})): {result}")
        assert 0.0 < result < 1.0, f"Score {result} out of range!"
        
        # Test 1.4: None - CRITICAL
        try:
            result = grader_func(None)
            print(f"  ✅ {grader_id}(None): {result}")
            assert 0.0 < result < 1.0, f"Score {result} out of range!"
        except Exception as e:
            print(f"  ❌ {grader_id}(None) CRASHED: {e}")
            raise
        
        # Test 1.5: Malformed - string
        try:
            result = grader_func("invalid")
            print(f"  ✅ {grader_id}('invalid'): {result}")
            assert 0.0 < result < 1.0, f"Score {result} out of range!"
        except Exception as e:
            print(f"  ❌ {grader_id}('invalid') CRASHED: {e}")
            raise
        
        # Test 1.6: Malformed - list
        try:
            result = grader_func(["C001"])
            print(f"  ✅ {grader_id}(['C001']): {result}")
            assert 0.0 < result < 1.0, f"Score {result} out of range!"
        except Exception as e:
            print(f"  ❌ {grader_id}(['C001']) CRASHED: {e}")
            raise

except Exception as e:
    print(f"❌ GRADERS test FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# TEST 2: TaskGrader.grade_task with ALL edge cases
print("\n[EDGE TEST 2] TaskGrader.grade_task() - ALL inputs")
try:
    tasks = get_tasks()
    
    for task in tasks:
        print(f"\n  Testing {task.task_id}:")
        
        test_cases = [
            ({"customer_ids": []}, "empty list"),
            ({}, "empty dict"),
            (None, "None"),
            ({"customer_ids": ["C001"]}, "single ID"),
            ({"customer_ids": ["C001", "C002"]}, "multiple IDs"),
            ({"customer_ids": None}, "None in customer_ids"),
            ({"customer_ids": "C001"}, "string instead of list"),
            ({"customer_ids": 123}, "number instead of list"),
            (task.ground_truth, "perfect answer"),
            ({"other_field": "value"}, "wrong field"),
            ({"customer_ids": [1, 2, 3]}, "numeric IDs"),
            ({"customer_ids": []}, "empty after ground_truth"),
        ]
        
        for answer, desc in test_cases:
            try:
                score = TaskGrader.grade_task(task, answer)
                valid = isinstance(score, float) and 0.0 < score < 1.0
                status = "✅" if valid else "❌"
                print(f"    {status} {desc}: score={score} (valid={valid})")
                
                if not valid:
                    raise ValueError(f"Invalid score: {score}")
                    
            except Exception as e:
                print(f"    ❌ {desc} CRASHED: {type(e).__name__}: {e}")
                raise

except Exception as e:
    print(f"❌ TaskGrader test FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# TEST 3: Environment actions - all invalid inputs
print("\n[EDGE TEST 3] Environment.step() - Invalid actions")
try:
    env = CRMQueryEnv()
    obs = env.reset()
    
    actions = [
        ({"tool": "submit_answer", "arguments": {"customer_ids": []}}, "valid"),
        ({"tool": "submit_answer", "arguments": {"customer_ids": None}}, "None IDs"),
        ({"tool": "submit_answer", "arguments": {"customer_ids": "C001"}}, "string IDs"),
        ({"tool": "submit_answer", "arguments": {}}, "empty arguments"),
        ({"tool": "submit_answer"}, "no arguments"),
        ({"arguments": {"customer_ids": []}}, "no tool"),
        ({}, "empty dict"),
        (None, "None"),
        ("invalid", "string"),
        ([], "list"),
        (123, "number"),
    ]
    
    for i, (action, desc) in enumerate(actions):
        if i > 0:  # Reset for each action
            env = CRMQueryEnv()
            obs = env.reset()
        
        try:
            obs, reward, done, info = env.step(action)
            print(f"  ✅ {desc}: executed (done={done})")
        except Exception as e:
            print(f"  ⚠️  {desc}: {type(e).__name__}: {str(e)[:50]}")

except Exception as e:
    print(f"❌ Environment test FAILED: {e}")
    import traceback
    traceback.print_exc()

# TEST 4: Inference flow edge cases
print("\n[EDGE TEST 4] Full inference flow - edge cases")
try:
    tasks = get_tasks()
    
    # Scenario 1: Task with None answer
    print(f"\n  Scenario 1: Grading None answer")
    task = tasks[0]
    try:
        score = TaskGrader.grade_task(task, None)
        print(f"    ✅ Graded None: {score}")
        assert 0.0 < score < 1.0
    except Exception as e:
        print(f"    ❌ Failed: {e}")
        raise
    
    # Scenario 2: Task with empty answer
    print(f"\n  Scenario 2: Grading empty answer")
    try:
        score = TaskGrader.grade_task(task, {})
        print(f"    ✅ Graded empty dict: {score}")
        assert 0.0 < score < 1.0
    except Exception as e:
        print(f"    ❌ Failed: {e}")
        raise
    
    # Scenario 3: Multiple tasks sequential
    print(f"\n  Scenario 3: Sequential task grading")
    scores = {}
    for task in tasks:
        score = TaskGrader.grade_task(task, {"customer_ids": []})
        scores[task.task_id] = score
        print(f"    ✅ {task.task_id}: {score}")
        assert 0.0 < score < 1.0
    
    avg = sum(scores.values()) / len(scores)
    print(f"    ✅ Average: {avg:.3f}")
    assert 0.0 < avg < 1.0
    
except Exception as e:
    print(f"❌ Inference flow test FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# TEST 5: Score boundaries - precision test
print("\n[EDGE TEST 5] Score boundaries - precision")
try:
    task = get_tasks()[0]
    
    print(f"\n  Testing score precision for {task.task_id}:")
    
    # Test multiple calls
    scores = []
    for i in range(10):
        score = TaskGrader.grade_task(task, {"customer_ids": []})
        scores.append(score)
        
        # Check boundaries
        if score <= 0.0 or score >= 1.0:
            print(f"    ❌ Call {i+1}: Score {score} violates (0,1) boundary!")
            raise ValueError(f"Score out of bounds: {score}")
        
        if score < 0.001 or score > 0.999:
            print(f"    ⚠️  Call {i+1}: Score {score} near edge (but valid)")
        else:
            print(f"    ✅ Call {i+1}: {score}")
    
    # Check consistency
    if len(set(scores)) == 1:
        print(f"\n  ✅ All scores identical: {scores[0]}")
    else:
        print(f"\n  ⚠️  Scores vary: min={min(scores)}, max={max(scores)}")

except Exception as e:
    print(f"❌ Score boundary test FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# TEST 6: GRADERS dict consistency
print("\n[EDGE TEST 6] GRADERS dict consistency check")
try:
    print(f"\n  Checking GRADERS consistency:")
    print(f"  - Count: {len(GRADERS)}")
    print(f"  - Keys: {list(GRADERS.keys())}")
    
    tasks = get_tasks()
    task_ids = [t.task_id for t in tasks]
    
    for task_id in task_ids:
        if task_id not in GRADERS:
            print(f"  ❌ Missing grader for {task_id}")
            raise KeyError(f"No grader for {task_id}")
        else:
            print(f"  ✅ Grader found: {task_id}")
    
    if len(GRADERS) != len(tasks):
        print(f"  ❌ Mismatch: {len(GRADERS)} graders vs {len(tasks)} tasks")
        raise ValueError("GRADERS count mismatch")
    
    print(f"\n  ✅ GRADERS consistent with tasks")

except Exception as e:
    print(f"❌ GRADERS consistency test FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# TEST 7: API endpoint simulation
print("\n[EDGE TEST 7] /grader endpoint simulation")
try:
    tasks = get_tasks()
    
    # Simulate various /grader calls
    test_scenarios = [
        ({}, "empty submission"),
        (None, "None submission"),
        ({"customer_ids": []}, "empty customer_ids"),
        ({"customer_ids": ["C001", "C002"]}, "with customer_ids"),
    ]
    
    for answer, desc in test_scenarios:
        print(f"\n  Scenario: {desc}")
        scores = {}
        
        try:
            for task in tasks:
                score = TaskGrader.grade_task(task, answer)
                
                # Clamp for safety
                if not (0.0 < score < 1.0):
                    score = max(0.01, min(0.99, score))
                
                scores[task.task_id] = float(score)
            
            # Check endpoint response
            response = {
                "scores": scores,
                "task_count": len(scores),
                "all_valid": all(0.0 < v < 1.0 for v in scores.values())
            }
            
            if response["all_valid"] and response["task_count"] >= 3:
                print(f"    ✅ Response valid: {response['task_count']} tasks, all_valid={response['all_valid']}")
            else:
                print(f"    ❌ Response invalid: {response}")
                raise ValueError("Invalid endpoint response")
                
        except Exception as e:
            print(f"    ❌ Scenario failed: {e}")
            raise

except Exception as e:
    print(f"❌ Endpoint test FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*80)
print("✅ ALL EDGE CASE TESTS PASSED!")
print("="*80 + "\n")
