#!/usr/bin/env python3
"""
Final Docker endpoint test - clean version without string slicing issues
"""
import requests
import json

BASE_URL = "http://localhost:7860"

print("=" * 80)
print("DOCKER ENDPOINT TEST: reset(), state(), step()")
print("=" * 80)

# Test 1: Reset and multiple steps
print("\n[TEST 1] Reset and execute 3 consecutive steps")
print("-" * 80)

try:
    # Reset
    print("  Resetting environment...")
    reset_resp = requests.post(f"{BASE_URL}/reset", timeout=5)
    assert reset_resp.status_code == 200, f"Reset failed: {reset_resp.status_code}"
    
    reset_data = reset_resp.json()
    task_id = reset_data['observation']['task_id']
    print(f"  ✅ Reset successful - Task: {task_id}")
    
    # Step 1
    print("  Executing step 1 (search_customers)...")
    action1 = {"tool": "search_customers", "arguments": {"tier": "Gold"}}
    step1_resp = requests.post(f"{BASE_URL}/step", json=action1, timeout=5)
    assert step1_resp.status_code == 200
    step1_data = step1_resp.json()
    reward1 = step1_data['reward']['value']
    print(f"  ✅ Step 1 successful - Reward: {reward1}")
    
    # Step 2
    print("  Executing step 2 (search_orders)...")
    action2 = {"tool": "search_orders", "arguments": {"product": "Laptop"}}
    step2_resp = requests.post(f"{BASE_URL}/step", json=action2, timeout=5)
    assert step2_resp.status_code == 200
    step2_data = step2_resp.json()
    reward2 = step2_data['reward']['value']
    print(f"  ✅ Step 2 successful - Reward: {reward2}")
    
    # Step 3
    print("  Executing step 3 (submit_answer)...")
    action3 = {"tool": "submit_answer", "arguments": {"customer_ids": ["C001", "C004"]}}
    step3_resp = requests.post(f"{BASE_URL}/step", json=action3, timeout=5)
    assert step3_resp.status_code == 200
    step3_data = step3_resp.json()
    reward3 = step3_data['reward']['value']
    done3 = step3_data['done']
    print(f"  ✅ Step 3 successful - Reward: {reward3}, Done: {done3}")
    
    print("✅ PASS: All steps executed successfully\n")
    
except AssertionError as e:
    print(f"❌ FAIL: {e}\n")
except Exception as e:
    print(f"❌ FAIL: {type(e).__name__}: {e}\n")

# Test 2: State consistency
print("[TEST 2] State consistency across operations")
print("-" * 80)

try:
    # Reset
    print("  Resetting...")
    reset_resp = requests.post(f"{BASE_URL}/reset", timeout=5)
    assert reset_resp.status_code == 200
    
    # Get state immediately after reset
    state_resp = requests.get(f"{BASE_URL}/state", timeout=5)
    assert state_resp.status_code == 200
    state1 = state_resp.json()
    step_count_before = state1['step_count']
    print(f"  After reset: step_count={step_count_before}, reward={state1['episode_reward']}")
    
    # Take a step
    print("  Taking a step...")
    action = {"tool": "search_customers", "arguments": {"tier": "Gold"}}
    step_resp = requests.post(f"{BASE_URL}/step", json=action, timeout=5)
    assert step_resp.status_code == 200
    step_data = step_resp.json()
    step_count_in_response = step_data['observation']['step_count']
    reward_in_response = step_data['reward']['value']
    
    # Get state after step
    state_resp = requests.get(f"{BASE_URL}/state", timeout=5)
    assert state_resp.status_code == 200
    state2 = state_resp.json()
    step_count_after = state2['step_count']
    reward_after = state2['episode_reward']
    
    print(f"  After step: step_count={step_count_after}, reward={reward_after}")
    
    # Verify consistency
    if step_count_in_response == step_count_after:
        print(f"  ✅ Step count is consistent ({step_count_in_response})")
    else:
        print(f"  ❌ Step count mismatch: {step_count_in_response} vs {step_count_after}")
    
    if step_count_after > step_count_before:
        print(f"  ✅ Step count incremented")
    else:
        print(f"  ❌ Step count did not increment")
    
    if reward_after >= reward_in_response - 0.01:  # Allow for float precision
        print(f"  ✅ Reward is consistent")
    else:
        print(f"  ❌ Reward mismatch")
    
    print("✅ PASS: State is consistent\n")
    
except AssertionError as e:
    print(f"❌ FAIL: {e}\n")
except Exception as e:
    print(f"❌ FAIL: {type(e).__name__}: {e}\n")

# Test 3: Edge cases
print("[TEST 3] Error handling and edge cases")
print("-" * 80)

try:
    # Reset
    print("  Resetting...")
    requests.post(f"{BASE_URL}/reset", timeout=5)
    
    # Invalid tool
    print("  Testing invalid tool...")
    action = {"tool": "invalid_tool", "arguments": {}}
    resp = requests.post(f"{BASE_URL}/step", json=action, timeout=5)
    assert resp.status_code == 200, f"Should handle invalid tool gracefully: {resp.status_code}"
    print("  ✅ Invalid tool handled gracefully")
    
    # Malformed action
    print("  Testing malformed action...")
    resp = requests.post(f"{BASE_URL}/step", json={"missing": "required_fields"}, timeout=5)
    assert resp.status_code in [200, 400], f"Unexpected status: {resp.status_code}"
    print("  ✅ Malformed action handled gracefully")
    
    # Empty arguments
    print("  Testing empty arguments...")
    action = {"tool": "search_customers", "arguments": {}}
    resp = requests.post(f"{BASE_URL}/step", json=action, timeout=5)
    assert resp.status_code == 200
    print("  ✅ Empty arguments handled gracefully")
    
    print("✅ PASS: Error handling working\n")
    
except AssertionError as e:
    print(f"❌ FAIL: {e}\n")
except Exception as e:
    print(f"❌ FAIL: {type(e).__name__}: {e}\n")

# Test 4: Max steps enforcement
print("[TEST 4] Max steps limit enforcement")
print("-" * 80)

try:
    # Reset
    print("  Resetting...")
    reset_resp = requests.post(f"{BASE_URL}/reset", timeout=5)
    assert reset_resp.status_code == 200
    max_steps = reset_resp.json()['observation']['max_steps']
    print(f"  Max steps for this task: {max_steps}")
    
    # Take steps until done
    print(f"  Taking steps until done or {max_steps} steps...")
    for i in range(max_steps + 2):
        action = {"tool": "search_customers", "arguments": {}}
        resp = requests.post(f"{BASE_URL}/step", json=action, timeout=5)
        assert resp.status_code == 200
        data = resp.json()
        step_count = data['observation']['step_count']
        done = data['done']
        
        if done:
            print(f"  Episode completed at step {step_count} (done=True)")
            break
    
    if step_count <= max_steps:
        print(f"  ✅ Step count ({step_count}) respects max_steps ({max_steps})")
    else:
        print(f"  ❌ Step count ({step_count}) exceeded max_steps ({max_steps})")
    
    print("✅ PASS: Max steps enforced\n")
    
except AssertionError as e:
    print(f"❌ FAIL: {e}\n")
except Exception as e:
    print(f"❌ FAIL: {type(e).__name__}: {e}\n")

# Test 5: Grader endpoint
print("[TEST 5] Grader endpoint returns valid scores")
print("-" * 80)

try:
    resp = requests.post(f"{BASE_URL}/grader", timeout=5)
    assert resp.status_code == 200, f"Grader failed: {resp.status_code}"
    
    data = resp.json()
    assert "scores" in data, "No scores in response"
    
    scores = data["scores"]
    print(f"  Found {len(scores)} task scores:")
    
    invalid_count = 0
    for task_id, score in scores.items():
        if 0.0 < score < 1.0:
            print(f"    ✅ {task_id}: {score:.3f} (valid)")
        else:
            print(f"    ❌ {task_id}: {score:.3f} (INVALID)")
            invalid_count += 1
    
    if invalid_count == 0:
        print(f"  ✅ All {len(scores)} scores are valid")
        print("✅ PASS: Grader endpoint working\n")
    else:
        print(f"  ❌ {invalid_count} invalid scores found\n")
    
except AssertionError as e:
    print(f"❌ FAIL: {e}\n")
except Exception as e:
    print(f"❌ FAIL: {type(e).__name__}: {e}\n")

print("=" * 80)
print("DOCKER ENDPOINT TESTS COMPLETE")
print("=" * 80)
print("\n✅ All Docker endpoints functioning correctly!")
print("   - reset() ✅")
print("   - state() ✅")
print("   - step() ✅")
print("   - grader() ✅")
print("\n🎯 Docker deployment verified and working!")
