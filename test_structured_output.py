#!/usr/bin/env python3
"""
Test to simulate inference output with structured logging only.
"""
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.tasks import get_tasks
from app.grader import TaskGrader

def test_structured_output():
    """Test structured output format."""
    
    # Simulate what the inference script does
    tasks = get_tasks()
    scores = {}
    
    print("[START] task=all env=CRMQueryEnv model=gpt-3.5-turbo", flush=True)
    
    # Simulate each task
    for task in tasks:
        task_id = task.task_id
        
        # Simulate a step
        print(f"[STEP] step=1 action=search_customers reward=0.10 done=false error=null", flush=True)
        print(f"[STEP] step=2 action=submit_answer reward=0.01 done=true error=null", flush=True)
        
        # Simulate task end with empty answer
        score = TaskGrader.grade_task(task, {'customer_ids': []})
        scores[task_id] = score
        
        print(f"[END] task_id={task_id} success=false steps=2 rewards=0.10,0.01 score={score:.3f}", flush=True)
    
    # Compute average
    average_score = TaskGrader.compute_average_score(scores)
    average_score = max(0.001, min(0.999, average_score))
    
    scores_str = ",".join(f"{v:.3f}" for v in scores.values())
    print(f"[END] task_id=multi success=false steps=0 rewards={scores_str} score={average_score:.3f}", flush=True)
    
    print(f"\nDEBUG: Individual scores: {scores}", file=sys.stderr)
    print(f"DEBUG: Average score: {average_score}", file=sys.stderr)

if __name__ == "__main__":
    test_structured_output()
