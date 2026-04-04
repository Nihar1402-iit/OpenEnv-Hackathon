#!/usr/bin/env python3
"""
Final Pre-Submission Validation Script
Mimics the external OpenEnv validator checks
"""

import os
import sys
import subprocess
from pathlib import Path

def check_repo_structure():
    """Check basic repository structure."""
    print("\n📋 REPOSITORY STRUCTURE CHECK")
    print("-" * 70)
    
    workspace = Path("/Users/niharshah/Desktop/Meta Hackathon")
    required_files = [
        "pyproject.toml",
        "setup.py",
        "requirements.txt",
        "Dockerfile",
        "openenv.yaml",
        "app.py",
        "inference.py",
        "README.md",
    ]
    
    required_dirs = [
        "app",
        "server",
        "tests",
    ]
    
    all_good = True
    for file in required_files:
        path = workspace / file
        if path.exists():
            print(f"✓ {file}")
        else:
            print(f"✗ {file} - MISSING")
            all_good = False
    
    for dir_name in required_dirs:
        path = workspace / dir_name
        if path.is_dir():
            print(f"✓ {dir_name}/")
        else:
            print(f"✗ {dir_name}/ - MISSING")
            all_good = False
    
    return all_good

def check_entry_points():
    """Check entry points configuration."""
    print("\n🔧 ENTRY POINTS CHECK")
    print("-" * 70)
    
    workspace = Path("/Users/niharshah/Desktop/Meta Hackathon")
    
    # Check pyproject.toml
    pyproject = workspace / "pyproject.toml"
    content = pyproject.read_text()
    
    checks = [
        ("[project.scripts]" in content, "pyproject.toml [project.scripts]"),
        ("openenv-crm-server" in content, "openenv-crm-server entry point"),
        ("server.app:main" in content, "server.app:main target"),
    ]
    
    all_good = True
    for check, desc in checks:
        if check:
            print(f"✓ {desc}")
        else:
            print(f"✗ {desc} - MISSING")
            all_good = False
    
    # Check setup.py
    setup_py = workspace / "setup.py"
    setup_content = setup_py.read_text()
    
    if "entry_points" in setup_content and "openenv-crm-server" in setup_content:
        print(f"✓ setup.py entry_points")
    else:
        print(f"✗ setup.py entry_points - MISSING")
        all_good = False
    
    # Check egg-info
    egg_info = workspace / "openenv_crm_query.egg-info" / "entry_points.txt"
    if egg_info.exists():
        print(f"✓ egg-info entry_points.txt generated")
    else:
        print(f"✗ egg-info entry_points.txt - NOT GENERATED")
        all_good = False
    
    return all_good

def check_package_installation():
    """Check package can be installed."""
    print("\n📦 PACKAGE INSTALLATION CHECK")
    print("-" * 70)
    
    try:
        result = subprocess.run(
            ["pip", "install", "-e", "/Users/niharshah/Desktop/Meta Hackathon", "--quiet"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✓ Package installation successful")
            
            # Check entry point
            result = subprocess.run(
                ["which", "openenv-crm-server"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print(f"✓ Entry point registered: {result.stdout.strip()}")
                return True
            else:
                print("✗ Entry point not registered")
                return False
        else:
            print(f"✗ Package installation failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Installation check error: {str(e)}")
        return False

def check_dockerfile():
    """Check Dockerfile."""
    print("\n🐳 DOCKERFILE CHECK")
    print("-" * 70)
    
    workspace = Path("/Users/niharshah/Desktop/Meta Hackathon")
    dockerfile = workspace / "Dockerfile"
    
    if not dockerfile.exists():
        print("✗ Dockerfile not found")
        return False
    
    content = dockerfile.read_text()
    
    checks = [
        ("FROM python:3.11" in content, "Python 3.11 image"),
        ("EXPOSE 7860" in content, "Port 7860 exposed"),
        ("HEALTHCHECK" in content, "Health check configured"),
        ("app.main:app" in content, "FastAPI app reference"),
    ]
    
    all_good = True
    for check, desc in checks:
        if check:
            print(f"✓ {desc}")
        else:
            print(f"✗ {desc} - MISSING")
            all_good = False
    
    return all_good

def check_openenv_yaml():
    """Check openenv.yaml."""
    print("\n📄 OPENENV.YAML CHECK")
    print("-" * 70)
    
    workspace = Path("/Users/niharshah/Desktop/Meta Hackathon")
    yaml_file = workspace / "openenv.yaml"
    
    if not yaml_file.exists():
        print("✗ openenv.yaml not found")
        return False
    
    print("✓ openenv.yaml exists")
    
    content = yaml_file.read_text()
    
    checks = [
        ("name:" in content, "Environment name"),
        ("tasks:" in content, "Tasks section"),
        ("ground_truth:" in content, "Ground truth section"),
        ("environment:" in content, "Environment section"),
        ("CRMQueryEnv" in content, "CRMQueryEnv class reference"),
    ]
    
    all_good = True
    for check, desc in checks:
        if check:
            print(f"✓ {desc}")
        else:
            print(f"✗ {desc} - MISSING")
            all_good = False
    
    return all_good

def check_inference_script():
    """Check inference.py."""
    print("\n🤖 INFERENCE.PY CHECK")
    print("-" * 70)
    
    workspace = Path("/Users/niharshah/Desktop/Meta Hackathon")
    inference = workspace / "inference.py"
    
    if not inference.exists():
        print("✗ inference.py not found")
        return False
    
    print("✓ inference.py exists")
    
    content = inference.read_text()
    
    checks = [
        ("CRMQueryEnv" in content, "Imports CRMQueryEnv"),
        ("OpenAI" in content or "openai" in content, "Uses OpenAI API"),
        ("reset()" in content, "Calls reset()"),
        ("step(" in content, "Calls step()"),
    ]
    
    all_good = True
    for check, desc in checks:
        if check:
            print(f"✓ {desc}")
        else:
            print(f"✗ {desc} - MISSING")
            all_good = False
    
    return all_good

def check_environment_functionality():
    """Check environment can be initialized."""
    print("\n⚙️  ENVIRONMENT FUNCTIONALITY CHECK")
    print("-" * 70)
    
    try:
        result = subprocess.run(
            ["python", "-c", """
import sys
sys.path.insert(0, '/Users/niharshah/Desktop/Meta Hackathon')
from app.env import CRMQueryEnv
from app.models import Action

# Test 1: Initialize
env = CRMQueryEnv()
obs = env.reset()
assert obs.task_id, "task_id missing"
print('✓ Environment initialization works')

# Test 2: Step execution
action = Action(tool='search_customers', arguments={'name': 'test'})
obs, reward, done, info = env.step(action)
assert reward.value is not None, "reward missing"
print('✓ Step execution works')

# Test 3: Available tools
assert len(obs.available_tools) > 0, "no tools"
print('✓ Available tools present')

# Test 4: Multiple episodes
env2 = CRMQueryEnv()
for _ in range(3):
    env2.reset()
print('✓ Multiple episodes work')
"""],
            cwd="/Users/niharshah/Desktop/Meta Hackathon",
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line.startswith('✓'):
                    print(line)
            return True
        else:
            print(f"✗ Environment test failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Environment check error: {str(e)}")
        return False

def check_tests():
    """Run all tests."""
    print("\n🧪 UNIT TESTS CHECK")
    print("-" * 70)
    
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/", "-v", "--tb=short", "-q"],
            cwd="/Users/niharshah/Desktop/Meta Hackathon",
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Count passed tests
        if "passed" in result.stdout:
            lines = result.stdout.strip().split('\n')
            summary = [l for l in lines if "passed" in l]
            if summary:
                print(f"✓ {summary[-1]}")
                return "failed" not in result.stdout.lower() or "0 failed" in result.stdout.lower()
        
        return False
    except Exception as e:
        print(f"✗ Test check error: {str(e)}")
        return False

def main():
    """Run all checks."""
    print("\n" + "=" * 70)
    print("FINAL PRE-SUBMISSION VALIDATION")
    print("=" * 70)
    
    results = {
        "Repository Structure": check_repo_structure(),
        "Entry Points": check_entry_points(),
        "Package Installation": check_package_installation(),
        "Dockerfile": check_dockerfile(),
        "OpenEnv YAML": check_openenv_yaml(),
        "Inference Script": check_inference_script(),
        "Environment Functionality": check_environment_functionality(),
        "Unit Tests": check_tests(),
    }
    
    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {check}")
    
    print("\n" + "=" * 70)
    print(f"OVERALL: {passed}/{total} checks passed")
    print("=" * 70)
    
    if passed == total:
        print("\n🎉 ✅ REPOSITORY READY FOR SUBMISSION")
        print("   All checks passed. Ready to submit!")
        return 0
    else:
        print("\n❌ SUBMISSION NOT READY")
        print("   Fix the failing checks above before submitting.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
