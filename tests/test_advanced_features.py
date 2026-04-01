"""
Tests for Advanced Memory System, Analytics, Task Generation, and Ranking.

Comprehensive test coverage (30+ tests) for:
- SemanticMemoryStore
- PerformanceMonitor
- CurriculumTaskGenerator
- AdaptiveTaskSelector
- SemanticRanker
- SmartFilterRecommender
- QueryOptimizer
"""

import pytest
from app.advanced_memory import SemanticMemoryStore, ReasoningOptimizer, SemanticVector
from app.analytics import PerformanceMonitor, QueryType, EpisodeAnalytics
from app.task_generator import (
    CurriculumTaskGenerator, AdaptiveTaskSelector, DifficultyEstimator,
    DifficultyLevel
)
from app.ranking import (
    SemanticRanker, SmartFilterRecommender, QueryOptimizer, RelevanceScorer
)


# ==================== ADVANCED MEMORY TESTS ====================

class TestSemanticMemoryStore:
    """Test semantic memory functionality."""
    
    def test_memory_store_initialization(self):
        """Test memory store initializes correctly."""
        store = SemanticMemoryStore()
        assert len(store.entries) == 0
        assert len(store.query_index) == 0
        assert store.efficiency_score == 1.0
    
    def test_add_entry_to_memory(self):
        """Test adding entries to memory."""
        store = SemanticMemoryStore()
        results = [{'customer_id': 'C001', 'name': 'John'}]
        
        entry = store.add_entry(
            entity_type='customers',
            filters={'tier': 'Gold'},
            results=results,
            reasoning='Find Gold customers'
        )
        
        assert len(store.entries) == 1
        assert entry.results_count == 1
        assert 'C001' in store.entity_cache['customers']
    
    def test_semantic_vector_hash(self):
        """Test semantic vector creates consistent hashes."""
        vec1 = SemanticVector("", "customers", {"tier": "Gold"})
        vec2 = SemanticVector("", "customers", {"tier": "Gold"})
        
        assert vec1.hash_key == vec2.hash_key
    
    def test_find_similar_queries_exact_match(self):
        """Test finding exact query matches."""
        store = SemanticMemoryStore()
        results = [{'customer_id': 'C001'}]
        
        store.add_entry('customers', {'tier': 'Gold'}, results)
        
        similar = store.find_similar_queries('customers', {'tier': 'Gold'})
        assert len(similar) > 0
        assert similar[0][1] == 1.0  # Exact match confidence
    
    def test_cached_results_retrieval(self):
        """Test retrieving cached results."""
        store = SemanticMemoryStore()
        results = [{'customer_id': 'C001'}, {'customer_id': 'C002'}]
        
        store.add_entry('customers', {'tier': 'Gold'}, results)
        
        cached = store.get_cached_results('customers', {'tier': 'Gold'})
        assert cached is not None
        assert len(cached) == 2
    
    def test_efficiency_metrics_computation(self):
        """Test efficiency metrics calculation."""
        store = SemanticMemoryStore()
        
        for i in range(5):
            store.add_entry('customers', {'tier': 'Gold'}, [{'id': f'C{i}'}])
        
        metrics = store.compute_efficiency_metrics()
        assert 'cache_hit_rate' in metrics
        assert 'memory_density' in metrics
        assert 'overall_efficiency' in metrics
        assert 0 <= metrics['overall_efficiency'] <= 1.0
    
    def test_memory_reset(self):
        """Test memory reset clears all data."""
        store = SemanticMemoryStore()
        store.add_entry('customers', {'tier': 'Gold'}, [{'id': 'C001'}])
        
        assert len(store.entries) > 0
        
        store.reset()
        
        assert len(store.entries) == 0
        assert len(store.query_index) == 0
        assert store.efficiency_score == 1.0


class TestReasoningOptimizer:
    """Test reasoning path optimization."""
    
    def test_optimizer_initialization(self):
        """Test reasoning optimizer initializes."""
        store = SemanticMemoryStore()
        optimizer = ReasoningOptimizer(store)
        
        assert len(optimizer.reasoning_paths) == 0
    
    def test_find_optimal_path(self):
        """Test finding optimal reasoning paths."""
        store = SemanticMemoryStore()
        optimizer = ReasoningOptimizer(store)
        
        state = {'task': 'find_gold_customers', 'step': 1}
        path = optimizer.find_optimal_path(state, 'find customers')
        
        assert isinstance(path, list)
    
    def test_cost_estimation(self):
        """Test path cost estimation."""
        store = SemanticMemoryStore()
        optimizer = ReasoningOptimizer(store)
        
        path1 = ['search_customers', 'filter_by_tier']
        path2 = ['search_customers', 'search_orders', 'intersect']
        
        cost1 = optimizer.estimate_cost(path1)
        cost2 = optimizer.estimate_cost(path2)
        
        assert cost1 > cost2  # Shorter path = higher cost benefit


# ==================== ANALYTICS TESTS ====================

class TestPerformanceMonitor:
    """Test performance monitoring."""
    
    def test_monitor_initialization(self):
        """Test monitor initializes correctly."""
        monitor = PerformanceMonitor(window_size=50)
        
        assert len(monitor.queries) == 0
        assert len(monitor.episodes) == 0
    
    def test_record_query(self):
        """Test recording query metrics."""
        monitor = PerformanceMonitor()
        
        monitor.record_query(
            query_type=QueryType.CUSTOMER_SEARCH,
            execution_time=0.05,
            result_count=5,
            cache_hit=False,
            filters={'tier': 'Gold'}
        )
        
        assert len(monitor.queries) == 1
        assert monitor.queries[0].query_type == QueryType.CUSTOMER_SEARCH
    
    def test_episode_tracking(self):
        """Test episode lifecycle tracking."""
        monitor = PerformanceMonitor()
        
        monitor.start_episode('ep_001', 'task_hard_001')
        monitor.record_query(QueryType.CUSTOMER_SEARCH, 0.05, 5)
        monitor.end_episode(total_reward=1.5, correctness_score=0.9)
        
        assert len(monitor.episodes) == 1
        assert monitor.episodes[0].total_reward == 1.5
    
    def test_performance_summary(self):
        """Test getting performance summary."""
        monitor = PerformanceMonitor()
        
        for i in range(3):
            monitor.start_episode(f'ep_{i}', 'task_easy_001')
            monitor.record_query(QueryType.CUSTOMER_SEARCH, 0.05, i + 1)
            monitor.end_episode(total_reward=1.0 - i * 0.1, correctness_score=1.0 - i * 0.1)
        
        summary = monitor.get_performance_summary()
        
        assert summary['total_episodes'] == 3
        assert 'average_reward' in summary
        assert 'average_correctness' in summary
    
    def test_query_profile(self):
        """Test query profiling."""
        monitor = PerformanceMonitor()
        
        monitor.record_query(QueryType.CUSTOMER_SEARCH, 0.05, 5)
        monitor.record_query(QueryType.TICKET_SEARCH, 0.08, 3)
        monitor.record_query(QueryType.CUSTOMER_SEARCH, 0.06, 4)
        
        profile = monitor.get_query_profile()
        
        assert QueryType.CUSTOMER_SEARCH.value in profile
        assert profile[QueryType.CUSTOMER_SEARCH.value]['count'] == 2
    
    def test_bottleneck_analysis(self):
        """Test bottleneck detection."""
        monitor = PerformanceMonitor()
        
        # Record low-performance episode
        monitor.start_episode('ep_001', 'task_hard_001')
        for _ in range(10):
            monitor.record_query(QueryType.CUSTOMER_SEARCH, 0.1, 1)
        monitor.end_episode(total_reward=0.3, correctness_score=0.5)
        
        bottlenecks = monitor.get_bottleneck_analysis()
        
        assert len(bottlenecks) > 0
        assert any('correctness' in b.lower() for b in bottlenecks)


# ==================== TASK GENERATION TESTS ====================

class TestCurriculumTaskGenerator:
    """Test curriculum task generation."""
    
    def test_generator_initialization(self):
        """Test generator initializes."""
        gen = CurriculumTaskGenerator()
        assert gen.task_counter == 0
    
    def test_generate_curriculum_linear(self):
        """Test generating linear curriculum."""
        gen = CurriculumTaskGenerator()
        tasks = gen.generate_curriculum(num_tasks=10, difficulty_curve="linear")
        
        assert len(tasks) == 10
        assert all(hasattr(t, 'difficulty') for t in tasks)
        # Should increase in difficulty
        difficulties = [t.difficulty.value for t in tasks]
        assert difficulties == sorted(difficulties)
    
    def test_generate_curriculum_exponential(self):
        """Test generating exponential curriculum."""
        gen = CurriculumTaskGenerator()
        tasks = gen.generate_curriculum(num_tasks=8, difficulty_curve="exponential")
        
        assert len(tasks) == 8
        difficulties = [t.difficulty.value for t in tasks]
        assert difficulties[0] <= difficulties[-1]  # Monotonic increase
    
    def test_generate_single_task(self):
        """Test generating individual task."""
        gen = CurriculumTaskGenerator()
        task = gen.generate_task(DifficultyLevel.HARD)
        
        assert task.difficulty == DifficultyLevel.HARD
        assert len(task.ground_truth) > 0
        assert task.estimated_optimal_steps > 0
    
    def test_task_description_generation(self):
        """Test task description generation."""
        gen = CurriculumTaskGenerator()
        
        for difficulty in DifficultyLevel:
            task = gen.generate_task(difficulty)
            assert len(task.description) > 0
            assert len(task.reasoning_explanation) > 0


class TestAdaptiveTaskSelector:
    """Test adaptive task selection."""
    
    def test_selector_initialization(self):
        """Test selector initializes."""
        gen = CurriculumTaskGenerator()
        curriculum = gen.generate_curriculum(num_tasks=5)
        selector = AdaptiveTaskSelector(curriculum)
        
        assert selector.current_index == 0
    
    def test_select_first_task(self):
        """Test selecting first task."""
        gen = CurriculumTaskGenerator()
        curriculum = gen.generate_curriculum(num_tasks=5)
        selector = AdaptiveTaskSelector(curriculum)
        
        task = selector.select_next_task()
        assert task == curriculum[0]
    
    def test_adaptive_difficulty_progression(self):
        """Test adaptive difficulty progression."""
        gen = CurriculumTaskGenerator()
        curriculum = gen.generate_curriculum(num_tasks=10)
        selector = AdaptiveTaskSelector(curriculum)
        
        # Strong performance -> advance
        task = selector.select_next_task()
        initial_index = selector.current_index
        
        selector.select_next_task(last_correctness=0.95)
        assert selector.current_index >= initial_index
    
    def test_performance_summary(self):
        """Test performance summary generation."""
        gen = CurriculumTaskGenerator()
        curriculum = gen.generate_curriculum(num_tasks=5)
        selector = AdaptiveTaskSelector(curriculum)
        
        selector.record_performance('task_1', 0.8)
        selector.record_performance('task_2', 0.9)
        
        summary = selector.get_performance_summary()
        assert summary['tasks_attempted'] == 2
        assert abs(summary['average_correctness'] - 0.85) < 0.001


class TestDifficultyEstimator:
    """Test difficulty estimation."""
    
    def test_estimator_initialization(self):
        """Test estimator initializes."""
        estimator = DifficultyEstimator()
        assert len(estimator.execution_metrics) == 0
    
    def test_estimate_difficulty(self):
        """Test difficulty estimation."""
        gen = CurriculumTaskGenerator()
        task = gen.generate_task(DifficultyLevel.MEDIUM)
        
        estimator = DifficultyEstimator()
        difficulty = estimator.estimate_difficulty(
            task=task,
            execution_time=0.1,
            correctness=0.8,
            steps_used=3
        )
        
        assert 0.0 <= difficulty <= 1.0
    
    def test_record_execution(self):
        """Test recording execution metrics."""
        estimator = DifficultyEstimator()
        
        estimator.record_execution('task_1', 0.5)
        estimator.record_execution('task_1', 0.6)
        
        assert len(estimator.execution_metrics['task_1']) == 2


# ==================== RANKING TESTS ====================

class TestSemanticRanker:
    """Test semantic ranking."""
    
    def test_ranker_initialization(self):
        """Test ranker initializes."""
        ranker = SemanticRanker()
        assert len(ranker.field_weights) > 0
    
    def test_rank_results(self):
        """Test ranking results."""
        ranker = SemanticRanker()
        
        results = [
            {'customer_id': 'C001', 'tier': 'Gold', 'priority': 'High'},
            {'customer_id': 'C002', 'tier': 'Silver', 'priority': 'Low'},
        ]
        
        context = {'tier': 'Gold', 'priority': 'High'}
        ranked = ranker.rank_results(results, context)
        
        assert len(ranked) == 2
        assert ranked[0].relevance_score > ranked[1].relevance_score


class TestSmartFilterRecommender:
    """Test filter recommendations."""
    
    def test_recommender_initialization(self):
        """Test recommender initializes."""
        stats = {'total_items': 100}
        recommender = SmartFilterRecommender(stats)
        
        assert len(recommender.field_selectivity) > 0
    
    def test_recommend_filters_too_many_results(self):
        """Test recommending filters for too many results."""
        stats = {'total_items': 100}
        recommender = SmartFilterRecommender(stats)
        
        recommendations = recommender.recommend_filters(
            current_result_count=50,
            target_count=10
        )
        
        assert len(recommendations) > 0


class TestQueryOptimizer:
    """Test query optimization."""
    
    def test_optimizer_initialization(self):
        """Test optimizer initializes."""
        optimizer = QueryOptimizer()
        assert len(optimizer.query_cache) == 0
    
    def test_optimize_execution_order(self):
        """Test execution order optimization."""
        optimizer = QueryOptimizer()
        
        filters = [('product', 'Laptop'), ('tier', 'Gold'), ('priority', 'High')]
        optimized = optimizer.optimize_execution_order(filters)
        
        assert len(optimized) == 3
    
    def test_estimate_result_size(self):
        """Test result size estimation."""
        optimizer = QueryOptimizer()
        
        filters = [('tier', 'Gold'), ('priority', 'High')]
        min_est, max_est = optimizer.estimate_result_size(filters)
        
        assert min_est > 0
        assert max_est >= min_est


class TestRelevanceScorer:
    """Test relevance scoring."""
    
    def test_scorer_initialization(self):
        """Test scorer initializes."""
        scorer = RelevanceScorer()
        assert len(scorer.importance_weights) > 0
    
    def test_score_result(self):
        """Test scoring individual result."""
        scorer = RelevanceScorer()
        
        item = {'tier': 'Gold', 'priority': 'High', 'product': 'Laptop'}
        query = {'tier': 'Gold', 'priority': 'High'}
        
        score = scorer.score_result(item, query)
        assert 0.0 <= score <= 1.0
    
    def test_rank_by_relevance(self):
        """Test ranking results by relevance."""
        scorer = RelevanceScorer()
        
        items = [
            {'tier': 'Gold', 'priority': 'High'},
            {'tier': 'Silver', 'priority': 'Low'},
            {'tier': 'Gold', 'priority': 'Low'},
        ]
        
        query = {'tier': 'Gold', 'priority': 'High'}
        ranked = scorer.rank_by_relevance(items, query)
        
        assert len(ranked) == 3
        assert ranked[0]['tier'] == 'Gold'  # Best match first
