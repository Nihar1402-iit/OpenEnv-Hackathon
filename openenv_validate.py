#!/usr/bin/env python3
"""
OpenEnv Validation Script
Validates openenv.yaml and environment compliance
"""

import sys
import yaml
from pathlib import Path
from openenv.env import Env

def validate_openenv():
    """Validate openenv.yaml compliance"""
    
    print("\n" + "="*80)
    print("🔍 OPENENV VALIDATION")
    print("="*80)
    
    # Load openenv.yaml
    yaml_path = Path(__file__).parent / "openenv.yaml"
    
    if not yaml_path.exists():
        print(f"✗ FAIL: openenv.yaml not found at {yaml_path}")
        return False
    
    print(f"\n✓ Found openenv.yaml")
    
    try:
        with open(yaml_path, 'r') as f:
            spec = yaml.safe_load(f)
        print("✓ YAML syntax is valid")
    except yaml.YAMLError as e:
        print(f"✗ FAIL: Invalid YAML: {e}")
        return False
    
    # Validate required fields
    required_fields = [
        'name',
        'version',
        'description',
        'environment',
        'compliance',
        'api',
        'tasks',
        'tools'
    ]
    
    print("\n" + "-"*80)
    print("Checking required fields:")
    
    missing_fields = []
    for field in required_fields:
        if field in spec:
            print(f"  ✓ {field}")
        else:
            print(f"  ✗ {field} MISSING")
            missing_fields.append(field)
    
    if missing_fields:
        print(f"\n✗ FAIL: Missing required fields: {missing_fields}")
        return False
    
    # Validate compliance section
    print("\n" + "-"*80)
    print("Checking compliance section:")
    
    compliance = spec.get('compliance', {})
    required_methods = ['step', 'reset', 'state']
    implements = compliance.get('implements', [])
    
    for method in required_methods:
        if method in implements:
            print(f"  ✓ Implements: {method}")
        else:
            print(f"  ✗ Missing method: {method}")
            return False
    
    # Validate API section
    print("\n" + "-"*80)
    print("Checking API types:")
    
    api = spec.get('api', {})
    required_types = ['observation', 'action', 'reward', 'state', 'info']
    
    for api_type in required_types:
        if api_type in api:
            type_def = api[api_type]
            if 'type' in type_def and 'properties' in type_def:
                print(f"  ✓ {api_type}")
            else:
                print(f"  ✗ {api_type} missing type or properties")
                return False
        else:
            print(f"  ✗ {api_type} MISSING")
            return False
    
    # Validate tasks
    print("\n" + "-"*80)
    print("Checking tasks:")
    
    tasks = spec.get('tasks', [])
    if len(tasks) < 3:
        print(f"  ✗ FAIL: Need at least 3 tasks, found {len(tasks)}")
        return False
    
    for task in tasks:
        task_id = task.get('task_id', 'unknown')
        difficulty = task.get('difficulty', 'unknown')
        has_ground_truth = 'ground_truth' in task
        
        status = "✓" if has_ground_truth else "✗"
        print(f"  {status} {task_id} ({difficulty})" + (" - has ground truth" if has_ground_truth else " - MISSING ground truth"))
    
    # Validate tools
    print("\n" + "-"*80)
    print("Checking tools:")
    
    tools = spec.get('tools', {})
    if not tools:
        print("  ✗ FAIL: No tools defined")
        return False
    
    for tool_name, tool_def in tools.items():
        has_description = 'description' in tool_def
        has_parameters = 'parameters' in tool_def
        
        status = "✓" if (has_description and has_parameters) else "✗"
        print(f"  {status} {tool_name}")
        if not has_description:
            print(f"      - Missing description")
        if not has_parameters:
            print(f"      - Missing parameters")
    
    # Try to instantiate environment with openenv
    print("\n" + "-"*80)
    print("Testing environment instantiation:")
    
    try:
        env = Env(spec)
        print("  ✓ Environment instantiated successfully")
    except Exception as e:
        print(f"  ✗ FAIL: Could not instantiate environment: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Validate reward shaping
    print("\n" + "-"*80)
    print("Checking reward shaping:")
    
    reward_shaping = spec.get('reward_shaping', {})
    if not reward_shaping:
        print("  ✗ FAIL: No reward shaping defined")
        return False
    
    print(f"  ✓ Found {len(reward_shaping)} reward components:")
    for component, value in reward_shaping.items():
        print(f"      - {component}: {value}")
    
    # Validate grading
    print("\n" + "-"*80)
    print("Checking grading configuration:")
    
    grading = spec.get('grading', {})
    if not grading:
        print("  ✗ FAIL: No grading configuration")
        return False
    
    metric = grading.get('metric')
    formula = grading.get('formula')
    scale = grading.get('scale', [])
    
    print(f"  ✓ Metric: {metric}")
    print(f"  ✓ Formula: {formula}")
    print(f"  ✓ Scale: {scale}")
    
    if scale != [0.0, 1.0]:
        print(f"  ⚠ Warning: Scale should be [0.0, 1.0], found {scale}")
    
    print("\n" + "="*80)
    print("✅ OPENENV VALIDATION PASSED")
    print("="*80)
    
    return True

if __name__ == "__main__":
    success = validate_openenv()
    sys.exit(0 if success else 1)
