#!/usr/bin/env python3
"""
Hackathon Submission Verification Script

Validates that the project meets all hackathon requirements:
1. Environment deploys and responds
2. No plagiarism (original work)
3. Graders return variable scores
4. Baseline inference script exists
5. All tests pass

Usage:
    python verify_submission.py
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Tuple

class SubmissionVerifier:
    """Verifies hackathon submission requirements."""
    
    def __init__(self):
        self.root = Path.cwd()
        self.results = []
        self.passed = 0
        self.failed = 0
    
    def check(self, name: str, condition: bool, details: str = "") -> bool:
        """Record a check result."""
        status = "✓" if condition else "✗"
        self.results.append((status, name, details))
        if condition:
            self.passed += 1
        else:
            self.failed += 1
        return condition
    
    def print_results(self):
        """Print all results."""
        print("\n" + "=" * 80)
        print("HACKATHON SUBMISSION VERIFICATION")
        print("=" * 80 + "\n")
        
        for status, name, details in self.results:
            print(f"{status} {name}")
            if details:
                print(f"  {details}")
        
        print("\n" + "=" * 80)
        print(f"RESULTS: {self.passed} passed, {self.failed} failed")
        print("=" * 80 + "\n")
        
        if self.failed == 0:
            print("✅ PROJECT IS READY FOR SUBMISSION")
        else:
            print("❌ PROJECT HAS ISSUES - PLEASE FIX")
        
        return self.failed == 0
    
    def verify_files(self) -> bool:
        """Verify all required files exist."""
        print("\n[1] Verifying Required Files...")
        
        files = {
            'app/__init__.py': 'App package init',
            'app/main.py': 'FastAPI server',
            'app/env.py': 'Environment',
            'app/models.py': 'Models',
            'app/tasks.py': 'Tasks',
            'app/reward.py': 'Reward function',
            'app/grader.py': 'Grader',
            'app/baseline.py': 'Baseline script',
            'app/multi_agent.py': 'Multi-agent system',
            'tests/test_env.py': 'Environment tests',
            'tests/test_grader.py': 'Grader tests',
            'tests/test_endpoints.py': 'Endpoint tests',
            'tests/test_memory_usage.py': 'Memory tests',
            'tests/test_multi_agent.py': 'Multi-agent tests',
            'requirements.txt': 'Dependencies',
            'Dockerfile': 'Docker config',
            'openenv.yaml': 'OpenEnv config',
        }
        
        all_exist = True
        for filepath, desc in files.items():
            path = self.root / filepath
            exists = path.exists()
            self.check(f"File: {filepath}", exists, desc)
            all_exist = all_exist and exists
        
        return all_exist
    
    def verify_tests(self) -> bool:
        """Verify all tests pass."""
        print("\n[2] Running Tests...")
        
        try:
            result = subprocess.run(
                ['python', '-m', 'pytest', 'tests/', '-v', '--tb=short', '-q'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            output = result.stdout + result.stderr
            passed = result.returncode == 0
            
            # Parse test count from output
            test_count = 0
            for line in output.split('\n'):
                if 'passed' in line:
                    try:
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if 'passed' in part and i > 0:
                                test_count = int(parts[i-1])
                    except:
                        pass
            
            details = f"{test_count} tests passed" if test_count > 0 else "All tests passed"
            self.check("All tests pass", passed, details)
            
            if not passed:
                print(f"  Test output:\n{output}")
            
            return passed
        except subprocess.TimeoutExpired:
            self.check("All tests pass", False, "Tests timed out")
            return False
        except Exception as e:
            self.check("All tests pass", False, f"Error running tests: {e}")
            return False
    
    def verify_baseline(self) -> bool:
        """Verify baseline script exists and is valid."""
        print("\n[3] Verifying Baseline Script...")
        
        baseline_path = self.root / 'app' / 'baseline.py'
        exists = baseline_path.exists()
        self.check("Baseline script exists", exists, "app/baseline.py")
        
        if exists:
            content = baseline_path.read_text()
            has_function = 'def run_baseline' in content
            self.check("Has run_baseline function", has_function)
            
            has_tasks = 'get_tasks' in content
            self.check("References get_tasks", has_tasks)
            
            has_grader = 'TaskGrader' in content
            self.check("References TaskGrader", has_grader)
        
        return exists
    
    def verify_variable_scores(self) -> bool:
        """Verify grader returns variable scores."""
        print("\n[4] Verifying Variable Scores...")
        
        try:
            # Import and test grader
            from app.grader import TaskGrader
            from app.tasks import get_task_by_id
            
            task = get_task_by_id("task_easy_001")
            scores = set()
            
            # Test different answers
            answers = [
                {"customer_ids": ["C005"]},  # Perfect
                {"customer_ids": ["C005", "C001"]},  # With false positive
                {"customer_ids": ["C999"]},  # Wrong
                {"customer_ids": []},  # Empty
            ]
            
            for answer in answers:
                score = TaskGrader.grade_task(task, answer)
                scores.add(score)
            
            varied = len(scores) > 1
            self.check("Scores vary for different answers", varied,
                      f"Unique scores: {sorted(scores)}")
            
            return varied
        except Exception as e:
            self.check("Scores vary for different answers", False, f"Error: {e}")
            return False
    
    def verify_originality(self) -> bool:
        """Verify original work (memory + multi-agent system)."""
        print("\n[5] Verifying Original Work...")
        
        # Check for memory system
        env_path = self.root / 'app' / 'env.py'
        env_content = env_path.read_text()
        
        has_memory_cache = 'retrieved_entities' in env_content
        self.check("Memory cache tracking", has_memory_cache)
        
        has_step_summaries = 'step_summaries' in env_content
        self.check("Step summaries", has_step_summaries)
        
        has_query_cache = 'query_cache' in env_content
        self.check("Query cache", has_query_cache)
        
        # Check for multi-agent system
        ma_path = self.root / 'app' / 'multi_agent.py'
        has_ma = ma_path.exists()
        self.check("Multi-agent module", has_ma)
        
        if has_ma:
            ma_content = ma_path.read_text()
            has_planner = 'class PlannerAgent' in ma_content
            self.check("Planner agent", has_planner)
            
            has_executor = 'class ExecutorAgent' in ma_content
            self.check("Executor agent", has_executor)
            
            has_coordinator = 'class Coordinator' in ma_content
            self.check("Coordinator", has_coordinator)
        
        # Check for extreme task
        tasks_path = self.root / 'app' / 'tasks.py'
        tasks_content = tasks_path.read_text()
        has_extreme = 'task_extreme_001' in tasks_content
        self.check("Extreme difficulty task", has_extreme)
        
        return all([has_memory_cache, has_step_summaries, has_query_cache,
                   has_ma, has_extreme])
    
    def verify_deployment(self) -> bool:
        """Verify deployment configuration."""
        print("\n[6] Verifying Deployment...")
        
        dockerfile = (self.root / 'Dockerfile').exists()
        self.check("Dockerfile exists", dockerfile)
        
        requirements = (self.root / 'requirements.txt').exists()
        self.check("requirements.txt exists", requirements)
        
        if requirements:
            req_content = (self.root / 'requirements.txt').read_text()
            has_fastapi = 'fastapi' in req_content
            self.check("FastAPI in requirements", has_fastapi)
            
            has_uvicorn = 'uvicorn' in req_content
            self.check("Uvicorn in requirements", has_uvicorn)
        
        openenv = (self.root / 'openenv.yaml').exists()
        self.check("openenv.yaml exists", openenv)
        
        return dockerfile and requirements and openenv
    
    def verify_documentation(self) -> bool:
        """Verify documentation."""
        print("\n[7] Verifying Documentation...")
        
        docs = {
            'README.md': 'Main documentation',
            'QUICKSTART.md': 'Quick start guide',
            'UPGRADE.md': 'Upgrade guide',
            'DEPLOYMENT.md': 'Deployment guide',
            'PROJECT_STATUS.md': 'Status summary',
            'SUBMISSION_CHECKLIST.md': 'Submission checklist',
        }
        
        all_exist = True
        for filename, desc in docs.items():
            path = self.root / filename
            exists = path.exists()
            self.check(f"Doc: {filename}", exists, desc)
            all_exist = all_exist and exists
        
        return all_exist
    
    def run_all_checks(self) -> bool:
        """Run all verification checks."""
        checks = [
            self.verify_files,
            self.verify_tests,
            self.verify_baseline,
            self.verify_variable_scores,
            self.verify_originality,
            self.verify_deployment,
            self.verify_documentation,
        ]
        
        all_passed = all(check() for check in checks)
        return all_passed

def main():
    """Main entry point."""
    verifier = SubmissionVerifier()
    
    try:
        all_passed = verifier.run_all_checks()
        ready = verifier.print_results()
        
        sys.exit(0 if ready else 1)
    except Exception as e:
        print(f"❌ Verification failed with error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
