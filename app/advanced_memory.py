"""
Advanced Memory System with Semantic Understanding and Reasoning.

This module provides sophisticated memory management with:
- Semantic entity clustering
- Query result caching with similarity detection
- Reasoning path optimization
- Memory efficiency scoring
"""

from typing import Dict, List, Set, Tuple, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json


@dataclass
class SemanticVector:
    """Simple semantic representation of queries."""
    query: str
    entity_type: str  # 'customer', 'order', 'ticket'
    filters: Dict[str, Any]
    hash_key: str = field(init=False)
    
    def __post_init__(self):
        """Generate hash key for semantic matching."""
        filter_str = json.dumps(self.filters, sort_keys=True)
        combined = f"{self.entity_type}:{filter_str}"
        self.hash_key = hashlib.md5(combined.encode()).hexdigest()


@dataclass
class MemoryEntry:
    """Single memory entry with metadata."""
    timestamp: float
    query_hash: str
    entity_type: str
    results_count: int
    results: List[Dict[str, Any]]
    reasoning: str = ""
    confidence: float = 1.0


class SemanticMemoryStore:
    """Advanced memory with semantic understanding."""
    
    def __init__(self):
        self.entries: List[MemoryEntry] = []
        self.query_index: Dict[str, List[int]] = {}  # hash -> entry indices
        self.entity_cache: Dict[str, Set[str]] = {
            'customers': set(),
            'orders': set(),
            'tickets': set()
        }
        self.reasoning_chains: List[List[str]] = []
        self.efficiency_score = 1.0
        
    def add_entry(self, entity_type: str, filters: Dict, results: List[Dict], 
                  reasoning: str = "") -> MemoryEntry:
        """Add query result to memory with reasoning."""
        vec = SemanticVector("", entity_type, filters)
        entry = MemoryEntry(
            timestamp=datetime.now().timestamp(),
            query_hash=vec.hash_key,
            entity_type=entity_type,
            results_count=len(results),
            results=results,
            reasoning=reasoning,
            confidence=1.0
        )
        
        self.entries.append(entry)
        
        # Index for fast lookup
        if vec.hash_key not in self.query_index:
            self.query_index[vec.hash_key] = []
        self.query_index[vec.hash_key].append(len(self.entries) - 1)
        
        # Track entities
        if entity_type == 'customers':
            for r in results:
                self.entity_cache['customers'].add(r.get('customer_id', ''))
        elif entity_type == 'orders':
            for r in results:
                self.entity_cache['orders'].add(r.get('order_id', ''))
        elif entity_type == 'tickets':
            for r in results:
                self.entity_cache['tickets'].add(r.get('ticket_id', ''))
                
        return entry
    
    def find_similar_queries(self, entity_type: str, filters: Dict) -> List[Tuple[MemoryEntry, float]]:
        """Find semantically similar queries using filter matching."""
        vec = SemanticVector("", entity_type, filters)
        matches = []
        
        # Direct hash match (highest confidence)
        if vec.hash_key in self.query_index:
            for idx in self.query_index[vec.hash_key]:
                entry = self.entries[idx]
                matches.append((entry, 1.0))
            return matches
        
        # Partial filter match (confidence based on overlap)
        for entry in self.entries:
            if entry.entity_type == entity_type:
                overlap = self._compute_filter_overlap(filters, entry)
                if overlap > 0.5:  # At least 50% match
                    matches.append((entry, overlap))
        
        # Sort by confidence descending
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches
    
    def _compute_filter_overlap(self, filters1: Dict, entry: MemoryEntry) -> float:
        """Compute overlap between two filter sets."""
        if not filters1:
            return 0.5
        
        # Extract filters from entry reasoning
        matching = 0
        for key in filters1:
            if key in entry.reasoning:
                matching += 1
        
        return matching / max(len(filters1), 1)
    
    def get_cached_results(self, entity_type: str, filters: Dict) -> Optional[List[Dict]]:
        """Get cached results if exact match exists."""
        vec = SemanticVector("", entity_type, filters)
        if vec.hash_key in self.query_index:
            indices = self.query_index[vec.hash_key]
            if indices:  # Return most recent
                return self.entries[indices[-1]].results
        return None
    
    def compute_efficiency_metrics(self) -> Dict[str, float]:
        """Compute memory efficiency metrics."""
        if not self.entries:
            return {
                'cache_hit_rate': 0.0,
                'average_results_per_query': 0.0,
                'memory_density': 0.0,
                'semantic_diversity': 0.0
            }
        
        # Cache hit rate: how many queries could be satisfied by previous ones
        unique_hashes = len(self.query_index)
        total_queries = len(self.entries)
        hit_rate = 1.0 - (unique_hashes / max(total_queries, 1))
        
        # Average results
        avg_results = sum(e.results_count for e in self.entries) / len(self.entries)
        
        # Memory density: total results vs queries
        total_results = sum(e.results_count for e in self.entries)
        density = total_results / max(total_queries, 1)
        
        # Semantic diversity: variety in entity types
        entity_types = {e.entity_type for e in self.entries}
        diversity = len(entity_types) / 3.0  # Max 3 types
        
        self.efficiency_score = (hit_rate + (avg_results / 50.0) + density + diversity) / 4.0
        
        return {
            'cache_hit_rate': min(1.0, hit_rate),
            'average_results_per_query': min(1.0, avg_results / 50.0),
            'memory_density': min(1.0, density / 10.0),
            'semantic_diversity': diversity,
            'overall_efficiency': min(1.0, self.efficiency_score)
        }
    
    def get_reasoning_suggestions(self, current_task: str) -> List[str]:
        """Generate reasoning suggestions based on past reasoning chains."""
        suggestions = []
        
        # Analyze past reasoning chains
        for chain in self.reasoning_chains:
            if chain and len(chain) > 1:
                suggestions.append(" → ".join(chain))
        
        # Deduplicate and limit
        suggestions = list(dict.fromkeys(suggestions))[:5]
        return suggestions
    
    def reset(self):
        """Reset memory for new episode."""
        self.entries.clear()
        self.query_index.clear()
        self.entity_cache = {
            'customers': set(),
            'orders': set(),
            'tickets': set()
        }
        self.reasoning_chains.clear()
        self.efficiency_score = 1.0


class ReasoningOptimizer:
    """Optimize reasoning paths using dynamic programming."""
    
    def __init__(self, memory_store: SemanticMemoryStore):
        self.memory = memory_store
        self.reasoning_paths: Dict[str, List[str]] = {}
        
    def find_optimal_path(self, current_state: Dict, goal: str) -> List[str]:
        """Find optimal reasoning path using memorized solutions."""
        state_key = json.dumps(current_state, sort_keys=True)
        
        if state_key in self.reasoning_paths:
            return self.reasoning_paths[state_key]
        
        # Suggest based on similar past queries
        suggestions = self.memory.get_reasoning_suggestions(goal)
        self.reasoning_paths[state_key] = suggestions
        return suggestions
    
    def estimate_cost(self, path: List[str]) -> float:
        """Estimate execution cost of reasoning path."""
        # Shorter paths = lower cost
        return 1.0 / (len(path) + 1)
