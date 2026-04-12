#!/usr/bin/env python3
"""
Platform Grader Validator Simulation

This simulates what the platform validator does:
1. Parse openenv.yaml
2. Extract grader paths from each task
3. Dynamically import and call each grader function
4. Verify scores are strictly in (0, 1)

This test validates that the platform CAN find and invoke the graders.
"""

import sys
import os
import importlib
from pathlib import Path

# Add workspace root to path
sys.path.insert(0, str(Path(__file__).parent))

def load_yaml_config():
    """Load openenv.yaml configuration"""
    try:
        import yaml
    except ImportError:
        print("ERROR: PyYAML not installed. Install with: pip install pyyaml")
        return None
    
    yaml_path = Path(__file__).parent / "openenv.yaml"
    with open(yaml_path, 'r') as f:
        return yaml.safe_load(f)


def import_grader_from_path(grader_path: str):
    """
    Dynamically import a grader function from a module path.
    
    Example: "standalone_graders.grade_task_task_easy_001"
    """
    parts = grader_path.rsplit('.', 1)
    if len(parts) != 2:
        raise ValueError(f"Invalid grader path: {grader_path}")
    
    module_name, func_name = parts
    try:
        module = importlib.import_module(module_name)
        grader_func = getattr(module, func_name)
        return grader_func
    except (ImportError, AttributeError) as e:
        raise ValueError(f"Cannot import {grader_path}: {e}")


def run_platform_grader_validation():
    """
    Simulate platform validator checking graders.
    This is the CRITICAL test - if this passes, the platform can find your graders.
    """
    print("\n" + "="*70)
    print("PLATFORM GRADER VALIDATOR SIMULATION")
    print("="*70)
    print("This simulates what the platform does when evaluating your submission:\n")
    
    # Load config
    config = load_yaml_config()
    if not config:
        print("❌ Failed to load openenv.yaml")
        return False
    
    tasks = config.get("tasks", [])
    print(f"Found {len(tasks)} tasks in openenv.yaml\n")
    
    all_valid = True
    results = {}
    
    for task_config in tasks:
        task_id = task_config.get("task_id")
        grader_path = task_config.get("grader")
        ground_truth = task_config.get("ground_truth", {})
        ground_truth_ids = ground_truth.get("customer_ids", [])
        
        print(f"Task: {task_id}")
        print(f"  Grader path: {grader_path}")
        print(f"  Ground truth: {ground_truth_ids}")
        
        # Step 1: Try to import grader
        try:
            grader_func = import_grader_from_path(grader_path)
            print(f"  ✅ Successfully imported grader function")
        except Exception as e:
            print(f"  ❌ Failed to import: {e}")
            all_valid = False
            continue
        
        # Step 2: Call grader with empty submission
        try:
            empty_score = grader_func({})
            if not (0.0 < empty_score < 1.0):
                print(f"  ❌ Empty submission score {empty_score} not in (0, 1)!")
                all_valid = False
            else:
                print(f"  ✅ Empty submission: score={empty_score:.4f}")
        except Exception as e:
            print(f"  ❌ Error calling grader with empty submission: {e}")
            all_valid = False
            continue
        
        # Step 3: Call grader with correct submission
        try:
            correct_answer = {"customer_ids": ground_truth_ids}
            correct_score = grader_func(correct_answer)
            if not (0.0 < correct_score < 1.0):
                print(f"  ❌ Correct submission score {correct_score} not in (0, 1)!")
                all_valid = False
            else:
                print(f"  ✅ Correct submission: score={correct_score:.4f}")
        except Exception as e:
            print(f"  ❌ Error calling grader with correct submission: {e}")
            all_valid = False
            continue
        
        # Step 4: Call grader with partial submission
        try:
            if len(ground_truth_ids) > 1:
                partial_answer = {"customer_ids": ground_truth_ids[:len(ground_truth_ids)//2]}
            else:
                partial_answer = {"customer_ids": []}
            
            partial_score = grader_func(partial_answer)
            if not (0.0 < partial_score < 1.0):
                print(f"  ❌ Partial submission score {partial_score} not in (0, 1)!")
                all_valid = False
            else:
                print(f"  ✅ Partial submission: score={partial_score:.4f}")
        except Exception as e:
            print(f"  ❌ Error calling grader with partial submission: {e}")
            all_valid = False
            continue
        
        results[task_id] = {
            "empty": empty_score,
            "correct": correct_score,
            "partial": partial_score
        }
        print()
    
    print("="*70)
    if all_valid:
        print("✅ PLATFORM VALIDATOR: All graders found and callable!")
        print("\nScore Summary:")
        for task_id, scores in results.items():
            print(f"  {task_id}:")
            print(f"    Empty:   {scores['empty']:.4f}")
            print(f"    Partial: {scores['partial']:.4f}")
            print(f"    Correct: {scores['correct']:.4f}")
    else:
        print("❌ PLATFORM VALIDATOR: Some graders failed!")
    print("="*70 + "\n")
    
    return all_valid


def validate_openenv_structure():
    """Validate the overall openenv.yaml structure"""
    print("\n" + "="*70)
    print("OPENENV.YAML STRUCTURE VALIDATION")
    print("="*70)
    
    config = load_yaml_config()
    if not config:
        return False
    
    # Check required fields
    required_fields = ["name", "version", "environment", "tasks"]
    for field in required_fields:
        if field in config:
            print(f"✅ Required field '{field}' present")
        else:
            print(f"❌ Missing required field '{field}'")
            return False
    
    # Check task structure
    tasks = config.get("tasks", [])
    expected_task_ids = {"task_easy_001", "task_medium_001", "task_hard_001", "task_extreme_001"}
    actual_task_ids = {t.get("task_id") for t in tasks}
    
    if expected_task_ids == actual_task_ids:
        print(f"✅ All 4 expected tasks present")
    else:
        print(f"❌ Task mismatch:")
        print(f"   Expected: {expected_task_ids}")
        print(f"   Got: {actual_task_ids}")
        return False
    
    # Check each task has required fields
    for task in tasks:
        task_id = task.get("task_id")
        required = ["description", "difficulty", "grader", "ground_truth"]
        all_present = all(field in task for field in required)
        if all_present:
            print(f"✅ {task_id}: all required fields present")
        else:
            print(f"❌ {task_id}: missing fields")
            return False
    
    print("="*70 + "\n")
    return True


def main():
    """Run all validation tests"""
    print("\n")
    print("*" * 70)
    print("GRADER VALIDATOR - PRE-SUBMISSION CHECK")
    print("*" * 70)
    
    # Test 1: openenv.yaml structure
    if not validate_openenv_structure():
        print("\n❌ openenv.yaml structure validation failed")
        return 1
    
    # Test 2: Platform grader validation
    if not run_platform_grader_validation():
        print("\n❌ Platform grader validation failed")
        return 1
    
    print("*" * 70)
    print("✅ ALL VALIDATION CHECKS PASSED!")
    print("   Your graders are properly configured and callable by the platform.")
    print("*" * 70 + "\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
