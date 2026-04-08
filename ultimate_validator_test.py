#!/usr/bin/env python3
"""
ULTIMATE PHASE 2 VALIDATOR SIMULATION
Tests all possible ways the Meta PyTorch Hackathon Phase 2 validator could access graders
"""

import sys
import yaml
import traceback
from pathlib import Path

def test_yaml_loading():
    """Test 1: Can we load and verify tasks from YAML?"""
    print("\n[TEST 1] YAML Task Loading")
    print("=" * 80)
    
    try:
        with open("openenv.yaml") as f:
            config = yaml.safe_load(f)
        
        tasks = config.get("tasks", [])
        print(f"✓ Loaded {len(tasks)} tasks from openenv.yaml")
        
        for task in tasks:
            print(f"  - {task['task_id']}: {task['difficulty']}")
        
        return len(tasks), tasks
    except Exception as e:
        print(f"✗ YAML loading failed: {e}")
        return 0, []

def test_grader_import_patterns():
    """Test 2: Can we import graders using all possible patterns?"""
    print("\n[TEST 2] Grader Import Patterns")
    print("=" * 80)
    
    results = {}
    
    # Pattern A: from app import GRADERS
    try:
        from app import GRADERS
        results['app.GRADERS'] = GRADERS
        print(f"✓ Pattern A (from app import GRADERS): {len(GRADERS)} graders")
    except Exception as e:
        print(f"✗ Pattern A failed: {e}")
    
    # Pattern B: from app.graders import GRADERS
    try:
        from app.graders import GRADERS
        results['app.graders.GRADERS'] = GRADERS
        print(f"✓ Pattern B (from app.graders import GRADERS): {len(GRADERS)} graders")
    except Exception as e:
        print(f"✗ Pattern B failed: {e}")
    
    # Pattern C: import app, then app.GRADERS
    try:
        import app
        if hasattr(app, 'GRADERS'):
            results['app.GRADERS_attr'] = app.GRADERS
            print(f"✓ Pattern C (app.GRADERS attribute): {len(app.GRADERS)} graders")
        else:
            print(f"✗ Pattern C: app has no GRADERS attribute")
    except Exception as e:
        print(f"✗ Pattern C failed: {e}")
    
    # Pattern D: Root-level __init__ import
    try:
        from __init__ import GRADERS
        results['root.__init__.GRADERS'] = GRADERS
        print(f"✓ Pattern D (from __init__ import GRADERS): {len(GRADERS)} graders")
    except Exception as e:
        print(f"✗ Pattern D failed: {e}")
    
    return results

def test_grader_functionality(graders_dict):
    """Test 3: Do graders actually work and return valid scores?"""
    print("\n[TEST 3] Grader Functionality")
    print("=" * 80)
    
    if not graders_dict:
        print("✗ No graders to test")
        return False, []
    
    # Use the first successful import
    GRADERS = list(graders_dict.values())[0]
    print(f"Testing {len(GRADERS)} graders...")
    
    all_valid = True
    test_results = []
    
    for task_id, grader in GRADERS.items():
        print(f"\n  {task_id}:")
        
        # Test 1: Empty answer
        try:
            score_empty = grader({})
            is_valid = 0 < score_empty < 1
            print(f"    • Empty answer: {score_empty:.4f} (valid: {is_valid})")
            if not is_valid:
                all_valid = False
        except Exception as e:
            print(f"    • Empty answer error: {e}")
            all_valid = False
        
        # Test 2: Random wrong answer
        try:
            score_wrong = grader({"customer_ids": ["X001", "X002"]})
            is_valid = 0 < score_wrong < 1
            print(f"    • Wrong answer: {score_wrong:.4f} (valid: {is_valid})")
            if not is_valid:
                all_valid = False
        except Exception as e:
            print(f"    • Wrong answer error: {e}")
            all_valid = False
        
        test_results.append({
            'task_id': task_id,
            'scores_valid': is_valid
        })
    
    return all_valid, test_results

def test_yaml_grader_integration(yaml_tasks, graders_dict):
    """Test 4: YAML tasks + Graders integration"""
    print("\n[TEST 4] YAML + Graders Integration")
    print("=" * 80)
    
    if not yaml_tasks or not graders_dict:
        print("✗ Missing YAML tasks or graders")
        return 0
    
    GRADERS = list(graders_dict.values())[0]
    tasks_with_graders = 0
    
    print(f"Checking {len(yaml_tasks)} YAML tasks for graders...")
    
    for yaml_task in yaml_tasks:
        task_id = yaml_task.get("task_id")
        
        if task_id in GRADERS:
            grader = GRADERS[task_id]
            ground_truth = yaml_task.get("ground_truth", {})
            
            try:
                score = grader(ground_truth)
                is_valid = 0 < score < 1
                
                if is_valid:
                    tasks_with_graders += 1
                    print(f"  ✓ {task_id}: score={score:.4f} (valid)")
                else:
                    print(f"  ✗ {task_id}: score={score:.4f} (INVALID)")
            except Exception as e:
                print(f"  ✗ {task_id}: Error - {e}")
        else:
            print(f"  ✗ {task_id}: No grader found")
    
    return tasks_with_graders

def test_requirement_compliance(yaml_count, graders_dict, scores_valid, tasks_with_valid_graders):
    """Test 5: Check Phase 2 requirements"""
    print("\n[TEST 5] Phase 2 Requirements Compliance")
    print("=" * 80)
    
    GRADERS = list(graders_dict.values())[0] if graders_dict else {}
    
    # Requirement 1: At least 3 tasks with graders
    req1_pass = len(GRADERS) >= 3 and tasks_with_valid_graders >= 3
    print(f"\nRequirement 1: At least 3 tasks with graders")
    print(f"  • GRADERS count: {len(GRADERS)}")
    print(f"  • Tasks with valid graders: {tasks_with_valid_graders}")
    print(f"  Status: {'✓ PASS' if req1_pass else '✗ FAIL'}")
    
    # Requirement 2: All scores strictly between 0 and 1
    req2_pass = scores_valid
    print(f"\nRequirement 2: All scores strictly between 0 and 1")
    print(f"  Status: {'✓ PASS' if req2_pass else '✗ FAIL'}")
    
    # Requirement 3: GRADERS accessible
    req3_pass = len(GRADERS) > 0
    print(f"\nRequirement 3: GRADERS registry accessible")
    print(f"  • GRADERS accessible: {req3_pass}")
    print(f"  Status: {'✓ PASS' if req3_pass else '✗ FAIL'}")
    
    all_pass = req1_pass and req2_pass and req3_pass
    
    print(f"\n{'='*80}")
    if all_pass:
        print("✅ ALL PHASE 2 REQUIREMENTS MET - SHOULD PASS VALIDATOR")
    else:
        print("❌ SOME REQUIREMENTS NOT MET")
        if not req1_pass:
            print(f"   • Requirement 1 FAILED: Only {tasks_with_valid_graders} tasks with valid graders")
        if not req2_pass:
            print(f"   • Requirement 2 FAILED: Some scores out of range")
        if not req3_pass:
            print(f"   • Requirement 3 FAILED: GRADERS not accessible")
    print(f"{'='*80}")
    
    return all_pass

def main():
    """Run all tests"""
    print("╔" + "=" * 78 + "╗")
    print("║" + "ULTIMATE PHASE 2 VALIDATOR SIMULATION".center(78) + "║")
    print("╚" + "=" * 78 + "╝")
    
    try:
        # Test 1: YAML loading
        yaml_count, yaml_tasks = test_yaml_loading()
        
        # Test 2: Grader imports
        graders_dict = test_grader_import_patterns()
        
        # Test 3: Grader functionality
        scores_valid, test_results = test_grader_functionality(graders_dict)
        
        # Test 4: Integration
        tasks_with_valid_graders = test_yaml_grader_integration(yaml_tasks, graders_dict)
        
        # Test 5: Requirements
        all_pass = test_requirement_compliance(yaml_count, graders_dict, scores_valid, tasks_with_valid_graders)
        
        print(f"\n{'='*80}")
        if all_pass:
            print("🚀 READY FOR SUBMISSION")
        else:
            print("⚠️  ISSUES FOUND - DO NOT SUBMIT")
        print(f"{'='*80}\n")
        
        return 0 if all_pass else 1
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
