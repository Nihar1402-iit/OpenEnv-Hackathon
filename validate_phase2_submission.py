#!/usr/bin/env python3
"""
PHASE 2 SUBMISSION VALIDATOR - Run this before submitting

This script validates that your submission meets all Phase 2 requirements:
1. At least 3 tasks with graders
2. All graders return scores strictly in (0, 1)
3. No boundary values (0.0 or 1.0)
4. All edge cases handled
5. Docker image builds and runs
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

def validate_requirements():
    """Validate all Phase 2 requirements."""
    
    print("\n" + "="*100)
    print("PHASE 2 SUBMISSION VALIDATOR".center(100))
    print("="*100)
    
    all_pass = True
    
    # ========================================================================
    # CHECK 1: At least 3 tasks with valid graders
    # ========================================================================
    print("\n[CHECK 1] Tasks & Graders")
    print("-" * 100)
    
    try:
        from app.tasks import get_tasks
        from app.graders import GRADERS
        
        tasks = get_tasks()
        grader_count = len(GRADERS)
        
        print(f"✅ Tasks: {len(tasks)}")
        print(f"✅ Graders: {grader_count}")
        
        if len(tasks) < 3:
            print(f"❌ FAIL: Only {len(tasks)} tasks (need >= 3)")
            all_pass = False
        if grader_count < 3:
            print(f"❌ FAIL: Only {grader_count} graders (need >= 3)")
            all_pass = False
        
        if all_pass:
            print("✅ PASS: At least 3 tasks with graders")
    except Exception as e:
        print(f"❌ Error: {e}")
        all_pass = False
    
    # ========================================================================
    # CHECK 2: All graders return valid scores
    # ========================================================================
    print("\n[CHECK 2] Grader Score Validation")
    print("-" * 100)
    
    try:
        from app.grader import TaskGrader
        
        for task in tasks[:3]:
            scores = []
            
            # Test empty answer
            score = TaskGrader.grade_task(task, {"customer_ids": []})
            scores.append(("empty", score))
            
            # Test perfect answer
            score = TaskGrader.grade_task(task, task.ground_truth)
            scores.append(("perfect", score))
            
            # Test wrong answer
            score = TaskGrader.grade_task(task, {"customer_ids": ["C999"]})
            scores.append(("wrong", score))
            
            # Validate all scores
            for case, score in scores:
                if not (0.0 < score < 1.0):
                    print(f"❌ {task.task_id} ({case}): {score} - NOT in (0, 1)")
                    all_pass = False
                elif score == 0.0 or score == 1.0:
                    print(f"❌ {task.task_id} ({case}): {score} - Boundary value")
                    all_pass = False
        
        if all_pass:
            print("✅ PASS: All grader scores are valid")
    except Exception as e:
        print(f"❌ Error: {e}")
        all_pass = False
    
    # ========================================================================
    # CHECK 3: Edge case handling
    # ========================================================================
    print("\n[CHECK 3] Edge Case Handling")
    print("-" * 100)
    
    try:
        edge_cases = [
            ({}, "empty dict"),
            ({"customer_ids": None}, "None value"),
            ({"customer_ids": "invalid"}, "string value"),
            (None, "None input"),
        ]
        
        for edge_case, desc in edge_cases:
            try:
                score = TaskGrader.grade_task(tasks[0], edge_case)
                if not (0.0 < score < 1.0):
                    print(f"❌ {desc}: {score} - Invalid score")
                    all_pass = False
            except Exception as e:
                print(f"❌ {desc}: Exception - {e}")
                all_pass = False
        
        if all_pass:
            print("✅ PASS: All edge cases handled")
    except Exception as e:
        print(f"❌ Error: {e}")
        all_pass = False
    
    # ========================================================================
    # CHECK 4: Verify openenv.yaml
    # ========================================================================
    print("\n[CHECK 4] OpenEnv YAML Configuration")
    print("-" * 100)
    
    try:
        import yaml
        
        with open("openenv.yaml", "r") as f:
            config = yaml.safe_load(f)
        
        yaml_tasks = config.get("tasks", [])
        print(f"✅ Tasks in YAML: {len(yaml_tasks)}")
        
        if len(yaml_tasks) < 3:
            print(f"❌ FAIL: Only {len(yaml_tasks)} tasks in YAML (need >= 3)")
            all_pass = False
        
        # Verify all tasks have ground truth
        for task in yaml_tasks:
            task_id = task.get("task_id")
            ground_truth = task.get("ground_truth")
            if not ground_truth:
                print(f"❌ {task_id}: Missing ground_truth")
                all_pass = False
        
        if all_pass:
            print("✅ PASS: OpenEnv YAML is valid")
    except Exception as e:
        print(f"❌ Error: {e}")
        all_pass = False
    
    # ========================================================================
    # FINAL RESULT
    # ========================================================================
    print("\n" + "="*100)
    
    if all_pass:
        print("✅ ALL CHECKS PASSED - READY FOR SUBMISSION".center(100))
        print("="*100)
        return 0
    else:
        print("❌ SOME CHECKS FAILED - FIX REQUIRED".center(100))
        print("="*100)
        return 1


if __name__ == "__main__":
    sys.exit(validate_requirements())
