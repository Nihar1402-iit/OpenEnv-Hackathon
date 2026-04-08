#!/usr/bin/env python3
"""
Diagnostic test to identify score issues.
"""
import sys
import os
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.grader import TaskGrader
from app.tasks import get_tasks

print("=" * 80)
print("SCORE DIAGNOSTIC TEST")
print("=" * 80)

# Get all tasks
tasks = get_tasks()
print(f"\n✓ Found {len(tasks)} tasks")
for task in tasks:
    print(f"  - {task.task_id}: {task.description[:60]}...")

print("\n" + "=" * 80)
print("Testing Grader Boundary Conditions")
print("=" * 80)

# Test 1: Perfect match
print("\n[TEST 1] Perfect match - should NOT return 1.0")
task = tasks[0]  # task_easy_001
answer = {"customer_ids": ["C005"]}
score = TaskGrader.grade_task(task, answer)
print(f"  Task: {task.task_id}")
print(f"  Ground truth: {task.ground_truth['customer_ids']}")
print(f"  Submitted: {answer['customer_ids']}")
print(f"  Score: {score}")
print(f"  ✓ Valid range (0, 1): {0.0 < score < 1.0}")
if score == 1.0:
    print(f"  ❌ ERROR: Score is exactly 1.0!")
elif score == 0.0:
    print(f"  ❌ ERROR: Score is exactly 0.0!")

# Test 2: Empty answer
print("\n[TEST 2] Empty answer - should NOT return 0.0")
answer = {"customer_ids": []}
score = TaskGrader.grade_task(task, answer)
print(f"  Submitted: {answer['customer_ids']}")
print(f"  Score: {score}")
print(f"  ✓ Valid range (0, 1): {0.0 < score < 1.0}")
if score == 0.0:
    print(f"  ❌ ERROR: Score is exactly 0.0!")
elif score == 1.0:
    print(f"  ❌ ERROR: Score is exactly 1.0!")

# Test 3: Partial match
print("\n[TEST 3] Partial match - should be in valid range")
task = tasks[1]  # task_medium_001 with 8 correct answers
answer = {"customer_ids": ["C001", "C004", "C006"]}  # 3 out of 8
score = TaskGrader.grade_task(task, answer)
print(f"  Task: {task.task_id}")
print(f"  Ground truth: {task.ground_truth['customer_ids']} (count={len(task.ground_truth['customer_ids'])})")
print(f"  Submitted: {answer['customer_ids']} (count={len(answer['customer_ids'])})")
print(f"  Score: {score}")
print(f"  ✓ Valid range (0, 1): {0.0 < score < 1.0}")
if score == 0.0:
    print(f"  ❌ ERROR: Score is exactly 0.0!")
elif score == 1.0:
    print(f"  ❌ ERROR: Score is exactly 1.0!")

# Test 4: Test all tasks with None/empty answers
print("\n" + "=" * 80)
print("Testing All Tasks with Various Answers")
print("=" * 80)

all_scores = {}
for task in tasks:
    print(f"\n[{task.task_id}]")
    print(f"  Ground truth: {task.ground_truth['customer_ids']}")
    
    # Test empty
    score_empty = TaskGrader.grade_task(task, {"customer_ids": []})
    all_scores[f"{task.task_id}_empty"] = score_empty
    print(f"    Empty answer score: {score_empty} - Valid (0,1): {0.0 < score_empty < 1.0}")
    
    # Test partial (50% of correct answers)
    correct_ids = task.ground_truth['customer_ids']
    partial_ids = correct_ids[:len(correct_ids)//2] if len(correct_ids) > 1 else correct_ids
    score_partial = TaskGrader.grade_task(task, {"customer_ids": partial_ids})
    all_scores[f"{task.task_id}_partial"] = score_partial
    print(f"    Partial ({len(partial_ids)}/{len(correct_ids)}) score: {score_partial} - Valid (0,1): {0.0 < score_partial < 1.0}")
    
    # Test perfect
    score_perfect = TaskGrader.grade_task(task, {"customer_ids": correct_ids})
    all_scores[f"{task.task_id}_perfect"] = score_perfect
    print(f"    Perfect match score: {score_perfect} - Valid (0,1): {0.0 < score_perfect < 1.0}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

invalid_scores = []
for test_name, score in all_scores.items():
    if not (0.0 < score < 1.0):
        invalid_scores.append((test_name, score))
        print(f"❌ {test_name}: {score} - INVALID (not in (0, 1))")
    else:
        print(f"✓ {test_name}: {score} - valid")

if invalid_scores:
    print(f"\n🚨 Found {len(invalid_scores)} INVALID scores!")
    sys.exit(1)
else:
    print(f"\n✅ All scores are valid!")
    sys.exit(0)
