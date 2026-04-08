#!/usr/bin/env python3
"""
Verify the fix is applied correctly
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("Checking if the fix was applied...")

with open("inference.py", "r") as f:
    content = f.read()

# Check for the fix
if "score=error_score" in content and "_log_task_end" in content:
    # Find the exception handler section
    start = content.find("except Exception as e:")
    end = content.find("total_time = time.time()", start)
    section = content[start:end]
    
    if "score=error_score" in section:
        print("✅ FIX APPLIED: Exception handler now logs correct score")
        
        # Show the relevant section
        lines = section.split('\n')
        for i, line in enumerate(lines[-5:], start=len(lines)-5):
            print(f"  {line}")
    else:
        print("❌ FIX NOT APPLIED: score=error_score not found in exception handler")
else:
    print("❌ FIX NOT APPLIED: Could not find the required code sections")
