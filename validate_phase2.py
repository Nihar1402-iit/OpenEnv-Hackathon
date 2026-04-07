#!/usr/bin/env python3
"""
Validator Simulation - Check if graders work as expected by the OpenEnv validator
"""

import sys
import json
from typing import Dict, Any, List

def validate_phase2() -> bool:
    """Simulate Phase 2 validation"""
    
    print("\n" + "="*80)
    print("🔍 PHASE 2 VALIDATOR SIMULATION")
    print("="*80 + "\n")
    
    # Step 1: Check if we can import the required modules
    print("STEP 1: Checking imports...")
    try:
        from app import GRADERS, get_task_by_id, get_tasks, get_all_graders
        print("✅ Successfully imported GRADERS, get_task_by_id, get_tasks, get_all_graders")
    except ImportError as e:
        print(f"❌ Failed to import: {e}")
        return False
    
    # Step 2: Check if we have at least 3 graders
    print("\nSTEP 2: Checking grader count (requirement: ≥3)...")
    grader_count = len(GRADERS)
    print(f"   Found {grader_count} graders")
    
    if grader_count < 3:
        print(f"❌ FAILED: Need at least 3 graders, found {grader_count}")
        return False
    print("✅ PASSED: Have at least 3 graders")
    
    # Step 3: Verify each grader is callable and returns valid scores
    print("\nSTEP 3: Testing each grader...")
    all_graders_valid = True
    
    for task_id, grader in GRADERS.items():
        # Test the grader
        try:
            score = grader({"customer_ids": ["C001"]})
            
            # Validate score range
            if not (0.0 < score < 1.0):
                print(f"❌ {task_id}: Score {score} is NOT strictly between 0 and 1")
                all_graders_valid = False
            else:
                print(f"✅ {task_id}: Score {score:.4f} is valid (0 < score < 1)")
                
        except Exception as e:
            print(f"❌ {task_id}: Exception when calling grader: {e}")
            all_graders_valid = False
    
    if not all_graders_valid:
        print("\n❌ FAILED: Some graders returned invalid scores")
        return False
    
    # Step 4: Test with actual task ground truth
    print("\nSTEP 4: Testing graders with task ground truth...")
    try:
        tasks = get_tasks()
        
        if len(tasks) < 3:
            print(f"❌ FAILED: Need at least 3 tasks, found {len(tasks)}")
            return False
        
        for task in tasks[:3]:  # Test first 3 tasks
            if not task.grader:
                print(f"❌ {task.task_id}: No grader attached to task")
                all_graders_valid = False
                continue
            
            # Test perfect match
            correct_answer = {"customer_ids": task.ground_truth.get("customer_ids", [])}
            score_correct = task.grader(correct_answer)
            
            # Test wrong answer
            score_wrong = task.grader({"customer_ids": ["C999"]})
            
            valid_correct = 0.0 < score_correct < 1.0
            valid_wrong = 0.0 < score_wrong < 1.0
            
            if valid_correct and valid_wrong:
                print(f"✅ {task.task_id}: Scores valid (correct={score_correct:.4f}, wrong={score_wrong:.4f})")
            else:
                print(f"❌ {task.task_id}: Invalid scores (correct={score_correct:.4f}, wrong={score_wrong:.4f})")
                all_graders_valid = False
    
    except Exception as e:
        print(f"❌ Error testing task graders: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    if not all_graders_valid:
        return False
    
    # Step 5: Final summary
    print("\n" + "="*80)
    print("✅ VALIDATION PASSED!")
    print("="*80)
    print(f"\n✅ Requirements met:")
    print(f"   • At least 3 tasks with graders: {len(tasks)} tasks")
    print(f"   • All task scores strictly in (0, 1): YES")
    print(f"   • GRADERS registry accessible: YES ({len(GRADERS)} graders)")
    print("\n🚀 Ready for submission!\n")
    
    return True

if __name__ == "__main__":
    success = validate_phase2()
    sys.exit(0 if success else 1)
