#!/usr/bin/env python3
"""
Capture inference output to check for issues.
"""
import subprocess
import sys
import json
import re

# Set dummy API key to use random scoring
env_vars = {
    "HF_TOKEN": "test-key",
    "OPENAI_API_KEY": "test-key",
}

print("=" * 80)
print("RUNNING INFERENCE TEST")
print("=" * 80)
print()

result = subprocess.run(
    ["python", "inference.py"],
    cwd="/Users/niharshah/Desktop/Meta Hackathon",
    capture_output=True,
    text=True,
    env={**dict(os.environ), **env_vars} if 'os' in dir() else env_vars,
)

print("STDOUT:")
print("-" * 80)
print(result.stdout)
print()

print("STDERR:")
print("-" * 80)
print(result.stderr)
print()

print("Return code:", result.returncode)
print()

# Parse log lines to extract scores
print("=" * 80)
print("PARSED LOG ANALYSIS")
print("=" * 80)

all_output = result.stdout + result.stderr
log_lines = all_output.split('\n')

print("\nAll [END] lines (task scores):")
end_pattern = r'\[END\].*task_id=(\w+).*score=([0-9.]+)'
for line in log_lines:
    if '[END]' in line:
        print(f"  {line}")
        match = re.search(end_pattern, line)
        if match:
            task_id, score = match.groups()
            score_float = float(score)
            print(f"    → task_id={task_id}, score={score_float}")
            if not (0.0 < score_float < 1.0):
                print(f"    ❌ ERROR: Score {score_float} is NOT in range (0, 1)")
            else:
                print(f"    ✓ Valid")

sys.exit(result.returncode)
