#!/usr/bin/env python3
"""Stress test - 100 iterations of task grading"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.grader import GRADERS, TaskGrader
from app.tasks import get_tasks
import random

print("\n" + "="*80)
print("STRESS TEST - 100 iterations of task grading")
print("="*80)

try:
    tasks = get_tasks()
    iterations = 100
    errors = 0
    out_of_range = 0
    
    for i in range(iterations):
        task = random.choice(tasks)
        
        # Random test case
        test_type = random.randint(0, 5)
        
        if test_type == 0:
            answer = {"customer_ids": []}
        elif test_type == 1:
            answer = {}
        elif test_type == 2:
            answer = None
        elif test_type == 3:
            answer = {"customer_ids": [f"C{random.randint(1, 999):03d}"]}
        elif test_type == 4:
            answer = task.ground_truth
        else:
            answer = {"customer_ids": "invalid"}
        
        try:
            score = TaskGrader.grade_task(task, answer)
            
            # Validate
            if not isinstance(score, float):
                errors += 1
                print(f"  ❌ Iteration {i+1}: score is {type(score)}, not float")
            elif score <= 0.0 or score >= 1.0:
                out_of_range += 1
                print(f"  ❌ Iteration {i+1}: score {score} out of (0,1)")
            
            if i % 10 == 0:
                print(f"  ✅ Iteration {i+1}: {task.task_id} -> {score:.4f}")
        
        except Exception as e:
            errors += 1
            print(f"  ❌ Iteration {i+1}: {e}")
    
    print(f"\n  Results: {iterations} iterations")
    print(f"    - Errors: {errors}")
    print(f"    - Out of range: {out_of_range}")
    print(f"    - Success: {iterations - errors - out_of_range}")
    
    if errors == 0 and out_of_range == 0:
        print(f"\n  ✅ STRESS TEST PASSED - 100% success rate")
    else:
        print(f"\n  ❌ STRESS TEST FAILED")
        sys.exit(1)

except Exception as e:
    print(f"❌ STRESS TEST FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*80)
print("✅ STRESS TEST COMPLETE")
print("="*80 + "\n")
