#!/usr/bin/env python3
"""
Deployment Readiness Test Script
Tests all endpoints locally before deploying to HF Spaces
"""

import json
import sys
from fastapi.testclient import TestClient
from app.main import app

def test_deployment():
    """Run all deployment readiness tests"""
    client = TestClient(app)
    tests_passed = 0
    tests_failed = 0
    
    print("\n" + "="*70)
    print("🚀 DEPLOYMENT READINESS TEST SUITE")
    print("="*70 + "\n")
    
    # Test 1: Health Check
    print("Test 1: Health Check (/health)")
    try:
        response = client.get("/health")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "status" in data, "Missing 'status' field"
        assert data["status"] == "healthy", f"Status should be 'healthy', got {data['status']}"
        print("  ✅ PASS - Health check returns 200 with status=healthy\n")
        tests_passed += 1
    except Exception as e:
        print(f"  ❌ FAIL - {str(e)}\n")
        tests_failed += 1
    
    # Test 2: Get Tasks
    print("Test 2: Get Tasks (/tasks)")
    try:
        response = client.get("/tasks")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "tasks" in data, "Missing 'tasks' field"
        tasks = data["tasks"]
        assert isinstance(tasks, list), "Tasks should be a list"
        assert len(tasks) >= 4, f"Expected at least 4 tasks, got {len(tasks)}"
        print(f"  ✅ PASS - Retrieved {len(tasks)} tasks\n")
        tests_passed += 1
    except Exception as e:
        print(f"  ❌ FAIL - {str(e)}\n")
        tests_failed += 1
    
    # Test 3: Reset Environment
    print("Test 3: Reset Environment (/reset)")
    try:
        response = client.post("/reset")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "observation" in data, "Missing 'observation' in response"
        obs = data["observation"]
        assert "task_id" in obs, "Missing task_id in observation"
        assert "step_count" in obs, "Missing step_count in observation"
        assert obs["step_count"] == 0, "Step count should be 0 after reset"
        assert "available_tools" in obs, "Missing available_tools in observation"
        assert "done" in obs, "Missing done in observation"
        print(f"  ✅ PASS - Reset returned valid observation for task: {obs['task_id']}\n")
        tests_passed += 1
    except Exception as e:
        print(f"  ❌ FAIL - {str(e)}\n")
        tests_failed += 1
    
    # Test 4: Step Environment (Valid Action)
    print("Test 4: Step Environment with Valid Action")
    try:
        # First reset
        client.post("/reset")
        
        # Then step
        response = client.post("/step", json={
            "tool": "search_customers",
            "arguments": {"tier": "Gold"}
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "observation" in data, "Missing observation in response"
        assert "reward" in data, "Missing reward in response"
        assert "done" in data, "Missing done in response"
        assert "info" in data, "Missing info in response"
        
        obs = data["observation"]
        assert obs["step_count"] == 1, "Step count should be 1"
        
        print(f"  ✅ PASS - Step executed successfully, reward: {data['reward']}\n")
        tests_passed += 1
    except Exception as e:
        print(f"  ❌ FAIL - {str(e)}\n")
        tests_failed += 1
    
    # Test 5: Get State
    print("Test 5: Get State (/state)")
    try:
        response = client.get("/state")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        state = response.json()
        assert "observation" in state or "task_id" in state, "Missing task info in state"
        # Check if wrapped or direct
        if "observation" in state:
            obs = state["observation"]
        else:
            obs = state
        step_count = obs.get("step_count", 0)
        print(f"  ✅ PASS - State returned with current step_count: {step_count}\n")
        tests_passed += 1
    except Exception as e:
        print(f"  ❌ FAIL - {str(e)}\n")
        tests_failed += 1
    
    # Test 6: Grade Answer
    print("Test 6: Grade Answer (/grader)")
    try:
        # First reset to get task_id
        reset_resp = client.post("/reset")
        assert reset_resp.status_code == 200
        
        # Step to submit answer
        step_resp = client.post("/step", json={
            "tool": "submit_answer",
            "arguments": {"customer_ids": ["C001", "C004"]}
        })
        assert step_resp.status_code == 200
        
        # Now grade
        response = client.post("/grader")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "score" in data, "Missing score"
        score = data["score"]
        assert isinstance(score, (int, float)), f"Score should be numeric, got {type(score)}"
        assert 0.0 <= score <= 1.0, f"Score should be 0.0-1.0, got {score}"
        print(f"  ✅ PASS - Grading returned score: {score}\n")
        tests_passed += 1
    except Exception as e:
        print(f"  ❌ FAIL - {str(e)}\n")
        tests_failed += 1
    
    # Test 7: Step with Invalid Action
    print("Test 7: Step with Invalid Action (Error Handling)")
    try:
        client.post("/reset")
        response = client.post("/step", json={
            "tool": "invalid_tool",
            "arguments": {}
        })
        # Should still return 200 but with error info
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        # Check that environment properly handled the error
        assert "observation" in data or "error" in str(data).lower(), "Should have observation or error"
        print(f"  ✅ PASS - Invalid action handled gracefully\n")
        tests_passed += 1
    except Exception as e:
        print(f"  ❌ FAIL - {str(e)}\n")
        tests_failed += 1
    
    # Test 8: Full Episode
    print("Test 8: Full Episode (Reset → Step → Grade → Submit)")
    try:
        # Reset
        reset_response = client.post("/reset")
        assert reset_response.status_code == 200
        
        # Multiple steps
        for i in range(2):
            step_response = client.post("/step", json={
                "tool": "search_customers",
                "arguments": {"tier": "Gold"} if i == 0 else {"customer_id": "C001"}
            })
            assert step_response.status_code == 200
            data = step_response.json()
            assert "observation" in data, "Missing observation in step response"
            assert "reward" in data, "Missing reward in step response"
        
        # Submit answer
        submit_response = client.post("/step", json={
            "tool": "submit_answer",
            "arguments": {"customer_ids": ["C001", "C004"]}
        })
        assert submit_response.status_code == 200
        
        # Grade
        grade_response = client.post("/grader")
        assert grade_response.status_code == 200
        grading_data = grade_response.json()
        assert "score" in grading_data
        assert 0.0 <= grading_data["score"] <= 1.0
        
        print(f"  ✅ PASS - Full episode executed successfully (score: {grading_data['score']})\n")
        tests_passed += 1
    except Exception as e:
        print(f"  ❌ FAIL - {str(e)}\n")
        tests_failed += 1
    
    # Print Summary
    print("="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    print(f"Tests Passed: {tests_passed}")
    print(f"Tests Failed: {tests_failed}")
    print(f"Total Tests: {tests_passed + tests_failed}")
    print(f"Success Rate: {100 * tests_passed / (tests_passed + tests_failed):.1f}%")
    print("="*70 + "\n")
    
    if tests_failed == 0:
        print("✅ ALL TESTS PASSED - READY FOR DEPLOYMENT ON HF SPACES\n")
        return 0
    else:
        print(f"❌ {tests_failed} TEST(S) FAILED - FIX BEFORE DEPLOYMENT\n")
        return 1

if __name__ == "__main__":
    sys.exit(test_deployment())
