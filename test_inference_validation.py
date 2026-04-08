#!/usr/bin/env python3
"""
Test what inference.py actually outputs and check for validation issues.
Focus on: Does it produce structured logs? Are scores in valid range?
"""
import sys
import os
from pathlib import Path
import json
import re

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("INFERENCE.PY OUTPUT ANALYSIS")
print("=" * 80)

# Import inference components
from app.tasks import get_tasks
from app.grader import TaskGrader

print("\n[1] Can we get all tasks?")
tasks = get_tasks()
print(f"✓ Got {len(tasks)} tasks:")
for t in tasks:
    print(f"  - {t.task_id}: {t.description[:50]}...")

print("\n[2] Simulate what inference.py logs")
print("\nSimulated inference output:")
print("-" * 80)

# Simulate inference output
run_id = "1234567890"
model = "gpt-3.5-turbo"
api_base = "https://api.openai.com/v1"

# Start
print(f"[START] task=all env=CRMQueryEnv model={model}")

# For each task, simulate a result
scores = {}
for task in tasks:
    # Simulate random answer (50% correct for demo)
    correct_ids = task.ground_truth['customer_ids']
    num_correct = len(correct_ids) // 2
    submitted_ids = correct_ids[:num_correct] if num_correct > 0 else []
    
    # Grade it
    answer = {"customer_ids": submitted_ids}
    score = TaskGrader.grade_task(task, answer)
    scores[task.task_id] = score
    
    # Log steps
    print(f"[STEP] step=1 action=submit_answer reward={score:.2f} done=true error=null")
    
    # Log end
    success = score >= 0.5
    print(f"[END] task_id={task.task_id} success={str(success).lower()} steps=1 rewards={score:.2f} score={score:.3f}")

# Calculate average
avg_score = sum(scores.values()) / len(scores)
score_str = ",".join(f"{s:.3f}" for s in scores.values())
print(f"[END] task_id=multi success={'true' if avg_score >= 0.5 else 'false'} steps=0 rewards={score_str} score={avg_score:.3f}")

print("-" * 80)

# Parse and validate
print("\n[3] Parse and validate logs")

output = ""
print(f"[START] task=all env=CRMQueryEnv model={model}")
for task in tasks:
    correct_ids = task.ground_truth['customer_ids']
    num_correct = len(correct_ids) // 2
    submitted_ids = correct_ids[:num_correct] if num_correct > 0 else []
    answer = {"customer_ids": submitted_ids}
    score = TaskGrader.grade_task(task, answer)
    scores[task.task_id] = score
    success = score >= 0.5
    print(f"[STEP] step=1 action=submit_answer reward={score:.2f} done=true error=null")
    print(f"[END] task_id={task.task_id} success={str(success).lower()} steps=1 rewards={score:.2f} score={score:.3f}")

avg_score = sum(scores.values()) / len(scores)
score_str = ",".join(f"{s:.3f}" for s in scores.values())
print(f"[END] task_id=multi success={'true' if avg_score >= 0.5 else 'false'} steps=0 rewards={score_str} score={avg_score:.3f}")

# Extract [END] lines with task_id
print("\n[4] Validator extracts task scores from [END] lines")
end_pattern = r'\[END\].*task_id=(\w+).*score=([0-9.]+)'
all_output = ""
for task in tasks:
    correct_ids = task.ground_truth['customer_ids']
    num_correct = len(correct_ids) // 2
    submitted_ids = correct_ids[:num_correct] if num_correct > 0 else []
    answer = {"customer_ids": submitted_ids}
    score = TaskGrader.grade_task(task, answer)
    all_output += f"[END] task_id={task.task_id} success=true steps=1 rewards={score:.2f} score={score:.3f}\n"

lines = all_output.strip().split('\n')
task_scores_from_logs = {}
for line in lines:
    if '[END]' in line and 'task_id=' in line:
        match = re.search(r'task_id=(\w+).*score=([0-9.]+)', line)
        if match:
            task_id, score_str = match.groups()
            score_val = float(score_str)
            
            # Skip 'multi' task
            if task_id != 'multi':
                task_scores_from_logs[task_id] = score_val
                valid = 0.0 < score_val < 1.0
                status = "✓" if valid else "❌"
                print(f"  {status} {task_id}: {score_val:.3f}")

print("\n[5] Validation checks")
print(f"  Number of tasks scored: {len(task_scores_from_logs)}")
if len(task_scores_from_logs) < 3:
    print(f"  ❌ FAIL: Less than 3 tasks with scores")
else:
    print(f"  ✓ PASS: At least 3 tasks with scores")

invalid = [s for s in task_scores_from_logs.values() if not (0.0 < s < 1.0)]
if invalid:
    print(f"  ❌ FAIL: {len(invalid)} scores out of range (not strictly between 0 and 1)")
    for score in invalid:
        print(f"    - {score}")
else:
    print(f"  ✓ PASS: All scores strictly between 0 and 1")

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)
if len(task_scores_from_logs) >= 3 and all(0.0 < s < 1.0 for s in task_scores_from_logs.values()):
    print("✅ Should PASS validation")
else:
    print("❌ Will FAIL validation")
