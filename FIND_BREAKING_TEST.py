#!/usr/bin/env python3
"""
AGGRESSIVE TEST HARNESS - Find breaking test cases
Systematically try to break the sanitization logic
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.env import CRMQueryEnv
from app.tasks import get_tasks
from app.grader import TaskGrader

def simulate_inference_action_sanitization(action):
    """Simulate EXACT sanitization from inference.py lines 197-224"""
    
    valid_tools = {
        "search_customers",
        "search_orders",
        "search_tickets",
        "submit_answer"
    }

    # Ensure action is dict
    if not isinstance(action, dict):
        action = {"tool": "submit_answer", "arguments": {"customer_ids": []}}

    # Normalize tool name (lowercase, strip whitespace)
    tool = action.get("tool", "")
    if not isinstance(tool, str):
        tool = ""
    
    tool = tool.lower().strip()

    # Reject invalid tool names - fallback to submit_answer
    if tool not in valid_tools:
        tool = "submit_answer"

    # Normalize arguments to dict
    arguments = action.get("arguments", {})
    if not isinstance(arguments, dict):
        arguments = {}

    # Special handling for submit_answer - ensure customer_ids is valid list
    if tool == "submit_answer":
        customer_ids = arguments.get("customer_ids", [])

        # Convert to list if not already
        if not isinstance(customer_ids, list):
            customer_ids = []

        # Ensure all elements are strings, filter None values
        customer_ids = [str(x) for x in customer_ids if x is not None]

        arguments = {"customer_ids": customer_ids}

    # Build final sanitized action
    action = {
        "tool": tool,
        "arguments": arguments
    }
    
    return action


def test_case(name, action_input):
    """Test a single action input"""
    print(f"\n{'='*70}")
    print(f"TEST: {name}")
    print(f"{'='*70}")
    print(f"Input:  {repr(action_input)}")
    
    try:
        sanitized = simulate_inference_action_sanitization(action_input)
        print(f"Output: {sanitized}")
        
        # Try to execute in env
        env = CRMQueryEnv()
        obs = env.reset()
        
        try:
            obs, reward, done, info = env.step(sanitized)
            print(f"✅ ENV STEP: OK - reward={reward.value:.2f}")
            return True
        except Exception as e:
            print(f"❌ ENV STEP FAILED: {str(e)[:100]}")
            return False
            
    except Exception as e:
        print(f"❌ SANITIZATION FAILED: {str(e)[:100]}")
        return False


def main():
    print("\n" + "="*70)
    print("AGGRESSIVE BREAKING TEST SUITE")
    print("="*70)
    
    passed = 0
    failed = 0
    
    # Category 1: Extreme edge cases
    print("\n\n[CATEGORY 1] EXTREME EDGE CASES")
    
    cases = [
        ("Empty dict", {}),
        ("None", None),
        ("Empty string tool", {"tool": ""}),
        ("Whitespace tool", {"tool": "   "}),
        ("Tool with newlines", {"tool": "submit_answer\n"}),
        ("Tool with tabs", {"tool": "\tsubmit_answer\t"}),
        ("Empty args", {"tool": "submit_answer", "arguments": {}}),
        ("None args", {"tool": "submit_answer", "arguments": None}),
        ("String args", {"tool": "submit_answer", "arguments": "invalid"}),
        ("Int args", {"tool": "submit_answer", "arguments": 123}),
        ("List args", {"tool": "submit_answer", "arguments": []}),
    ]
    
    for name, action in cases:
        if test_case(name, action):
            passed += 1
        else:
            failed += 1
    
    # Category 2: Malformed customer_ids
    print("\n\n[CATEGORY 2] MALFORMED customer_ids")
    
    cases = [
        ("customer_ids=None", {"tool": "submit_answer", "arguments": {"customer_ids": None}}),
        ("customer_ids=string", {"tool": "submit_answer", "arguments": {"customer_ids": "C001"}}),
        ("customer_ids=int", {"tool": "submit_answer", "arguments": {"customer_ids": 123}}),
        ("customer_ids=dict", {"tool": "submit_answer", "arguments": {"customer_ids": {"id": "C001"}}}),
        ("customer_ids=empty string", {"tool": "submit_answer", "arguments": {"customer_ids": ""}}),
        ("customer_ids with None elements", {"tool": "submit_answer", "arguments": {"customer_ids": ["C001", None, "C002"]}}),
        ("customer_ids with numeric", {"tool": "submit_answer", "arguments": {"customer_ids": ["C001", 123, "C002"]}}),
        ("customer_ids with bools", {"tool": "submit_answer", "arguments": {"customer_ids": ["C001", True, False]}}),
    ]
    
    for name, action in cases:
        if test_case(name, action):
            passed += 1
        else:
            failed += 1
    
    # Category 3: Case sensitivity attacks
    print("\n\n[CATEGORY 3] CASE SENSITIVITY ATTACKS")
    
    cases = [
        ("UPPERCASE", {"tool": "SUBMIT_ANSWER", "arguments": {"customer_ids": []}}),
        ("MixedCase", {"tool": "Submit_Answer", "arguments": {"customer_ids": []}}),
        ("snake_case variation", {"tool": "SEARCH_CUSTOMERS", "arguments": {}}),
        ("Extra spaces", {"tool": "  submit_answer  ", "arguments": {"customer_ids": []}}),
    ]
    
    for name, action in cases:
        if test_case(name, action):
            passed += 1
        else:
            failed += 1
    
    # Category 4: Invalid tools that should fallback
    print("\n\n[CATEGORY 4] INVALID TOOLS - SHOULD FALLBACK")
    
    cases = [
        ("Typo: submit_answers", {"tool": "submit_answers", "arguments": {}}),
        ("Typo: submitanswer", {"tool": "submitanswer", "arguments": {}}),
        ("Invalid: get_customers", {"tool": "get_customers", "arguments": {}}),
        ("Gibberish: xyzabc", {"tool": "xyzabc", "arguments": {}}),
        ("SQL injection attempt", {"tool": "submit_answer'; DROP TABLE tasks;--", "arguments": {}}),
    ]
    
    for name, action in cases:
        if test_case(name, action):
            passed += 1
        else:
            failed += 1
    
    # Category 5: Missing required keys
    print("\n\n[CATEGORY 5] MISSING REQUIRED KEYS")
    
    cases = [
        ("No arguments key", {"tool": "submit_answer"}),
        ("No tool key", {"arguments": {"customer_ids": []}}),
        ("No customer_ids key", {"tool": "submit_answer", "arguments": {}}),
        ("Extra keys only", {"extra1": "value1", "extra2": "value2"}),
    ]
    
    for name, action in cases:
        if test_case(name, action):
            passed += 1
        else:
            failed += 1
    
    # Category 6: Type injection attacks
    print("\n\n[CATEGORY 6] TYPE INJECTION ATTACKS")
    
    cases = [
        ("tool is list", {"tool": ["submit_answer"], "arguments": {}}),
        ("tool is dict", {"tool": {"name": "submit_answer"}, "arguments": {}}),
        ("tool is float", {"tool": 3.14, "arguments": {}}),
        ("arguments is list", {"tool": "submit_answer", "arguments": ["C001"]}),
        ("arguments is string", {"tool": "submit_answer", "arguments": "C001"}),
    ]
    
    for name, action in cases:
        if test_case(name, action):
            passed += 1
        else:
            failed += 1
    
    # Category 7: Nested structure attacks
    print("\n\n[CATEGORY 7] NESTED STRUCTURE ATTACKS")
    
    cases = [
        ("Deeply nested", {"tool": "submit_answer", "arguments": {"customer_ids": [[["C001"]]]}}),
        ("customer_ids with nested list", {"tool": "submit_answer", "arguments": {"customer_ids": ["C001", ["C002"], "C003"]}}),
        ("customer_ids with nested dict", {"tool": "submit_answer", "arguments": {"customer_ids": ["C001", {"id": "C002"}, "C003"]}}),
    ]
    
    for name, action in cases:
        if test_case(name, action):
            passed += 1
        else:
            failed += 1
    
    # Category 8: Grader evaluation after sanitization
    print("\n\n[CATEGORY 8] GRADER EVALUATION AFTER SANITIZATION")
    
    try:
        env = CRMQueryEnv()
        obs = env.reset()
        
        # Sanitize and submit various malformed inputs
        malformed_submissions = [
            {"tool": "SUBMIT_ANSWER", "arguments": {"customer_ids": "C001"}},
            {"tool": "submit_answer", "arguments": {"customer_ids": None}},
            {"tool": "submit_answer", "arguments": None},
            {"tool": "submit_answer"},
            None,
            "invalid",
        ]
        
        for i, submission in enumerate(malformed_submissions):
            print(f"\nGrader Test {i+1}: {repr(submission)[:60]}")
            
            try:
                sanitized = simulate_inference_action_sanitization(submission)
                
                # Extract customer_ids and grade
                customer_ids = sanitized.get("arguments", {}).get("customer_ids", [])
                answer = {"customer_ids": customer_ids}
                
                task = get_tasks()[0]
                score = TaskGrader.grade_task(task, answer)
                
                if 0.0 < score < 1.0:
                    print(f"  ✅ Score valid: {score:.3f}")
                    passed += 1
                else:
                    print(f"  ❌ Score invalid: {score:.3f}")
                    failed += 1
                    
            except Exception as e:
                print(f"  ❌ Exception: {str(e)[:50]}")
                failed += 1
    
    except Exception as e:
        print(f"❌ Grader category setup failed: {e}")
    
    # Print summary
    print("\n\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)
    print(f"✅ PASSED: {passed}")
    print(f"❌ FAILED: {failed}")
    print(f"TOTAL:    {passed + failed}")
    print(f"Success Rate: {passed/(passed+failed)*100:.1f}%")
    print("="*70)
    
    if failed > 0:
        print("\n🔴 BREAKING TEST CASE FOUND!")
        sys.exit(1)
    else:
        print("\n✅ ALL TESTS PASSED - No breaking cases found")
        sys.exit(0)


if __name__ == "__main__":
    main()
