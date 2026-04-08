#!/usr/bin/env python3
"""
Comprehensive Docker & API validation test suite.
Tests every possible test case including:
- Score range validation (0, 1) exclusive
- All 4 tasks with graders
- Health check endpoint
- Grader endpoint with various inputs
- Edge cases and error conditions
"""

import subprocess
import time
import requests
import json
import sys
from typing import Dict, Any, List

# Docker configuration
DOCKER_IMAGE = "openenv-crm:latest"
CONTAINER_NAME = "openenv-test-" + str(int(time.time()))
PORT = 8860  # Use different port to avoid conflicts
BASE_URL = f"http://localhost:{PORT}"

class DockerTestSuite:
    def __init__(self):
        self.container_id = None
        self.passed = 0
        self.failed = 0
        self.results = []

    def log(self, message: str, status: str = "INFO"):
        """Log with status prefix."""
        print(f"[{status}] {message}", flush=True)

    def start_container(self) -> bool:
        """Start Docker container."""
        self.log("Starting Docker container...", "INFO")
        try:
            result = subprocess.run(
                [
                    "docker", "run", "-d",
                    "--name", CONTAINER_NAME,
                    "-p", f"{PORT}:7860",
                    DOCKER_IMAGE
                ],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                self.log(f"Failed to start container: {result.stderr}", "ERROR")
                return False
            
            self.container_id = result.stdout.strip()
            self.log(f"Container started: {self.container_id[:12]}", "SUCCESS")
            
            # Wait for container to be ready
            time.sleep(5)
            return True
        except Exception as e:
            self.log(f"Exception starting container: {str(e)}", "ERROR")
            return False

    def stop_container(self) -> None:
        """Stop Docker container."""
        if self.container_id:
            self.log("Stopping Docker container...", "INFO")
            try:
                subprocess.run(
                    ["docker", "stop", CONTAINER_NAME],
                    capture_output=True,
                    timeout=10
                )
                subprocess.run(
                    ["docker", "rm", CONTAINER_NAME],
                    capture_output=True,
                    timeout=10
                )
                self.log("Container stopped", "SUCCESS")
            except Exception as e:
                self.log(f"Error stopping container: {str(e)}", "WARNING")

    def test_health_check(self) -> bool:
        """Test health check endpoint."""
        self.log("Testing health check endpoint...", "INFO")
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                self.log("✅ Health check passed", "SUCCESS")
                self.passed += 1
                return True
            else:
                self.log(f"❌ Health check failed: {response.status_code}", "ERROR")
                self.failed += 1
                return False
        except Exception as e:
            self.log(f"❌ Health check error: {str(e)}", "ERROR")
            self.failed += 1
            return False

    def test_grader_endpoint(self, test_cases: List[Dict[str, Any]]) -> None:
        """Test grader endpoint with various inputs."""
        self.log("Testing /grader endpoint with various inputs...", "INFO")
        
        for i, test_case in enumerate(test_cases, 1):
            payload = test_case.get("payload", {})
            description = test_case.get("description", f"Test case {i}")
            
            try:
                response = requests.post(
                    f"{BASE_URL}/grader",
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    scores_dict = data.get("scores", {})
                    
                    # Validate response structure
                    if not isinstance(scores_dict, dict):
                        self.log(f"❌ {description}: Invalid response structure", "ERROR")
                        self.failed += 1
                        continue
                    
                    if len(scores_dict) != 4:
                        self.log(f"❌ {description}: Expected 4 tasks, got {len(scores_dict)}", "ERROR")
                        self.failed += 1
                        continue
                    
                    # Validate each task score
                    all_valid = True
                    scores = []
                    for task_id, score in scores_dict.items():
                        # Validate score is in (0, 1) exclusive
                        if not isinstance(score, (int, float)):
                            self.log(f"  ❌ {task_id}: Score is not numeric: {score}", "ERROR")
                            all_valid = False
                            continue
                        
                        if not (0.0 < score < 1.0):
                            self.log(f"  ❌ {task_id}: Score out of range: {score} (must be > 0 and < 1)", "ERROR")
                            all_valid = False
                            continue
                        
                        scores.append(score)
                        self.log(f"  ✅ {task_id}: score={score:.4f}", "SUCCESS")
                    
                    if all_valid and len(scores) == 4:
                        self.log(f"✅ {description}: All 4 tasks valid with scores in (0, 1)", "SUCCESS")
                        self.passed += 1
                        self.results.append({
                            "test": description,
                            "scores": scores,
                            "average": sum(scores) / len(scores)
                        })
                    else:
                        self.failed += 1
                else:
                    self.log(f"❌ {description}: HTTP {response.status_code}", "ERROR")
                    self.failed += 1
                    
            except Exception as e:
                self.log(f"❌ {description}: {str(e)}", "ERROR")
                self.failed += 1

    def run_all_tests(self) -> bool:
        """Run complete test suite."""
        self.log("="*60, "INFO")
        self.log("COMPREHENSIVE DOCKER & API TEST SUITE", "INFO")
        self.log("="*60, "INFO")
        
        # Start container
        if not self.start_container():
            return False
        
        try:
            # Test 1: Health check
            self.test_health_check()
            
            # Test 2: Grader endpoint with various inputs
            test_cases = [
                {
                    "description": "Empty payload",
                    "payload": {}
                },
                {
                    "description": "Empty customer_ids list",
                    "payload": {"customer_ids": []}
                },
                {
                    "description": "Valid customer_ids",
                    "payload": {"customer_ids": ["C001", "C002"]}
                },
                {
                    "description": "Invalid customer_ids (strings)",
                    "payload": {"customer_ids": ["X1", "X2"]}
                },
                {
                    "description": "Mixed valid/invalid",
                    "payload": {"customer_ids": ["C001", "X999"]}
                },
                {
                    "description": "Numeric customer_ids",
                    "payload": {"customer_ids": [1, 2, 3]}
                },
                {
                    "description": "None values in list",
                    "payload": {"customer_ids": ["C001", None, "C002"]}
                },
                {
                    "description": "Task ID parameter",
                    "payload": {"task_id": "task_easy_001"}
                },
            ]
            
            self.test_grader_endpoint(test_cases)
            
        finally:
            self.stop_container()
        
        # Print summary
        self.print_summary()
        return self.failed == 0

    def print_summary(self) -> None:
        """Print test summary."""
        self.log("="*60, "INFO")
        self.log("TEST SUMMARY", "INFO")
        self.log("="*60, "INFO")
        self.log(f"Total Passed: {self.passed}", "SUCCESS")
        self.log(f"Total Failed: {self.failed}", "ERROR" if self.failed > 0 else "SUCCESS")
        self.log(f"Pass Rate: {self.passed / (self.passed + self.failed) * 100:.1f}%", "INFO")
        
        self.log("\nScore Analysis:", "INFO")
        for result in self.results:
            self.log(f"  {result['test']}: avg={result['average']:.4f}", "INFO")
        
        if self.results:
            all_scores = []
            for result in self.results:
                all_scores.extend(result['scores'])
            
            self.log(f"\nOverall Statistics:", "INFO")
            self.log(f"  Min score: {min(all_scores):.4f}", "INFO")
            self.log(f"  Max score: {max(all_scores):.4f}", "INFO")
            self.log(f"  Avg score: {sum(all_scores) / len(all_scores):.4f}", "INFO")
            self.log(f"  All scores in (0, 1): {all(0 < s < 1 for s in all_scores)}", "SUCCESS")

if __name__ == "__main__":
    suite = DockerTestSuite()
    success = suite.run_all_tests()
    sys.exit(0 if success else 1)
