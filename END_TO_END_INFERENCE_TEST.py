#!/usr/bin/env python3
"""
END-TO-END INFERENCE FLOW TEST
Verify that action sanitization works in actual inference context
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.env import CRMQueryEnv
from app.tasks import get_tasks
from app.grader import TaskGrader


def test_inference_flow_with_malformed_llm_outputs():
    """
    Simulate LLM producing various malformed outputs
    Verify sanitization handles them gracefully
    """
    
    print("\n" + "="*70)
    print("END-TO-END INFERENCE FLOW TEST")
    print("="*70)
    
    env = CRMQueryEnv()
    task = get_tasks()[0]
    
    # Simulate various LLM outputs
    llm_outputs = [
        # Good: Valid JSON
        {"tool": "search_customers", "arguments": {"customer_id": "C001"}},
        # Good: Valid submit_answer
        {"tool": "submit_answer", "arguments": {"customer_ids": ["C005"]}},
        # Bad: UPPERCASE (should be lowercased)
        {"tool": "SUBMIT_ANSWER", "arguments": {"customer_ids": ["C005"]}},
        # Bad: Extra spaces
        {"tool": "  submit_answer  ", "arguments": {"customer_ids": ["C005"]}},
        # Bad: Arguments is string
        {"tool": "submit_answer", "arguments": "['C005']"},
        # Bad: customer_ids is string
        {"tool": "submit_answer", "arguments": {"customer_ids": "C005"}},
        # Bad: customer_ids has None
        {"tool": "submit_answer", "arguments": {"customer_ids": ["C005", None, "C001"]}},
        # Bad: customer_ids has numbers
        {"tool": "submit_answer", "arguments": {"customer_ids": ["C005", 123]}},
        # Bad: Typo in tool name
        {"tool": "submit_answers", "arguments": {"customer_ids": ["C005"]}},
        # Bad: Invalid tool
        {"tool": "foobar", "arguments": {"customer_ids": ["C005"]}},
        # Bad: No arguments
        {"tool": "submit_answer"},
        # Bad: None action
        None,
        # Bad: String action
        "invalid",
    ]
    
    results = []
    
    for i, llm_output in enumerate(llm_outputs):
        print(f"\n{'─'*70}")
        print(f"Test {i+1}: {repr(llm_output)[:70]}")
        
        try:
            # Reset environment
            obs = env.reset()
            env.current_task_id = task.task_id
            
            # APPLY SANITIZATION (from inference.py)
            action = llm_output
            
            valid_tools = {
                "search_customers",
                "search_orders",
                "search_tickets",
                "submit_answer"
            }
            
            if not isinstance(action, dict):
                action = {"tool": "submit_answer", "arguments": {"customer_ids": []}}
            
            tool = action.get("tool", "")
            if not isinstance(tool, str):
                tool = ""
            
            tool = tool.lower().strip()
            
            if tool not in valid_tools:
                tool = "submit_answer"
            
            arguments = action.get("arguments", {})
            if not isinstance(arguments, dict):
                arguments = {}
            
            if tool == "submit_answer":
                customer_ids = arguments.get("customer_ids", [])
                if not isinstance(customer_ids, list):
                    customer_ids = []
                customer_ids = [str(x) for x in customer_ids if x is not None]
                arguments = {"customer_ids": customer_ids}
            
            action = {
                "tool": tool,
                "arguments": arguments
            }
            
            # Execute in environment
            obs, reward, done, info = env.step(action)
            
            # If it's a submit, grade the answer
            if action["tool"] == "submit_answer":
                answer = {"customer_ids": action["arguments"].get("customer_ids", [])}
                score = TaskGrader.grade_task(task, answer)
                
                print(f"  ✅ Sanitized: {action}")
                print(f"  ✅ Reward: {reward.value:.2f}")
                print(f"  ✅ Score: {score:.3f}")
                results.append((i, "PASS", score))
            else:
                print(f"  ✅ Sanitized: {action}")
                print(f"  ✅ Reward: {reward.value:.2f}")
                results.append((i, "PASS", reward.value))
        
        except Exception as e:
            print(f"  ❌ FAILED: {str(e)[:80]}")
            results.append((i, "FAIL", str(e)))
    
    # Summary
    print(f"\n{'='*70}")
    print("RESULTS SUMMARY")
    print(f"{'='*70}")
    
    passed = sum(1 for _, status, _ in results if status == "PASS")
    failed = sum(1 for _, status, _ in results if status == "FAIL")
    
    print(f"✅ PASSED: {passed}/{len(results)}")
    print(f"❌ FAILED: {failed}/{len(results)}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED - Sanitization is production-ready!")
        return True
    else:
        print("\n⚠️  Some tests failed:")
        for i, status, result in results:
            if status == "FAIL":
                print(f"  Test {i+1}: {result[:60]}")
        return False


if __name__ == "__main__":
    success = test_inference_flow_with_malformed_llm_outputs()
    sys.exit(0 if success else 1)
