#!/usr/bin/env python3
"""
Test that all graders are properly registered and callable.
This validates that the platform can find and invoke each grader.
"""

import sys
import os
from pathlib import Path

# Add workspace root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_standalone_graders():
    """Test standalone_graders module"""
    print("\n" + "="*60)
    print("TEST 1: Standalone Graders Module")
    print("="*60)
    
    try:
        from standalone_graders import GRADERS, get_grader, grade_task_task_easy_001, grade_task_task_medium_001, grade_task_task_hard_001, grade_task_task_extreme_001
        print("✅ Successfully imported all grader functions")
    except ImportError as e:
        print(f"❌ Failed to import: {e}")
        return False
    
    # Check that all 4 graders are registered
    expected_graders = {"task_easy_001", "task_medium_001", "task_hard_001", "task_extreme_001"}
    actual_graders = set(GRADERS.keys())
    
    if expected_graders == actual_graders:
        print(f"✅ All 4 graders registered: {sorted(actual_graders)}")
    else:
        print(f"❌ Grader mismatch!")
        print(f"   Expected: {expected_graders}")
        print(f"   Got: {actual_graders}")
        return False
    
    # Test each grader with empty submission (should give ~0.01)
    print("\n  Testing with empty submission {}:")
    for task_id in sorted(GRADERS.keys()):
        grader = GRADERS[task_id]
        score = grader({})
        valid = 0.0 < score < 1.0
        status = "✅" if valid else "❌"
        print(f"    {status} {task_id}: score={score:.4f} (valid={valid})")
        if not valid:
            return False
    
    # Test with some correct answers
    print("\n  Testing with correct answers:")
    test_cases = {
        "task_easy_001": {"customer_ids": ["C005"]},
        "task_medium_001": {"customer_ids": ["C001", "C004", "C006", "C009", "C011", "C014", "C016", "C019"]},
        "task_hard_001": {"customer_ids": ["C001", "C004", "C006", "C009", "C011", "C014", "C016", "C019"]},
        "task_extreme_001": {"customer_ids": ["C001", "C004", "C006", "C009", "C011", "C014", "C016", "C019"]},
    }
    
    for task_id, answer in test_cases.items():
        grader = GRADERS[task_id]
        score = grader(answer)
        valid = 0.0 < score < 1.0
        status = "✅" if valid else "❌"
        # Perfect answers should give high score (0.99 or close to 1.0)
        high_score = score > 0.90
        score_status = "✅" if high_score else "⚠️"
        print(f"    {status} {task_id}: score={score:.4f} {score_status} (high_score={high_score})")
        if not valid:
            return False
    
    return True


def test_yaml_grader_paths():
    """Test that openenv.yaml has correct grader paths"""
    print("\n" + "="*60)
    print("TEST 2: openenv.yaml Grader Paths")
    print("="*60)
    
    try:
        import yaml
    except ImportError:
        print("⚠️  PyYAML not installed, skipping YAML test")
        return True
    
    yaml_path = Path(__file__).parent / "openenv.yaml"
    if not yaml_path.exists():
        print(f"❌ openenv.yaml not found at {yaml_path}")
        return False
    
    with open(yaml_path, 'r') as f:
        config = yaml.safe_load(f)
    
    tasks = config.get("tasks", [])
    print(f"Found {len(tasks)} tasks")
    
    for task in tasks:
        task_id = task.get("task_id")
        grader = task.get("grader")
        
        if isinstance(grader, str):
            # This is the correct format - a callable path
            expected = f"standalone_graders.grade_task_{task_id}"
            if grader == expected:
                print(f"✅ {task_id}: grader={grader}")
            else:
                print(f"⚠️  {task_id}: grader={grader} (expected {expected})")
        elif isinstance(grader, dict):
            # Old format - HTTP endpoint
            print(f"❌ {task_id}: grader is dict (HTTP endpoint) - should be callable path!")
            return False
        else:
            print(f"❌ {task_id}: grader type unknown: {type(grader)}")
            return False
    
    return True


def test_inference_integration():
    """Test that inference.py can use graders"""
    print("\n" + "="*60)
    print("TEST 3: Inference Integration")
    print("="*60)
    
    try:
        from app.grader import TaskGrader
        from app.tasks import get_tasks
        print("✅ Successfully imported TaskGrader and tasks")
    except ImportError as e:
        print(f"❌ Failed to import: {e}")
        return False
    
    tasks = get_tasks()
    print(f"✅ Found {len(tasks)} tasks in app.tasks")
    
    # Test TaskGrader with each task
    for task in tasks:
        try:
            # Test with empty answer
            score_empty = TaskGrader.grade_task(task, {})
            valid_empty = 0.0 < score_empty < 1.0
            
            # Test with full answer
            full_answer = {"customer_ids": task.ground_truth.get("customer_ids", [])}
            score_full = TaskGrader.grade_task(task, full_answer)
            valid_full = 0.0 < score_full < 1.0
            
            status = "✅" if (valid_empty and valid_full) else "❌"
            print(f"  {status} {task.task_id}: empty={score_empty:.4f}, full={score_full:.4f}")
            
            if not (valid_empty and valid_full):
                return False
        except Exception as e:
            print(f"  ❌ {task.task_id}: {e}")
            return False
    
    return True


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("GRADER REGISTRATION & VALIDATION TEST SUITE")
    print("="*60)
    
    all_passed = True
    
    # Test 1: Standalone graders
    if not test_standalone_graders():
        print("\n❌ TEST 1 FAILED")
        all_passed = False
    else:
        print("\n✅ TEST 1 PASSED")
    
    # Test 2: YAML configuration
    if not test_yaml_grader_paths():
        print("\n❌ TEST 2 FAILED")
        all_passed = False
    else:
        print("\n✅ TEST 2 PASSED")
    
    # Test 3: Inference integration
    if not test_inference_integration():
        print("\n❌ TEST 3 FAILED")
        all_passed = False
    else:
        print("\n✅ TEST 3 PASSED")
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL TESTS PASSED - Graders are properly registered!")
    else:
        print("❌ SOME TESTS FAILED - See details above")
    print("="*60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
