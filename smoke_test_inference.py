#!/usr/bin/env python3
"""
End-to-End Inference Smoke Test

This test validates that:
1. Inference runs without errors
2. Scores are strictly in (0, 1) for all tasks
3. Output format is correct
4. The grading pipeline is properly wired
"""

import sys
import os
import re
from pathlib import Path
from io import StringIO

# Add workspace root to path
sys.path.insert(0, str(Path(__file__).parent))

# Set test API key
os.environ["HF_TOKEN"] = "test-key-for-random-scores"


def run_inference_and_capture_output():
    """Run inference and capture output"""
    from inference import run_inference
    
    print("\n" + "="*70)
    print("RUNNING INFERENCE WITH VERBOSE=FALSE (structured output only)")
    print("="*70 + "\n")
    
    # Capture both stdout and the return value
    results = run_inference(verbose=False)
    
    return results


def parse_and_validate_scores(results):
    """Validate the results from inference"""
    print("\n" + "="*70)
    print("INFERENCE RESULTS VALIDATION")
    print("="*70)
    
    if not results:
        print("❌ No results returned from inference")
        return False
    
    if "error" in results:
        print(f"❌ Inference returned error: {results.get('message')}")
        return False
    
    # Check task scores
    task_scores = results.get("task_scores", {})
    print(f"\nTask Scores ({len(task_scores)} tasks):")
    
    all_valid = True
    for task_id in sorted(task_scores.keys()):
        score = task_scores[task_id]
        
        # Validate score is in (0, 1) exclusive
        valid = 0.0 < score < 1.0
        status = "✅" if valid else "❌"
        
        print(f"  {status} {task_id}: {score:.4f} (valid={valid})")
        
        if not valid:
            print(f"       ERROR: Score must be strictly between 0 and 1, got {score}")
            all_valid = False
    
    # Check average score
    avg_score = results.get("average_score", 0)
    avg_valid = 0.0 < avg_score < 1.0
    status = "✅" if avg_valid else "❌"
    print(f"\n  {status} Average Score: {avg_score:.4f} (valid={avg_valid})")
    
    if not avg_valid:
        print(f"       ERROR: Average score must be strictly between 0 and 1, got {avg_score}")
        all_valid = False
    
    # Validate individual task results have required fields
    print("\nTask Result Structure Validation:")
    task_results = results.get("results", {})
    required_fields = {"score", "steps", "episode_reward", "final_answer"}
    
    for task_id in sorted(task_results.keys()):
        result = task_results[task_id]
        has_all = all(field in result for field in required_fields)
        status = "✅" if has_all else "❌"
        print(f"  {status} {task_id}: has required fields")
        
        if not has_all:
            missing = required_fields - set(result.keys())
            print(f"       Missing: {missing}")
            all_valid = False
        
        # Validate final_answer format
        final_answer = result.get("final_answer", {})
        if not isinstance(final_answer, dict) or "customer_ids" not in final_answer:
            print(f"       ERROR: final_answer must have 'customer_ids' key")
            all_valid = False
    
    print("\n" + "="*70)
    return all_valid


def simulate_platform_output_parsing():
    """Simulate what platform output parser sees"""
    print("\n" + "="*70)
    print("SIMULATING PLATFORM OUTPUT PARSING")
    print("="*70)
    
    from inference import run_inference
    import subprocess
    import json
    
    # Run inference as subprocess to capture actual stdout
    print("\nRunning inference subprocess...\n")
    
    env = os.environ.copy()
    env["HF_TOKEN"] = "test-key-for-random-scores"
    
    try:
        result = subprocess.run(
            [sys.executable, "inference.py"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=120,
            env=env
        )
        
        stdout = result.stdout
        stderr = result.stderr
        returncode = result.returncode
        
        print("=== STDOUT ===")
        print(stdout if stdout else "(empty)")
        print("\n=== STDERR ===")
        print(stderr if stderr else "(empty)")
        print(f"\n=== RETURN CODE ===")
        print(returncode)
        
        # Parse output for structured markers
        print("\n" + "="*70)
        print("PARSING STRUCTURED OUTPUT MARKERS")
        print("="*70)
        
        start_matches = re.findall(r'\[START\](.*)', stdout)
        step_matches = re.findall(r'\[STEP\](.*)', stdout)
        end_matches = re.findall(r'\[END\](.*)', stdout)
        
        print(f"\n✅ Found {len(start_matches)} START markers")
        print(f"✅ Found {len(step_matches)} STEP markers")
        print(f"✅ Found {len(end_matches)} END markers")
        
        # Validate END markers contain scores in (0, 1)
        print("\nValidating END marker scores:")
        score_pattern = r'score=(\d+\.\d+)'
        all_scores_valid = True
        
        for end_line in end_matches:
            score_match = re.search(score_pattern, end_line)
            if score_match:
                score_val = float(score_match.group(1))
                valid = 0.0 < score_val < 1.0
                status = "✅" if valid else "❌"
                print(f"  {status} {end_line.strip()[:60]}... (score={score_val:.4f})")
                if not valid:
                    all_scores_valid = False
            else:
                print(f"  ⚠️  Could not parse score from: {end_line[:60]}...")
        
        if returncode == 0:
            print(f"\n✅ Process exited with code 0 (success)")
            return all_scores_valid
        else:
            print(f"\n❌ Process exited with code {returncode}")
            return False
        
    except subprocess.TimeoutExpired:
        print("❌ Inference subprocess timed out after 120 seconds")
        return False
    except Exception as e:
        print(f"❌ Error running inference subprocess: {e}")
        return False


def main():
    """Run all smoke tests"""
    print("\n")
    print("*" * 70)
    print("END-TO-END INFERENCE SMOKE TEST")
    print("*" * 70)
    
    all_valid = True
    
    # Test 1: Run inference and validate results
    try:
        results = run_inference_and_capture_output()
        if not parse_and_validate_scores(results):
            all_valid = False
    except Exception as e:
        print(f"\n❌ Error running inference: {e}")
        import traceback
        traceback.print_exc()
        all_valid = False
    
    # Test 2: Simulate platform output parsing
    try:
        if not simulate_platform_output_parsing():
            all_valid = False
    except Exception as e:
        print(f"\n❌ Error simulating platform output parsing: {e}")
        import traceback
        traceback.print_exc()
        all_valid = False
    
    print("\n" + "*" * 70)
    if all_valid:
        print("✅ ALL SMOKE TESTS PASSED!")
        print("   Inference is working correctly and graders are properly wired.")
    else:
        print("❌ SOME SMOKE TESTS FAILED!")
        print("   See details above.")
    print("*" * 70 + "\n")
    
    return 0 if all_valid else 1


if __name__ == "__main__":
    sys.exit(main())
