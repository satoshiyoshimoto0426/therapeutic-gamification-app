"""
Query optimization utilities for Firestore repositories
Provides query planning, index optimization, and performance monitoring
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
import logging
from dataclasses import dataclass
from enum import Enum


class QueryType(str, Enum):
    SIMPLE = "simple"
    COMPOUND = "compound"
    RANGE = "range"
    ARRAY_CONTAINS = "array_contains"
    IN_QUERY = "in_query"
    PAGINATION = "pagination"


@dataclass
class QueryPlan:
    """Query execution plan"""
    query_type: QueryType
    estimated_cost: int
    index_required: bool
    suggested_indexes: List[str]
    optimization_hints: List[str]
    execution_time_estimate: float  # seconds


@dataclass
class QueryMetrics:
    """Query performance metrics"""
    query_id: str
    collection_name: str
    query_type: QueryType
    execution_time: float
    documents_read: int
    documents_returned: int
    index_used: bool
    timestamp: datetime


class QueryOptimizer:
    """Query optimization and performance monitoring"""
    
    def __init__(self, db_client: firestore.Client):
        self.db = db_client
        self.logger = logging.getLogger(__name__)
        self.query_metrics: List[QueryMetrics] = []
        
        # Common index patterns for therapeutic app
        self.recommended_indexes = {
            "user_profiles": [
                ["email"],
                ["last_active", "player_level"],
                ["total_xp", "created_at"],
                ["crystal_gauges.self_discipline", "player_level"]
            ],
            "tasks": [
                ["uid", "status"],
                ["uid", "created_at"],
                ["uid", "task_type", "status"],
                ["uid", "due_date", "status"],
                ["mandala_cell_id", "status"],
                ["habit_tag", "uid", "status"]
            ],
            "mood_logs": [
                ["uid", "log_date"],
                ["uid", "mood_score", "log_date"],
                ["log_date", "mood_score"]
            ],
            "story_states": [
                ["uid"],
                ["current_chapter", "last_story_time"],
                ["uid", "current_chapter"]
            ],
            "game_states": [
                ["uid"],
                ["player_level", "total_xp"],
                ["current_chapter", "player_level"]
            ],
            "therapeutic_safety_logs": [
                ["uid", "timestamp"],
                ["content_type", "flagged", "timestamp"],
                ["safety_score", "timestamp"],
                ["uid", "intervention_triggered", "timestamp"]
            ]
        }
    
    def analyze_query(self, collection_name: str, filters: Dict[str, Any], 
                     order_by: str = None, limit: int = None) -> QueryPlan:
        """Analyze query and provide optimization recommendations"""
        try:
            # Determine query type
            query_type = self._classify_query(filters, order_by, limit)
            
            # Estimate query cost
            estimated_cost = self._estimate_query_cost(filters, order_by, limit)
            
            # Check index requirements
            index_required, suggested_indexes = self._analyze_index_requirements(
                collection_name, filters, order_by
            )
            
            # Generate optimization hints
            optimization_hints = self._generate_optimization_hints(
                collection_name, filters, order_by, limit
            )
            
            # Estimate execution time
            execution_time_estimate = self._estimate_execution_time(estimated_cost)
            
            plan = QueryPlan(
                query_type=query_type,
                estimated_cost=estimated_cost,
                index_required=index_required,
                suggested_indexes=suggested_indexes,
                optimization_hints=optimization_hints,
                execution_time_estimate=execution_time_estimate
            )
            
            self.logger.debug(f"Query plan for {collection_name}: {plan}")
            return plan
            
        except Exception as e:
            self.logger.error(f"Failed to analyze query for {collection_name}: {str(e)}")
            # Return default plan
            return QueryPlan(
                query_type=QueryType.SIMPLE,
                estimated_cost=100,
                index_required=False,
                suggested_indexes=[],
                optimization_hints=["Consider adding query analysis"],
                execution_time_estimate=0.1
            )
    
    def _classify_query(self, filters: Dict[str, Any], order_by: str = None, 
                       limit: int = None) -> QueryType:
        """Classify query type based on filters and operations"""
        if not filters:
            return QueryType.SIMPLE
        
        # Check for range queries
        for value in filters.values():
            if isinstance(value, dict) and 'operator' in value:
                operator = value['operator']
                if operator in ['>', '>=', '<', '<=']:
                    return QueryType.RANGE
        
        # Check for array contains
        for value in filters.values():
            if isinstance(value, list):
                return QueryType.ARRAY_CONTAINS
        
        # Check for IN queries
        for value in filters.values():
            if isinstance(value, list) and len(value) > 1:
                return QueryType.IN_QUERY
        
        # Check for compound queries
        if len(filters) > 1:
            return QueryType.COMPOUND
        
        # Check for pagination
        if limit and order_by:
            return QueryType.PAGINATION
        
        return QueryType.SIMPLE
    
    def _estimate_query_cost(self, filters: Dict[str, Any], order_by: str = None, 
                           limit: int = None) -> int:
        """Estimate query cost in terms of document reads"""
        base_cost = 1
        
        # Add cost for each filter
        for field, value in filters.items():
            if isinstance(value, dict) and 'operator' in value:
                # Range queries are more expensive
                base_cost += 5
            elif isinstance(value, list):
                # Array operations are expensive
                base_cost += len(value) * 2
            else:
                # Simple equality filter
                base_cost += 1
        
        # Add cost for ordering
        if order_by:
            base_cost += 2
        
        # Limit reduces cost
        if limit:
            base_cost = min(base_cost, limit)
        
        return base_cost
    
    def _analyze_index_requirements(self, collection_name: str, filters: Dict[str, Any], 
                                  order_by: str = None) -> Tuple[bool, List[str]]:
        """Analyze index requirements for query"""
        required_fields = list(filters.keys())
        
        if order_by and order_by not in required_fields:
            required_fields.append(order_by)
        
        # Check if we have recommended indexes for this pattern
        recommended = self.recommended_indexes.get(collection_name, [])
        
        suggested_indexes = []
        index_required = False
        
        # For compound queries, suggest composite indexes
        if len(required_fields) > 1:
            index_required = True
            suggested_indexes.append(required_fields)
        
        # Check against existing recommendations
        for index_fields in recommended:
            if all(field in index_fields for field in required_fields[:2]):  # Check first 2 fields
                suggested_indexes.append(index_fields)
                break
        
        return index_required, suggested_indexes
    
    def _generate_optimization_hints(self, collection_name: str, filters: Dict[str, Any], 
                                   order_by: str = None, limit: int = None) -> List[str]:
        """Generate query optimization hints"""
        hints = []
        
        # Check for inefficient patterns
        if len(filters) > 3:
            hints.append("Consider reducing the number of filters for better performance")
        
        # Check for missing limits
        if not limit and len(filters) <= 1:
            hints.append("Consider adding a limit to prevent large result sets")
        
        # Check for range queries without limits
        for value in filters.values():
            if isinstance(value, dict) and value.get('operator') in ['>', '>=', '<', '<=']:
                if not limit:
                    hints.append("Range queries should include limits to prevent full collection scans")
                break
        
        # Check for ordering without limits
        if order_by and not limit:
            hints.append("Ordered queries should include limits for better performance")
        
        # Collection-specific hints
        if collection_name == "tasks":
            if "uid" not in filters:
                hints.append("Task queries should always include uid filter for data isolation")
        
        elif collection_name == "mood_logs":
            if "uid" not in filters:
                hints.append("Mood queries should always include uid filter for privacy")
        
        elif collection_name == "therapeutic_safety_logs":
            if "timestamp" not in filters and not order_by == "timestamp":
                hints.append("Safety log queries should include timestamp for efficient retrieval")
        
        return hints
    
    def _estimate_execution_time(self, estimated_cost: int) -> float:
        """Estimate query execution time based on cost"""
        # Base time per document read (milliseconds)
        base_time_ms = 2.0
        
        # Network latency
        network_latency_ms = 50.0
        
        # Calculate total time
        total_time_ms = network_latency_ms + (estimated_cost * base_time_ms)
        
        # Convert to seconds
        return total_time_ms / 1000.0
    
    def record_query_metrics(self, collection_name: str, query_type: QueryType,
                           execution_time: float, documents_read: int,
                           documents_returned: int, index_used: bool = True) -> None:
        """Record query performance metrics"""
        try:
            metrics = QueryMetrics(
                query_id=f"{collection_name}_{datetime.utcnow().timestamp()}",
                collection_name=collection_name,
                query_type=query_type,
                execution_time=execution_time,
                documents_read=documents_read,
                documents_returned=documents_returned,
                index_used=index_used,
                timestamp=datetime.utcnow()
            )
            
            self.query_metrics.append(metrics)
            
            # Keep only recent metrics (last 1000 queries)
            if len(self.query_metrics) > 1000:
                self.query_metrics = self.query_metrics[-1000:]
            
            # Log slow queries
            if execution_time > 1.0:  # Queries taking more than 1 second
                self.logger.warning(
                    f"Slow query detected: {collection_name} took {execution_time:.2f}s, "
                    f"read {documents_read} docs, returned {documents_returned} docs"
                )
            
        except Exception as e:
            self.logger.error(f"Failed to record query metrics: {str(e)}")
    
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get query performance summary for the last N hours"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            recent_metrics = [m for m in self.query_metrics if m.timestamp >= cutoff_time]
            
            if not recent_metrics:
                return {"error": "No recent query metrics available"}
            
            # Calculate statistics
            total_queries = len(recent_metrics)
            avg_execution_time = sum(m.execution_time for m in recent_metrics) / total_queries
            total_documents_read = sum(m.documents_read for m in recent_metrics)
            total_documents_returned = sum(m.documents_returned for m in recent_metrics)
            
            # Find slow queries
            slow_queries = [m for m in recent_metrics if m.execution_time > 1.0]
            
            # Group by collection
            collection_stats = {}
            for metric in recent_metrics:
                collection = metric.collection_name
                if collection not in collection_stats:
                    collection_stats[collection] = {
                        "query_count": 0,
                        "avg_execution_time": 0,
                        "total_documents_read": 0
                    }
                
                collection_stats[collection]["query_count"] += 1
                collection_stats[collection]["total_documents_read"] += metric.documents_read
            
            # Calculate averages
            for collection, stats in collection_stats.items():
                collection_metrics = [m for m in recent_metrics if m.collection_name == collection]
                stats["avg_execution_time"] = sum(m.execution_time for m in collection_metrics) / len(collection_metrics)
            
            # Group by query type
            query_type_stats = {}
            for metric in recent_metrics:
                query_type = metric.query_type.value
                if query_type not in query_type_stats:
                    query_type_stats[query_type] = 0
                query_type_stats[query_type] += 1
            
            summary = {
                "period_hours": hours,
                "total_queries": total_queries,
                "average_execution_time": round(avg_execution_time, 3),
                "total_documents_read": total_documents_read,
                "total_documents_returned": total_documents_returned,
                "read_efficiency": round(total_documents_returned / total_documents_read * 100, 2) if total_documents_read > 0 else 0,
                "slow_queries_count": len(slow_queries),
                "collection_stats": collection_stats,
                "query_type_distribution": query_type_stats,
                "index_usage_rate": round(sum(1 for m in recent_metrics if m.index_used) / total_queries * 100, 2)
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to generate performance summary: {str(e)}")
            return {"error": "Failed to generate performance summary"}
    
    def suggest_index_creation(self, collection_name: str) -> List[Dict[str, Any]]:
        """Suggest indexes to create based on query patterns"""
        try:
            # Analyze recent queries for this collection
            recent_metrics = [m for m in self.query_metrics[-100:] if m.collection_name == collection_name]
            
            if not recent_metrics:
                # Return recommended indexes for this collection
                recommended = self.recommended_indexes.get(collection_name, [])
                return [{"fields": fields, "reason": "Recommended for common queries"} for fields in recommended]
            
            # Find queries that might benefit from indexes
            slow_queries = [m for m in recent_metrics if m.execution_time > 0.5 and not m.index_used]
            
            suggestions = []
            
            # Add collection-specific recommendations
            if collection_name in self.recommended_indexes:
                for index_fields in self.recommended_indexes[collection_name]:
                    suggestions.append({
                        "fields": index_fields,
                        "reason": f"Recommended for {collection_name} queries",
                        "priority": "high" if any("uid" in index_fields) else "medium"
                    })
            
            # Add suggestions based on slow queries
            if slow_queries:
                suggestions.append({
                    "fields": ["timestamp"],
                    "reason": f"Found {len(slow_queries)} slow queries that might benefit from timestamp index",
                    "priority": "medium"
                })
            
            return suggestions
            
        except Exception as e:
            self.logger.error(f"Failed to suggest indexes for {collection_name}: {str(e)}")
            return []
    
    def optimize_query_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize query filters for better performance"""
        try:
            optimized_filters = filters.copy()
            
            # Move most selective filters first (Firestore optimization)
            # This is more of a documentation/planning optimization
            # as Firestore handles filter ordering internally
            
            # Convert IN queries with single values to equality
            for field, value in optimized_filters.items():
                if isinstance(value, list) and len(value) == 1:
                    optimized_filters[field] = value[0]
            
            # Remove redundant filters
            # (This would require more complex analysis in a real implementation)
            
            return optimized_filters
            
        except Exception as e:
            self.logger.error(f"Failed to optimize query filters: {str(e)}")
            return filters
    
    def get_query_recommendations(self, collection_name: str) -> List[str]:
        """Get general query recommendations for a collection"""
        recommendations = []
        
        # General recommendations
        recommendations.extend([
            "Always include user-specific filters (uid) for data isolation",
            "Use limits on queries that might return large result sets",
            "Consider pagination for queries returning more than 50 documents",
            "Use composite indexes for multi-field queries",
            "Avoid queries with more than 3 filters when possible"
        ])
        
        # Collection-specific recommendations
        if collection_name == "tasks":
            recommendations.extend([
                "Filter by uid and status for task lists",
                "Use date ranges with limits for task history",
                "Index on (uid, task_type, status) for filtered task views"
            ])
        
        elif collection_name == "mood_logs":
            recommendations.extend([
                "Always filter by uid for privacy",
                "Use date ranges for mood history queries",
                "Index on (uid, log_date) for efficient mood retrieval"
            ])
        
        elif collection_name == "therapeutic_safety_logs":
            recommendations.extend([
                "Include timestamp filters for recent safety checks",
                "Filter by content_type for specific safety analysis",
                "Use flagged field for quick identification of concerning content"
            ])
        
        return recommendations


class QueryProfiler:
    """Query profiling and performance monitoring"""
    
    def __init__(self, optimizer: QueryOptimizer):
        self.optimizer = optimizer
        self.logger = logging.getLogger(__name__)
    
    def profile_query(self, collection_name: str, query_func, *args, **kwargs):
        """Profile a query execution"""
        start_time = datetime.utcnow()
        
        try:
            # Execute the query
            result = query_func(*args, **kwargs)
            
            # Calculate execution time
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            # Estimate documents read/returned
            documents_returned = len(result) if isinstance(result, list) else 1
            documents_read = documents_returned  # Simplified estimation
            
            # Record metrics
            self.optimizer.record_query_metrics(
                collection_name=collection_name,
                query_type=QueryType.SIMPLE,  # Would need more analysis to determine
                execution_time=execution_time,
                documents_read=documents_read,
                documents_returned=documents_returned,
                index_used=True  # Assume index is used unless we can detect otherwise
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Query profiling failed for {collection_name}: {str(e)}")
            raise
    
    async def profile_async_query(self, collection_name: str, query_func, *args, **kwargs):
        """Profile an async query execution"""
        start_time = datetime.utcnow()
        
        try:
            # Execute the async query
            result = await query_func(*args, **kwargs)
            
            # Calculate execution time
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            # Estimate documents read/returned
            documents_returned = len(result) if isinstance(result, list) else 1
            documents_read = documents_returned  # Simplified estimation
            
            # Record metrics
            self.optimizer.record_query_metrics(
                collection_name=collection_name,
                query_type=QueryType.SIMPLE,  # Would need more analysis to determine
                execution_time=execution_time,
                documents_read=documents_read,
                documents_returned=documents_returned,
                index_used=True  # Assume index is used unless we can detect otherwise
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Async query profiling failed for {collection_name}: {str(e)}")
            raise