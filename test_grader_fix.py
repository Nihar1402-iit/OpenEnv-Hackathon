#!/usr/bin/env python3
"""
Test script to verify grader produces scores strictly between 0 and 1.
"""

from app.grader import TaskGrader
from app.tasks import get_tasks

def test_grader():
    """Test that grader returns scores in (0, 1)."""
    tasks = get_tasks()
    
    print("=" * 80)
    print("🧪 Testing Grader Score Range Validation")
    print("=" * 80)
    print(f"✅ Total tasks: {len(tasks)}")
    assert len(tasks) >= 3, "Must have at least 3 tasks"
    print("✅ At least 3 tasks present\n")
    
    # Test cases
    test_cases = [
        # (task_index, submitted_answer, description)
        (0, {"customer_ids": ["C005"]}, "Perfect match"),
        (0, {"customer_ids": []}, "Empty answer"),
        (0, {"customer_ids": ["C999"]}, "Wrong answer"),
        (0, {"customer_ids": ["C005", "C001"]}, "Partial match with false positive"),
        (1, {"customer_ids": ["C001", "C004"]}, "Partial match for medium task"),
        (2, {"customer_ids": []}, "Empty answer for hard task"),
    ]
    
    all_scores = []
    
    for task_idx, answer, description in test_cases:
        task = tasks[task_idx]
        score = TaskGrader.grade_task(task, answer)
        all_scores.append(score)
        
        # Validate score is strictly between 0 and 1
        is_valid = 0.0 < score < 1.0
        status = "✅" if is_valid else "❌"
        
        print(f"{status} Task {task.task_id}: {description}")
        print(f"   Score: {score:.4f} (Valid: {is_valid})")
        
        if not is_valid:
            print(f"   ERROR: Score must be strictly between 0 and 1!")
        
    print("\n" + "=" * 80)
    print("📊 Score Summary")
    print("=" * 80)
    print(f"Min score: {min(all_scores):.4f}")
    print(f"Max score: {max(all_scores):.4f}")
    print(f"All scores in (0, 1): {all(0.0 < s < 1.0 for s in all_scores)}")
    
    if all(0.0 < s < 1.0 for s in all_scores):
        print("\n✅ SUCCESS: All grader scores are strictly between 0 and 1!")
        return True
    else:
        print("\n❌ FAILURE: Some scores are not strictly between 0 and 1!")
        return False

if __name__ == "__main__":
    success = test_grader()
    exit(0 if success else 1)
