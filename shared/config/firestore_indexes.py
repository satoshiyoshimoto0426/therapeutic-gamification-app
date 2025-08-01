"""
Firestore indexes configuration for optimal query performance
Supports complex queries for therapeutic gamification features
"""

from typing import Dict, List, Any

# Composite indexes for complex queries
FIRESTORE_INDEXES = [
    # User profiles - performance critical queries
    {
        "collectionGroup": "user_profiles",
        "fields": [
            {"fieldPath": "email", "order": "ASCENDING"},
            {"fieldPath": "last_active", "order": "DESCENDING"}
        ]
    },
    {
        "collectionGroup": "user_profiles",
        "fields": [
            {"fieldPath": "player_level", "order": "DESCENDING"},
            {"fieldPath": "total_xp", "order": "DESCENDING"},
            {"fieldPath": "created_at", "order": "ASCENDING"}
        ]
    },
    {
        "collectionGroup": "user_profiles",
        "fields": [
            {"fieldPath": "care_points", "order": "DESCENDING"},
            {"fieldPath": "subscription_status", "order": "ASCENDING"}
        ]
    },
    
    # Tasks - multi-dimensional queries for task management
    {
        "collectionGroup": "tasks",
        "fields": [
            {"fieldPath": "uid", "order": "ASCENDING"},
            {"fieldPath": "status", "order": "ASCENDING"},
            {"fieldPath": "due_date", "order": "ASCENDING"}
        ]
    },
    {
        "collectionGroup": "tasks",
        "fields": [
            {"fieldPath": "uid", "order": "ASCENDING"},
            {"fieldPath": "task_type", "order": "ASCENDING"},
            {"fieldPath": "created_at", "order": "DESCENDING"}
        ]
    },
    {
        "collectionGroup": "tasks",
        "fields": [
            {"fieldPath": "uid", "order": "ASCENDING"},
            {"fieldPath": "status", "order": "ASCENDING"},
            {"fieldPath": "difficulty", "order": "DESCENDING"}
        ]
    },
    {
        "collectionGroup": "tasks",
        "fields": [
            {"fieldPath": "mandala_cell_id", "order": "ASCENDING"},
            {"fieldPath": "status", "order": "ASCENDING"},
            {"fieldPath": "completed_at", "order": "DESCENDING"}
        ]
    },
    {
        "collectionGroup": "tasks",
        "fields": [
            {"fieldPath": "habit_tag", "order": "ASCENDING"},
            {"fieldPath": "status", "order": "ASCENDING"},
            {"fieldPath": "created_at", "order": "DESCENDING"}
        ]
    },
    {
        "collectionGroup": "tasks",
        "fields": [
            {"fieldPath": "uid", "order": "ASCENDING"},
            {"fieldPath": "completed_at", "order": "DESCENDING"},
            {"fieldPath": "xp_earned", "order": "DESCENDING"}
        ]
    },
    
    # Story states - story progression queries
    {
        "collectionGroup": "story_states",
        "fields": [
            {"fieldPath": "uid", "order": "ASCENDING"},
            {"fieldPath": "current_chapter", "order": "ASCENDING"},
            {"fieldPath": "last_generation_time", "order": "DESCENDING"}
        ]
    },
    {
        "collectionGroup": "story_states",
        "fields": [
            {"fieldPath": "uid", "order": "ASCENDING"},
            {"fieldPath": "unlocked_chapters", "arrayContains": True},
            {"fieldPath": "last_generation_time", "order": "DESCENDING"}
        ]
    },
    
    # Story nodes - content discovery queries
    {
        "collectionGroup": "story_nodes",
        "fields": [
            {"fieldPath": "chapter_type", "order": "ASCENDING"},
            {"fieldPath": "node_type", "order": "ASCENDING"},
            {"fieldPath": "therapeutic_elements", "arrayContains": True}
        ]
    },
    {
        "collectionGroup": "story_nodes",
        "fields": [
            {"fieldPath": "therapeutic_tags", "arrayContains": True},
            {"fieldPath": "estimated_read_time", "order": "ASCENDING"}
        ]
    },
    {
        "collectionGroup": "story_nodes",
        "fields": [
            {"fieldPath": "chapter_type", "order": "ASCENDING"},
            {"fieldPath": "unlock_conditions", "arrayContains": True}
        ]
    },
    
    # Story edges - choice and task linking queries
    {
        "collectionGroup": "story_edges",
        "fields": [
            {"fieldPath": "from_node", "order": "ASCENDING"},
            {"fieldPath": "xp_reward", "order": "DESCENDING"}
        ]
    },
    {
        "collectionGroup": "story_edges",
        "fields": [
            {"fieldPath": "real_task_id", "order": "ASCENDING"},
            {"fieldPath": "created_at", "order": "DESCENDING"}
        ]
    },
    {
        "collectionGroup": "story_edges",
        "fields": [
            {"fieldPath": "habit_tag", "order": "ASCENDING"},
            {"fieldPath": "therapeutic_outcome", "order": "ASCENDING"}
        ]
    },
    
    # Mood logs - temporal and analytical queries
    {
        "collectionGroup": "mood_logs",
        "fields": [
            {"fieldPath": "uid", "order": "ASCENDING"},
            {"fieldPath": "log_date", "order": "DESCENDING"}
        ]
    },
    {
        "collectionGroup": "mood_logs",
        "fields": [
            {"fieldPath": "uid", "order": "ASCENDING"},
            {"fieldPath": "mood_score", "order": "ASCENDING"},
            {"fieldPath": "log_date", "order": "DESCENDING"}
        ]
    },
    {
        "collectionGroup": "mood_logs",
        "fields": [
            {"fieldPath": "uid", "order": "ASCENDING"},
            {"fieldPath": "energy_level", "order": "ASCENDING"},
            {"fieldPath": "stress_level", "order": "ASCENDING"},
            {"fieldPath": "log_date", "order": "DESCENDING"}
        ]
    },
    {
        "collectionGroup": "mood_logs",
        "fields": [
            {"fieldPath": "log_date", "order": "DESCENDING"},
            {"fieldPath": "mood_score", "order": "ASCENDING"}
        ]
    },
    
    # Mandala grids - progress tracking queries
    {
        "collectionGroup": "mandala_grids",
        "fields": [
            {"fieldPath": "uid", "order": "ASCENDING"},
            {"fieldPath": "completion_percentage", "order": "DESCENDING"}
        ]
    },
    {
        "collectionGroup": "mandala_grids",
        "fields": [
            {"fieldPath": "completion_percentage", "order": "DESCENDING"},
            {"fieldPath": "updated_at", "order": "DESCENDING"}
        ]
    },
    {
        "collectionGroup": "mandala_grids",
        "fields": [
            {"fieldPath": "uid", "order": "ASCENDING"},
            {"fieldPath": "chapter_progress", "arrayContains": True}
        ]
    },
    
    # Guardian links - permission and relationship queries
    {
        "collectionGroup": "guardian_links",
        "fields": [
            {"fieldPath": "guardian_id", "order": "ASCENDING"},
            {"fieldPath": "approved_by_user", "order": "ASCENDING"},
            {"fieldPath": "created_at", "order": "DESCENDING"}
        ]
    },
    {
        "collectionGroup": "guardian_links",
        "fields": [
            {"fieldPath": "user_id", "order": "ASCENDING"},
            {"fieldPath": "permission_level", "order": "ASCENDING"},
            {"fieldPath": "weekly_report_enabled", "order": "ASCENDING"}
        ]
    },
    {
        "collectionGroup": "guardian_links",
        "fields": [
            {"fieldPath": "guardian_id", "order": "ASCENDING"},
            {"fieldPath": "care_points_allocated", "order": "DESCENDING"}
        ]
    },
    
    # Game states - leaderboard and progression queries
    {
        "collectionGroup": "game_states",
        "fields": [
            {"fieldPath": "player_level", "order": "DESCENDING"},
            {"fieldPath": "total_xp", "order": "DESCENDING"}
        ]
    },
    {
        "collectionGroup": "game_states",
        "fields": [
            {"fieldPath": "uid", "order": "ASCENDING"},
            {"fieldPath": "last_resonance_check", "order": "ASCENDING"}
        ]
    },
    {
        "collectionGroup": "game_states",
        "fields": [
            {"fieldPath": "resonance_events", "order": "DESCENDING"},
            {"fieldPath": "updated_at", "order": "DESCENDING"}
        ]
    },
    
    # Therapeutic safety logs - monitoring and analysis queries
    {
        "collectionGroup": "therapeutic_safety_logs",
        "fields": [
            {"fieldPath": "uid", "order": "ASCENDING"},
            {"fieldPath": "timestamp", "order": "DESCENDING"}
        ]
    },
    {
        "collectionGroup": "therapeutic_safety_logs",
        "fields": [
            {"fieldPath": "flagged", "order": "ASCENDING"},
            {"fieldPath": "safety_score", "order": "ASCENDING"},
            {"fieldPath": "timestamp", "order": "DESCENDING"}
        ]
    },
    {
        "collectionGroup": "therapeutic_safety_logs",
        "fields": [
            {"fieldPath": "intervention_triggered", "order": "ASCENDING"},
            {"fieldPath": "cbt_intervention_type", "order": "ASCENDING"},
            {"fieldPath": "timestamp", "order": "DESCENDING"}
        ]
    },
    {
        "collectionGroup": "therapeutic_safety_logs",
        "fields": [
            {"fieldPath": "content_type", "order": "ASCENDING"},
            {"fieldPath": "safety_score", "order": "ASCENDING"},
            {"fieldPath": "timestamp", "order": "DESCENDING"}
        ]
    },
    
    # ADHD support settings - configuration queries
    {
        "collectionGroup": "adhd_support_settings",
        "fields": [
            {"fieldPath": "pomodoro_enabled", "order": "ASCENDING"},
            {"fieldPath": "daily_task_limit", "order": "ASCENDING"}
        ]
    },
    {
        "collectionGroup": "adhd_support_settings",
        "fields": [
            {"fieldPath": "uid", "order": "ASCENDING"},
            {"fieldPath": "updated_at", "order": "DESCENDING"}
        ]
    }
]

# TTL (Time To Live) configurations for automatic cleanup
TTL_CONFIGURATIONS = {
    "therapeutic_safety_logs": {
        "field": "timestamp",
        "duration_days": 365  # Keep safety logs for 1 year
    },
    "mood_logs": {
        "field": "created_at", 
        "duration_days": 1095  # Keep mood logs for 3 years
    },
    "story_states": {
        "field": "last_generation_time",
        "duration_days": 30  # Clean up inactive story states after 30 days
    }
}

# Query optimization hints
QUERY_OPTIMIZATION_HINTS = {
    "user_leaderboard": {
        "collection": "game_states",
        "suggested_index": ["player_level", "DESC", "total_xp", "DESC"],
        "limit_recommendation": 100,
        "cache_duration_minutes": 15
    },
    "daily_tasks_by_user": {
        "collection": "tasks", 
        "suggested_index": ["uid", "ASC", "created_at", "DESC"],
        "filter_recommendation": "WHERE DATE(created_at) = TODAY()",
        "limit_recommendation": 16  # ADHD daily task limit
    },
    "mood_trend_analysis": {
        "collection": "mood_logs",
        "suggested_index": ["uid", "ASC", "log_date", "DESC"],
        "limit_recommendation": 30,  # 30 days of mood data
        "aggregation_hint": "Use client-side aggregation for trend calculation"
    },
    "story_progression_check": {
        "collection": "story_states",
        "suggested_index": ["uid", "ASC", "current_chapter", "ASC"],
        "cache_duration_minutes": 5,
        "real_time_updates": True
    },
    "guardian_dashboard": {
        "collection": "guardian_links",
        "suggested_index": ["guardian_id", "ASC", "approved_by_user", "ASC"],
        "join_collections": ["user_profiles", "tasks", "mood_logs"],
        "cache_duration_minutes": 10
    }
}

def get_index_for_query(collection: str, fields: List[str]) -> Dict[str, Any]:
    """Find the best index for a given query pattern"""
    for index in FIRESTORE_INDEXES:
        if index["collectionGroup"] == collection:
            index_fields = [field["fieldPath"] for field in index["fields"]]
            if all(field in index_fields for field in fields):
                return index
    return None

def get_ttl_config(collection: str) -> Dict[str, Any]:
    """Get TTL configuration for a collection"""
    return TTL_CONFIGURATIONS.get(collection, {})

def get_optimization_hint(query_type: str) -> Dict[str, Any]:
    """Get optimization hints for common query patterns"""
    return QUERY_OPTIMIZATION_HINTS.get(query_type, {})

# Index creation script for Firebase CLI
def generate_firestore_indexes_json() -> Dict[str, Any]:
    """Generate firestore.indexes.json for Firebase deployment"""
    return {
        "indexes": FIRESTORE_INDEXES,
        "fieldOverrides": [
            {
                "collectionGroup": "therapeutic_safety_logs",
                "fieldPath": "timestamp",
                "ttl": True
            },
            {
                "collectionGroup": "mood_logs", 
                "fieldPath": "created_at",
                "ttl": True
            }
        ]
    }

# Performance monitoring queries
PERFORMANCE_MONITORING_QUERIES = {
    "slow_queries": """
    SELECT 
      collection_id,
      query_type,
      avg_execution_time_ms,
      p95_execution_time_ms,
      query_count
    FROM firestore_query_stats 
    WHERE avg_execution_time_ms > 1200  -- 1.2 second threshold
    ORDER BY avg_execution_time_ms DESC
    """,
    
    "index_usage": """
    SELECT 
      collection_id,
      index_name,
      usage_count,
      last_used_timestamp
    FROM firestore_index_stats
    WHERE usage_count = 0 
    AND created_timestamp < TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
    """,
    
    "hot_collections": """
    SELECT 
      collection_id,
      read_count,
      write_count,
      delete_count,
      total_operations
    FROM firestore_collection_stats
    WHERE total_operations > 10000
    ORDER BY total_operations DESC
    """
}