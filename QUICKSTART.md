# Quick Start: Memory & Multi-Agent Features

## Memory System Examples

### 1. Accessing Cached Entities

```python
from app.env import CRMQueryEnv

env = CRMQueryEnv()
obs = env.reset()

# Execute a search
action = {"tool": "search_customers", "arguments": {"tier": "Gold"}}
obs, reward, done, info = env.step(action)

# Access cached data from observation
cached_customers = obs.memory_cache["customers"]  # 8 Gold tier customers
print(f"Cached: {len(cached_customers)} customers")

# Check step summaries for context
print(f"History: {obs.step_summaries}")  
# Output: ['Step 1: search_customers {...} -> 8 results']
```

### 2. Memory Rewards

```python
# First query
obs1, reward1, _, _ = env.step({"tool": "search_customers", "arguments": {"tier": "Gold"}})
print(f"Reward 1: {reward1.value}")  # Contains valid_schema, narrowing_search

# Different query (no penalty)
obs2, reward2, _, _ = env.step({"tool": "search_tickets", "arguments": {"priority": "High"}})
print(f"Reward 2: {reward2.value}")  # Also positive

# Repeated query (penalty)
obs3, reward3, _, _ = env.step({"tool": "search_customers", "arguments": {"tier": "Gold"}})
print(f"Reward 3: {reward3.value}")  # Includes -0.5 repeated_query penalty
```

---

## Multi-Agent Planner & Executor

### 1. Generate a Plan

```python
from app.multi_agent import PlannerAgent
from app.env import CRMQueryEnv
from app.tasks import get_task_by_id

env = CRMQueryEnv()
obs = env.reset()

# Create planner with API key
planner = PlannerAgent(api_key="sk-your-api-key")

# Generate plan for current task
task = get_task_by_id(env.current_task_id)
plan = planner.generate_plan(
    task_id=env.current_task_id,
    task_description=task.description,
    tables_summary=obs.tables_summary,
    max_steps=task.max_steps
)

# Inspect the plan
print(f"Plan for {plan.task_id}:")
print(f"Strategy: {plan.reasoning}")
for step in plan.steps:
    print(f"  Step {step.step_number}: {step.tool}")
    print(f"    Arguments: {step.arguments}")
    print(f"    Rationale: {step.rationale}")
```

### 2. Execute a Plan

```python
from app.multi_agent import ExecutorAgent
from app.env import CRMQueryEnv

env = CRMQueryEnv()
obs = env.reset()

# Use planner to generate plan (or fallback)
planner = PlannerAgent(api_key="sk-...")
plan = planner.generate_plan(...)

# Create executor
executor = ExecutorAgent()

# Execute the plan
results = executor.execute_plan(plan, env)

print(f"Execution Results:")
print(f"  Steps executed: {results['steps_executed']}")
print(f"  Memory efficiency: {results['memory_efficiency']:.2f}")
print(f"  Final answer: {results['final_answer']}")
print(f"  Plan adherence: {results['plan_adherence']:.2f}")
```

### 3. Full Pipeline (Coordinator)

```python
from app.multi_agent import Coordinator
from app.env import CRMQueryEnv

env = CRMQueryEnv()
obs = env.reset()

# Create coordinator with API key
coordinator = Coordinator(api_key="sk-your-api-key")

# Run full pipeline: plan → execute → grade
results = coordinator.run_pipeline(env, max_iterations=1)

print(f"Pipeline Results:")
print(f"  Task: {results['task_id']}")
print(f"  Plans generated: {results['iterations']}")
print(f"  Final answer: {results['final_answer']}")
print(f"  Episode reward: {results['episode_reward']:.2f}")
print(f"  Steps taken: {results['steps_taken']}")
print(f"  Success: {results['success']}")

# Inspect plan and execution details
if results['plans']:
    print(f"  Plan reasoning: {results['plans'][0]['reasoning']}")
if results['execution_results']:
    print(f"  Memory efficiency: {results['execution_results'][0]['memory_efficiency']:.2f}")
```

---

## API Examples

### Get Current Memory State

```bash
curl http://localhost:8000/state | jq '.observation | {memory_cache, step_summaries}'
```

### Generate Plan via API

```bash
# Step 1: Reset environment
curl -X POST http://localhost:8000/reset

# Step 2: Generate plan
curl -X POST http://localhost:8000/plan \
  -H "Content-Type: application/json" \
  | jq '.plan.steps'
```

### Execute Full Pipeline via API

```bash
# Step 1: Reset environment
curl -X POST http://localhost:8000/reset

# Step 2: Execute multi-agent pipeline
curl -X POST http://localhost:8000/execute_plan \
  -H "Content-Type: application/json" \
  | jq '{final_answer: .results.final_answer, reward: .episode_reward, steps: .steps_taken}'
```

---

## Memory System Internals

### Retrieved Entities Cache Structure

```python
retrieved_entities = {
    "customers": [
        {"customer_id": "C001", "name": "Alice Johnson", "tier": "Gold", ...},
        {"customer_id": "C004", "name": "David Brown", "tier": "Gold", ...},
        ...
    ],
    "orders": [
        {"order_id": "O001", "customer_id": "C001", "product": "Laptop", ...},
        ...
    ],
    "tickets": [
        {"ticket_id": "T001", "customer_id": "C001", "priority": "High", ...},
        ...
    ]
}
```

### Step Summary Format

```
"Step 1: search_customers {'tier': 'Gold'} -> 8 results"
"Step 2: search_tickets {'priority': 'High', 'status': 'Open'} -> 12 results"
"Step 3: submit_answer {'customer_ids': ['C001', 'C004', ...]} -> Task complete"
```

### Reward Components with Memory

```python
{
    "valid_schema": 0.5,          # Valid tool and arguments
    "narrowing_search": 0.3,      # Good filter (0-50 results)
    "memory_reuse": 0.4,          # [NEW] Used cached data
    "cache_maintained": 0.2,      # [NEW] Efficient cache management
    "answer_accuracy": 2.4,       # Correct answer items
    "false_positives": -0.4,      # Extra incorrect items (-0.2 each)
    "repeated_query": -0.5,       # Duplicate query
    "step_inefficiency": -0.5,    # Using too many steps
}
```

---

## Extreme Task: Memory Reuse Challenge

The `task_extreme_001` task showcases memory system value:

```
Task: Find all customers who appeared in previous Gold-tier queries
      AND have at least one HIGH priority OPEN support ticket.

Optimal Strategy:
1. Search: customers with tier=Gold (cache 8 results)
2. Search: tickets with priority=High AND status=Open
3. Intersect: Which customers from step 1 appear in step 2's results
4. Submit: The intersection

Agents that reuse cached customers from step 1 get +0.4 reward bonus
Agents that re-query customers in step 3 get -0.5 penalty
```

---

## Testing Memory Features

```bash
# Test memory system (20 tests)
pytest tests/test_memory_usage.py -v

# Test multi-agent system (24 tests)
pytest tests/test_multi_agent.py -v

# Run all tests
pytest tests/ -v
```

---

## Performance Tips

### 1. Use Memory Cache
- Always check `obs.memory_cache` before making new queries
- Reuse entities across steps for +0.4 reward bonus

### 2. Generate Good Plans
- Use PlannerAgent to get structured step-by-step guidance
- Temperature=0 ensures reproducible planning

### 3. Minimize Redundancy
- Avoid identical queries (penalized -0.5 each)
- Combine filters when possible to reduce queries

### 4. Track Efficiency
- Monitor `memory_efficiency` in executor results
- Higher efficiency = more memory-aware execution

---

## Troubleshooting

### Plan Generation Fails
```python
# Fallback to simple plan (no API key needed)
planner = PlannerAgent(api_key=None)
plan = planner._generate_fallback_plan(task_id, description)
```

### API Key Not Set
```bash
# Set before running multi-agent features
export OPENAI_API_KEY="sk-your-key"
```

### Memory Not Appearing in Observation
```python
# Check environment was properly reset
env.reset()  # Must call reset first
obs = env.state()  # Then get observation
assert hasattr(obs, 'memory_cache')
```

---

## Quick Reference: Classes & Methods

### PlannerAgent
```python
planner = PlannerAgent(api_key="sk-...")
plan = planner.generate_plan(task_id, task_description, tables_summary, max_steps)
plan = planner._generate_fallback_plan(task_id, task_description)
```

### ExecutorAgent
```python
executor = ExecutorAgent()
results = executor.execute_plan(plan, env)
executor.reset()
```

### Coordinator
```python
coordinator = Coordinator(api_key="sk-...")
pipeline_results = coordinator.run_pipeline(env, max_iterations=1)
```

### Plan/PlanStep
```python
plan = Plan(task_id, description, total_steps, reasoning, steps=[...])
step = PlanStep(step_number, tool, arguments, rationale, expected_output)
```

---

## Next Steps

1. ✅ Try the memory system with `test_memory_usage.py`
2. ✅ Experiment with multi-agent planning
3. ✅ Solve the extreme task using memory reuse
4. ✅ Compare agent performance with/without memory
5. ✅ Integrate with your agent training loop
