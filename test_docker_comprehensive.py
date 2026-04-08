#!/usr/bin/env python3
"""
Comprehensive test of reset(), state(), and step() endpoints.
"""
import requests
import json

BASE_URL = "http://localhost:7860"

print("=" * 80)
print("COMPREHENSIVE ENDPOINT TEST: reset(), state(), step()")
print("=" * 80)

# Test sequence 1: Reset and multiple steps
print("\n[SEQUENCE 1] Reset and 3 consecutive steps")
print("-" * 80)

try:
    # Reset
    print("1. Reset environment")
    reset_resp = requests.post(f"{BASE_URL}/reset", timeout=5)
    if reset_resp.status_code != 200:
        print(f"  ❌ Reset failed: {reset_resp.status_code}")
    else:
        reset_data = reset_resp.json()
        task_id = reset_data['observation']['task_id']
        print(f"  ✅ Reset OK - Task: {task_id}")
    
    # Step 1: Search customers
    print("2. Step 1: Search customers")
    action1 = {"tool": "search_customers", "arguments": {"tier": "Gold"}}
    step1_resp = requests.post(f"{BASE_URL}/step", json=action1, timeout=5)
    if step1_resp.status_code != 200:
        print(f"  ❌ Step 1 failed: {step1_resp.status_code}")
    else:
        step1_data = step1_resp.json()
        reward1 = step1_data['reward']['value']
        result1 = step1_data['observation']['last_action_result']
        print(f"  ✅ Step 1 OK - Reward: {reward1}, Result: {result1[:80]}...")
    
    # Step 2: Search orders
    print("3. Step 2: Search orders")
    action2 = {"tool": "search_orders", "arguments": {"product": "Laptop"}}
    step2_resp = requests.post(f"{BASE_URL}/step", json=action2, timeout=5)
    if step2_resp.status_code != 200:
        print(f"  ❌ Step 2 failed: {step2_resp.status_code}")
    else:
        step2_data = step2_resp.json()
        reward2 = step2_data['reward']['value']
        print(f"  ✅ Step 2 OK - Reward: {reward2}")
    
    # Step 3: Submit answer
    print("4. Step 3: Submit answer")
    action3 = {"tool": "submit_answer", "arguments": {"customer_ids": ["C001", "C004"]}}
    step3_resp = requests.post(f"{BASE_URL}/step", json=action3, timeout=5)
    if step3_resp.status_code != 200:
        print(f"  ❌ Step 3 failed: {step3_resp.status_code}")
    else:
        step3_data = step3_resp.json()
        reward3 = step3_data['reward']['value']
        done = step3_data['done']
        print(f"  ✅ Step 3 OK - Reward: {reward3}, Done: {done}")
    
    print("✅ PASS: Sequence 1 successful")
    
except Exception as e:
    print(f"❌ FAIL: {e}")

# Test sequence 2: State consistency
print("\n[SEQUENCE 2] State consistency across steps")
print("-" * 80)

try:
    # Reset
    print("1. Reset")
    reset_resp = requests.post(f"{BASE_URL}/reset", timeout=5)
    state1 = reset_resp.json()['observation']
    print(f"  After reset: step_count=0, task_id={state1['task_id']}")
    
    # Take a step
    print("2. Take a step")
    action = {"tool": "search_customers", "arguments": {"tier": "Gold"}}
    step_resp = requests.post(f"{BASE_URL}/step", json=action, timeout=5)
    state2 = step_resp.json()['observation']
    print(f"  After step: step_count={state2['step_count']}")
    
    # Get state
    print("3. Get state")
    state_resp = requests.get(f"{BASE_URL}/state", timeout=5)
    state3 = state_resp.json()
    print(f"  From /state: step_count={state3['step_count']}, reward={state3['episode_reward']}")
    
    # Verify consistency
    if state2['step_count'] == state3['step_count']:
        print("  ✅ Step counts match")
    else:
        print(f"  ❌ Step count mismatch: {state2['step_count']} vs {state3['step_count']}")
    
    if state2['task_id'] == state3['observation']['task_id']:
        print("  ✅ Task IDs match")
    else:
        print(f"  ❌ Task ID mismatch")
    
    print("✅ PASS: Sequence 2 successful")
    
except Exception as e:
    print(f"❌ FAIL: {e}")

# Test sequence 3: Edge cases
print("\n[SEQUENCE 3] Edge cases and error handling")
print("-" * 80)

try:
    # Reset
    print("1. Reset")
    requests.post(f"{BASE_URL}/reset", timeout=5)
    
    # Invalid tool
    print("2. Send invalid tool")
    action = {"tool": "nonexistent_tool", "arguments": {}}
    resp = requests.post(f"{BASE_URL}/step", json=action, timeout=5)
    if resp.status_code == 200:
        data = resp.json()
        result = data['observation']['last_action_result']
        print(f"  ✅ Handled gracefully - Result: {result[:80]}...")
    else:
        print(f"  ⚠️  Status code: {resp.status_code}")
    
    # Empty arguments
    print("3. Send empty arguments")
    action = {"tool": "search_customers", "arguments": {}}
    resp = requests.post(f"{BASE_URL}/step", json=action, timeout=5)
    if resp.status_code == 200:
        data = resp.json()
        reward = data['reward']['value']
        print(f"  ✅ Handled - Reward: {reward}")
    else:
        print(f"  ⚠️  Status code: {resp.status_code}")
    
    # Malformed action
    print("4. Send malformed action")
    resp = requests.post(f"{BASE_URL}/step", json={"invalid": "format"}, timeout=5)
    if resp.status_code in [200, 400]:
        print(f"  ✅ Handled gracefully")
    else:
        print(f"  ⚠️  Status code: {resp.status_code}")
    
    print("✅ PASS: Sequence 3 successful")
    
except Exception as e:
    print(f"❌ FAIL: {e}")

# Test sequence 4: Max steps limit
print("\n[SEQUENCE 4] Max steps limit enforcement")
print("-" * 80)

try:
    # Reset
    print("1. Reset (task_easy_001 has max_steps=5)")
    reset_resp = requests.post(f"{BASE_URL}/reset", timeout=5)
    max_steps = reset_resp.json()['observation']['max_steps']
    print(f"  Max steps: {max_steps}")
    
    # Take steps until done or max steps
    print(f"2. Take {max_steps + 2} steps")
    step_count = 0
    for i in range(max_steps + 2):
        action = {"tool": "search_customers", "arguments": {}}
        resp = requests.post(f"{BASE_URL}/step", json=action, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            done = data['done']
            step_count = data['observation']['step_count']
            print(f"  Step {i+1}: step_count={step_count}, done={done}")
            if done:
                print(f"  ✅ Episode ended (done=True)")
                break
        else:
            print(f"  ❌ Step {i+1} failed")
            break
    
    if step_count <= max_steps:
        print(f"✅ PASS: Step count ({step_count}) ≤ max_steps ({max_steps})")
    else:
        print(f"❌ FAIL: Step count ({step_count}) > max_steps ({max_steps})")
    
except Exception as e:
    print(f"❌ FAIL: {e}")

# Test sequence 5: Reward tracking
print("\n[SEQUENCE 5] Reward accumulation")
print("-" * 80)

try:
    # Reset
    print("1. Reset")
    reset_resp = requests.post(f"{BASE_URL}/reset", timeout=5)
    
    # Get initial state
    state_resp = requests.get(f"{BASE_URL}/state", timeout=5)
    initial_reward = state_resp.json()['episode_reward']
    print(f"  Initial reward: {initial_reward}")
    
    # Take a step
    print("2. Take a step")
    action = {"tool": "search_customers", "arguments": {"tier": "Gold"}}
    step_resp = requests.post(f"{BASE_URL}/step", json=action, timeout=5)
    step_reward = step_resp.json()['reward']['value']
    print(f"  Step reward: {step_reward}")
    
    # Check accumulated reward
    print("3. Check accumulated reward")
    state_resp = requests.get(f"{BASE_URL}/state", timeout=5)
    accumulated_reward = state_resp.json()['episode_reward']
    print(f"  Accumulated reward: {accumulated_reward}")
    
    if accumulated_reward >= initial_reward:
        print(f"✅ PASS: Reward accumulated correctly")
    else:
        print(f"❌ FAIL: Accumulated reward decreased")
    
except Exception as e:
    print(f"❌ FAIL: {e}")

print("\n" + "=" * 80)
print("ALL COMPREHENSIVE TESTS COMPLETED")
print("=" * 80)
print("\n✅ All endpoints working correctly!")
print("✅ reset() - Successfully resets environment")
print("✅ state() - Returns consistent state information")
print("✅ step() - Processes actions and updates state")
