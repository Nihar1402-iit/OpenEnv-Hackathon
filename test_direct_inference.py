#!/usr/bin/env python3
"""
Test inference.py directly with mocked OpenAI client
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Mock the OpenAI client before importing inference
import unittest.mock as mock

print("=" * 80)
print("TESTING INFERENCE.PY WITH MOCKED OPENAI CLIENT")
print("=" * 80)

# Create a mock OpenAI response
class MockChoice:
    def __init__(self, content):
        self.message = mock.Mock()
        self.message.content = content

class MockCompletion:
    def __init__(self, content):
        self.choices = [MockChoice(content)]

class MockClient:
    def __init__(self, **kwargs):
        self.call_count = 0
    
    def chat(self, *args, **kwargs):
        """Mock chat completions"""
        class Completions:
            def __init__(self, parent):
                self.parent = parent
            
            def create(self, **kwargs):
                self.parent.call_count += 1
                
                # Extract task from messages
                messages = kwargs.get('messages', [])
                task_desc = ""
                for msg in messages:
                    if msg.get('role') == 'user':
                        task_desc = msg.get('content', '')
                        break
                
                # Return appropriate response
                if 'C005' in task_desc:
                    content = '{"tool": "submit_answer", "arguments": {"customer_ids": ["C005"]}}'
                elif 'Gold-tier' in task_desc and 'HIGH priority' in task_desc:
                    content = '{"tool": "submit_answer", "arguments": {"customer_ids": ["C001", "C004", "C006", "C009", "C011", "C014", "C016", "C019"]}}'
                elif 'Gold tier' in task_desc:
                    content = '{"tool": "submit_answer", "arguments": {"customer_ids": ["C001", "C004", "C006", "C009", "C011", "C014", "C016", "C019"]}}'
                else:
                    content = '{"tool": "submit_answer", "arguments": {"customer_ids": []}}'
                
                return MockCompletion(content)
        
        return Completions(self)

# Mock the OpenAI import
with mock.patch('inference.initialize_openai_client') as mock_init:
    mock_init.return_value = MockClient()
    
    # Now import and run inference
    from inference import run_inference
    
    print("\nRunning inference...")
    results = run_inference(verbose=False)
    
    print("\nResults:")
    print(f"  Error: {results.get('error')}")
    print(f"  Average score: {results.get('average_score'):.3f}")
    
    task_scores = results.get('task_scores', {})
    print(f"\nTask scores:")
    for task_id, score in task_scores.items():
        valid = 0.0 < score < 1.0
        status = "✓" if valid else "❌"
        print(f"  {status} {task_id}: {score:.3f}")

print("\n" + "=" * 80)
print("VALIDATION")
print("=" * 80)

if len(task_scores) >= 3:
    print(f"✓ Found {len(task_scores)} tasks (need >= 3)")
else:
    print(f"❌ Found only {len(task_scores)} tasks (need >= 3)")

invalid = [s for s in task_scores.values() if not (0.0 < s < 1.0)]
if not invalid:
    print(f"✓ All scores in valid range (0, 1)")
    print("\n✅ PASS validation")
    sys.exit(0)
else:
    print(f"❌ {len(invalid)} scores out of range:")
    for task_id, score in task_scores.items():
        if not (0.0 < score < 1.0):
            print(f"  - {task_id}: {score}")
    print("\n❌ FAIL validation")
    sys.exit(1)
