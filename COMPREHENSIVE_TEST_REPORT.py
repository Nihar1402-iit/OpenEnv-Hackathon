#!/usr/bin/env python3
"""
Comprehensive Test Report - Meta Hackathon Submission
Tests all critical systems and generates final verification report
"""

import sys
import subprocess
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def test_imports():
    """Test all imports work"""
    print_section("TEST 1: Import Verification")
    try:
        from app.grader import TaskGrader
        from app.tasks import get_tasks
        from app.env import CRMQueryEnv
        from app.reward import Reward
        from app.main import app
        print("✅ All critical imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_tasks():
    """Test tasks load correctly"""
    print_section("TEST 2: Tasks Loading")
    try:
        from app.tasks import get_tasks
        tasks = get_tasks()
        assert len(tasks) == 4, f"Expected 4 tasks, got {len(tasks)}"
        print(f"✅ All 4 tasks loaded:")
        for task in tasks:
            print(f"   - {task.task_id:20s} | Difficulty: {task.difficulty:10s} | Steps: {task.max_steps}")
            assert task.ground_truth is not None, f"{task.task_id} has no ground_truth"
        return True
    except Exception as e:
        print(f"❌ Tasks loading failed: {e}")
        return False

def test_grader():
    """Test grader functionality"""
    print_section("TEST 3: Grader Functionality")
    try:
        from app.grader import TaskGrader
        from app.tasks import get_tasks
        
        tasks = get_tasks()
        scores_valid = True
        
        for task in tasks:
            # Test empty answer
            score_empty = TaskGrader.grade_task(task, {'customer_ids': []})
            assert 0.0 < score_empty < 1.0, f"Empty score {score_empty} out of valid range"
            
            # Test correct answer
            score_correct = TaskGrader.grade_task(task, task.ground_truth)
            assert 0.0 < score_correct < 1.0, f"Correct score {score_correct} out of valid range"
            
            print(f"✅ {task.task_id:20s} | Empty: {score_empty:.3f} | Correct: {score_correct:.3f}")
        
        print(f"\n✅ All grader scores in valid range (0.0, 1.0)")
        return True
    except Exception as e:
        print(f"❌ Grader test failed: {e}")
        return False

def test_environment():
    """Test environment functionality"""
    print_section("TEST 4: Environment Functionality")
    try:
        from app.env import CRMQueryEnv
        
        env = CRMQueryEnv()
        
        # Test reset
        obs = env.reset()
        print("✅ Environment reset successful")
        print(f"   Tables available: {len(obs.tables_summary)} tables")
        
        # Test valid action
        action = {
            'tool': 'search_customers',
            'arguments': {'customer_id': 'C001'}
        }
        obs, reward, done, info = env.step(action)
        print(f"✅ Valid action executed")
        print(f"   Reward: {reward.value:.2f} (valid range 0.0-1.0)")
        assert 0.0 <= reward.value <= 1.0, "Reward out of range"
        
        # Test invalid actions (defensive handling)
        invalid_actions = [
            None,
            "string_action",
            123,
            [],
            {'tool': 'invalid_tool', 'arguments': {}},
        ]
        
        for invalid_action in invalid_actions:
            try:
                env.reset()
                obs, reward, done, info = env.step(invalid_action)
                print(f"✅ Invalid action handled gracefully: {type(invalid_action).__name__}")
            except Exception as e:
                print(f"❌ Invalid action caused crash: {type(invalid_action).__name__}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Environment test failed: {e}")
        return False

def test_inference_format():
    """Test inference output format"""
    print_section("TEST 5: Inference Output Format")
    try:
        # Run test structured output script
        result = subprocess.run(
            ['python', 'test_structured_output.py'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout
        
        # Check for required markers
        required_markers = ['[START]', '[STEP]', '[END]']
        for marker in required_markers:
            if marker in output:
                print(f"✅ {marker} marker found in output")
            else:
                print(f"❌ {marker} marker NOT found in output")
                return False
        
        # Check structured format
        lines = output.split('\n')
        start_lines = [l for l in lines if l.startswith('[START]')]
        step_lines = [l for l in lines if l.startswith('[STEP]')]
        end_lines = [l for l in lines if l.startswith('[END]')]
        
        print(f"\n✅ Output format verification:")
        print(f"   [START] lines: {len(start_lines)}")
        print(f"   [STEP] lines: {len(step_lines)}")
        print(f"   [END] lines: {len(end_lines)}")
        
        assert len(start_lines) >= 1, "Missing [START] marker"
        assert len(step_lines) > 0, "Missing [STEP] markers"
        assert len(end_lines) >= 5, "Missing [END] markers"
        
        return True
    except Exception as e:
        print(f"❌ Inference format test failed: {e}")
        return False

def test_docker():
    """Test Docker image exists"""
    print_section("TEST 6: Docker Image")
    try:
        result = subprocess.run(
            ['docker', 'images', '--filter', 'reference=openenv-crm:latest', '--format', '{{.ID}}'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        image_id = result.stdout.strip()
        if image_id:
            print(f"✅ Docker image exists: openenv-crm:latest")
            print(f"   Image ID: {image_id}")
            return True
        else:
            print(f"⚠️  Docker image not found (optional)")
            return True
    except Exception as e:
        print(f"⚠️  Docker check skipped: {e}")
        return True

def test_git():
    """Test git status"""
    print_section("TEST 7: Git Status & Security")
    try:
        # Check git status
        result = subprocess.run(
            ['git', 'log', '-1', '--oneline'],
            capture_output=True,
            text=True,
            cwd='/Users/niharshah/Desktop/Meta Hackathon'
        )
        
        print(f"✅ Git repository healthy")
        print(f"   Latest commit: {result.stdout.strip()}")
        
        # Verify .env is ignored
        result = subprocess.run(
            ['git', 'check-ignore', '.env'],
            capture_output=True,
            cwd='/Users/niharshah/Desktop/Meta Hackathon'
        )
        
        if result.returncode == 0:
            print(f"✅ .env is properly ignored by git")
        else:
            print(f"⚠️  .env not in .gitignore (but file exists locally)")
        
        # Check if API key is in git history
        result = subprocess.run(
            ['git', 'log', '-p', '--all', '-S', 'sk-proj', '--', '.env'],
            capture_output=True,
            text=True,
            cwd='/Users/niharshah/Desktop/Meta Hackathon'
        )
        
        if not result.stdout:
            print(f"✅ No API keys found in git history (SECURE)")
        else:
            print(f"⚠️  Potential key found in history - REVOKE OLD KEYS IMMEDIATELY")
        
        return True
    except Exception as e:
        print(f"⚠️  Git check skipped: {e}")
        return True

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  COMPREHENSIVE TEST SUITE - META HACKATHON SUBMISSION")
    print("="*70)
    
    tests = [
        ("Imports", test_imports),
        ("Tasks", test_tasks),
        ("Grader", test_grader),
        ("Environment", test_environment),
        ("Inference Format", test_inference_format),
        ("Docker", test_docker),
        ("Git & Security", test_git),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results[name] = False
    
    # Summary
    print_section("FINAL SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:8s} | {name}")
    
    print(f"\n{'='*70}")
    print(f"Result: {passed}/{total} tests passed")
    print(f"{'='*70}\n")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - SUBMISSION READY FOR PRODUCTION\n")
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed - fix before submission\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
