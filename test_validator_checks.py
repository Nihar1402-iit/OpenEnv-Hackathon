#!/usr/bin/env python3
"""
Simulate the validator's checks on graders and task scores.
This mimics what the Meta hackathon validator would do.
"""
import sys
import os
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("VALIDATOR META-TEST SIMULATION")
print("=" * 80)

# Step 1: Check if graders module exists and can be imported
print("\n[CHECK 1] Can import graders")
try:
    from app.graders import GRADERS, get_all_graders
    print(f"✓ Successfully imported GRADERS")
    print(f"  GRADERS type: {type(GRADERS)}")
    print(f"  GRADERS keys: {list(GRADERS.keys())}")
except Exception as e:
    print(f"❌ FAILED to import GRADERS: {e}")
    sys.exit(1)

# Step 2: Check if we have at least 3 graders
print("\n[CHECK 2] Have at least 3 graders")
graders_dict = get_all_graders()
if len(graders_dict) < 3:
    print(f"❌ FAILED: Found only {len(graders_dict)} graders, need at least 3")
    print(f"  Available: {list(graders_dict.keys())}")
    sys.exit(1)
else:
    print(f"✓ Have {len(graders_dict)} graders")
    for task_id in graders_dict:
        print(f"  - {task_id}")

# Step 3: Test each grader with various answers
print("\n[CHECK 3] Test each grader returns valid scores in (0, 1)")
from app.tasks import get_tasks

all_tasks = get_tasks()
print(f"  Found {len(all_tasks)} tasks")

invalid_scores = []

for task in all_tasks:
    task_id = task.task_id
    grader = graders_dict.get(task_id)
    
    if grader is None:
        print(f"❌ NO GRADER for {task_id}")
        invalid_scores.append((task_id, "MISSING_GRADER", None))
        continue
    
    print(f"\n  Testing {task_id}:")
    
    # Test 1: Empty answer
    try:
        score = grader({"customer_ids": []})
        score = float(score)
        print(f"    Empty answer: {score:.3f}", end="")
        if not (0.0 < score < 1.0):
            print(f" ❌ INVALID (not in (0,1))")
            invalid_scores.append((task_id, "empty_answer", score))
        else:
            print(f" ✓")
    except Exception as e:
        print(f"    Empty answer: ❌ Exception {e}")
        invalid_scores.append((task_id, "empty_answer_error", str(e)))
    
    # Test 2: Partial answer (50% of correct)
    try:
        correct_ids = task.ground_truth.get("customer_ids", [])
        partial_ids = correct_ids[:max(1, len(correct_ids)//2)]
        score = grader({"customer_ids": partial_ids})
        score = float(score)
        print(f"    Partial answer: {score:.3f}", end="")
        if not (0.0 < score < 1.0):
            print(f" ❌ INVALID (not in (0,1))")
            invalid_scores.append((task_id, "partial_answer", score))
        else:
            print(f" ✓")
    except Exception as e:
        print(f"    Partial answer: ❌ Exception {e}")
        invalid_scores.append((task_id, "partial_answer_error", str(e)))
    
    # Test 3: Perfect answer
    try:
        correct_ids = task.ground_truth.get("customer_ids", [])
        score = grader({"customer_ids": correct_ids})
        score = float(score)
        print(f"    Perfect answer: {score:.3f}", end="")
        if not (0.0 < score < 1.0):
            print(f" ❌ INVALID (not in (0,1))")
            invalid_scores.append((task_id, "perfect_answer", score))
        else:
            print(f" ✓")
    except Exception as e:
        print(f"    Perfect answer: ❌ Exception {e}")
        invalid_scores.append((task_id, "perfect_answer_error", str(e)))

# Step 4: Test /grader endpoint simulation
print("\n[CHECK 4] Test /grader endpoint (FastAPI)")
try:
    from app.main import app, grade_episode
    from app.env import CRMQueryEnv
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    
    # Call /grader endpoint
    response = client.post("/grader")
    print(f"  /grader endpoint response status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ FAILED: /grader returned {response.status_code}")
        print(f"  Response: {response.text}")
        sys.exit(1)
    
    data = response.json()
    print(f"  Response keys: {list(data.keys())}")
    
    if "scores" not in data:
        print(f"❌ FAILED: /grader response missing 'scores' key")
        sys.exit(1)
    
    scores = data["scores"]
    print(f"  Scores: {scores}")
    
    # Check each score
    print(f"\n  Validating scores from /grader:")
    for task_id, score in scores.items():
        score = float(score)
        valid = 0.0 < score < 1.0
        status = "✓" if valid else "❌"
        print(f"    {status} {task_id}: {score:.3f}", end="")
        if not valid:
            print(f" INVALID")
            invalid_scores.append((task_id, "grader_endpoint", score))
        else:
            print()

except Exception as e:
    print(f"❌ Exception during /grader test: {e}")
    import traceback
    traceback.print_exc()

# Step 5: Summary
print("\n" + "=" * 80)
print("VALIDATION SUMMARY")
print("=" * 80)

if invalid_scores:
    print(f"\n❌ FAILED: {len(invalid_scores)} invalid scores found:")
    for task_id, test_name, score in invalid_scores:
        print(f"  - {task_id} ({test_name}): {score}")
    print("\n✗ Not enough tasks with graders · One or more task scores are out of range")
    sys.exit(1)
else:
    print(f"\n✅ PASSED: All graders present and return valid scores in (0, 1)")
    print(f"✓ Ready for submission")
    sys.exit(0)
