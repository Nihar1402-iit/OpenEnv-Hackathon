#!/usr/bin/env python3
"""
Comprehensive test of all API endpoints for Meta hackathon submission.
Tests: /reset, /state, /step, /grader
"""
import sys
import requests
import json
import time

BASE_URL = "http://localhost:7860"

class Color:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    BOLD = '\033[1m'
    NC = '\033[0m'

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")

def pass_test(msg):
    print(f"{Color.GREEN}✓{Color.NC} {msg}")

def fail_test(msg):
    print(f"{Color.RED}✗{Color.NC} {msg}")

def info(msg):
    print(f"{Color.BLUE}ℹ{Color.NC} {msg}")

print(f"\n{Color.BOLD}{'='*60}{Color.NC}")
print(f"{Color.BOLD}  API Endpoint Validation{Color.NC}")
print(f"{Color.BOLD}{'='*60}{Color.NC}")
info(f"Testing endpoints at: {BASE_URL}")
print()

total_tests = 0
passed_tests = 0

# ==============================================================================
# TEST 1: /reset endpoint
# ==============================================================================
print(f"{Color.BOLD}TEST 1: /reset endpoint{Color.NC}")
total_tests += 1

try:
    response = requests.post(
        f"{BASE_URL}/reset",
        json={},
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        if "observation" in data:
            pass_test("/reset endpoint returns observation")
            passed_tests += 1
            info(f"Response keys: {list(data.keys())}")
        else:
            fail_test("/reset response missing 'observation' key")
    else:
        fail_test(f"/reset returned HTTP {response.status_code}")
except Exception as e:
    fail_test(f"/reset failed: {e}")

print()

# ==============================================================================
# TEST 2: /state endpoint
# ==============================================================================
print(f"{Color.BOLD}TEST 2: /state endpoint{Color.NC}")
total_tests += 1

try:
    response = requests.get(
        f"{BASE_URL}/state",
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        if "observation" in data:
            pass_test("/state endpoint works")
            passed_tests += 1
            info(f"Response keys: {list(data.keys())}")
        else:
            fail_test("/state response missing 'observation' key")
    else:
        fail_test(f"/state returned HTTP {response.status_code}")
except Exception as e:
    fail_test(f"/state failed: {e}")

print()

# ==============================================================================
# TEST 3: /step endpoint
# ==============================================================================
print(f"{Color.BOLD}TEST 3: /step endpoint{Color.NC}")
total_tests += 1

try:
    # First reset
    requests.post(f"{BASE_URL}/reset", json={}, timeout=10)
    
    # Now execute a step
    response = requests.post(
        f"{BASE_URL}/step",
        json={
            "tool": "search_customers",
            "arguments": {"customer_id": "C001"}
        },
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        if "reward" in data and "observation" in data and "done" in data:
            pass_test("/step endpoint works")
            passed_tests += 1
            reward_value = data.get("reward", {}).get("value", "unknown")
            info(f"Step reward: {reward_value}")
            info(f"Done: {data.get('done', False)}")
        else:
            fail_test(f"/step response missing required keys: {list(data.keys())}")
    else:
        fail_test(f"/step returned HTTP {response.status_code}")
except Exception as e:
    fail_test(f"/step failed: {e}")

print()

# ==============================================================================
# TEST 4: /grader endpoint
# ==============================================================================
print(f"{Color.BOLD}TEST 4: /grader endpoint{Color.NC}")
total_tests += 1

try:
    response = requests.post(
        f"{BASE_URL}/grader",
        json={},
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        if "scores" in data:
            scores = data["scores"]
            task_count = len(scores)
            info(f"Found {task_count} tasks")
            
            # Check if all scores are valid (0, 1)
            valid_scores = True
            invalid_tasks = []
            
            for task_id, score in scores.items():
                if not (0.0 < score < 1.0):
                    valid_scores = False
                    invalid_tasks.append((task_id, score))
                    print(f"  {Color.RED}✗{Color.NC} {task_id}: {score} (out of range)")
                else:
                    print(f"  {Color.GREEN}✓{Color.NC} {task_id}: {score:.3f}")
            
            if task_count >= 3:
                if valid_scores:
                    pass_test(f"/grader has {task_count} tasks with valid scores")
                    passed_tests += 1
                else:
                    fail_test(f"Some task scores are out of range (0, 1): {invalid_tasks}")
            else:
                fail_test(f"Only {task_count} tasks found (need >= 3)")
        else:
            fail_test("/grader response missing 'scores' key")
    else:
        fail_test(f"/grader returned HTTP {response.status_code}")
except Exception as e:
    fail_test(f"/grader failed: {e}")

print()

# ==============================================================================
# TEST 5: Multiple steps and final submission
# ==============================================================================
print(f"{Color.BOLD}TEST 5: Multi-step workflow{Color.NC}")
total_tests += 1

try:
    # Reset
    requests.post(f"{BASE_URL}/reset", json={}, timeout=10)
    
    # Do a few steps
    steps = [
        {"tool": "search_customers", "arguments": {"tier": "Gold"}},
        {"tool": "search_tickets", "arguments": {"priority": "High"}},
        {"tool": "submit_answer", "arguments": {"customer_ids": ["C001", "C004"]}}
    ]
    
    for i, step in enumerate(steps, 1):
        response = requests.post(
            f"{BASE_URL}/step",
            json=step,
            timeout=10
        )
        
        if response.status_code != 200:
            fail_test(f"Step {i} failed with HTTP {response.status_code}")
            break
    else:
        pass_test("Multi-step workflow completed successfully")
        passed_tests += 1
        
except Exception as e:
    fail_test(f"Multi-step workflow failed: {e}")

print()

# ==============================================================================
# SUMMARY
# ==============================================================================
print(f"{Color.BOLD}{'='*60}{Color.NC}")
print(f"{Color.BOLD}RESULTS: {passed_tests}/{total_tests} tests passed{Color.NC}")

if passed_tests == total_tests:
    print(f"{Color.GREEN}{Color.BOLD}✓ All API endpoints are working correctly!{Color.NC}")
    print(f"{Color.GREEN}{Color.BOLD}✓ Your submission is ready for deployment.{Color.NC}")
    sys.exit(0)
else:
    print(f"{Color.RED}{Color.BOLD}✗ Some tests failed. Please fix the issues above.{Color.NC}")
    sys.exit(1)
