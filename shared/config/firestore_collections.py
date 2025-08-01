"""
Firestore collections schema for therapeutic gamification app
Comprehensive collection definitions with data integrity constraints and indexes
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

class TaskType(Enum):
    ROUTINE = "routine"
    ONE_SHOT = "one_shot"
    SKILL_UP = "skill_up"
    SOCIAL = "social"

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class StoryNodeType(Enum):
    OPENING = "opening"
    CHOICE = "choice"
    OUTCOME = "outcome"
    REFLECTION = "reflection"

class CrystalAttribute(Enum):
    SELF_DISCIPLINE = "self_discipline"
    EMPATHY = "empathy"
    RESILIENCE = "resilience"
    CURIOSITY = "curiosity"
    COMMUNICATION = "communication"
    CREATIVITY = "creativity"
    COURAGE = "courage"
    WISDOM = "wisdom"

# Collection schemas with validation rules
COLLECTION_SCHEMAS = {
    "user_profiles": {
        "description": "ユーザー",
        "required_fields": [
            "uid", "email", "display_name", "created_at", "last_active",
            "player_level", "yu_level", "total_xp", "crystal_gauges"
        ],
        "optional_fields": [
            "adhd_profile", "therapeutic_goals", "guardian_links",
            "care_points", "subscription_status", "preferences"
        ],
        "validation_rules": {
            "player_level": {"type": "int", "min": 1, "max": 100},
            "yu_level": {"type": "int", "min": 1, "max": 100},
            "total_xp": {"type": "int", "min": 0},
            "crystal_gauges": {"type": "dict", "keys": [attr.value for attr in CrystalAttribute]},
            "email": {"type": "string", "format": "email"}
        },
        "indexes": [
            ["email"],
            ["last_active", "DESC"],
            ["player_level", "DESC", "created_at", "ASC"],
            ["care_points", "DESC"]
        ]
    },
    
    "tasks": {
        "description": "タスク4?",
        "required_fields": [
            "task_id", "uid", "task_type", "title", "description",
            "difficulty", "status", "created_at"
        ],
        "optional_fields": [
            "due_date", "completed_at", "xp_earned", "mood_coefficient",
            "adhd_assist", "mandala_cell_id", "habit_tag", "pomodoro_sessions",
            "linked_story_edge", "estimated_duration"
        ],
        "validation_rules": {
            "task_type": {"type": "enum", "values": [t.value for t in TaskType]},
            "status": {"type": "enum", "values": [s.value for s in TaskStatus]},
            "difficulty": {"type": "int", "min": 1, "max": 5},
            "xp_earned": {"type": "int", "min": 0},
            "mood_coefficient": {"type": "float", "min": 0.8, "max": 1.2},
            "adhd_assist": {"type": "float", "min": 1.0, "max": 1.3}
        },
        "indexes": [
            ["uid", "status", "due_date"],
            ["uid", "task_type", "created_at", "DESC"],
            ["mandala_cell_id", "status"],
            ["habit_tag", "status"],
            ["uid", "completed_at", "DESC"]
        ]
    },
    
    "story_states": {
        "description": "ユーザー",
        "required_fields": [
            "uid", "current_chapter", "current_node", "story_history",
            "last_generation_time", "available_edges"
        ],
        "optional_fields": [
            "unlocked_chapters", "completed_nodes", "choice_history",
            "therapeutic_insights", "personalization_data"
        ],
        "validation_rules": {
            "current_chapter": {"type": "enum", "values": [attr.value for attr in CrystalAttribute]},
            "story_history": {"type": "array", "max_length": 1000},
            "available_edges": {"type": "array", "max_length": 10}
        },
        "indexes": [
            ["uid"],
            ["uid", "last_generation_time", "DESC"],
            ["current_chapter", "current_node"]
        ]
    },
    
    "story_nodes": {
        "description": "ストーリーDAG?",
        "required_fields": [
            "node_id", "chapter_type", "node_type", "title", "content",
            "therapeutic_elements", "estimated_read_time"
        ],
        "optional_fields": [
            "unlock_conditions", "therapeutic_tags", "mood_requirements",
            "xp_requirements", "predecessor_nodes", "successor_edges"
        ],
        "validation_rules": {
            "chapter_type": {"type": "enum", "values": [attr.value for attr in CrystalAttribute]},
            "node_type": {"type": "enum", "values": [t.value for t in StoryNodeType]},
            "estimated_read_time": {"type": "int", "min": 1, "max": 30},
            "therapeutic_elements": {"type": "array", "items": "string"}
        },
        "indexes": [
            ["chapter_type", "node_type"],
            ["therapeutic_tags"],
            ["unlock_conditions"]
        ]
    },
    
    "story_edges": {
        "description": "ストーリー",
        "required_fields": [
            "edge_id", "from_node", "to_node", "choice_text", "created_at"
        ],
        "optional_fields": [
            "real_task_id", "habit_tag", "xp_reward", "therapeutic_outcome",
            "unlock_conditions", "mood_impact", "difficulty_modifier"
        ],
        "validation_rules": {
            "xp_reward": {"type": "int", "min": 0, "max": 500},
            "mood_impact": {"type": "float", "min": -0.5, "max": 0.5},
            "difficulty_modifier": {"type": "float", "min": 0.5, "max": 2.0}
        },
        "indexes": [
            ["from_node"],
            ["to_node"],
            ["real_task_id"],
            ["habit_tag"]
        ]
    },
    
    "mood_logs": {
        "description": "?XP係数",
        "required_fields": [
            "uid", "log_date", "mood_score", "mood_coefficient", "created_at"
        ],
        "optional_fields": [
            "notes", "energy_level", "stress_level", "sleep_quality",
            "medication_taken", "therapeutic_activities", "triggers"
        ],
        "validation_rules": {
            "mood_score": {"type": "int", "min": 1, "max": 5},
            "mood_coefficient": {"type": "float", "min": 0.8, "max": 1.2},
            "energy_level": {"type": "int", "min": 1, "max": 5},
            "stress_level": {"type": "int", "min": 1, "max": 5},
            "sleep_quality": {"type": "int", "min": 1, "max": 5}
        },
        "indexes": [
            ["uid", "log_date", "DESC"],
            ["uid", "mood_score", "log_date", "DESC"],
            ["log_date", "DESC"]
        ]
    },
    
    "mandala_grids": {
        "description": "9x9 Mandala?",
        "required_fields": [
            "uid", "grid_data", "unlocked_cells", "center_values", "updated_at"
        ],
        "optional_fields": [
            "completion_percentage", "chapter_progress", "memory_cells",
            "act_therapy_values", "personalized_goals"
        ],
        "validation_rules": {
            "grid_data": {"type": "array", "length": 81},
            "unlocked_cells": {"type": "int", "min": 0, "max": 81},
            "completion_percentage": {"type": "float", "min": 0.0, "max": 100.0}
        },
        "indexes": [
            ["uid"],
            ["completion_percentage", "DESC"],
            ["updated_at", "DESC"]
        ]
    },
    
    "guardian_links": {
        "description": "?RBAC?",
        "required_fields": [
            "link_id", "guardian_id", "user_id", "permission_level",
            "created_at", "approved_by_user"
        ],
        "optional_fields": [
            "relationship_type", "care_points_allocated", "weekly_report_enabled",
            "emergency_contact", "medical_discount_applied", "notes"
        ],
        "validation_rules": {
            "permission_level": {"type": "enum", "values": ["view_only", "task_edit", "chat_send"]},
            "approved_by_user": {"type": "boolean"},
            "care_points_allocated": {"type": "int", "min": 0},
            "medical_discount_applied": {"type": "boolean"}
        },
        "indexes": [
            ["guardian_id", "approved_by_user"],
            ["user_id", "permission_level"],
            ["guardian_id", "user_id"]
        ]
    },
    
    "game_states": {
        "description": "ゲームXP管理",
        "required_fields": [
            "uid", "player_level", "yu_level", "total_xp", "crystal_gauges",
            "resonance_events", "last_resonance_check", "updated_at"
        ],
        "optional_fields": [
            "level_up_history", "xp_sources", "daily_xp_earned",
            "weekly_xp_earned", "achievement_unlocked", "bonus_multipliers"
        ],
        "validation_rules": {
            "player_level": {"type": "int", "min": 1, "max": 100},
            "yu_level": {"type": "int", "min": 1, "max": 100},
            "total_xp": {"type": "int", "min": 0},
            "resonance_events": {"type": "int", "min": 0}
        },
        "indexes": [
            ["uid"],
            ["player_level", "DESC"],
            ["total_xp", "DESC"],
            ["last_resonance_check"]
        ]
    },
    
    "therapeutic_safety_logs": {
        "description": "治療CBT?",
        "required_fields": [
            "uid", "content_type", "original_content", "safety_score",
            "flagged", "intervention_triggered", "timestamp"
        ],
        "optional_fields": [
            "moderation_result", "custom_filter_result", "cbt_intervention_type",
            "intervention_content", "user_response", "follow_up_required"
        ],
        "validation_rules": {
            "safety_score": {"type": "float", "min": 0.0, "max": 1.0},
            "flagged": {"type": "boolean"},
            "intervention_triggered": {"type": "boolean"},
            "content_type": {"type": "enum", "values": ["story", "task", "mood", "chat"]}
        },
        "indexes": [
            ["uid", "timestamp", "DESC"],
            ["flagged", "timestamp", "DESC"],
            ["intervention_triggered", "timestamp", "DESC"],
            ["safety_score", "timestamp", "DESC"]
        ]
    },
    
    "adhd_support_settings": {
        "description": "ADHD支援",
        "required_fields": [
            "uid", "pomodoro_enabled", "break_reminders", "daily_task_limit",
            "cognitive_load_settings", "updated_at"
        ],
        "optional_fields": [
            "font_preferences", "color_scheme", "animation_reduced",
            "notification_schedule", "buffer_extensions_used", "time_perception_aids"
        ],
        "validation_rules": {
            "daily_task_limit": {"type": "int", "min": 1, "max": 16},
            "buffer_extensions_used": {"type": "int", "min": 0, "max": 2},
            "pomodoro_enabled": {"type": "boolean"},
            "break_reminders": {"type": "boolean"}
        },
        "indexes": [
            ["uid"],
            ["pomodoro_enabled"],
            ["updated_at", "DESC"]
        ]
    }
}

# Firestore security rules
FIRESTORE_SECURITY_RULES = """
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Helper functions
    function isAuthenticated() {
      return request.auth != null;
    }
    
    function isOwner(uid) {
      return request.auth.uid == uid;
    }
    
    function isGuardianOf(userId) {
      return exists(/databases/$(database)/documents/guardian_links/$(request.auth.uid + '_' + userId)) &&
             get(/databases/$(database)/documents/guardian_links/$(request.auth.uid + '_' + userId)).data.approved_by_user == true;
    }
    
    function hasGuardianPermission(userId, requiredLevel) {
      let link = get(/databases/$(database)/documents/guardian_links/$(request.auth.uid + '_' + userId));
      let permissionLevels = ['view_only', 'task_edit', 'chat_send'];
      let userLevel = permissionLevels.indexOf(link.data.permission_level);
      let required = permissionLevels.indexOf(requiredLevel);
      return userLevel >= required;
    }
    
    // User profiles - users can manage their own data
    match /user_profiles/{userId} {
      allow read: if isAuthenticated() && (isOwner(userId) || isGuardianOf(userId));
      allow write: if isAuthenticated() && isOwner(userId);
    }
    
    // Tasks - users and guardians with task_edit permission
    match /tasks/{taskId} {
      allow read: if isAuthenticated() && 
        (isOwner(resource.data.uid) || isGuardianOf(resource.data.uid));
      allow write: if isAuthenticated() && 
        (isOwner(resource.data.uid) || 
         (isGuardianOf(resource.data.uid) && hasGuardianPermission(resource.data.uid, 'task_edit')));
    }
    
    // Story states - users can manage their own story progress
    match /story_states/{stateId} {
      allow read, write: if isAuthenticated() && isOwner(resource.data.uid);
    }
    
    // Story nodes and edges - read-only for authenticated users
    match /story_nodes/{nodeId} {
      allow read: if isAuthenticated();
      allow write: if false; // Only system can write
    }
    
    match /story_edges/{edgeId} {
      allow read: if isAuthenticated();
      allow write: if false; // Only system can write
    }
    
    // Mood logs - users can manage their own mood data
    match /mood_logs/{moodId} {
      allow read: if isAuthenticated() && 
        (isOwner(resource.data.uid) || isGuardianOf(resource.data.uid));
      allow write: if isAuthenticated() && isOwner(resource.data.uid);
    }
    
    // Mandala grids - users can manage their own grids
    match /mandala_grids/{gridId} {
      allow read: if isAuthenticated() && 
        (isOwner(resource.data.uid) || isGuardianOf(resource.data.uid));
      allow write: if isAuthenticated() && isOwner(resource.data.uid);
    }
    
    // Guardian links - special permission handling
    match /guardian_links/{linkId} {
      allow read: if isAuthenticated() && 
        (request.auth.uid == resource.data.guardian_id || 
         request.auth.uid == resource.data.user_id);
      allow create: if isAuthenticated() && 
        request.auth.uid == request.resource.data.guardian_id;
      allow update: if isAuthenticated() && 
        request.auth.uid == resource.data.user_id;
      allow delete: if isAuthenticated() && 
        (request.auth.uid == resource.data.guardian_id || 
         request.auth.uid == resource.data.user_id);
    }
    
    // Game states - users can manage their own game state
    match /game_states/{userId} {
      allow read: if isAuthenticated() && 
        (isOwner(userId) || isGuardianOf(userId));
      allow write: if isAuthenticated() && isOwner(userId);
    }
    
    // Therapeutic safety logs - read-only for users, system writes
    match /therapeutic_safety_logs/{logId} {
      allow read: if isAuthenticated() && isOwner(resource.data.uid);
      allow write: if false; // Only system can write
    }
    
    // ADHD support settings - users can manage their own settings
    match /adhd_support_settings/{userId} {
      allow read, write: if isAuthenticated() && isOwner(userId);
    }
  }
}
"""

# Data integrity constraints
DATA_INTEGRITY_CONSTRAINTS = {
    "user_profiles": {
        "crystal_gauges_sum": "SUM(crystal_gauges.values) <= 800",  # 8 attributes * 100 max
        "level_xp_consistency": "total_xp >= calculate_xp_for_level(player_level)",
        "email_uniqueness": "UNIQUE(email)",
        "uid_format": "MATCHES(uid, '^[a-zA-Z0-9_-]{1,128}$')"
    },
    "tasks": {
        "daily_task_limit": "COUNT(tasks WHERE uid = ? AND DATE(created_at) = TODAY()) <= 16",
        "xp_calculation": "xp_earned = difficulty * mood_coefficient * adhd_assist * 10",
        "completion_consistency": "status = 'completed' IFF completed_at IS NOT NULL",
        "mandala_cell_uniqueness": "UNIQUE(uid, mandala_cell_id) WHERE mandala_cell_id IS NOT NULL"
    },
    "mood_logs": {
        "daily_uniqueness": "UNIQUE(uid, DATE(log_date))",
        "coefficient_calculation": "mood_coefficient = 0.6 + (mood_score * 0.15)",
        "score_range": "mood_score BETWEEN 1 AND 5"
    },
    "story_states": {
        "node_existence": "current_node EXISTS IN story_nodes",
        "chapter_consistency": "current_chapter = story_nodes[current_node].chapter_type",
        "edge_validity": "ALL(available_edges) EXIST IN story_edges"
    }
}

def get_collection_schema(collection_name: str) -> Dict[str, Any]:
    """Get schema definition for a collection"""
    return COLLECTION_SCHEMAS.get(collection_name, {})

def validate_document_data(collection_name: str, data: Dict[str, Any]) -> List[str]:
    """Validate document data against schema"""
    schema = get_collection_schema(collection_name)
    errors = []
    
    if not schema:
        return ["Unknown collection"]
    
    # Check required fields
    for field in schema.get("required_fields", []):
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    # Validate field types and constraints
    validation_rules = schema.get("validation_rules", {})
    for field, rules in validation_rules.items():
        if field in data:
            value = data[field]
            
            # Type validation
            if rules.get("type") == "int" and not isinstance(value, int):
                errors.append(f"Field {field} must be integer")
            elif rules.get("type") == "float" and not isinstance(value, (int, float)):
                errors.append(f"Field {field} must be number")
            elif rules.get("type") == "string" and not isinstance(value, str):
                errors.append(f"Field {field} must be string")
            elif rules.get("type") == "boolean" and not isinstance(value, bool):
                errors.append(f"Field {field} must be boolean")
            elif rules.get("type") == "array" and not isinstance(value, list):
                errors.append(f"Field {field} must be array")
            elif rules.get("type") == "dict" and not isinstance(value, dict):
                errors.append(f"Field {field} must be object")
            
            # Range validation
            if "min" in rules and isinstance(value, (int, float)) and value < rules["min"]:
                errors.append(f"Field {field} must be >= {rules['min']}")
            if "max" in rules and isinstance(value, (int, float)) and value > rules["max"]:
                errors.append(f"Field {field} must be <= {rules['max']}")
            
            # Enum validation
            if "values" in rules and value not in rules["values"]:
                errors.append(f"Field {field} must be one of: {rules['values']}")
    
    return errors