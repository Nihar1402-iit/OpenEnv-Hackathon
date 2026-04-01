"""
Neural Ranking and Smart Filtering System.

Provides:
- Semantic ranking of results
- Smart filter recommendations
- Query optimization
- Result relevance scoring
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import math


@dataclass
class RankedResult:
    """A result with relevance score."""
    item: Dict[str, Any]
    relevance_score: float
    ranking_reason: str


class SemanticRanker:
    """Rank search results by semantic relevance."""
    
    def __init__(self):
        self.field_weights = {
            'tier': 0.3,
            'priority': 0.25,
            'status': 0.25,
            'product': 0.2
        }
        
    def rank_results(self, results: List[Dict], 
                    query_context: Dict[str, Any]) -> List[RankedResult]:
        """Rank results by relevance to query context.
        
        Args:
            results: Search results to rank
            query_context: Original query filters and constraints
        
        Returns:
            Ranked results with scores
        """
        ranked = []
        
        for item in results:
            score = self._compute_relevance(item, query_context)
            reason = self._generate_ranking_reason(item, query_context, score)
            ranked.append(RankedResult(item, score, reason))
        
        # Sort by relevance descending
        ranked.sort(key=lambda x: x.relevance_score, reverse=True)
        return ranked
    
    def _compute_relevance(self, item: Dict[str, Any], 
                          context: Dict[str, Any]) -> float:
        """Compute relevance score (0.0 - 1.0)."""
        score = 0.0
        total_weight = 0.0
        
        for field, weight in self.field_weights.items():
            if field in context and field in item:
                if self._values_match(item[field], context[field]):
                    score += weight
                total_weight += weight
            elif field not in context:
                # Field not queried, slight boost for having it
                score += weight * 0.1
                total_weight += weight
        
        if total_weight == 0:
            return 0.5
        
        return min(1.0, score / total_weight)
    
    def _values_match(self, value1: Any, value2: Any) -> bool:
        """Check if values match for relevance."""
        if isinstance(value1, str) and isinstance(value2, str):
            # Case-insensitive match or contains
            v1_lower = value1.lower()
            v2_lower = value2.lower()
            return v1_lower == v2_lower or v1_lower in v2_lower or v2_lower in v1_lower
        return value1 == value2
    
    def _generate_ranking_reason(self, item: Dict, context: Dict, 
                                score: float) -> str:
        """Generate human-readable ranking reason."""
        if score > 0.8:
            return "Excellent match across multiple fields"
        elif score > 0.6:
            return "Good match on primary fields"
        elif score > 0.4:
            return "Partial match, supplementary result"
        else:
            return "Weak match, peripheral result"


class SmartFilterRecommender:
    """Recommend effective filters based on data distribution."""
    
    def __init__(self, data_stats: Dict[str, Any]):
        """
        Args:
            data_stats: Statistics about the data distribution
        """
        self.data_stats = data_stats
        self.field_selectivity = {}
        self._compute_selectivity()
        
    def _compute_selectivity(self):
        """Compute how selective each filter is."""
        # Selectivity = how much data it filters out
        # Higher = more selective = better for narrow searches
        
        stats = self.data_stats
        total_items = stats.get('total_items', 100)
        
        self.field_selectivity = {
            'tier': 3 / total_items,  # 3 values (Bronze, Silver, Gold)
            'priority': 3 / total_items,  # 3 values (Low, Medium, High)
            'status': 2 / total_items,  # 2 values (Open, Closed)
            'product': 4 / total_items,  # 4 values (Laptop, Monitor, etc)
        }
    
    def recommend_filters(self, current_result_count: int,
                         target_count: int = None) -> List[Tuple[str, str]]:
        """Recommend filters to achieve target result count.
        
        Args:
            current_result_count: Current number of results
            target_count: Desired result count (default: 5-20)
        
        Returns:
            List of (field, reason) recommendations
        """
        if target_count is None:
            target_count = (5, 20)
        
        if isinstance(target_count, int):
            target_min, target_max = target_count, target_count * 2
        else:
            target_min, target_max = target_count
        
        recommendations = []
        
        if current_result_count > target_max:
            # Too many results, need more restrictive filters
            # Sort by selectivity descending
            sorted_fields = sorted(
                self.field_selectivity.items(),
                key=lambda x: x[1],
                reverse=True
            )
            for field, selectivity in sorted_fields[:2]:
                recommendations.append((field, f"Add {field} filter to narrow results"))
        
        elif current_result_count < target_min:
            # Too few results, need less restrictive filters
            sorted_fields = sorted(
                self.field_selectivity.items(),
                key=lambda x: x[1]
            )
            for field, selectivity in sorted_fields[:2]:
                recommendations.append((field, f"Remove {field} filter to broaden results"))
        
        return recommendations


class QueryOptimizer:
    """Optimize query execution strategy."""
    
    def __init__(self):
        self.query_cache: Dict[str, List[Dict]] = {}
        self.execution_history: List[Dict[str, Any]] = []
        
    def optimize_execution_order(self, filters: List[Tuple[str, Any]]) -> List[Tuple[str, Any]]:
        """Optimize order of filter application.
        
        Heuristic: Apply most selective filters first to reduce intermediate results.
        """
        selectivity = {
            'tier': 0.33,      # 3 tiers
            'priority': 0.33,  # 3 priorities
            'status': 0.5,     # 2 statuses
            'product': 0.25,   # 4 products
        }
        
        # Sort by selectivity (ascending = most selective first)
        optimized = sorted(
            filters,
            key=lambda x: selectivity.get(x[0], 0.5)
        )
        
        return optimized
    
    def estimate_result_size(self, filters: List[Tuple[str, Any]],
                            total_items: int = 100) -> Tuple[float, float]:
        """Estimate min and max result size for given filters.
        
        Returns:
            (min_estimate, max_estimate)
        """
        selectivities = {
            'tier': 0.33,
            'priority': 0.33,
            'status': 0.5,
            'product': 0.25,
        }
        
        # Combine selectivities (rough approximation)
        combined_selectivity = 1.0
        for field, _ in filters:
            sel = selectivities.get(field, 0.5)
            combined_selectivity *= sel
        
        min_est = total_items * combined_selectivity
        max_est = total_items * combined_selectivity * 1.5  # 50% variance
        
        return (max(1, min_est), max_est)
    
    def can_use_cache(self, current_query: Dict[str, Any],
                     cached_query: Dict[str, Any]) -> bool:
        """Check if cached query results can satisfy current query.
        
        Cached results can be reused if:
        - Same entity type
        - All cached filters match current filters
        - Cached results are superset
        """
        if current_query.get('entity_type') != cached_query.get('entity_type'):
            return False
        
        # Check if cached filters are subset of current
        cached_filters = cached_query.get('filters', {})
        current_filters = current_query.get('filters', {})
        
        for field, value in current_filters.items():
            if field in cached_filters and cached_filters[field] != value:
                return False
        
        return True


class RelevanceScorer:
    """Score relevance of results for ranking."""
    
    def __init__(self):
        self.importance_weights = {
            'exact_match': 1.0,
            'partial_match': 0.7,
            'fuzzy_match': 0.4,
            'no_match': 0.0
        }
        
    def score_result(self, item: Dict[str, Any],
                    query_fields: Dict[str, Any]) -> float:
        """Score how relevant a result is to the query.
        
        Args:
            item: The result item
            query_fields: The query filters
        
        Returns:
            Score from 0.0 to 1.0
        """
        if not query_fields:
            return 0.5
        
        matches = 0
        total = 0
        
        for field, query_value in query_fields.items():
            total += 1
            
            if field not in item:
                continue
            
            item_value = item[field]
            
            # Exact match
            if item_value == query_value:
                matches += 1
            # String contains
            elif isinstance(item_value, str) and isinstance(query_value, str):
                if query_value.lower() in item_value.lower():
                    matches += 0.7
            # Partial type match
            elif type(item_value) == type(query_value):
                matches += 0.4
        
        return matches / total if total > 0 else 0.5
    
    def rank_by_relevance(self, items: List[Dict[str, Any]],
                         query_fields: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Sort items by relevance to query.
        
        Returns:
            Items sorted by relevance (highest first)
        """
        scored = [
            (item, self.score_result(item, query_fields))
            for item in items
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [item for item, score in scored]
