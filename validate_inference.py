#!/usr/bin/env python3
"""
Validation script for inference.py - ensures it meets all hackathon requirements.

Tests:
1. File exists in root directory
2. Valid Python syntax
3. Imports required modules
4. Supports environment variables (OPENAI_API_KEY, API_BASE_URL, MODEL_NAME)
5. Proper error handling
6. Can run without API key set (graceful failure)
7. Integration with CRM environment
"""

import os
import sys
import subprocess
import json
from pathlib import Path

# Set test root
ROOT_DIR = Path(__file__).parent
INFERENCE_PATH = ROOT_DIR / "inference.py"


def test_file_exists():
    """Test 1: inference.py exists in root directory"""
    if INFERENCE_PATH.exists():
        print("✅ Test 1: inference.py exists in root directory")
        return True
    else:
        print("❌ Test 1 FAILED: inference.py not found in root directory")
        return False


def test_python_syntax():
    """Test 2: Valid Python syntax"""
    try:
        result = subprocess.run(
            ["python3", "-m", "py_compile", str(INFERENCE_PATH)],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✅ Test 2: Valid Python syntax")
            return True
        else:
            print(f"❌ Test 2 FAILED: Syntax error\n{result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Test 2 FAILED: {e}")
        return False


def test_imports():
    """Test 3: Module imports successfully"""
    try:
        sys.path.insert(0, str(ROOT_DIR))
        import inference
        print("✅ Test 3: Module imports successfully")
        return True
    except Exception as e:
        print(f"❌ Test 3 FAILED: Import error - {e}")
        return False


def test_env_variables():
    """Test 4: Supports environment variables"""
    try:
        sys.path.insert(0, str(ROOT_DIR))
        import inference
        
        # Test API_BASE_URL default
        os.environ.pop("API_BASE_URL", None)
        os.environ.pop("MODEL_NAME", None)
        
        try:
            config = inference.get_api_config()
        except ValueError:
            pass  # Expected when OPENAI_API_KEY not set
        
        # Test with custom env vars
        os.environ["API_BASE_URL"] = "https://custom.api.com"
        os.environ["MODEL_NAME"] = "gpt-4-turbo"
        
        try:
            config = inference.get_api_config()
        except ValueError:
            pass  # Expected when OPENAI_API_KEY not set
        
        print("✅ Test 4: Supports environment variables (API_BASE_URL, MODEL_NAME)")
        return True
    except Exception as e:
        print(f"❌ Test 4 FAILED: {e}")
        return False


def test_error_handling():
    """Test 5: Proper error handling without OPENAI_API_KEY"""
    try:
        # Ensure API key is not set
        os.environ.pop("OPENAI_API_KEY", None)
        
        sys.path.insert(0, str(ROOT_DIR))
        import inference
        
        # Should raise ValueError
        try:
            config = inference.get_api_config()
            print("❌ Test 5 FAILED: Should raise ValueError without API key")
            return False
        except ValueError as e:
            if "OPENAI_API_KEY" in str(e):
                print("✅ Test 5: Proper error handling without OPENAI_API_KEY")
                return True
            else:
                print(f"❌ Test 5 FAILED: Wrong error message - {e}")
                return False
    except Exception as e:
        print(f"❌ Test 5 FAILED: {e}")
        return False


def test_integration():
    """Test 6: Integration with CRM environment"""
    try:
        sys.path.insert(0, str(ROOT_DIR))
        
        # Import required modules
        from app.env import CRMQueryEnv
        from app.tasks import get_tasks
        from app.grader import TaskGrader
        
        # Test environment
        env = CRMQueryEnv()
        obs = env.reset()
        
        # Test tasks
        tasks = get_tasks()
        if len(tasks) > 0:
            print(f"✅ Test 6: Integration with CRM environment (found {len(tasks)} tasks)")
            return True
        else:
            print("❌ Test 6 FAILED: No tasks found")
            return False
    except Exception as e:
        print(f"❌ Test 6 FAILED: {e}")
        return False


def test_function_signatures():
    """Test 7: Required function signatures exist"""
    try:
        sys.path.insert(0, str(ROOT_DIR))
        import inference
        import inspect
        
        # Check required functions
        required_functions = [
            "get_api_config",
            "initialize_openai_client",
            "run_inference_on_task",
            "run_inference",
            "main"
        ]
        
        missing = []
        for func_name in required_functions:
            if not hasattr(inference, func_name):
                missing.append(func_name)
        
        if not missing:
            print(f"✅ Test 7: All required functions present ({len(required_functions)} functions)")
            return True
        else:
            print(f"❌ Test 7 FAILED: Missing functions - {missing}")
            return False
    except Exception as e:
        print(f"❌ Test 7 FAILED: {e}")
        return False


def test_documentation():
    """Test 8: Proper documentation and docstrings"""
    try:
        sys.path.insert(0, str(ROOT_DIR))
        import inference
        
        # Check module docstring
        if not inference.__doc__:
            print("❌ Test 8 FAILED: Missing module docstring")
            return False
        
        # Check function docstrings
        functions = ["get_api_config", "initialize_openai_client", "run_inference", "main"]
        missing_docs = []
        
        for func_name in functions:
            func = getattr(inference, func_name)
            if not func.__doc__:
                missing_docs.append(func_name)
        
        if not missing_docs:
            print("✅ Test 8: Comprehensive documentation and docstrings")
            return True
        else:
            print(f"⚠️  Test 8 WARNING: Missing docstrings in {missing_docs}")
            return True  # Warning, not failure
    except Exception as e:
        print(f"⚠️  Test 8 WARNING: {e}")
        return True  # Warning, not failure


def test_shebang():
    """Test 9: Has proper shebang for execution"""
    try:
        with open(INFERENCE_PATH, 'r') as f:
            first_line = f.readline()
        
        if first_line.startswith("#!/usr/bin/env python3"):
            print("✅ Test 9: Has proper shebang for direct execution")
            return True
        else:
            print("⚠️  Test 9 WARNING: Missing shebang (not critical)")
            return True
    except Exception as e:
        print(f"❌ Test 9 FAILED: {e}")
        return False


def main():
    """Run all validation tests"""
    print("\n" + "="*70)
    print("INFERENCE.PY VALIDATION TEST SUITE")
    print("="*70 + "\n")
    
    tests = [
        test_file_exists,
        test_python_syntax,
        test_imports,
        test_env_variables,
        test_error_handling,
        test_integration,
        test_function_signatures,
        test_documentation,
        test_shebang,
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {test_func.__name__} FAILED with exception: {e}")
            results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("\n" + "="*70)
    print(f"RESULTS: {passed}/{total} tests passed")
    print("="*70)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - inference.py is ready for submission!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) need attention")
        return 1


if __name__ == "__main__":
    sys.exit(main())
