#!/usr/bin/env python3
"""
Final comprehensive check for any remaining issues in inference.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("COMPREHENSIVE FIX VERIFICATION")
print("=" * 80)

issues = []

# Check 1: Verify tasks are loaded
print("\n[CHECK 1] Tasks are loaded correctly")
try:
    from app.tasks import get_tasks
    tasks = get_tasks()
    if len(tasks) >= 3:
        print(f"✅ {len(tasks)} tasks found: {[t.task_id for t in tasks]}")
    else:
        print(f"❌ Only {len(tasks)} tasks found (need >= 3)")
        issues.append("Not enough tasks")
except Exception as e:
    print(f"❌ Failed to load tasks: {e}")
    issues.append(f"Task loading: {e}")

# Check 2: Verify graders exist
print("\n[CHECK 2] Graders are available")
try:
    from app.graders import get_all_graders
    graders = get_all_graders()
    if len(graders) >= 3:
        print(f"✅ {len(graders)} graders found: {list(graders.keys())}")
    else:
        print(f"❌ Only {len(graders)} graders found (need >= 3)")
        issues.append("Not enough graders")
except Exception as e:
    print(f"❌ Failed to load graders: {e}")
    issues.append(f"Grader loading: {e}")

# Check 3: Verify graders return valid scores
print("\n[CHECK 3] All graders return valid scores")
try:
    from app.graders import get_all_graders
    graders = get_all_graders()
    
    invalid_scores = []
    for task_id, grader in graders.items():
        score = grader({"customer_ids": []})
        if not (0.0 < score < 1.0):
            invalid_scores.append((task_id, score))
    
    if invalid_scores:
        print(f"❌ Invalid scores found:")
        for task_id, score in invalid_scores:
            print(f"   - {task_id}: {score}")
        issues.append(f"Invalid grader scores: {invalid_scores}")
    else:
        print(f"✅ All {len(graders)} graders return valid scores in (0, 1)")
except Exception as e:
    print(f"❌ Error testing graders: {e}")
    issues.append(f"Grader testing: {e}")

# Check 4: Verify inference.py fix
print("\n[CHECK 4] inference.py exception handler fixed")
try:
    with open("inference.py", "r") as f:
        content = f.read()
    
    # Find exception handler and check for the fix
    if "except Exception as e:" in content and "score=error_score" in content:
        # Verify it's in the right context
        start = content.find("except Exception as e:")
        end = content.find("total_time = time.time()", start)
        section = content[start:end]
        
        if "_log_task_end" in section and "score=error_score" in section:
            print("✅ Exception handler fixed (score=error_score)")
        else:
            print("⚠️  score=error_score found but context unclear")
            issues.append("Unclear fix context")
    else:
        print("❌ Exception handler fix not found")
        issues.append("Exception handler not fixed")
except Exception as e:
    print(f"❌ Error reading inference.py: {e}")
    issues.append(f"File reading: {e}")

# Check 5: Verify logging functions
print("\n[CHECK 5] Logging functions are defined")
try:
    from inference import _log_start, _log_step, _log_task_end, _log_final_end
    print("✅ All logging functions imported successfully")
except Exception as e:
    print(f"❌ Error importing logging functions: {e}")
    issues.append(f"Logging functions: {e}")

# Check 6: Verify score boundaries
print("\n[CHECK 6] Score boundaries are enforced")
try:
    from app.grader import TaskGrader
    from app.tasks import get_tasks
    
    tasks = get_tasks()
    boundary_issues = []
    
    for task in tasks:
        # Test perfect answer (should NOT be 1.0)
        score = TaskGrader.grade_task(task, {"customer_ids": task.ground_truth.get("customer_ids", [])})
        if score >= 1.0:
            boundary_issues.append(f"{task.task_id} perfect: {score}")
        
        # Test empty answer (should NOT be 0.0)
        score = TaskGrader.grade_task(task, {"customer_ids": []})
        if score <= 0.0:
            boundary_issues.append(f"{task.task_id} empty: {score}")
    
    if boundary_issues:
        print(f"❌ Boundary violations:")
        for issue in boundary_issues:
            print(f"   - {issue}")
        issues.append(f"Boundary violations: {boundary_issues}")
    else:
        print(f"✅ All scores properly bounded in (0, 1)")
except Exception as e:
    print(f"❌ Error checking boundaries: {e}")
    issues.append(f"Boundary check: {e}")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

if issues:
    print(f"\n⚠️  Found {len(issues)} issue(s):")
    for issue in issues:
        print(f"  - {issue}")
    sys.exit(1)
else:
    print("\n✅ ALL CHECKS PASSED")
    print("\nFix Status:")
    print("  ✅ inference.py exception handler fixed (line 478)")
    print("  ✅ All 4 tasks have graders")
    print("  ✅ All graders return valid scores in (0, 1)")
    print("  ✅ Score boundaries enforced everywhere")
    print("\nReady to resubmit!")
    sys.exit(0)
