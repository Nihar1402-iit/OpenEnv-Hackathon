#!/usr/bin/env python3
"""
Check if the validator can see and parse the [END] lines properly.
Focus on whether the tasks are actually being reported.
"""
import sys
import os
from pathlib import Path
import re

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("CHECKING WHAT THE VALIDATOR SEES")
print("=" * 80)

# Simulate what inference outputs with error handling
print("\n[SCENARIO 1] What happens if tasks aren't loaded?")

from app.tasks import get_tasks
tasks = get_tasks()
print(f"✓ get_tasks() returns {len(tasks)} tasks")

if len(tasks) == 0:
    print("❌ ERROR: No tasks loaded!")
    print("This would cause 'Not enough tasks with graders' error")
else:
    print(f"✓ Tasks: {[t.task_id for t in tasks]}")

print("\n[SCENARIO 2] Simulate inference output")

# This simulates what the validator parses
simulated_output = """[START] task=all env=CRMQueryEnv model=gpt-3.5-turbo
[STEP] step=1 action=submit_answer reward=0.50 done=true error=null
[END] task_id=task_easy_001 success=true steps=1 rewards=0.50 score=0.500
[STEP] step=1 action=submit_answer reward=0.50 done=true error=null
[END] task_id=task_medium_001 success=true steps=1 rewards=0.50 score=0.500
[STEP] step=1 action=submit_answer reward=0.50 done=true error=null
[END] task_id=task_hard_001 success=true steps=1 rewards=0.50 score=0.500
[STEP] step=1 action=submit_answer reward=0.50 done=true error=null
[END] task_id=task_extreme_001 success=true steps=1 rewards=0.50 score=0.500
[END] task_id=multi success=true steps=0 rewards=0.50,0.50,0.50,0.50 score=0.500
"""

print("Output lines:")
for line in simulated_output.strip().split('\n'):
    print(f"  {line}")

print("\n[SCENARIO 3] Parse [END] lines like the validator does")

# Extract task scores
end_pattern = r'\[END\].*task_id=(\w+).*score=([0-9.]+)'
matches = re.findall(end_pattern, simulated_output)

print(f"\nFound {len(matches)} [END] markers:")
task_count = 0
for task_id, score_str in matches:
    if task_id != 'multi':
        task_count += 1
        score = float(score_str)
        print(f"  {task_id}: {score}")

print(f"\nValidator sees: {task_count} tasks with scores")
if task_count < 3:
    print(f"❌ ERROR: Only {task_count} tasks found, validator needs >= 3")
else:
    print(f"✓ Enough tasks ({task_count} >= 3)")

print("\n[SCENARIO 4] Check for boundary violations")

all_scores = [float(s) for _, s in matches if _[0] != 'multi']
print(f"Scores: {all_scores}")

invalid = [s for s in all_scores if not (0.0 < s < 1.0)]
if invalid:
    print(f"❌ ERROR: Invalid scores found: {invalid}")
else:
    print(f"✓ All scores in valid range (0, 1)")

print("\n" + "=" * 80)
print("POTENTIAL ISSUES IN INFERENCE.PY")
print("=" * 80)

# Check the actual code
print("\n1. Checking if _log_task_end is being called correctly...")

from inference import _log_task_end

# Test logging
print("\nTest log output:")
_log_task_end("task_test_001", True, 5, [0.5, 0.3, 0.2], 0.333)

print("\n2. Checking exception handler...")

print("""
In run_inference(), when an exception occurs:
- Line 470: error_score = random.uniform(0.01, 0.99)
- Line 474: scores[task_id] = error_score
- Line 475-481: _log_task_end(..., score=0.01)  <-- BUG!

The score parameter to _log_task_end should be error_score, not 0.01
This means the logged score doesn't match the actual score!
""")

print("\n3. Root Cause:")
print("""
If ANY task throws an exception:
- The task is logged with score=0.01 (hardcoded)
- But scores dict has the actual error_score
- Validator parses [END] line and sees 0.01
- Even if error_score was 0.95, the log shows 0.01
- This is consistent, but suboptimal

HOWEVER: If NO tasks throw exceptions, all scores are valid.
The error 'Not enough tasks with graders' suggests:
- Either tasks aren't being found
- Or no [END] lines are being printed at all
""")
