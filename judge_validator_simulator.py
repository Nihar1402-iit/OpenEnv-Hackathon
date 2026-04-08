#!/usr/bin/env python3
"""
Judge Validator Simulator
Mimics what the Meta judge validator does to test if graders are accessible
"""

import sys
import json
import yaml
from pathlib import Path

def main():
    print("\n" + "=" * 100)
    print("JUDGE VALIDATOR SIMULATOR".center(100))
    print("=" * 100)
    
    # Step 1: Load openenv.yaml
    print("\n[Step 1] Loading openenv.yaml")
    try:
        with open("openenv.yaml", "r") as f:
            spec = yaml.safe_load(f)
        print("✓ openenv.yaml loaded")
    except Exception as e:
        print(f"✗ Failed to load openenv.yaml: {e}")
        return False
    
    # Step 2: Extract tasks from YAML
    print("\n[Step 2] Extracting tasks from openenv.yaml")
    yaml_tasks = spec.get("tasks", [])
    print(f"✓ Found {len(yaml_tasks)} tasks in YAML")
    
    if len(yaml_tasks) < 3:
        print(f"✗ FAIL: Only {len(yaml_tasks)} tasks (need >= 3)")
        return False
    
    # Step 3: Check each task has a grader reference
    print("\n[Step 3] Checking for grader references in YAML")
    tasks_with_graders_yaml = 0
    for task in yaml_tasks:
        task_id = task.get("task_id")
        grader_ref = task.get("grader")
        if grader_ref:
            print(f"✓ {task_id}: grader={grader_ref}")
            tasks_with_graders_yaml += 1
        else:
            print(f"✗ {task_id}: NO GRADER REFERENCE")
    
    if tasks_with_graders_yaml < 3:
        print(f"✗ FAIL: Only {tasks_with_graders_yaml} tasks with grader refs (need >= 3)")
        return False
    
    # Step 4: Try to access GRADERS registry
    print("\n[Step 4] Attempting to import GRADERS")
    try:
        # Try main import path
        from app.graders import GRADERS
        print(f"✓ Successfully imported GRADERS from app.graders")
        print(f"✓ GRADERS has {len(GRADERS)} entries: {list(GRADERS.keys())}")
    except Exception as e:
        print(f"✗ Failed to import GRADERS: {e}")
        return False
    
    # Step 5: Validate each grader can be called
    print("\n[Step 5] Testing each grader function")
    valid_graders = 0
    for task_id, grader in GRADERS.items():
        try:
            # Call with empty submission (worst case)
            score = grader({})
            
            # Check score is valid
            is_valid = isinstance(score, float) and 0 < score < 1
            if is_valid:
                print(f"✓ {task_id}: score={score:.6f} (VALID)")
                valid_graders += 1
            else:
                print(f"✗ {task_id}: score={score} (INVALID - not strictly between 0 and 1)")
        except Exception as e:
            print(f"✗ {task_id}: ERROR - {e}")
    
    if valid_graders < 3:
        print(f"\n✗ FAIL: Only {valid_graders} valid graders (need >= 3)")
        return False
    
    # Step 6: Test with ground truth
    print("\n[Step 6] Testing graders with ground truth")
    try:
        from app.tasks import get_tasks
        tasks = get_tasks()
        
        gt_valid = 0
        for task in tasks:
            try:
                grader = GRADERS.get(task.task_id)
                if grader:
                    score = grader(task.ground_truth)
                    is_valid = isinstance(score, float) and 0 < score < 1
                    if is_valid:
                        print(f"✓ {task.task_id} (GT): score={score:.6f} (VALID)")
                        gt_valid += 1
                    else:
                        print(f"✗ {task.task_id} (GT): score={score} (INVALID)")
            except Exception as e:
                print(f"✗ {task.task_id} (GT): ERROR - {e}")
        
        if gt_valid < 3:
            print(f"✗ WARNING: Only {gt_valid} valid graders with ground truth")
    except Exception as e:
        print(f"✗ Could not test with ground truth: {e}")
    
    # Final verdict
    print("\n" + "=" * 100)
    if valid_graders >= 3:
        print("✅ JUDGE VALIDATOR: WOULD PASS".center(100))
        print("=" * 100)
        return True
    else:
        print("❌ JUDGE VALIDATOR: WOULD FAIL".center(100))
        print("=" * 100)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
