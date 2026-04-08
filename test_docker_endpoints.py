#!/usr/bin/env python3
"""
Test the Docker container endpoints: reset(), state(), and step()
"""
import requests
import json
import time

BASE_URL = "http://localhost:7860"

print("=" * 80)
print("TESTING DOCKER CONTAINER ENDPOINTS")
print("=" * 80)

# Test 1: Health check
print("\n[TEST 1] Health Check")
print("-" * 80)
try:
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    if response.status_code == 200:
        print("✅ PASS: Server is healthy")
    else:
        print("❌ FAIL: Unexpected status code")
except Exception as e:
    print(f"❌ FAIL: {e}")

# Test 2: Reset endpoint
print("\n[TEST 2] Reset Endpoint")
print("-" * 80)
try:
    response = requests.post(f"{BASE_URL}/reset", timeout=5)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response keys: {list(data.keys())}")
    
    if response.status_code == 200:
        if "observation" in data:
            obs = data["observation"]
            print(f"  observation keys: {list(obs.keys())}")
            print(f"  task_id: {obs.get('task_id')}")
            print(f"  done: {obs.get('done')}")
            print("✅ PASS: Reset returns proper observation")
        else:
            print("❌ FAIL: No observation in response")
    else:
        print(f"❌ FAIL: Unexpected status code {response.status_code}")
except Exception as e:
    print(f"❌ FAIL: {e}")

# Test 3: State endpoint
print("\n[TEST 3] State Endpoint")
print("-" * 80)
try:
    response = requests.get(f"{BASE_URL}/state", timeout=5)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response keys: {list(data.keys())}")
    
    if response.status_code == 200:
        if "observation" in data:
            obs = data["observation"]
            print(f"  observation keys: {list(obs.keys())}")
            print(f"  step_count: {data.get('step_count')}")
            print(f"  done: {data.get('done')}")
            print(f"  episode_reward: {data.get('episode_reward')}")
            print("✅ PASS: State returns proper data")
        else:
            print("❌ FAIL: No observation in response")
    else:
        print(f"❌ FAIL: Unexpected status code {response.status_code}")
except Exception as e:
    print(f"❌ FAIL: {e}")

# Test 4: Step endpoint with valid action
print("\n[TEST 4] Step Endpoint (Valid Action)")
print("-" * 80)
try:
    action = {
        "tool": "search_customers",
        "arguments": {"tier": "Gold"}
    }
    response = requests.post(
        f"{BASE_URL}/step",
        json=action,
        timeout=5
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response keys: {list(data.keys())}")
    
    if response.status_code == 200:
        if "observation" in data and "reward" in data:
            print(f"  observation keys: {list(data['observation'].keys())}")
            print(f"  reward: {data['reward']}")
            print(f"  done: {data.get('done')}")
            print("✅ PASS: Step returns proper response")
        else:
            print("❌ FAIL: Missing keys in response")
    else:
        print(f"❌ FAIL: Unexpected status code {response.status_code}")
except Exception as e:
    print(f"❌ FAIL: {e}")

# Test 5: Step endpoint with invalid action
print("\n[TEST 5] Step Endpoint (Invalid Action)")
print("-" * 80)
try:
    action = {
        "tool": "invalid_tool",
        "arguments": {}
    }
    response = requests.post(
        f"{BASE_URL}/step",
        json=action,
        timeout=5
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)[:200]}")
    
    if response.status_code in [200, 400]:
        print("✅ PASS: Step handles invalid action gracefully")
    else:
        print(f"⚠️  Unexpected status code {response.status_code}")
except Exception as e:
    print(f"❌ FAIL: {e}")

# Test 6: Reset and full workflow
print("\n[TEST 6] Full Workflow (Reset → Step → State)")
print("-" * 80)
try:
    # Reset
    print("  Step 1: Reset")
    response = requests.post(f"{BASE_URL}/reset", timeout=5)
    if response.status_code != 200:
        print(f"  ❌ Reset failed: {response.status_code}")
    else:
        print(f"  ✅ Reset successful")
    
    # First step
    print("  Step 2: Search customers (Gold tier)")
    action = {"tool": "search_customers", "arguments": {"tier": "Gold"}}
    response = requests.post(f"{BASE_URL}/step", json=action, timeout=5)
    if response.status_code != 200:
        print(f"  ❌ Step failed: {response.status_code}")
    else:
        step_data = response.json()
        print(f"  ✅ Step successful (reward: {step_data.get('reward')})")
    
    # Get state
    print("  Step 3: Get state")
    response = requests.get(f"{BASE_URL}/state", timeout=5)
    if response.status_code != 200:
        print(f"  ❌ State failed: {response.status_code}")
    else:
        state_data = response.json()
        print(f"  ✅ State successful (step_count: {state_data.get('step_count')})")
        print(f"  ✅ episode_reward: {state_data.get('episode_reward')}")
    
    print("✅ PASS: Full workflow successful")
except Exception as e:
    print(f"❌ FAIL: {e}")

# Test 7: Grader endpoint
print("\n[TEST 7] Grader Endpoint")
print("-" * 80)
try:
    response = requests.post(f"{BASE_URL}/grader", timeout=5)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response keys: {list(data.keys())}")
    
    if response.status_code == 200:
        if "scores" in data:
            scores = data["scores"]
            print(f"  Task scores:")
            for task_id, score in scores.items():
                valid = 0.0 < score < 1.0
                status = "✅" if valid else "❌"
                print(f"    {status} {task_id}: {score:.3f}")
            
            if all(0.0 < s < 1.0 for s in scores.values()):
                print("✅ PASS: All scores in valid range (0, 1)")
            else:
                print("❌ FAIL: Some scores out of range")
        else:
            print("❌ FAIL: No scores in response")
    else:
        print(f"❌ FAIL: Unexpected status code {response.status_code}")
except Exception as e:
    print(f"❌ FAIL: {e}")

# Test 8: Tasks endpoint
print("\n[TEST 8] Tasks Endpoint")
print("-" * 80)
try:
    response = requests.get(f"{BASE_URL}/tasks", timeout=5)
    print(f"Status: {response.status_code}")
    data = response.json()
    
    if response.status_code == 200:
        if "tasks" in data:
            tasks = data["tasks"]
            print(f"  Found {len(tasks)} tasks:")
            for task in tasks:
                print(f"    - {task.get('task_id')}: {task.get('difficulty')}")
            
            if len(tasks) >= 3:
                print("✅ PASS: Found >= 3 tasks")
            else:
                print(f"❌ FAIL: Only {len(tasks)} tasks found")
        else:
            print("❌ FAIL: No tasks in response")
    else:
        print(f"❌ FAIL: Unexpected status code {response.status_code}")
except Exception as e:
    print(f"❌ FAIL: {e}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("\nAll endpoints tested. Check results above for any failures.")
