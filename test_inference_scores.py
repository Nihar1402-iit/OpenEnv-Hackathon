#!/usr/bin/env python3
"""
Simulate inference to capture actual scores being generated.
"""
import sys
import os
from pathlib import Path
import json

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Mock API to avoid actual LLM calls
import random
from app.env import CRMQueryEnv
from app.tasks import get_tasks
from app.grader import TaskGrader

print("=" * 80)
print("INFERENCE SIMULATION WITH SCORE CAPTURE")
print("=" * 80)

tasks = get_tasks()
print(f"\n✓ Found {len(tasks)} tasks\n")

# Mock LLM - just return random valid or invalid customer_ids
class MockClient:
    def __init__(self):
        self.call_count = 0
    
    def get_completion(self, task_id):
        """Return a mock answer - sometimes empty, sometimes partial, sometimes complete"""
        self.call_count += 1
        
        task = next(t for t in tasks if t.task_id == task_id)
        correct_ids = task.ground_truth['customer_ids']
        
        rand = random.random()
        if rand < 0.3:
            # Return empty answer
            return {"customer_ids": []}
        elif rand < 0.6:
            # Return partial answer (50%)
            num_to_return = max(1, len(correct_ids) // 2)
            return {"customer_ids": correct_ids[:num_to_return]}
        else:
            # Return all correct answers
            return {"customer_ids": correct_ids}

client = MockClient()
scores = {}

print("[START] task=all env=CRMQueryEnv model=mock-llm")

for task in tasks:
    print(f"\n[Processing {task.task_id}]")
    
    # Simulate getting an answer from the mock LLM
    answer = client.get_completion(task.task_id)
    
    # Grade it
    score = TaskGrader.grade_task(task, answer)
    scores[task.task_id] = score
    
    print(f"  Ground truth: {task.ground_truth['customer_ids']}")
    print(f"  Submitted: {answer['customer_ids']}")
    print(f"  Score: {score:.3f}")
    print(f"  Valid (0, 1): {0.0 < score < 1.0}")
    print(f"[STEP] step=1 action=submit_answer reward={score:.2f} done=true error=null")
    print(f"[END] task_id={task.task_id} success={'true' if score >= 0.5 else 'false'} steps=1 rewards={score:.2f} score={score:.3f}")

print("\n" + "=" * 80)
print("FINAL SUMMARY")
print("=" * 80)

avg_score = sum(scores.values()) / len(scores) if scores else 0
print(f"\nTotal tasks: {len(scores)}")
print(f"Task scores: {', '.join(f'{k}={v:.3f}' for k, v in scores.items())}")
print(f"Average: {avg_score:.3f}")

# Check if all are in valid range
invalid_count = sum(1 for s in scores.values() if not (0.0 < s < 1.0))
print(f"\n✓ Valid scores: {len(scores) - invalid_count}/{len(scores)}")
if invalid_count > 0:
    print(f"❌ Invalid scores: {invalid_count}")
    for task_id, score in scores.items():
        if not (0.0 < score < 1.0):
            print(f"   - {task_id}: {score}")
    sys.exit(1)

print(f"\n✅ All scores in valid range (0, 1)")
print(f"[END] task_id=multi success={'true' if avg_score >= 0.5 else 'false'} steps=0 rewards={','.join(f'{s:.2f}' for s in scores.values())} score={avg_score:.3f}")
