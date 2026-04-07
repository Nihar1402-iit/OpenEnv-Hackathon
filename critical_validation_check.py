#!/usr/bin/env python3
"""
CRITICAL FIX: Ensure graders are ALWAYS accessible and valid
This module provides additional safety checks and ensures all requirements are met.
"""

import sys
from pathlib import Path

def validate_all_requirements():
    """
    Comprehensive validation that checks EVERY SINGLE requirement
    exactly as the validator would check them.
    """
    
    print("\n" + "="*100)
    print("CRITICAL VALIDATION CHECK - PHASE 2")
    print("="*100)
    
    errors = []
    warnings = []
    
    # ========================================================================
    # CHECK 1: openenv.yaml is valid and has all 4 tasks
    # ========================================================================
    print("\n[CHECK 1] openenv.yaml Configuration")
    try:
        import yaml
        with open('openenv.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        tasks = config.get('tasks', [])
        print(f"  ✓ Tasks in YAML: {len(tasks)}")
        
        if len(tasks) < 3:
            errors.append(f"Only {len(tasks)} tasks in openenv.yaml (need ≥3)")
        
        # Verify each task has ground truth
        for task in tasks:
            task_id = task.get('task_id')
            gt = task.get('ground_truth', {})
            if 'customer_ids' not in gt:
                errors.append(f"Task {task_id} missing ground_truth.customer_ids")
        
        # Check grading config
        grading = config.get('grading', {})
        bounds = grading.get('actual_bounds', [])
        if bounds and (bounds[0] <= 0.0 or bounds[1] >= 1.0):
            errors.append(f"Grading bounds {bounds} not strictly between 0 and 1")
        
        print("  ✓ All tasks have valid ground truth")
        
    except Exception as e:
        errors.append(f"openenv.yaml error: {e}")
    
    # ========================================================================
    # CHECK 2: Python tasks module
    # ========================================================================
    print("\n[CHECK 2] Python Tasks Module")
    try:
        from app import get_tasks
        tasks = get_tasks()
        
        print(f"  ✓ Tasks from get_tasks(): {len(tasks)}")
        
        if len(tasks) < 3:
            errors.append(f"Only {len(tasks)} tasks from get_tasks() (need ≥3)")
        
        # Verify each task has required fields
        for task in tasks:
            if not task.task_id:
                errors.append("Task missing task_id")
            if not task.ground_truth:
                errors.append(f"Task {task.task_id} missing ground_truth")
        
    except Exception as e:
        errors.append(f"Tasks module error: {e}")
    
    # ========================================================================
    # CHECK 3: Graders module and registry
    # ========================================================================
    print("\n[CHECK 3] Graders Module & Registry")
    try:
        from app import GRADERS, get_all_graders
        
        print(f"  ✓ GRADERS registry: {len(GRADERS)} entries")
        
        if len(GRADERS) < 3:
            errors.append(f"Only {len(GRADERS)} graders in registry (need ≥3)")
        
        # Check each grader is callable
        for task_id, grader in GRADERS.items():
            if not callable(grader):
                errors.append(f"Grader for {task_id} is not callable")
        
        # Check get_all_graders works
        all_graders = get_all_graders()
        if len(all_graders) < 3:
            errors.append(f"get_all_graders() returned only {len(all_graders)} (need ≥3)")
        
        print("  ✓ All graders are callable")
        
    except Exception as e:
        errors.append(f"Graders module error: {e}")
    
    # ========================================================================
    # CHECK 4: Grader execution - scores strictly in (0, 1)
    # ========================================================================
    print("\n[CHECK 4] Grader Score Validation")
    try:
        from app import GRADERS, get_task_by_id
        
        score_count = 0
        for task_id in sorted(GRADERS.keys()):
            grader = GRADERS[task_id]
            task = get_task_by_id(task_id)
            
            # Test multiple scenarios
            test_cases = [
                ("empty", {"customer_ids": []}),
                ("full", {"customer_ids": task.ground_truth.get("customer_ids", [])}),
                ("wrong", {"customer_ids": ["C999"]}),
            ]
            
            for case_name, answer in test_cases:
                score = grader(answer)
                score_count += 1
                
                # CRITICAL: Score MUST be strictly between 0 and 1
                if not (0.0 < score < 1.0):
                    errors.append(
                        f"Task {task_id} ({case_name}): "
                        f"score {score:.4f} NOT in (0, 1) - INVALID!"
                    )
        
        print(f"  ✓ Tested {score_count} scenarios")
        print(f"  ✓ All scores strictly between 0 and 1")
        
    except Exception as e:
        errors.append(f"Score validation error: {e}")
    
    # ========================================================================
    # CHECK 5: Task & Grader integration
    # ========================================================================
    print("\n[CHECK 5] Task-Grader Integration")
    try:
        from app import get_tasks, GRADERS
        
        tasks = get_tasks()
        tasks_with_graders = 0
        
        for task in tasks:
            if task.grader is not None and callable(task.grader):
                tasks_with_graders += 1
                # Verify it works
                try:
                    score = task.grader({"customer_ids": []})
                    if not (0.0 < score < 1.0):
                        errors.append(
                            f"Task {task.task_id}.grader() returned "
                            f"score {score:.4f} NOT in (0, 1)"
                        )
                except Exception as e:
                    errors.append(f"Task {task.task_id}.grader() failed: {e}")
        
        print(f"  ✓ Tasks with graders: {tasks_with_graders}")
        
        if tasks_with_graders < 3:
            errors.append(f"Only {tasks_with_graders} tasks with graders (need ≥3)")
        
    except Exception as e:
        errors.append(f"Integration error: {e}")
    
    # ========================================================================
    # CHECK 6: Validator access patterns
    # ========================================================================
    print("\n[CHECK 6] Validator Access Patterns")
    try:
        # Pattern 1: Direct GRADERS access
        from app import GRADERS
        assert len(GRADERS) >= 3, "GRADERS registry too small"
        print("  ✓ Pattern 1: from app import GRADERS")
        
        # Pattern 2: get_grader function
        from app import get_grader
        test_grader = get_grader("task_easy_001")
        assert callable(test_grader), "get_grader returned non-callable"
        print("  ✓ Pattern 2: from app import get_grader")
        
        # Pattern 3: get_all_graders function
        from app import get_all_graders
        all_g = get_all_graders()
        assert len(all_g) >= 3, "get_all_graders returned too few"
        print("  ✓ Pattern 3: from app import get_all_graders")
        
        # Pattern 4: get_tasks with graders
        from app import get_tasks
        all_tasks = get_tasks()
        assert all(hasattr(t, 'grader') for t in all_tasks), "Tasks missing grader attribute"
        print("  ✓ Pattern 4: get_tasks() returns tasks with graders")
        
    except Exception as e:
        errors.append(f"Validator access error: {e}")
    
    # ========================================================================
    # FINAL REPORT
    # ========================================================================
    print("\n" + "="*100)
    print("FINAL VALIDATION REPORT")
    print("="*100)
    
    if errors:
        print(f"\n❌ ERRORS FOUND ({len(errors)}):")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}")
    
    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for i, warning in enumerate(warnings, 1):
            print(f"  {i}. {warning}")
    
    if not errors:
        print("\n✅ ALL CHECKS PASSED!")
        print("\nThe submission SHOULD pass Phase 2 validation.")
        print("If it's still failing, the issue might be:")
        print("  1. Validator caching (try clearing cache)")
        print("  2. Environment differences (Docker, Python version)")
        print("  3. Stale code on submission platform")
        return True
    else:
        print("\n❌ CRITICAL ERRORS - Cannot proceed with submission")
        print("Fix the errors above before resubmitting.")
        return False

if __name__ == "__main__":
    success = validate_all_requirements()
    sys.exit(0 if success else 1)
