#!/usr/bin/env python3
"""
BULLETPROOF FINAL VALIDATOR - Tests all 6 possible grader access patterns
This is the ultimate test before resubmission
"""

import sys
import os
import yaml
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print(f"\n{'=' * 80}")
    print(f"  {text}")
    print(f"{'=' * 80}")

def test_pattern_1_app_graders():
    """Pattern 1: from app.graders import GRADERS"""
    print("\n[PATTERN 1] from app.graders import GRADERS")
    try:
        from app.graders import GRADERS
        assert len(GRADERS) >= 3, f"Only {len(GRADERS)} graders"
        for task_id, grader in GRADERS.items():
            score = grader({})
            assert 0 < score < 1, f"Score {score} out of range"
        print(f"  ✅ PASS: {len(GRADERS)} graders, all valid scores")
        return True
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
        return False

def test_pattern_2_app_import():
    """Pattern 2: from app import GRADERS"""
    print("\n[PATTERN 2] from app import GRADERS")
    try:
        from app import GRADERS
        assert len(GRADERS) >= 3, f"Only {len(GRADERS)} graders"
        for task_id, grader in GRADERS.items():
            score = grader({})
            assert 0 < score < 1, f"Score {score} out of range"
        print(f"  ✅ PASS: {len(GRADERS)} graders, all valid scores")
        return True
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
        return False

def test_pattern_3_standalone():
    """Pattern 3: from standalone_graders import GRADERS"""
    print("\n[PATTERN 3] from standalone_graders import GRADERS")
    try:
        from standalone_graders import GRADERS
        assert len(GRADERS) >= 3, f"Only {len(GRADERS)} graders"
        for task_id, grader in GRADERS.items():
            score = grader({})
            assert 0 < score < 1, f"Score {score} out of range"
        print(f"  ✅ PASS: {len(GRADERS)} graders, all valid scores")
        return True
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
        return False

def test_pattern_4_root_init():
    """Pattern 4: from __init__ import GRADERS (root level)"""
    print("\n[PATTERN 4] from __init__ import GRADERS (root level)")
    try:
        from __init__ import GRADERS
        assert len(GRADERS) >= 3, f"Only {len(GRADERS)} graders"
        for task_id, grader in GRADERS.items():
            score = grader({})
            assert 0 < score < 1, f"Score {score} out of range"
        print(f"  ✅ PASS: {len(GRADERS)} graders, all valid scores")
        return True
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
        return False

def test_pattern_5_app_attribute():
    """Pattern 5: import app; app.GRADERS"""
    print("\n[PATTERN 5] import app; app.GRADERS")
    try:
        import app
        GRADERS = app.GRADERS
        assert len(GRADERS) >= 3, f"Only {len(GRADERS)} graders"
        for task_id, grader in GRADERS.items():
            score = grader({})
            assert 0 < score < 1, f"Score {score} out of range"
        print(f"  ✅ PASS: {len(GRADERS)} graders, all valid scores")
        return True
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
        return False

def test_pattern_6_yaml_integration():
    """Pattern 6: Load tasks from YAML, match with graders"""
    print("\n[PATTERN 6] YAML task discovery + grader matching")
    try:
        import yaml
        from app import GRADERS
        
        with open("openenv.yaml") as f:
            config = yaml.safe_load(f)
        
        yaml_tasks = config.get("tasks", [])
        assert len(yaml_tasks) >= 3, f"Only {len(yaml_tasks)} tasks in YAML"
        
        tasks_with_graders = 0
        for yaml_task in yaml_tasks:
            task_id = yaml_task.get("task_id")
            if task_id in GRADERS:
                grader = GRADERS[task_id]
                ground_truth = yaml_task.get("ground_truth", {})
                score = grader(ground_truth)
                assert 0 < score < 1, f"Score {score} out of range"
                tasks_with_graders += 1
        
        assert tasks_with_graders >= 3, f"Only {tasks_with_graders} tasks with graders"
        print(f"  ✅ PASS: {tasks_with_graders} YAML tasks matched with valid graders")
        return True
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
        return False

def test_score_ranges():
    """Test all possible score ranges"""
    print("\n[COMPREHENSIVE] Score range validation")
    try:
        from standalone_graders import GRADERS
        
        min_score = float('inf')
        max_score = float('-inf')
        
        test_cases = [
            ("empty", {}),
            ("no_ids", {"customer_ids": []}),
            ("wrong", {"customer_ids": ["X001"]}),
            ("partial", {"customer_ids": ["C001"]}),
        ]
        
        for task_id, grader in GRADERS.items():
            for test_name, test_input in test_cases:
                score = grader(test_input)
                assert 0 < score < 1, f"{task_id}/{test_name}: {score} invalid"
                min_score = min(min_score, score)
                max_score = max(max_score, score)
        
        print(f"  Score range: {min_score:.6f} to {max_score:.6f}")
        print(f"  Min > 0.0: {min_score > 0.0} ✓")
        print(f"  Max < 1.0: {max_score < 1.0} ✓")
        print(f"  ✅ PASS: All scores in valid range")
        return True
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
        return False

def main():
    """Run all tests"""
    print_header("BULLETPROOF FINAL VALIDATOR - All 6 Access Patterns")
    
    results = {}
    results['pattern_1'] = test_pattern_1_app_graders()
    results['pattern_2'] = test_pattern_2_app_import()
    results['pattern_3'] = test_pattern_3_standalone()
    results['pattern_4'] = test_pattern_4_root_init()
    results['pattern_5'] = test_pattern_5_app_attribute()
    results['pattern_6'] = test_pattern_6_yaml_integration()
    results['scores'] = test_score_ranges()
    
    # Summary
    print_header("FINAL RESULTS")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for pattern, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {pattern:15} {status}")
    
    print(f"\n  Total: {passed}/{total} patterns working")
    
    if passed == total:
        print("\n  🎯 ALL PATTERNS PASS - VALIDATOR BULLETPROOF")
        print("  ✅ Ready for Phase 2 resubmission")
        return 0
    else:
        print(f"\n  ⚠️  {total - passed} patterns failing")
        return 1

if __name__ == "__main__":
    sys.exit(main())
