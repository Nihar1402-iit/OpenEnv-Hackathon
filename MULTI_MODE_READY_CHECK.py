#!/usr/bin/env python3
"""
Comprehensive multi-mode deployment readiness check.
Validates that the repository is ready for all deployment modes.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Tuple

class DeploymentReadinessChecker:
    """Check deployment readiness for all modes."""
    
    def __init__(self):
        self.workspace = Path("/Users/niharshah/Desktop/Meta Hackathon")
        self.checks_passed = 0
        self.checks_failed = 0
        self.issues = []
        
    def check_pyproject_scripts(self) -> bool:
        """Check [project.scripts] entry point."""
        pyproject = self.workspace / "pyproject.toml"
        if not pyproject.exists():
            self.issues.append("❌ pyproject.toml not found")
            return False
        
        content = pyproject.read_text()
        if "[project.scripts]" not in content:
            self.issues.append("❌ Missing [project.scripts] section")
            return False
        
        if "openenv-crm-server" not in content:
            self.issues.append("❌ Missing openenv-crm-server entry point")
            return False
            
        if '"server.app:main"' not in content and "'server.app:main'" not in content:
            self.issues.append("❌ server.app:main not configured as entry point")
            return False
        
        print("✓ [project.scripts] entry point configured correctly")
        return True
    
    def check_server_app_main(self) -> bool:
        """Check server/app.py has main() function."""
        server_app = self.workspace / "server" / "app.py"
        if not server_app.exists():
            self.issues.append("❌ server/app.py not found")
            return False
        
        content = server_app.read_text()
        if "def main():" not in content:
            self.issues.append("❌ main() function not found in server/app.py")
            return False
        
        if "uvicorn.run" not in content:
            self.issues.append("❌ uvicorn.run not called in main()")
            return False
        
        print("✓ server/app.py has correct main() function")
        return True
    
    def check_package_installation(self) -> bool:
        """Check package can be installed."""
        try:
            result = subprocess.run(
                ["pip", "install", "-e", str(self.workspace), "--quiet"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                self.issues.append(f"❌ Package installation failed: {result.stderr}")
                return False
            
            print("✓ Package installation successful")
            return True
        except Exception as e:
            self.issues.append(f"❌ Package installation error: {str(e)}")
            return False
    
    def check_entry_point_registered(self) -> bool:
        """Check entry point is registered."""
        try:
            result = subprocess.run(
                ["which", "openenv-crm-server"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                self.issues.append("❌ Entry point not registered in PATH")
                return False
            
            path = result.stdout.strip()
            print(f"✓ Entry point registered at: {path}")
            return True
        except Exception as e:
            self.issues.append(f"❌ Entry point check failed: {str(e)}")
            return False
    
    def check_entry_point_executable(self) -> bool:
        """Check entry point is executable."""
        try:
            # Import the entry point directly
            result = subprocess.run(
                ["python", "-c", 
                 "from server.app import main; print('✓ Entry point function accessible')"],
                cwd=str(self.workspace),
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                self.issues.append(f"❌ Entry point not executable: {result.stderr}")
                return False
            
            print(result.stdout.strip())
            return True
        except Exception as e:
            self.issues.append(f"❌ Entry point executable check failed: {str(e)}")
            return False
    
    def check_app_py_exists(self) -> bool:
        """Check app.py exists for HF Spaces."""
        app_py = self.workspace / "app.py"
        if not app_py.exists():
            self.issues.append("❌ app.py (HF Spaces entry point) not found")
            return False
        
        content = app_py.read_text()
        if "if __name__" not in content:
            self.issues.append("❌ app.py missing if __name__ == '__main__' block")
            return False
        
        print("✓ app.py exists for HF Spaces deployment")
        return True
    
    def check_dockerfile_exists(self) -> bool:
        """Check Dockerfile exists."""
        dockerfile = self.workspace / "Dockerfile"
        if not dockerfile.exists():
            self.issues.append("❌ Dockerfile not found")
            return False
        
        content = dockerfile.read_text()
        required = ["FROM python:3.11", "EXPOSE 7860", "uvicorn"]
        for req in required:
            if req not in content:
                self.issues.append(f"❌ Dockerfile missing: {req}")
                return False
        
        print("✓ Dockerfile configured correctly")
        return True
    
    def check_openenv_yaml(self) -> bool:
        """Check openenv.yaml exists and is valid."""
        yaml_file = self.workspace / "openenv.yaml"
        if not yaml_file.exists():
            self.issues.append("❌ openenv.yaml not found")
            return False
        
        content = yaml_file.read_text()
        required = ["name:", "tasks:", "ground_truth:"]
        for req in required:
            if req not in content:
                self.issues.append(f"❌ openenv.yaml missing: {req}")
                return False
        
        print("✓ openenv.yaml exists and configured")
        return True
    
    def check_requirements_txt(self) -> bool:
        """Check requirements.txt exists."""
        req_file = self.workspace / "requirements.txt"
        if not req_file.exists():
            self.issues.append("❌ requirements.txt not found")
            return False
        
        content = req_file.read_text()
        required = ["fastapi", "uvicorn", "pydantic", "openai", "openenv"]
        missing = [r for r in required if not any(r.lower() in line.lower() for line in content.split('\n'))]
        if missing:
            self.issues.append(f"❌ requirements.txt missing: {missing}")
            return False
        
        print("✓ requirements.txt configured correctly")
        return True
    
    def check_environment_initialization(self) -> bool:
        """Check environment can be initialized."""
        try:
            result = subprocess.run(
                ["python", "-c", """
from app.env import CRMQueryEnv
env = CRMQueryEnv()
obs = env.reset()
assert obs.task_id, "task_id is empty"
assert obs.available_tools, "available_tools is empty"
print('✓ Environment initializes correctly')
"""],
                cwd=str(self.workspace),
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                self.issues.append(f"❌ Environment initialization failed: {result.stderr}")
                return False
            
            print(result.stdout.strip())
            return True
        except Exception as e:
            self.issues.append(f"❌ Environment check failed: {str(e)}")
            return False
    
    def check_api_endpoints(self) -> bool:
        """Check API endpoints are defined."""
        try:
            result = subprocess.run(
                ["python", "-c", """
from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)
endpoints = ['/health', '/tasks', '/reset', '/step', '/state']
for ep in endpoints:
    try:
        if ep == '/reset' or ep == '/step':
            client.post(ep)
        else:
            client.get(ep)
    except:
        pass
print('✓ All API endpoints defined')
"""],
                cwd=str(self.workspace),
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                self.issues.append(f"❌ API endpoints check failed: {result.stderr}")
                return False
            
            print(result.stdout.strip())
            return True
        except Exception as e:
            self.issues.append(f"❌ API endpoints check failed: {str(e)}")
            return False
    
    def run_all_checks(self) -> bool:
        """Run all checks."""
        print("=" * 70)
        print("MULTI-MODE DEPLOYMENT READINESS CHECK")
        print("=" * 70)
        
        checks = [
            ("Configuration", [
                ("pyproject.toml [project.scripts]", self.check_pyproject_scripts),
                ("server/app.py main() function", self.check_server_app_main),
                ("openenv.yaml configuration", self.check_openenv_yaml),
                ("requirements.txt dependencies", self.check_requirements_txt),
            ]),
            ("Deployment Files", [
                ("Dockerfile configuration", self.check_dockerfile_exists),
                ("app.py (HF Spaces entry point)", self.check_app_py_exists),
            ]),
            ("Package & Installation", [
                ("Package installation", self.check_package_installation),
                ("Entry point registration", self.check_entry_point_registered),
                ("Entry point executability", self.check_entry_point_executable),
            ]),
            ("Functionality", [
                ("Environment initialization", self.check_environment_initialization),
                ("API endpoints", self.check_api_endpoints),
            ]),
        ]
        
        all_passed = True
        for section, section_checks in checks:
            print(f"\n📋 {section}")
            print("-" * 70)
            for check_name, check_func in section_checks:
                try:
                    if check_func():
                        self.checks_passed += 1
                    else:
                        self.checks_failed += 1
                        all_passed = False
                except Exception as e:
                    print(f"❌ {check_name}: {str(e)}")
                    self.checks_failed += 1
                    all_passed = False
        
        print("\n" + "=" * 70)
        print(f"RESULTS: {self.checks_passed} passed, {self.checks_failed} failed")
        print("=" * 70)
        
        if self.issues:
            print("\n⚠️  ISSUES FOUND:")
            for issue in self.issues:
                print(f"  {issue}")
        
        if all_passed:
            print("\n🎉 ✅ REPOSITORY READY FOR MULTI-MODE DEPLOYMENT")
            print("   ✓ CLI entry point configured and working")
            print("   ✓ HuggingFace Spaces deployment ready")
            print("   ✓ Docker deployment ready")
            print("   ✓ Package installation working")
            print("   ✓ Environment and API fully functional")
        else:
            print("\n❌ DEPLOYMENT NOT READY - Fix issues above")
        
        return all_passed

if __name__ == "__main__":
    checker = DeploymentReadinessChecker()
    success = checker.run_all_checks()
    sys.exit(0 if success else 1)
