#!/usr/bin/env python3
"""
Comprehensive Phase 2 Diagnostic - Ensures submission will pass validation
"""

import sys
import json
import yaml
from pathlib import Path

def check_yaml_tasks():
    """Check if openenv.yaml has all tasks with graders"""
    print("\n" + "="*80)
    print("📋 YAML TASK CONFIGURATION CHECK")
    print("="*80)
    
    try:
        with open('openenv.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        tasks_in_yaml = config.get('tasks', [])
        print(f"✅ Tasks defined in openenv.yaml: {len(tasks_in_yaml)}")
        
        for task in tasks_in_yaml:
            print(f"   - {task['task_id']}: {task['difficulty']}")
            ground_truth = task.get('ground_truth', {})
            print(f"     Ground truth: {ground_truth}")
        
        if len(tasks_in_yaml) < 3:
            print(f"\n❌ ERROR: Only {len(tasks_in_yaml)} tasks in yaml, need ≥3")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading openenv.yaml: {e}")
        return False

def check_python_tasks_and_graders():
    """Check if Python code has all tasks with graders"""
    print("\n" + "="*80)
    print("🐍 PYTHON TASK & GRADER CHECK")
    print("="*80)
    
    try:
        from app import get_tasks, GRADERS, get_all_graders
        
        tasks = get_tasks()
        graders = get_all_graders()
        
        print(f"✅ Tasks in Python code: {len(tasks)}")
        
        # Check each task
        all_valid = True
        for task in tasks:
            has_grader = task.grader is not None
            in_registry = task.task_id in GRADERS
            
            status = "✅" if (has_grader and in_registry) else "❌"
            print(f"   {status} {task.task_id}:")
            print(f"      Has grader function: {has_grader}")
            print(f"      In GRADERS registry: {in_registry}")
            print(f"      Difficulty: {task.difficulty}")
            
            if not (has_grader and in_registry):
                all_valid = False
        
        if len(tasks) < 3:
            print(f"\n❌ ERROR: Only {len(tasks)} tasks in Python, need ≥3")
            return False
        
        if len(graders) < 3:
            print(f"\n❌ ERROR: Only {len(graders)} graders, need ≥3")
            return False
        
        if not all_valid:
            print("\n❌ ERROR: Some tasks missing graders")
            return False
        
        print(f"\n✅ Graders in registry: {len(graders)}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_score_ranges():
    """Verify all graders return scores strictly in (0, 1)"""
    print("\n" + "="*80)
    print("📊 SCORE RANGE VALIDATION")
    print("="*80)
    
    try:
        from app import GRADERS, get_task_by_id
        
        test_cases = [
            ("Perfect match", lambda gt: {"customer_ids": gt}, "all"),
            ("Wrong answer", lambda gt: {"customer_ids": ["C999"]}, "none"),
            ("Empty answer", lambda gt: {"customer_ids": []}, "none"),
        ]
        
        all_valid = True
        
        for task_id, grader in GRADERS.items():
            print(f"\n{task_id}:")
            task = get_task_by_id(task_id)
            ground_truth = task.ground_truth.get("customer_ids", [])
            
            for test_name, answer_gen, expected in test_cases:
                answer = answer_gen(ground_truth)
                score = grader(answer)
                
                is_valid = 0.0 < score < 1.0
                status = "✅" if is_valid else "❌"
                
                print(f"   {status} {test_name:20} score={score:.4f} (valid: {is_valid})")
                
                if not is_valid:
                    all_valid = False
        
        if not all_valid:
            print("\n❌ ERROR: Some scores are not strictly between 0 and 1")
            return False
        
        print("\n✅ All scores are strictly in (0, 1)")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_api_exports():
    """Verify all necessary APIs are exported"""
    print("\n" + "="*80)
    print("🔗 API EXPORT CHECK")
    print("="*80)
    
    required_exports = [
        'GRADERS',
        'get_grader',
        'get_all_graders',
        'get_tasks',
        'get_task_by_id',
        'TaskGrader',
    ]
    
    try:
        import app
        
        all_exported = True
        for export in required_exports:
            has_export = hasattr(app, export)
            status = "✅" if has_export else "❌"
            print(f"{status} app.{export}")
            
            if not has_export:
                all_exported = False
        
        if not all_exported:
            print("\n❌ ERROR: Some required APIs are not exported")
            return False
        
        print("\n✅ All required APIs are exported")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all diagnostic checks"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "🔍 COMPREHENSIVE PHASE 2 DIAGNOSTIC" + " "*24 + "║")
    print("╚" + "="*78 + "╝")
    
    checks = [
        ("YAML Configuration", check_yaml_tasks),
        ("Python Tasks & Graders", check_python_tasks_and_graders),
        ("Score Ranges", check_score_ranges),
        ("API Exports", check_api_exports),
    ]
    
    results = {}
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"\n❌ FATAL ERROR in {check_name}: {e}")
            results[check_name] = False
    
    # Summary
    print("\n" + "="*80)
    print("📋 DIAGNOSTIC SUMMARY")
    print("="*80)
    
    for check_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {check_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*80)
    if all_passed:
        print("✅ ALL CHECKS PASSED - READY FOR SUBMISSION")
        print("="*80)
        print("\n✨ Your submission meets all Phase 2 requirements:")
        print("   ✅ At least 3 tasks with graders")
        print("   ✅ All scores strictly between 0 and 1")
        print("   ✅ GRADERS registry properly exposed")
        print("   ✅ All APIs exported")
        print("\n🚀 Ready to submit to Meta PyTorch Hackathon!\n")
        return 0
    else:
        print("❌ SOME CHECKS FAILED - FIX ERRORS BEFORE SUBMISSION")
        print("="*80)
        print("\n⚠️  Please review the errors above and fix them.\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
