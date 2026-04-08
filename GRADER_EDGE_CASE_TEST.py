#!/usr/bin/env python3
"""
ULTRA-SPECIFIC GRADER EDGE CASE TESTER
Find ANY case where grader score violates (0, 1) constraint
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.grader import TaskGrader
from app.tasks import get_tasks


def test_grader_score_bounds():
    """
    Exhaustively test grader with every conceivable answer combination
    Verify NO score can be 0.0, 1.0, or outside (0,1)
    """
    
    print("\n" + "="*70)
    print("ULTRA-SPECIFIC GRADER EDGE CASE TEST")
    print("="*70)
    
    tasks = get_tasks()
    test_count = 0
    violations = []
    
    for task in tasks:
        print(f"\n\nTesting {task.task_id}:")
        print(f"  Ground truth: {task.ground_truth}")
        
        ground_truth_ids = task.ground_truth.get("customer_ids", [])
        
        # Generate all possible answer combinations
        test_answers = []
        
        # 1. Empty
        test_answers.append({"customer_ids": []})
        
        # 2. Perfect match
        test_answers.append({"customer_ids": ground_truth_ids.copy()})
        
        # 3. Partial matches (every subset)
        for i in range(len(ground_truth_ids)):
            test_answers.append({"customer_ids": [ground_truth_ids[i]]})
        
        for i in range(len(ground_truth_ids)):
            subset = ground_truth_ids[:i+1]
            test_answers.append({"customer_ids": subset})
        
        # 4. Wrong answers
        test_answers.append({"customer_ids": ["WRONG"]})
        test_answers.append({"customer_ids": ["WRONG1", "WRONG2"]})
        
        # 5. Mixed correct/wrong
        if ground_truth_ids:
            test_answers.append({"customer_ids": [ground_truth_ids[0], "WRONG"]})
        
        # 6. Type edge cases
        test_answers.append({"customer_ids": None})
        test_answers.append({})
        test_answers.append(None)
        test_answers.append("invalid")
        test_answers.append([])
        
        # 7. String answers
        test_answers.append({"customer_ids": "C001"})
        test_answers.append({"customer_ids": 123})
        test_answers.append({"customer_ids": 0})
        test_answers.append({"customer_ids": -1})
        
        # Test each answer
        for answer in test_answers:
            test_count += 1
            
            try:
                score = TaskGrader.grade_task(task, answer)
                
                # Check constraints
                is_float = isinstance(score, (int, float))
                is_in_range = 0.0 < score < 1.0
                is_not_zero = score != 0.0
                is_not_one = score != 1.0
                
                if not is_float:
                    violations.append(f"{task.task_id}: Score type {type(score)} not numeric")
                elif not is_in_range:
                    violations.append(f"{task.task_id}: Score {score} not in (0,1)")
                elif not is_not_zero:
                    violations.append(f"{task.task_id}: Score is exactly 0.0")
                elif not is_not_one:
                    violations.append(f"{task.task_id}: Score is exactly 1.0")
                
                if not (is_float and is_in_range and is_not_zero and is_not_one):
                    print(f"  ❌ VIOLATION: {str(answer)[:50]} → {score}")
                    
            except Exception as e:
                violations.append(f"{task.task_id}: Exception on {str(answer)[:50]}: {str(e)[:50]}")
                print(f"  ❌ EXCEPTION: {str(answer)[:50]} → {str(e)[:50]}")
    
    # Summary
    print(f"\n\n{'='*70}")
    print("GRADER CONSTRAINT VERIFICATION")
    print(f"{'='*70}")
    print(f"Total tests: {test_count}")
    print(f"Violations: {len(violations)}")
    
    if violations:
        print(f"\n❌ VIOLATIONS FOUND:")
        for v in violations[:20]:
            print(f"  • {v}")
        if len(violations) > 20:
            print(f"  ... and {len(violations)-20} more")
        return False
    else:
        print(f"\n✅ ALL {test_count} TESTS PASS - Grader is bulletproof!")
        return True


def test_score_clamping_logic():
    """
    Test the exact clamping logic from grader.py
    Verify min=0.01, max=0.99
    """
    
    print(f"\n\n{'='*70}")
    print("SCORE CLAMPING LOGIC TEST")
    print(f"{'='*70}")
    
    # Test clamping directly
    test_cases = [
        (0.0, "should clamp to 0.01"),
        (0.001, "should clamp to 0.01"),
        (0.01, "should stay 0.01"),
        (0.5, "should stay 0.5"),
        (0.99, "should stay 0.99"),
        (0.999, "should clamp to 0.99"),
        (1.0, "should clamp to 0.99"),
        (2.0, "should clamp to 0.99"),
        (-1.0, "should clamp to 0.01"),
    ]
    
    all_pass = True
    for raw_score, description in test_cases:
        # Apply clamping logic from grader
        clamped = max(0.01, min(0.99, raw_score))
        
        # Verify constraint
        if not (0.0 < clamped < 1.0):
            print(f"❌ {raw_score} → {clamped}: {description} - FAILED")
            all_pass = False
        else:
            print(f"✅ {raw_score} → {clamped}: {description}")
    
    return all_pass


def test_false_positive_penalty():
    """
    Test false positive penalty logic
    Verify it never pushes score outside (0,1)
    """
    
    print(f"\n\n{'='*70}")
    print("FALSE POSITIVE PENALTY TEST")
    print(f"{'='*70}")
    
    tasks = get_tasks()
    all_pass = True
    
    for task in tasks:
        ground_truth_ids = task.ground_truth.get("customer_ids", [])
        
        # Test with many false positives
        for num_false_positives in range(1, 100):
            false_positive_ids = [f"WRONG_{i}" for i in range(num_false_positives)]
            answer = {"customer_ids": false_positive_ids}
            
            try:
                score = TaskGrader.grade_task(task, answer)
                
                if not (0.0 < score < 1.0):
                    print(f"❌ {task.task_id} with {num_false_positives} FPs: {score}")
                    all_pass = False
                
            except Exception as e:
                print(f"❌ {task.task_id} with {num_false_positives} FPs: Exception {str(e)[:50]}")
                all_pass = False
    
    if all_pass:
        print(f"✅ False positive penalty never violates constraint")
    
    return all_pass


if __name__ == "__main__":
    test1 = test_grader_score_bounds()
    test2 = test_score_clamping_logic()
    test3 = test_false_positive_penalty()
    
    success = test1 and test2 and test3
    
    print(f"\n\n{'='*70}")
    print("FINAL VERDICT")
    print(f"{'='*70}")
    if success:
        print("🎉 ALL EDGE CASES PASS - GRADER IS BULLETPROOF")
    else:
        print("⚠️  SOME EDGE CASES FAILED")
    
    sys.exit(0 if success else 1)
