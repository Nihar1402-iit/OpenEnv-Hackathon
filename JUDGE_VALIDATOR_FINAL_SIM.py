#!/usr/bin/env python3
"""
JUDGE VALIDATOR SIMULATOR
Simulates exactly what the Meta Hackathon judge validator will do
"""

import sys
import requests
import json
import time
import subprocess
import threading
from pathlib import Path

def start_server():
    """Start the FastAPI server in background."""
    print("🚀 Starting FastAPI server...")
    try:
        result = subprocess.Popen(
            ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
            cwd="/Users/niharshah/Desktop/Meta Hackathon",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(2)  # Wait for server to start
        return result
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return None

def stop_server(process):
    """Stop the server."""
    if process:
        process.terminate()
        time.sleep(1)

def run_validator_simulation():
    """Run the judge validator simulation."""
    base_url = "http://localhost:8000"
    
    print("\n" + "=" * 80)
    print("🔍 JUDGE VALIDATOR SIMULATION")
    print("=" * 80)
    
    results = {
        "checks": [],
        "passed": 0,
        "failed": 0
    }
    
    # Check 1: Health check
    print("\n✓ Check 1: Health Check")
    try:
        resp = requests.get(f"{base_url}/health", timeout=5)
        if resp.status_code == 200:
            print(f"  ✅ PASS: Server is running")
            results["passed"] += 1
            results["checks"].append({"name": "Health Check", "status": "PASS"})
        else:
            print(f"  ❌ FAIL: Expected 200, got {resp.status_code}")
            results["failed"] += 1
            results["checks"].append({"name": "Health Check", "status": "FAIL"})
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
        results["failed"] += 1
        results["checks"].append({"name": "Health Check", "status": "FAIL"})
    
    # Check 2: Get tasks
    print("\n✓ Check 2: Get Tasks")
    try:
        resp = requests.get(f"{base_url}/tasks", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            task_count = len(data.get("tasks", []))
            if task_count == 4:
                print(f"  ✅ PASS: Found 4 tasks")
                results["passed"] += 1
                results["checks"].append({"name": "Get Tasks", "status": "PASS"})
            else:
                print(f"  ❌ FAIL: Expected 4 tasks, got {task_count}")
                results["failed"] += 1
                results["checks"].append({"name": "Get Tasks", "status": "FAIL"})
        else:
            print(f"  ❌ FAIL: Expected 200, got {resp.status_code}")
            results["failed"] += 1
            results["checks"].append({"name": "Get Tasks", "status": "FAIL"})
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
        results["failed"] += 1
        results["checks"].append({"name": "Get Tasks", "status": "FAIL"})
    
    # Check 3: Reset environment (on cold start)
    print("\n✓ Check 3: Reset Environment (Cold Start Simulation)")
    try:
        resp = requests.post(f"{base_url}/reset", timeout=5)
        if resp.status_code == 200:
            print(f"  ✅ PASS: Environment reset")
            results["passed"] += 1
            results["checks"].append({"name": "Reset Environment", "status": "PASS"})
        else:
            print(f"  ❌ FAIL: Expected 200, got {resp.status_code}")
            results["failed"] += 1
            results["checks"].append({"name": "Reset Environment", "status": "FAIL"})
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
        results["failed"] += 1
        results["checks"].append({"name": "Reset Environment", "status": "FAIL"})
    
    # Check 4: Call /grader on cold start (THIS WAS THE CRITICAL TEST)
    print("\n✓ Check 4: Call /grader on Cold Start (CRITICAL)")
    print("  This is what was failing in 30+ rejections!")
    try:
        resp = requests.post(f"{base_url}/grader", timeout=5)
        
        if resp.status_code != 200:
            print(f"  ❌ FAIL: Expected 200, got {resp.status_code}")
            print(f"     Response: {resp.text}")
            results["failed"] += 1
            results["checks"].append({"name": "Grader Cold Start", "status": "FAIL"})
        else:
            data = resp.json()
            
            # Check for required fields
            if "scores" not in data:
                print(f"  ❌ FAIL: Missing 'scores' in response")
                results["failed"] += 1
                results["checks"].append({"name": "Grader Cold Start", "status": "FAIL"})
            else:
                scores = data["scores"]
                
                # Check score count
                if len(scores) != 4:
                    print(f"  ❌ FAIL: Expected 4 scores, got {len(scores)}")
                    results["failed"] += 1
                    results["checks"].append({"name": "Grader Cold Start", "status": "FAIL"})
                else:
                    # Check score range
                    all_valid = True
                    for task_id, score in scores.items():
                        if not (0.0 < score < 1.0):
                            print(f"  ❌ FAIL: Task {task_id} score {score} not in (0, 1)")
                            all_valid = False
                    
                    if not all_valid:
                        results["failed"] += 1
                        results["checks"].append({"name": "Grader Cold Start", "status": "FAIL"})
                    else:
                        print(f"  ✅ PASS: Grader endpoint works on cold start")
                        print(f"     - Status: 200 OK")
                        print(f"     - Tasks found: 4")
                        print(f"     - Scores: {json.dumps(scores, indent=6)}")
                        print(f"     - All scores in (0, 1): YES")
                        results["passed"] += 1
                        results["checks"].append({"name": "Grader Cold Start", "status": "PASS"})
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
        results["failed"] += 1
        results["checks"].append({"name": "Grader Cold Start", "status": "FAIL"})
    
    # Check 5: Verify grader scores are deterministic
    print("\n✓ Check 5: Verify Grader Scores Are Deterministic")
    try:
        # Call grader again, should get same scores
        resp2 = requests.post(f"{base_url}/grader", timeout=5)
        if resp2.status_code == 200:
            data2 = resp2.json()
            scores2 = data2.get("scores", {})
            
            # Compare with previous scores
            if scores == scores2:
                print(f"  ✅ PASS: Scores are deterministic")
                results["passed"] += 1
                results["checks"].append({"name": "Deterministic Scores", "status": "PASS"})
            else:
                print(f"  ❌ FAIL: Scores differ on second call")
                results["failed"] += 1
                results["checks"].append({"name": "Deterministic Scores", "status": "FAIL"})
        else:
            print(f"  ❌ FAIL: Second grader call failed")
            results["failed"] += 1
            results["checks"].append({"name": "Deterministic Scores", "status": "FAIL"})
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
        results["failed"] += 1
        results["checks"].append({"name": "Deterministic Scores", "status": "FAIL"})
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 VALIDATOR SIMULATION SUMMARY")
    print("=" * 80)
    total = results["passed"] + results["failed"]
    print(f"✅ Checks Passed: {results['passed']}/{total}")
    print(f"❌ Checks Failed: {results['failed']}/{total}")
    
    if results["failed"] == 0:
        print("\n" + "🎉 " * 15)
        print("✅ ALL VALIDATOR CHECKS PASSED - READY FOR SUBMISSION")
        print("🎉 " * 15)
        return True
    else:
        print("\n⚠️  Some checks failed - do not submit yet")
        return False

def main():
    """Main entry point."""
    print("=" * 80)
    print("🔍 STARTING JUDGE VALIDATOR SIMULATION")
    print("=" * 80)
    
    # Start server
    server_process = start_server()
    
    if not server_process:
        print("❌ Failed to start server")
        return 1
    
    try:
        # Run validator
        success = run_validator_simulation()
        return 0 if success else 1
    finally:
        # Stop server
        stop_server(server_process)
        print("\n🛑 Server stopped")

if __name__ == "__main__":
    sys.exit(main())
