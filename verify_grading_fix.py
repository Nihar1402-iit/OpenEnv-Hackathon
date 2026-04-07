#!/usr/bin/env python3
"""
Final verification script for Phase 2 grading validation fix.
Run this before resubmitting to confirm all requirements are met.
"""

import sys
from app.grader import TaskGrader
from app.tasks import get_tasks

def verify_task_count():
    """Verify at least 3 tasks exist."""
    tasks = get_tasks()
    task_count = len(tasks)
    
    print("\n📋 TASK COUNT VERIFICATION")
    print("-" * 70)
    print(f"Total tasks: {task_count}")
    
    for task in tasks:
        print(f"  ✅ {task.task_id} ({task.difficulty.capitalize()})")
    
    if task_count >= 3:
        print(f"\n✅ PASS: {task_count} tasks (requirement: ≥3)")
        return True
    else:
        print(f"\n❌ FAIL: {task_count} tasks (requirement: ≥3)")
        return False

def verify_score_ranges():
    """Verify all task scores are strictly in (0, 1)."""
    tasks = get_tasks()
    
    print("\n📊 SCORE RANGE VERIFICATION")
    print("-" * 70)
    
    # Test cases: (task_idx, answer, description)
    test_cases = [
        (0, {"customer_ids": ["C005"]}, "Perfect match"),
        (0, {"customer_ids": []}, "Empty answer"),
        (0, {"customer_ids": ["C999"]}, "Wrong answer"),
        (1, {"customer_ids": ["C001", "C004"]}, "Partial match 2/8"),
        (1, {"customer_ids": ["C001", "C004", "C006", "C009", "C011", "C014", "C016", "C019"]}, "Perfect match 8/8"),
        (2, {"customer_ids": []}, "Hard empty"),
        (3, {"customer_ids": ["C001"]}, "Extreme partial"),
    ]
    
    all_valid = True
    invalid_cases = []
    
    for task_idx, answer, description in test_cases:
        task = tasks[task_idx]
        score = TaskGrader.grade_task(task, answer)
        is_valid = 0.0 < score < 1.0
        
        status = "✅" if is_valid else "❌"
        print(f"{status} {task.task_id}: {description}")
        print(f"   Score: {score:.4f} (Valid: {is_valid})")
        
        if not is_valid:
            all_valid = False
            invalid_cases.append({
                "task": task.task_id,
                "description": description,
                "score": score
            })
    
    if all_valid:
        print(f"\n✅ PASS: All {len(test_cases)} test cases produce valid scores in (0, 1)")
        return True
    else:
        print(f"\n❌ FAIL: {len(invalid_cases)} test cases have invalid scores:")
        for case in invalid_cases:
            print(f"   - {case['task']} ({case['description']}): {case['score']}")
        return False

def verify_edge_cases():
    """Verify edge cases don't return exactly 0 or 1."""
    tasks = get_tasks()
    task = tasks[0]
    
    print("\n🔍 EDGE CASE VERIFICATION")
    print("-" * 70)
    
    edge_cases = [
        ("No customer_ids key", {}),
        ("customer_ids is None", {"customer_ids": None}),
        ("customer_ids is string", {"customer_ids": "invalid"}),
        ("Empty list", {"customer_ids": []}),
        ("Exact match", {"customer_ids": ["C005"]}),
    ]
    
    all_valid = True
    for description, answer in edge_cases:
        try:
            score = TaskGrader.grade_task(task, answer)
            is_valid = 0.0 < score < 1.0
            status = "✅" if is_valid else "❌"
            print(f"{status} {description}: {score:.4f}")
            if not is_valid:
                all_valid = False
        except Exception as e:
            print(f"❌ {description}: ERROR - {str(e)}")
            all_valid = False
    
    if all_valid:
        print(f"\n✅ PASS: All edge cases handled correctly")
        return True
    else:
        print(f"\n❌ FAIL: Some edge cases failed")
        return False

def main():
    """Run all verifications."""
    print("=" * 70)
    print("🔧 PHASE 2 GRADING VALIDATION FIX - VERIFICATION")
    print("=" * 70)
    
    results = {
        "task_count": verify_task_count(),
        "score_ranges": verify_score_ranges(),
        "edge_cases": verify_edge_cases(),
    }
    
    print("\n" + "=" * 70)
    print("📋 SUMMARY")
    print("=" * 70)
    
    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {check.replace('_', ' ').title()}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL VERIFICATIONS PASSED!")
        print("\n✅ Ready to resubmit to Meta Hackathon")
        print("\nNext steps:")
        print("1. Commit changes: git add app/grader.py inference.py")
        print("2. Push changes: git push origin")
        print("3. Resubmit to hackathon platform")
        print("\nDeadline: 8 April 2026, 11:59 PM IST")
        print("=" * 70)
        return 0
    else:
        print("❌ SOME VERIFICATIONS FAILED")
        print("\nPlease fix the issues above before resubmitting.")
        print("=" * 70)
        return 1

if __name__ == "__main__":
    sys.exit(main())
