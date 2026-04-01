"""
Advanced Task Generator with Curriculum Learning.

Generates diverse tasks with:
- Progressive difficulty scaling
- Synthetic task generation
- Curriculum learning paths
- Difficulty estimation
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import random


class DifficultyLevel(Enum):
    """Task difficulty levels."""
    TRIVIAL = 0
    EASY = 1
    MEDIUM = 2
    HARD = 3
    EXTREME = 4
    IMPOSSIBLE = 5


@dataclass
class SyntheticTask:
    """A generated synthetic task."""
    task_id: str
    difficulty: DifficultyLevel
    description: str
    reasoning_steps: int
    filter_complexity: int  # Number of filters needed
    result_size_range: tuple  # (min, max) expected results
    ground_truth: List[str]
    reasoning_explanation: str = ""
    estimated_optimal_steps: int = 0


class CurriculumTaskGenerator:
    """Generate curriculum learning task sequences."""
    
    def __init__(self):
        self.task_counter = 0
        self.generated_tasks: Dict[str, SyntheticTask] = {}
        
    def generate_curriculum(self, num_tasks: int = 20, 
                           difficulty_curve: str = "linear") -> List[SyntheticTask]:
        """Generate a curriculum of tasks with progressive difficulty.
        
        Args:
            num_tasks: Number of tasks to generate
            difficulty_curve: "linear", "exponential", or "adaptive"
        
        Returns:
            Ordered list of tasks from easy to hard
        """
        tasks = []
        
        if difficulty_curve == "linear":
            difficulties = [
                DifficultyLevel.TRIVIAL,
                DifficultyLevel.EASY,
                DifficultyLevel.EASY,
                DifficultyLevel.MEDIUM,
                DifficultyLevel.MEDIUM,
                DifficultyLevel.HARD,
                DifficultyLevel.HARD,
                DifficultyLevel.EXTREME,
                DifficultyLevel.EXTREME,
                DifficultyLevel.IMPOSSIBLE,
            ]
            # Extend if needed
            while len(difficulties) < num_tasks:
                difficulties.append(DifficultyLevel.IMPOSSIBLE)
            difficulties = difficulties[:num_tasks]
            
        elif difficulty_curve == "exponential":
            difficulties = []
            for i in range(num_tasks):
                level = int((2 ** (i / max(num_tasks - 1, 1))) - 1)
                level = min(level, 5)  # Cap at IMPOSSIBLE
                difficulties.append(DifficultyLevel(level))
        
        else:  # adaptive
            difficulties = []
            current_level = 0
            for i in range(num_tasks):
                if i % 3 == 0 and current_level < 5:
                    current_level += 1
                difficulties.append(DifficultyLevel(current_level))
        
        for diff in difficulties:
            task = self.generate_task(difficulty=diff)
            tasks.append(task)
        
        return tasks
    
    def generate_task(self, difficulty: DifficultyLevel) -> SyntheticTask:
        """Generate a single task at specified difficulty."""
        self.task_counter += 1
        task_id = f"synthetic_{difficulty.name.lower()}_{self.task_counter:03d}"
        
        # Difficulty parameters
        params = {
            DifficultyLevel.TRIVIAL: {
                'filters': 1,
                'steps': 1,
                'result_range': (1, 5)
            },
            DifficultyLevel.EASY: {
                'filters': 1,
                'steps': 2,
                'result_range': (1, 10)
            },
            DifficultyLevel.MEDIUM: {
                'filters': 2,
                'steps': 3,
                'result_range': (1, 15)
            },
            DifficultyLevel.HARD: {
                'filters': 3,
                'steps': 4,
                'result_range': (1, 20)
            },
            DifficultyLevel.EXTREME: {
                'filters': 4,
                'steps': 5,
                'result_range': (1, 25)
            },
            DifficultyLevel.IMPOSSIBLE: {
                'filters': 5,
                'steps': 6,
                'result_range': (1, 30)
            }
        }
        
        p = params[difficulty]
        
        # Generate random filters
        all_filters = [
            ('tier', ['Bronze', 'Silver', 'Gold']),
            ('priority', ['Low', 'Medium', 'High']),
            ('status', ['Open', 'Closed', 'Pending', 'Completed']),
            ('product', ['Laptop', 'Monitor', 'Keyboard', 'Mouse']),
        ]
        
        selected_filters = random.sample(all_filters, min(p['filters'], len(all_filters)))
        filter_str = ", ".join(f"{f[0]}={random.choice(f[1])}" for f, _ in selected_filters)
        
        description = self._generate_description(difficulty, filter_str)
        ground_truth = self._generate_ground_truth(p['result_range'])
        reasoning = self._generate_reasoning(difficulty, selected_filters)
        
        return SyntheticTask(
            task_id=task_id,
            difficulty=difficulty,
            description=description,
            reasoning_steps=p['steps'],
            filter_complexity=p['filters'],
            result_size_range=p['result_range'],
            ground_truth=ground_truth,
            reasoning_explanation=reasoning,
            estimated_optimal_steps=p['steps']
        )
    
    def _generate_description(self, difficulty: DifficultyLevel, filters: str) -> str:
        """Generate task description."""
        templates = {
            DifficultyLevel.TRIVIAL: f"Find items with {filters}.",
            DifficultyLevel.EASY: f"Find all items matching {filters}. Return their IDs.",
            DifficultyLevel.MEDIUM: f"Find items that meet both: (1) {filters}, (2) another criterion. Return IDs.",
            DifficultyLevel.HARD: f"Find items combining multiple filters: {filters}. Apply logical reasoning.",
            DifficultyLevel.EXTREME: f"Complex task: {filters}. Use memory and efficient reasoning. Find matching items.",
            DifficultyLevel.IMPOSSIBLE: f"Find items where {filters}. Requires multi-step reasoning, memory reuse, and semantic understanding.",
        }
        return templates[difficulty]
    
    def _generate_ground_truth(self, result_range: tuple) -> List[str]:
        """Generate random ground truth."""
        min_results, max_results = result_range
        num_results = random.randint(min_results, max_results)
        
        # Generate customer IDs
        return [f"C{i:03d}" for i in random.sample(range(1, 101), num_results)]
    
    def _generate_reasoning(self, difficulty: DifficultyLevel, filters: List) -> str:
        """Generate reasoning explanation."""
        if difficulty == DifficultyLevel.TRIVIAL:
            return "Single filter direct lookup."
        elif difficulty == DifficultyLevel.EASY:
            return "One or two sequential queries."
        elif difficulty == DifficultyLevel.MEDIUM:
            return "Multiple filters with AND logic. Requires 2-3 queries."
        elif difficulty == DifficultyLevel.HARD:
            return "Complex filtering with multiple conditions. Requires set operations."
        elif difficulty == DifficultyLevel.EXTREME:
            return "Multi-step reasoning with memory reuse. Use cached results from previous queries."
        else:  # IMPOSSIBLE
            return "Advanced: Requires semantic understanding, memory optimization, and sophisticated reasoning."


class AdaptiveTaskSelector:
    """Select appropriate tasks based on agent performance."""
    
    def __init__(self, curriculum: List[SyntheticTask]):
        self.curriculum = curriculum
        self.performance_history: Dict[str, float] = {}
        self.current_index = 0
        
    def select_next_task(self, last_correctness: Optional[float] = None) -> SyntheticTask:
        """Select next task based on performance."""
        if last_correctness is None:
            # First task
            return self.curriculum[min(self.current_index, len(self.curriculum) - 1)]
        
        # Adaptive selection
        if last_correctness > 0.85:  # Strong performance
            self.current_index = min(self.current_index + 1, len(self.curriculum) - 1)
        elif last_correctness < 0.5:  # Weak performance
            self.current_index = max(self.current_index - 1, 0)
        # else: maintain current difficulty
        
        return self.curriculum[self.current_index]
    
    def record_performance(self, task_id: str, correctness: float):
        """Record performance on task."""
        self.performance_history[task_id] = correctness
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get learning progress summary."""
        if not self.performance_history:
            return {'tasks_attempted': 0, 'average_correctness': 0.0}
        
        scores = list(self.performance_history.values())
        return {
            'tasks_attempted': len(scores),
            'average_correctness': sum(scores) / len(scores),
            'best_score': max(scores),
            'worst_score': min(scores),
            'current_difficulty_level': self.current_index
        }


class DifficultyEstimator:
    """Estimate actual difficulty based on agent performance."""
    
    def __init__(self):
        self.execution_metrics: Dict[str, List[float]] = {}
        
    def estimate_difficulty(self, task: SyntheticTask, 
                           execution_time: float,
                           correctness: float,
                           steps_used: int) -> float:
        """Estimate actual difficulty (0.0 - 1.0) based on metrics.
        
        Actual difficulty may differ from assigned difficulty based on:
        - Execution time relative to estimated time
        - Correctness achieved
        - Steps required vs estimated
        """
        # Normalize metrics to 0-1
        time_ratio = min(1.0, execution_time / (task.estimated_optimal_steps * 0.05))
        step_ratio = min(1.0, steps_used / max(task.estimated_optimal_steps * 2, 1))
        correctness_penalty = 1.0 - correctness
        
        # Weighted combination
        actual_difficulty = (time_ratio * 0.3 + step_ratio * 0.3 + correctness_penalty * 0.4)
        
        return min(1.0, max(0.0, actual_difficulty))
    
    def record_execution(self, task_id: str, metric_value: float):
        """Record execution metric."""
        if task_id not in self.execution_metrics:
            self.execution_metrics[task_id] = []
        self.execution_metrics[task_id].append(metric_value)
    
    def get_difficulty_distribution(self) -> Dict[str, float]:
        """Get statistics on difficulty distribution."""
        all_metrics = []
        for metrics in self.execution_metrics.values():
            all_metrics.extend(metrics)
        
        if not all_metrics:
            return {}
        
        all_metrics.sort()
        return {
            'min_difficulty': min(all_metrics),
            'max_difficulty': max(all_metrics),
            'median_difficulty': all_metrics[len(all_metrics) // 2],
            'avg_difficulty': sum(all_metrics) / len(all_metrics),
            'std_dev': self._compute_std_dev(all_metrics)
        }
    
    @staticmethod
    def _compute_std_dev(values: List[float]) -> float:
        """Compute standard deviation."""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
