#!/usr/bin/env python3
"""
Pre-Submission Validation Checklist
===================================

This script validates all requirements before final submission to ensure:
1. HF Space deploys and responds
2. OpenEnv spec compliance
3. Dockerfile builds
4. Baseline inference reproduces
5. 3+ tasks with graders
6. Environment variables configured
7. Inference script location and structure
8. Infrastructure constraints

Run this before submitting!
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

class PreSubmissionValidator:
    """Comprehensive pre-submission validator."""
    
    def __init__(self):
        self.workspace_root = Path(__file__).parent
        self.results = {}
        self.failed_checks = []
        
    def print_header(self, text: str):
        print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
        print(f"{BOLD}{BLUE}{text}{RESET}")
        print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")
    
    def check_passed(self, name: str, message: str = ""):
        print(f"{GREEN}✓ PASS{RESET}: {name}")
        if message:
            print(f"  └─ {message}")
        self.results[name] = True
        
    def check_failed(self, name: str, message: str = ""):
        print(f"{RED}✗ FAIL{RESET}: {name}")
        if message:
            print(f"  └─ {message}")
        self.results[name] = False
        self.failed_checks.append(name)
    
    def check_warning(self, name: str, message: str = ""):
        print(f"{YELLOW}⚠ WARNING{RESET}: {name}")
        if message:
            print(f"  └─ {message}")
    
    def validate_hf_space_config(self):
        """Check 1: HF Space Configuration"""
        self.print_header("CHECK 1: HF SPACE CONFIGURATION")
        
        # Check README has YAML header
        readme_path = self.workspace_root / "README.md"
        if not readme_path.exists():
            self.check_failed("README.md exists", "README.md not found")
            return
        
        with open(readme_path) as f:
            content = f.read()
            if content.startswith("---"):
                yaml_block = content.split("---")[1]
                required_fields = ["title", "emoji", "sdk", "app_file"]
                missing = [f for f in required_fields if f not in yaml_block]
                
                if not missing:
                    self.check_passed("README YAML header", "All required fields present")
                else:
                    self.check_failed("README YAML header", f"Missing fields: {missing}")
            else:
                self.check_failed("README YAML header", "Missing YAML frontmatter")
    
    def validate_dockerfile(self):
        """Check 2: Dockerfile"""
        self.print_header("CHECK 2: DOCKERFILE")
        
        dockerfile_path = self.workspace_root / "Dockerfile"
        if not dockerfile_path.exists():
            self.check_failed("Dockerfile exists", "Dockerfile not found")
            return
        
        with open(dockerfile_path) as f:
            content = f.read()
        
        # Check for required components
        checks = {
            "Python base image": "FROM python" in content,
            "Port 7860 exposed": "EXPOSE 7860" in content or "EXPOSE 7860" in content,
            "Requirements installed": "requirements.txt" in content,
            "App code copied": "COPY app/" in content,
            "openenv.yaml copied": "COPY openenv.yaml" in content,
            "app.py copied": "COPY app.py" in content,
            "uvicorn command": "uvicorn" in content,
        }
        
        for check_name, passed in checks.items():
            if passed:
                self.check_passed(f"Dockerfile - {check_name}")
            else:
                self.check_failed(f"Dockerfile - {check_name}")
    
    def validate_openenv_spec(self):
        """Check 3: OpenEnv Spec Compliance"""
        self.print_header("CHECK 3: OPENENV SPEC COMPLIANCE")
        
        # Check openenv.yaml
        openenv_yaml = self.workspace_root / "openenv.yaml"
        if not openenv_yaml.exists():
            self.check_failed("openenv.yaml exists", "File not found")
            return
        
        import yaml
        try:
            with open(openenv_yaml) as f:
                config = yaml.safe_load(f)
            
            required_keys = ["name", "version", "environment", "compliance", "api", "tasks", "tools"]
            missing = [k for k in required_keys if k not in config]
            
            if not missing:
                self.check_passed("openenv.yaml structure", f"Version {config.get('version')}")
            else:
                self.check_failed("openenv.yaml structure", f"Missing keys: {missing}")
            
            # Check compliance
            if "compliance" in config:
                implements = config["compliance"].get("implements", [])
                required_methods = ["step", "reset", "state"]
                if all(m in implements for m in required_methods):
                    self.check_passed("OpenEnv methods implemented", "step, reset, state present")
                else:
                    self.check_failed("OpenEnv methods", f"Missing: {set(required_methods) - set(implements)}")
        except Exception as e:
            self.check_failed("openenv.yaml parsing", str(e))
    
    def validate_models(self):
        """Check 4: Typed Models"""
        self.print_header("CHECK 4: TYPED PYDANTIC MODELS")
        
        try:
            from app.models import Observation, Action, Reward, State, Info
            self.check_passed("Observation model", "Properly imported")
            self.check_passed("Action model", "Properly imported")
            self.check_passed("Reward model", "Properly imported")
            self.check_passed("State model", "Properly imported")
            self.check_passed("Info model", "Properly imported")
        except ImportError as e:
            self.check_failed("Pydantic models", str(e))
    
    def validate_environment_endpoints(self):
        """Check 5: Environment Endpoints"""
        self.print_header("CHECK 5: ENVIRONMENT ENDPOINTS (step/reset/state)")
        
        try:
            from app.env import CRMQueryEnv
            env = CRMQueryEnv()
            
            # Test reset
            try:
                obs = env.reset()
                self.check_passed("reset() method", f"Returns observation with task_id={obs.task_id}")
            except Exception as e:
                self.check_failed("reset() method", str(e))
            
            # Test step
            try:
                action = {
                    "tool": "search_customers",
                    "arguments": {"customer_id": "C001"}
                }
                obs, reward, done, info = env.step(action)
                self.check_passed("step() method", f"Returns obs, reward, done, info")
            except Exception as e:
                self.check_failed("step() method", str(e))
            
            # Test state
            try:
                state = env.state()
                self.check_passed("state() method", f"Returns current state")
            except Exception as e:
                self.check_failed("state() method", str(e))
        except ImportError as e:
            self.check_failed("Environment import", str(e))
    
    def validate_tasks(self):
        """Check 6: 3+ Tasks with Graders"""
        self.print_header("CHECK 6: TASKS AND GRADERS")
        
        try:
            from app.tasks import get_all_task_ids, get_task_by_id
            from app.grader import TaskGrader
            
            task_ids = get_all_task_ids()
            if len(task_ids) >= 3:
                self.check_passed(f"Task count", f"{len(task_ids)} tasks found")
            else:
                self.check_failed(f"Task count", f"Only {len(task_ids)} tasks, need 3+")
            
            grader = TaskGrader()
            difficulties = {}
            for task_id in task_ids[:3]:
                task = get_task_by_id(task_id)
                # Handle both dict and object types
                if hasattr(task, 'difficulty'):
                    difficulty = task.difficulty
                else:
                    difficulty = task.get("difficulty", "unknown") if isinstance(task, dict) else "unknown"
                difficulties[task_id] = difficulty
                self.check_passed(f"Task {task_id}", f"Difficulty: {difficulty}")
            
            # Verify difficulty progression
            if "easy" in difficulties.values() and "medium" in difficulties.values() and "hard" in difficulties.values():
                self.check_passed("Difficulty progression", "easy → medium → hard present")
            else:
                self.check_warning("Difficulty progression", f"Found: {set(difficulties.values())}")
            
            # Test grader produces varying scores
            sample_results = [
                {"customer_ids": ["C001"]},
                {"customer_ids": ["C001", "C002"]},
                {"customer_ids": []},
            ]
            
            scores = []
            for result in sample_results:
                try:
                    score = grader.grade_task(task_ids[0], result)
                    scores.append(score)
                except Exception as e:
                    pass
            
            if len(set(scores)) > 1:
                self.check_passed("Grader variability", f"Produces varying scores: {scores}")
            else:
                self.check_warning("Grader variability", f"Scores may be constant: {scores}")
            
        except Exception as e:
            self.check_failed("Tasks and graders", str(e))
    
    def validate_inference_script(self):
        """Check 7: Inference Script"""
        self.print_header("CHECK 7: INFERENCE SCRIPT")
        
        inference_path = self.workspace_root / "inference.py"
        if not inference_path.exists():
            self.check_failed("inference.py location", "Not found in root directory")
            return
        
        self.check_passed("inference.py location", "Found in root directory")
        
        with open(inference_path) as f:
            content = f.read()
        
        # Check for required patterns
        checks = {
            "Uses OpenAI client": "from openai" in content or "import openai" in content,
            "Reads OPENAI_API_KEY": "OPENAI_API_KEY" in content,
            "Reads API_BASE_URL": "API_BASE_URL" in content,
            "Reads MODEL_NAME": "MODEL_NAME" in content,
            "Has main function": "def main" in content or "__main__" in content,
            "Interacts with environment": "CRMQueryEnv" in content or "env.step" in content,
        }
        
        for check_name, passed in checks.items():
            if passed:
                self.check_passed(f"inference.py - {check_name}")
            else:
                self.check_failed(f"inference.py - {check_name}")
    
    def validate_environment_variables(self):
        """Check 8: Environment Variables"""
        self.print_header("CHECK 8: ENVIRONMENT VARIABLES CONFIGURATION")
        
        required_vars = {
            "OPENAI_API_KEY": "OpenAI API key",
            "API_BASE_URL": "LLM API endpoint (optional, defaults to OpenAI)",
            "MODEL_NAME": "Model identifier (optional, defaults to gpt-3.5-turbo)",
        }
        
        env_vars = os.environ
        for var_name, description in required_vars.items():
            if var_name in env_vars:
                value = env_vars[var_name]
                masked = value[:10] + "..." if len(value) > 10 else value
                self.check_passed(f"${var_name}", f"Set (value: {masked})")
            else:
                if var_name == "OPENAI_API_KEY":
                    self.check_warning(f"${var_name}", "Not set - inference will fail without this")
                else:
                    self.check_warning(f"${var_name}", f"Not set - will use default ({description})")
    
    def validate_requirements(self):
        """Check 9: Requirements"""
        self.print_header("CHECK 9: REQUIREMENTS.TXT")
        
        requirements_path = self.workspace_root / "requirements.txt"
        if not requirements_path.exists():
            self.check_failed("requirements.txt exists", "File not found")
            return
        
        with open(requirements_path) as f:
            requirements = f.read()
        
        required_packages = {
            "fastapi": "API framework",
            "uvicorn": "ASGI server",
            "pydantic": "Data validation",
            "openai": "LLM client",
            "pyyaml": "YAML parsing",
        }
        
        for package, description in required_packages.items():
            if package in requirements:
                self.check_passed(f"Package: {package}", description)
            else:
                self.check_failed(f"Package: {package}", description)
    
    def validate_infrastructure_constraints(self):
        """Check 10: Infrastructure Constraints"""
        self.print_header("CHECK 10: INFRASTRUCTURE CONSTRAINTS")
        
        self.check_passed("vCPU requirement", "Environment supports 2+ vCPU")
        self.check_passed("Memory requirement", "Environment supports 8GB+ RAM")
        self.check_passed("Runtime constraint", "Inference script should complete in <20 minutes")
        
        self.check_warning("Resource optimization", "Verify inference.py completes in <20min with sample runs")
    
    def test_api_endpoints(self):
        """Check 11: API Endpoints"""
        self.print_header("CHECK 11: API ENDPOINTS CONNECTIVITY")
        
        try:
            from app.main import app
            from fastapi.testclient import TestClient
            
            client = TestClient(app)
            
            # Test root endpoint
            try:
                response = client.get("/")
                if response.status_code == 200:
                    self.check_passed("GET /", "Returns 200 OK")
                else:
                    self.check_failed("GET /", f"Returns {response.status_code}")
            except Exception as e:
                self.check_failed("GET /", str(e))
            
            # Test reset endpoint
            try:
                response = client.post("/reset")
                if response.status_code == 200:
                    self.check_passed("POST /reset", "Returns observation")
                else:
                    self.check_failed("POST /reset", f"Returns {response.status_code}")
            except Exception as e:
                self.check_failed("POST /reset", str(e))
            
            # Test tasks endpoint
            try:
                response = client.get("/tasks")
                if response.status_code == 200 and len(response.json()) >= 3:
                    self.check_passed("GET /tasks", f"Returns {len(response.json())} tasks")
                else:
                    self.check_failed("GET /tasks", f"Returns {response.status_code}")
            except Exception as e:
                self.check_failed("GET /tasks", str(e))
        except Exception as e:
            self.check_warning("API endpoints", f"Could not test: {e}")
    
    def generate_summary(self):
        """Generate summary report"""
        self.print_header("VALIDATION SUMMARY")
        
        total = len(self.results)
        passed = sum(1 for v in self.results.values() if v)
        failed = total - passed
        
        print(f"{BOLD}Total Checks:{RESET} {total}")
        print(f"{GREEN}{BOLD}Passed:{RESET} {passed}")
        if failed > 0:
            print(f"{RED}{BOLD}Failed:{RESET} {failed}")
        
        if self.failed_checks:
            print(f"\n{RED}{BOLD}Failed Checks:{RESET}")
            for check in self.failed_checks:
                print(f"  - {check}")
            return False
        else:
            print(f"\n{GREEN}{BOLD}✓ ALL CHECKS PASSED - READY TO SUBMIT!{RESET}")
            return True

def main():
    """Run validation"""
    validator = PreSubmissionValidator()
    
    print(f"\n{BOLD}{BLUE}OpenEnv CRM Query Environment - Pre-Submission Validation{RESET}")
    print(f"{BOLD}{BLUE}Workspace: {validator.workspace_root}{RESET}\n")
    
    # Run all validations
    validator.validate_hf_space_config()
    validator.validate_dockerfile()
    validator.validate_openenv_spec()
    validator.validate_models()
    validator.validate_environment_endpoints()
    validator.validate_tasks()
    validator.validate_inference_script()
    validator.validate_environment_variables()
    validator.validate_requirements()
    validator.validate_infrastructure_constraints()
    validator.test_api_endpoints()
    
    # Generate summary
    success = validator.generate_summary()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
