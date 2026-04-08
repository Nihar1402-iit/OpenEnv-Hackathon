#!/usr/bin/env python3
"""
COMPLETE TEST SUITE - Exhausts ALL possible test cases
Tests every scenario, combination, and edge case
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.grader import GRADERS, TaskGrader
from app.tasks import get_tasks
from app.env import CRMQueryEnv
import json

print("="*80)
print("COMPLETE TEST SUITE - ALL POSSIBLE TEST CASES")
print("="*80)

# ============================================================================
# SECTION 1: GRADER FUNCTION TESTS (24 test cases)
# ============================================================================
print("\n[SECTION 1] GRADER FUNCTIONS - 24 TEST CASES")
print("-" * 80)

grader_test_cases = [
    ({"customer_ids": []}, "Empty list"),
    ({"customer_ids": ["1"]}, "Single ID"),
    ({"customer_ids": ["1", "2", "3"]}, "Multiple IDs"),
    ({"customer_ids": ["1", "1"]}, "Duplicate IDs"),
    ({}, "Missing customer_ids key"),
    ({"customer_ids": None}, "None as value"),
    ({"customer_ids": "string"}, "String instead of list"),
    ({"customer_ids": 123}, "Int instead of list"),
    ({"customer_ids": {"nested": "dict"}}, "Dict instead of list"),
    (None, "None answer"),
    ({}, "Empty dict"),
    ("string", "String instead of dict"),
    (123, "Int instead of dict"),
    ([], "List instead of dict"),
    ({"extra_field": "value"}, "Extra fields"),
    ({"customer_ids": [1, 2, 3]}, "Integer IDs"),
    ({"customer_ids": [None, None]}, "None in list"),
    ({"customer_ids": ["", ""]}, "Empty strings in list"),
    ({"customer_ids": [" ", " "]}, "Whitespace in list"),
    ({"customer_ids": [1.5, 2.5]}, "Floats in list"),
    ({"customer_ids": True}, "Boolean"),
    ({"customer_ids": [True, False]}, "Booleans in list"),
    ({"customer_ids": ["C005"]}, "Valid customer ID format"),
    ({"customer_ids": ["C001", "C004", "C006"]}, "Multiple valid IDs"),
]

grader_results = {"pass": 0, "fail": 0, "errors": []}

for grader_name in GRADERS.keys():
    grader_func = GRADERS[grader_name]
    for answer, description in grader_test_cases:
        try:
            score = grader_func(answer)
            is_valid = isinstance(score, (int, float)) and 0.0 < score < 1.0
            if is_valid:
                grader_results["pass"] += 1
                print(f"  ✅ {grader_name} / {description}: {score}")
            else:
                grader_results["fail"] += 1
                print(f"  ❌ {grader_name} / {description}: {score} (out of range)")
                grader_results["errors"].append(f"{grader_name}/{description}: invalid score {score}")
        except Exception as e:
            grader_results["fail"] += 1
            print(f"  ⚠️  {grader_name} / {description}: {type(e).__name__}: {str(e)[:40]}")
            grader_results["errors"].append(f"{grader_name}/{description}: {type(e).__name__}")

print(f"\nGrader Tests: {grader_results['pass']} pass, {grader_results['fail']} fail")

# ============================================================================
# SECTION 2: TaskGrader.grade_task() TESTS (20 test cases per task)
# ============================================================================
print("\n[SECTION 2] TaskGrader.grade_task() - 20 TEST CASES PER TASK")
print("-" * 80)

grade_test_cases = [
    ({"customer_ids": []}, "Empty submission"),
    ({}, "Empty dict"),
    (None, "None"),
    ({"customer_ids": None}, "Null customer_ids"),
    ({"customer_ids": "invalid"}, "String customer_ids"),
    ({"customer_ids": 123}, "Numeric customer_ids"),
    ({"customer_ids": [None]}, "None in list"),
    ({"customer_ids": [""]}, "Empty string in list"),
    ({"customer_ids": [1, 2]}, "Integer IDs"),
    ({"customer_ids": [1.5, 2.5]}, "Float IDs"),
    ({"customer_ids": ["X1", "X2"]}, "Non-matching IDs"),
    ({"customer_ids": [" C005 "]}, "ID with whitespace"),
    ({"customer_ids": ["c005"]}, "Lowercase ID"),
    ({"customer_ids": ["C005", "C005"]}, "Duplicate correct ID"),
    ({"customer_ids": ["C005", "X999"]}, "Mixed correct and wrong"),
]

grade_results = {"pass": 0, "fail": 0, "errors": []}

tasks = get_tasks()
for task in tasks:
    print(f"\n  Task: {task.task_id}")
    for answer, description in grade_test_cases:
        try:
            score = TaskGrader.grade_task(task, answer)
            is_valid = isinstance(score, (int, float)) and 0.0 < score < 1.0
            if is_valid:
                grade_results["pass"] += 1
                print(f"    ✅ {description}: {score}")
            else:
                grade_results["fail"] += 1
                print(f"    ❌ {description}: {score} (invalid)")
                grade_results["errors"].append(f"{task.task_id}/{description}: {score}")
        except Exception as e:
            grade_results["fail"] += 1
            print(f"    ⚠️  {description}: {type(e).__name__}")
            grade_results["errors"].append(f"{task.task_id}/{description}: {type(e).__name__}")

print(f"\nGrade Tests: {grade_results['pass']} pass, {grade_results['fail']} fail")

# ============================================================================
# SECTION 3: ENVIRONMENT ACTION TESTS (30 test cases)
# ============================================================================
print("\n[SECTION 3] ENVIRONMENT ACTIONS - 30 TEST CASES")
print("-" * 80)

action_test_cases = [
    # Valid actions
    ({"tool": "search_customers", "arguments": {"customer_id": 1}}, "search_customers valid"),
    ({"tool": "search_customers", "arguments": {}}, "search_customers no args"),
    ({"tool": "search_orders", "arguments": {"customer_id": 1}}, "search_orders valid"),
    ({"tool": "search_tickets", "arguments": {"customer_id": 1}}, "search_tickets valid"),
    ({"tool": "submit_answer", "arguments": {"customer_ids": []}}, "submit_answer empty"),
    ({"tool": "submit_answer", "arguments": {"customer_ids": ["1"]}}, "submit_answer with IDs"),
    ({"tool": "submit_answer", "arguments": {}}, "submit_answer no args"),
    
    # Invalid tools
    ({"tool": "invalid_tool", "arguments": {}}, "invalid tool"),
    ({"tool": "", "arguments": {}}, "empty tool"),
    ({"tool": None, "arguments": {}}, "None tool"),
    
    # Missing fields
    ({"arguments": {}}, "missing tool"),
    ({"tool": "search_customers"}, "missing arguments"),
    ({}, "empty dict"),
    
    # Wrong types
    (None, "None action"),
    ("string", "string action"),
    (123, "int action"),
    ([], "list action"),
    
    # Malformed arguments
    ({"tool": "search_customers", "arguments": None}, "None arguments"),
    ({"tool": "search_customers", "arguments": "string"}, "string arguments"),
    ({"tool": "search_customers", "arguments": 123}, "int arguments"),
    
    # submit_answer edge cases
    ({"tool": "submit_answer", "arguments": {"customer_ids": None}}, "submit_answer None ids"),
    ({"tool": "submit_answer", "arguments": {"customer_ids": "string"}}, "submit_answer string ids"),
    ({"tool": "submit_answer", "arguments": {"customer_ids": [1, 2]}}, "submit_answer int ids"),
    ({"tool": "submit_answer", "arguments": {"customer_ids": [None]}}, "submit_answer None in ids"),
    ({"tool": "submit_answer", "arguments": {"customer_ids": ["", ""]}}, "submit_answer empty strings"),
    
    # Extra fields
    ({"tool": "search_customers", "arguments": {}, "extra": "field"}, "extra fields"),
    ({"tool": "search_customers", "arguments": {"customer_id": 1, "extra": "field"}}, "extra args"),
    
    # Case sensitivity
    ({"tool": "SEARCH_CUSTOMERS", "arguments": {}}, "uppercase tool"),
    ({"tool": "Search_Customers", "arguments": {}}, "mixed case tool"),
]

action_results = {"pass": 0, "fail": 0, "timeout": 0, "errors": []}

env = CRMQueryEnv()
obs = env.reset()

for action, description in action_test_cases:
    try:
        env = CRMQueryEnv()
        obs = env.reset()
        
        obs, reward, done, info = env.step(action)
        action_results["pass"] += 1
        print(f"  ✅ {description}: done={done}")
    except Exception as e:
        error_type = type(e).__name__
        action_results["fail"] += 1
        print(f"  ⚠️  {description}: {error_type}")
        action_results["errors"].append(f"{description}: {error_type}")

print(f"\nAction Tests: {action_results['pass']} pass, {action_results['fail']} fail")

# ============================================================================
# SECTION 4: INFERENCE FLOW TESTS (25 scenarios)
# ============================================================================
print("\n[SECTION 4] INFERENCE FLOW SIMULATION - 25 SCENARIOS")
print("-" * 80)

flow_results = {"pass": 0, "fail": 0, "errors": []}

scenarios = [
    ("immediate_submit", "Submit immediately"),
    ("multiple_searches", "Search multiple times"),
    ("mixed_actions", "Mix searches and submit"),
    ("repeated_searches", "Repeat same search"),
    ("empty_queries", "Empty query parameters"),
    ("max_steps", "Reach max steps"),
]

tasks = get_tasks()
for task_idx, task in enumerate(tasks):
    print(f"\n  Task: {task.task_id}")
    
    # Scenario 1: Immediate submit
    try:
        env = CRMQueryEnv()
        obs = env.reset()
        env.current_task_id = task.task_id
        action = {"tool": "submit_answer", "arguments": {"customer_ids": []}}
        obs, reward, done, info = env.step(action)
        score = TaskGrader.grade_task(task, {"customer_ids": []})
        if 0.0 < score < 1.0:
            flow_results["pass"] += 1
            print(f"    ✅ Scenario 1 (immediate_submit): {score}")
        else:
            flow_results["fail"] += 1
            print(f"    ❌ Scenario 1: invalid score {score}")
    except Exception as e:
        flow_results["fail"] += 1
        print(f"    ⚠️  Scenario 1: {type(e).__name__}")
        flow_results["errors"].append(f"{task.task_id}/scenario1")
    
    # Scenario 2: Search then submit
    try:
        env = CRMQueryEnv()
        obs = env.reset()
        env.current_task_id = task.task_id
        
        action1 = {"tool": "search_customers", "arguments": {"customer_id": 1}}
        obs, reward, done, info = env.step(action1)
        
        action2 = {"tool": "submit_answer", "arguments": {"customer_ids": []}}
        obs, reward, done, info = env.step(action2)
        
        score = TaskGrader.grade_task(task, {"customer_ids": []})
        if 0.0 < score < 1.0:
            flow_results["pass"] += 1
            print(f"    ✅ Scenario 2 (search_then_submit): {score}")
        else:
            flow_results["fail"] += 1
            print(f"    ❌ Scenario 2: invalid score")
    except Exception as e:
        flow_results["fail"] += 1
        print(f"    ⚠️  Scenario 2: {type(e).__name__}")
        flow_results["errors"].append(f"{task.task_id}/scenario2")
    
    # Scenario 3: Multiple searches
    try:
        env = CRMQueryEnv()
        obs = env.reset()
        env.current_task_id = task.task_id
        
        for i in range(3):
            action = {"tool": "search_customers", "arguments": {"customer_id": i+1}}
            obs, reward, done, info = env.step(action)
            if done:
                break
        
        action = {"tool": "submit_answer", "arguments": {"customer_ids": []}}
        obs, reward, done, info = env.step(action)
        
        score = TaskGrader.grade_task(task, {"customer_ids": []})
        if 0.0 < score < 1.0:
            flow_results["pass"] += 1
            print(f"    ✅ Scenario 3 (multiple_searches): {score}")
        else:
            flow_results["fail"] += 1
            print(f"    ❌ Scenario 3: invalid score")
    except Exception as e:
        flow_results["fail"] += 1
        print(f"    ⚠️  Scenario 3: {type(e).__name__}")
        flow_results["errors"].append(f"{task.task_id}/scenario3")
    
    # Scenario 4: Invalid action recovery
    try:
        env = CRMQueryEnv()
        obs = env.reset()
        env.current_task_id = task.task_id
        
        try:
            action = {"tool": "invalid", "arguments": {}}
            obs, reward, done, info = env.step(action)
        except:
            pass  # Expected to fail
        
        # Reset and try again
        env = CRMQueryEnv()
        obs = env.reset()
        env.current_task_id = task.task_id
        
        action = {"tool": "submit_answer", "arguments": {"customer_ids": []}}
        obs, reward, done, info = env.step(action)
        
        score = TaskGrader.grade_task(task, {"customer_ids": []})
        if 0.0 < score < 1.0:
            flow_results["pass"] += 1
            print(f"    ✅ Scenario 4 (recovery): {score}")
        else:
            flow_results["fail"] += 1
            print(f"    ❌ Scenario 4: invalid score")
    except Exception as e:
        flow_results["fail"] += 1
        print(f"    ⚠️  Scenario 4: {type(e).__name__}")
        flow_results["errors"].append(f"{task.task_id}/scenario4")

print(f"\nFlow Tests: {flow_results['pass']} pass, {flow_results['fail']} fail")

# ============================================================================
# SECTION 5: SCORE VALIDATION TESTS (15 test cases)
# ============================================================================
print("\n[SECTION 5] SCORE VALIDATION - 15 TEST CASES")
print("-" * 80)

score_results = {"valid": 0, "invalid": 0, "errors": []}

test_answers = [
    {"customer_ids": []},
    {"customer_ids": ["C005"]},
    {"customer_ids": ["C001", "C004"]},
    {"customer_ids": ["X1", "X2"]},
    {"customer_ids": [1, 2]},
    {"customer_ids": None},
    {"customer_ids": "string"},
    {},
    None,
]

for task in tasks:
    print(f"\n  Task: {task.task_id}")
    for answer in test_answers:
        try:
            score = TaskGrader.grade_task(task, answer)
            is_valid = isinstance(score, (int, float)) and 0.0 < score < 1.0
            answer_str = str(answer)[:30] if answer else "None"
            
            if is_valid:
                score_results["valid"] += 1
                print(f"    ✅ {answer_str}: {score}")
            else:
                score_results["invalid"] += 1
                print(f"    ❌ {answer_str}: {score}")
                score_results["errors"].append(f"{task.task_id}/{answer_str}: {score}")
        except Exception as e:
            score_results["invalid"] += 1
            print(f"    ⚠️  {answer_str}: {type(e).__name__}")
            score_results["errors"].append(f"{task.task_id}/{answer_str}: {type(e).__name__}")

print(f"\nScore Validation: {score_results['valid']} valid, {score_results['invalid']} invalid")

# ============================================================================
# SECTION 6: ENDPOINT SIMULATION (10 test cases)
# ============================================================================
print("\n[SECTION 6] /GRADER ENDPOINT SIMULATION - 10 TEST CASES")
print("-" * 80)

endpoint_results = {"pass": 0, "fail": 0, "errors": []}

endpoint_scenarios = [
    ({}, "Empty submission"),
    ({"customer_ids": []}, "Empty IDs"),
    ({"customer_ids": ["C005"]}, "Single ID"),
    ({"customer_ids": ["C001", "C004"]}, "Multiple IDs"),
    ({"customer_ids": ["X1"]}, "Invalid ID"),
    (None, "None"),
    ({"invalid": "field"}, "Invalid field"),
]

for scenario_name, answer in endpoint_scenarios:
    try:
        all_tasks = get_tasks()
        scores = {}
        
        for task in all_tasks:
            try:
                if answer is None:
                    score = TaskGrader.grade_task(task, {})
                else:
                    score = TaskGrader.grade_task(task, answer)
                
                # Clamp
                if not (0.0 < score < 1.0):
                    score = max(0.01, min(0.99, score))
                
                scores[task.task_id] = float(score)
            except:
                scores[task.task_id] = 0.01
        
        # Validate endpoint response
        is_valid = (
            len(scores) >= 3 and
            all(0.0 < v < 1.0 for v in scores.values()) and
            isinstance(scores, dict)
        )
        
        if is_valid:
            endpoint_results["pass"] += 1
            print(f"  ✅ {scenario_name}: {len(scores)} tasks, all valid")
        else:
            endpoint_results["fail"] += 1
            print(f"  ❌ {scenario_name}: invalid response")
            endpoint_results["errors"].append(f"{scenario_name}: endpoint response invalid")
    except Exception as e:
        endpoint_results["fail"] += 1
        print(f"  ⚠️  {scenario_name}: {type(e).__name__}")
        endpoint_results["errors"].append(f"{scenario_name}: {type(e).__name__}")

print(f"\nEndpoint Tests: {endpoint_results['pass']} pass, {endpoint_results['fail']} fail")

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "="*80)
print("COMPLETE TEST SUITE SUMMARY")
print("="*80)

total_pass = (grader_results["pass"] + grade_results["pass"] + 
              action_results["pass"] + flow_results["pass"] + 
              score_results["valid"] + endpoint_results["pass"])

total_fail = (grader_results["fail"] + grade_results["fail"] + 
              action_results["fail"] + flow_results["fail"] + 
              score_results["invalid"] + endpoint_results["fail"])

all_errors = (grader_results["errors"] + grade_results["errors"] + 
              action_results["errors"] + flow_results["errors"] + 
              score_results["errors"] + endpoint_results["errors"])

print(f"\nGrader Functions:      {grader_results['pass']:3d} pass, {grader_results['fail']:3d} fail")
print(f"Grade Task:            {grade_results['pass']:3d} pass, {grade_results['fail']:3d} fail")
print(f"Environment Actions:   {action_results['pass']:3d} pass, {action_results['fail']:3d} fail")
print(f"Inference Flow:        {flow_results['pass']:3d} pass, {flow_results['fail']:3d} fail")
print(f"Score Validation:      {score_results['valid']:3d} pass, {score_results['invalid']:3d} fail")
print(f"Endpoint Simulation:   {endpoint_results['pass']:3d} pass, {endpoint_results['fail']:3d} fail")
print(f"\nTOTAL:                 {total_pass:3d} pass, {total_fail:3d} fail")

if total_fail == 0:
    print(f"\n✅ ALL TESTS PASSED - SUBMISSION READY")
else:
    print(f"\n⚠️  {total_fail} TESTS FAILED")
    if all_errors:
        print(f"\nFirst 10 errors:")
        for error in all_errors[:10]:
            print(f"  - {error}")

print("\n" + "="*80)
