"""
Advanced Analytics and Performance Monitoring System.

Provides:
- Real-time performance metrics
- Query execution analysis
- Memory efficiency tracking
- Agent behavior profiling
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import time
from collections import defaultdict, deque


class QueryType(Enum):
    """Types of queries."""
    CUSTOMER_SEARCH = "customer_search"
    ORDER_SEARCH = "order_search"
    TICKET_SEARCH = "ticket_search"
    ANSWER_SUBMISSION = "answer_submission"


@dataclass
class QueryMetrics:
    """Metrics for a single query."""
    query_type: QueryType
    timestamp: float
    execution_time: float
    result_count: int
    cache_hit: bool = False
    filters_used: Dict[str, Any] = field(default_factory=dict)
    intermediate_results: int = 0
    

@dataclass
class EpisodeAnalytics:
    """Analytics for a complete episode."""
    episode_id: str
    task_id: str
    total_steps: int
    total_reward: float
    execution_time: float
    memory_efficiency: float = 0.0
    cache_utilization: float = 0.0
    average_query_time: float = 0.0
    correctness_score: float = 0.0
    queries: List[QueryMetrics] = field(default_factory=list)
    

class PerformanceMonitor:
    """Monitor and analyze system performance."""
    
    def __init__(self, window_size: int = 100):
        self.queries: deque = deque(maxlen=window_size)
        self.episodes: deque = deque(maxlen=window_size)
        self.query_statistics: Dict[QueryType, Dict[str, Any]] = defaultdict(
            lambda: {
                'count': 0,
                'total_time': 0.0,
                'cache_hits': 0,
                'avg_results': 0.0
            }
        )
        self.current_episode: Optional[EpisodeAnalytics] = None
        self.start_time = time.time()
        
    def start_episode(self, episode_id: str, task_id: str):
        """Mark start of new episode."""
        self.current_episode = EpisodeAnalytics(
            episode_id=episode_id,
            task_id=task_id,
            total_steps=0,
            total_reward=0.0,
            execution_time=0.0
        )
    
    def record_query(self, query_type: QueryType, execution_time: float,
                    result_count: int, cache_hit: bool = False,
                    filters: Optional[Dict] = None):
        """Record a query execution."""
        metrics = QueryMetrics(
            query_type=query_type,
            timestamp=time.time(),
            execution_time=execution_time,
            result_count=result_count,
            cache_hit=cache_hit,
            filters_used=filters or {}
        )
        
        self.queries.append(metrics)
        
        if self.current_episode:
            self.current_episode.queries.append(metrics)
            self.current_episode.total_steps += 1
        
        # Update statistics
        stats = self.query_statistics[query_type]
        stats['count'] += 1
        stats['total_time'] += execution_time
        if cache_hit:
            stats['cache_hits'] += 1
        
        # Running average of results
        old_avg = stats['avg_results']
        count = stats['count']
        stats['avg_results'] = (old_avg * (count - 1) + result_count) / count
    
    def end_episode(self, total_reward: float, correctness_score: float):
        """Mark end of episode and compute final analytics."""
        if not self.current_episode:
            return
        
        self.current_episode.total_reward = total_reward
        self.current_episode.correctness_score = correctness_score
        self.current_episode.execution_time = time.time() - self.start_time
        
        # Compute averages
        if self.current_episode.queries:
            self.current_episode.average_query_time = (
                sum(q.execution_time for q in self.current_episode.queries) /
                len(self.current_episode.queries)
            )
            
            # Cache utilization
            cache_hits = sum(1 for q in self.current_episode.queries if q.cache_hit)
            self.current_episode.cache_utilization = (
                cache_hits / len(self.current_episode.queries)
            )
        
        self.episodes.append(self.current_episode)
        self.current_episode = None
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get overall performance summary."""
        if not self.episodes:
            return {}
        
        episodes_list = list(self.episodes)
        total_episodes = len(episodes_list)
        
        avg_reward = sum(e.total_reward for e in episodes_list) / total_episodes
        avg_correctness = sum(e.correctness_score for e in episodes_list) / total_episodes
        avg_query_time = sum(e.average_query_time for e in episodes_list) / total_episodes
        avg_cache_util = sum(e.cache_utilization for e in episodes_list) / total_episodes
        
        # Task-specific stats
        task_stats = defaultdict(lambda: {
            'count': 0,
            'avg_reward': 0.0,
            'avg_correctness': 0.0
        })
        
        for episode in episodes_list:
            task = episode.task_id
            task_stats[task]['count'] += 1
            task_stats[task]['avg_reward'] += episode.total_reward
            task_stats[task]['avg_correctness'] += episode.correctness_score
        
        for task in task_stats:
            count = task_stats[task]['count']
            task_stats[task]['avg_reward'] /= count
            task_stats[task]['avg_correctness'] /= count
        
        return {
            'total_episodes': total_episodes,
            'average_reward': avg_reward,
            'average_correctness': avg_correctness,
            'average_query_time': avg_query_time,
            'average_cache_utilization': avg_cache_util,
            'query_type_stats': dict(self.query_statistics),
            'task_statistics': dict(task_stats),
            'total_runtime': time.time() - self.start_time
        }
    
    def get_query_profile(self) -> Dict[str, Any]:
        """Get detailed query profiling information."""
        if not self.queries:
            return {}
        
        queries_list = list(self.queries)
        
        by_type = defaultdict(list)
        for q in queries_list:
            by_type[q.query_type.value].append(q)
        
        profiles = {}
        for qtype in QueryType:
            qtype_queries = by_type[qtype.value]
            if qtype_queries:
                profiles[qtype.value] = {
                    'count': len(qtype_queries),
                    'avg_time': sum(q.execution_time for q in qtype_queries) / len(qtype_queries),
                    'avg_results': sum(q.result_count for q in qtype_queries) / len(qtype_queries),
                    'cache_hit_rate': sum(1 for q in qtype_queries if q.cache_hit) / len(qtype_queries),
                    'min_time': min(q.execution_time for q in qtype_queries),
                    'max_time': max(q.execution_time for q in qtype_queries)
                }
        
        return profiles
    
    def get_bottleneck_analysis(self) -> List[str]:
        """Identify performance bottlenecks."""
        bottlenecks = []
        
        summary = self.get_performance_summary()
        if not summary:
            return bottlenecks
        
        # Cache utilization < 30%
        if summary['average_cache_utilization'] < 0.3:
            bottlenecks.append("Low cache utilization - consider reusing more cached results")
        
        # Query time too high
        if summary['average_query_time'] > 0.05:
            bottlenecks.append("High average query time - optimize filter strategies")
        
        # Correctness < 80%
        if summary['average_correctness'] < 0.8:
            bottlenecks.append("Low correctness - improve query logic or filtering")
        
        # Low reward
        if summary['average_reward'] < 0.5:
            bottlenecks.append("Low average reward - reconsider reward strategy")
        
        return bottlenecks
    
    def reset(self):
        """Reset monitoring for new session."""
        self.queries.clear()
        self.episodes.clear()
        self.query_statistics.clear()
        self.current_episode = None
        self.start_time = time.time()
