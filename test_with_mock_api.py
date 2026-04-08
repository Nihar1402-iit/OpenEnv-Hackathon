#!/usr/bin/env python3
"""
Mock OpenAI API server for testing inference.py
"""
import json
import random
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

class MockOpenAIHandler(BaseHTTPRequestHandler):
    """Mock OpenAI API handler"""
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == "/v1/chat/completions":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            try:
                request = json.loads(body)
            except:
                self.send_response(400)
                self.end_headers()
                return
            
            # Extract messages to determine what task we're on
            messages = request.get('messages', [])
            
            # Check if this is a task description (in user message)
            task_id = None
            for msg in messages:
                if msg.get('role') == 'user' and 'Task:' in msg.get('content', ''):
                    if 'C005' in msg.get('content', ''):
                        task_id = 'task_easy_001'
                    elif 'Gold tier' in msg.get('content', '') and 'HIGH priority' in msg.get('content', ''):
                        task_id = 'task_hard_001'
                    elif 'Gold tier' in msg.get('content', ''):
                        task_id = 'task_medium_001'
                    elif 'previous' in msg.get('content', '').lower():
                        task_id = 'task_extreme_001'
                    break
            
            # Generate a response based on task
            if task_id == 'task_easy_001':
                # Return correct answer for easy task
                response_content = json.dumps({
                    "tool": "submit_answer",
                    "arguments": {"customer_ids": ["C005"]}
                })
            elif task_id == 'task_medium_001':
                # Return some correct answers for medium task (50%)
                response_content = json.dumps({
                    "tool": "submit_answer",
                    "arguments": {"customer_ids": ["C001", "C004", "C006", "C009"]}
                })
            elif task_id == 'task_hard_001':
                # Return some correct answers for hard task (50%)
                response_content = json.dumps({
                    "tool": "submit_answer",
                    "arguments": {"customer_ids": ["C001", "C004", "C006", "C009"]}
                })
            else:
                # Default to empty answer
                response_content = json.dumps({
                    "tool": "submit_answer",
                    "arguments": {"customer_ids": []}
                })
            
            # Build response
            response = {
                "id": "chatcmpl-test",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": request.get('model', 'gpt-3.5-turbo'),
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_content
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": 100,
                    "completion_tokens": 50,
                    "total_tokens": 150
                }
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress logging"""
        pass


def run_mock_server(port=8888):
    """Run mock server in background"""
    server = HTTPServer(('localhost', port), MockOpenAIHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"✓ Mock OpenAI server started on port {port}")
    return server


if __name__ == "__main__":
    import os
    import subprocess
    import sys
    
    # Start mock server
    server = run_mock_server(port=8888)
    time.sleep(1)
    
    # Set environment to use mock API
    env = os.environ.copy()
    env['HF_TOKEN'] = 'test-key'
    env['OPENAI_API_KEY'] = 'test-key'
    env['API_BASE_URL'] = 'http://localhost:8888/v1'
    env['MODEL_NAME'] = 'gpt-3.5-turbo'
    
    print("\n" + "=" * 80)
    print("RUNNING INFERENCE.PY WITH MOCK API")
    print("=" * 80)
    print(f"API_BASE_URL: {env['API_BASE_URL']}")
    print()
    
    # Run inference
    result = subprocess.run(
        [sys.executable, "inference.py"],
        cwd="/Users/niharshah/Desktop/Meta Hackathon",
        capture_output=True,
        text=True,
        env=env,
        timeout=60
    )
    
    print("STDOUT:")
    print(result.stdout)
    
    if result.stderr:
        print("\nSTDERR:")
        print(result.stderr)
    
    print(f"\nReturn code: {result.returncode}")
    
    # Parse output
    print("\n" + "=" * 80)
    print("OUTPUT VALIDATION")
    print("=" * 80)
    
    import re
    output = result.stdout
    
    # Find all [END] task_id=xxx score=yyy lines
    end_pattern = r'\[END\].*task_id=(\w+).*score=([0-9.]+)'
    matches = re.findall(end_pattern, output)
    
    print(f"\nFound {len(matches)} [END] markers")
    
    task_scores = {}
    for task_id, score_str in matches:
        if task_id != 'multi':
            score = float(score_str)
            task_scores[task_id] = score
            valid = 0.0 < score < 1.0
            status = "✓" if valid else "❌"
            print(f"  {status} {task_id}: {score:.3f}")
    
    print(f"\nValidation:")
    if len(task_scores) >= 3:
        print(f"  ✓ Found {len(task_scores)} tasks (need >= 3)")
    else:
        print(f"  ❌ Found only {len(task_scores)} tasks (need >= 3)")
    
    invalid = [s for s in task_scores.values() if not (0.0 < s < 1.0)]
    if not invalid:
        print(f"  ✓ All scores in valid range (0, 1)")
    else:
        print(f"  ❌ {len(invalid)} scores out of range")
    
    sys.exit(result.returncode)
