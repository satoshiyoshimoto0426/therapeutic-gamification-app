"""
Firestore collections schema and index definitions
Defines the database structure for multi-region deployment
"""

from typing import Dict, List, Any
from datetime import datetime

# Collection names
COLLECTIONS = {
    "users": "users",
    "tasks": "tasks", 
    "mood_logs": "mood_logs",
    "story_nodes": "story_nodes",
    "story_edges": "story_edges",
    "story_states": "story_states",
    "mandala_grids": "mandala_grids",
    "guardian_links": "guardian_links",
    "game_states": "game_states",
    "purchases": "purchases",
    "adhd_settings": "adhd_settings",
    "chapter_progress": "chapter_progress"
}

# Firestore indexes configuration
FIRESTORE_INDEXES = [
    # Users collection indexes
    {
        "collectionGroup": "users",
        "fields": [
            {"fieldPath": "email", "order": "ASCENDING"},
            {"fieldPath": "last_active", "order": "DESCENDING"}
        ]
    },
    {
        "collectionGroup": "users", 
        "fields": [
            {"fieldPath": "player_level", "order": "DESCENDING"},
            {"fieldPath": "created_at", "order": "ASCENDING"}
        ]
    },
    
    # Tasks collection indexes
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
            {"fieldPath": "mandala_cell_id", "order": "ASCENDING"},
            {"fieldPath": "status", "order": "ASCENDING"}
        ]
    },
    
    # Mood logs indexes
    {
        "collectionGroup": "mood_logs",
        "fields": [
            {"fieldPath": "uid", "order": "ASCENDING"},
            {"fieldPath": "log_date", "order": "DESCENDING"}
        ]
    },
    
    # Story states indexes
    {
        "collectionGroup": "story_states",
        "fields": [
            {"fieldPath": "uid", "order": "ASCENDING"},
            {"fieldPath": "unlocked_at", "order": "DESCENDING"}
        ]
    },
    {
        "collectionGroup": "story_states",
        "fields": [
            {"fieldPath": "uid", "order": "ASCENDING"},
            {"fieldPath": "read_flag", "order": "ASCENDING"},
            {"fieldPath": "unlocked_at", "order": "ASCENDING"}
        ]
    },
    
    # Story nodes indexes
    {
        "collectionGroup": "story_nodes",
        "fields": [
            {"fieldPath": "chapter_type", "order": "ASCENDING"},
            {"fieldPath": "node_type", "order": "ASCENDING"}
        ]
    },
    
    # Guardian links indexes
    {
        "collectionGroup": "guardian_links",
        "fields": [
            {"fieldPath": "guardian_id", "order": "ASCENDING"},
            {"fieldPath": "approved_by_user", "order": "ASCENDING"}
        ]
    },
    {
        "collectionGroup": "guardian_links",
        "fields": [
            {"fieldPath": "user_id", "order": "ASCENDING"},
            {"fieldPath": "permission_level", "order": "ASCENDING"}
        ]
    }
]

# Collection security rules template
FIRESTORE_RULES = """
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Users can read/write their own data
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Tasks - users can manage their own tasks
    match /tasks/{taskId} {
      allow read, write: if request.auth != null && 
        (request.auth.uid == resource.data.uid || 
         exists(/databases/$(database)/documents/guardian_links/$(request.auth.uid + '_' + resource.data.uid)));
    }
    
    // Mood logs - users can manage their own mood data
    match /mood_logs/{moodId} {
      allow read, write: if request.auth != null && request.auth.uid == resource.data.uid;
    }
    
    // Story states - users can read/write their own story progress
    match /story_states/{stateId} {
      allow read, write: if request.auth != null && request.auth.uid == resource.data.uid;
    }
    
    // Story nodes and edges - read-only for authenticated users
    match /story_nodes/{nodeId} {
      allow read: if request.auth != null;
    }
    
    match /story_edges/{edgeId} {
      allow read: if request.auth != null;
    }
    
    // Guardian links - special permission handling
    match /guardian_links/{linkId} {
      allow read: if request.auth != null && 
        (request.auth.uid == resource.data.guardian_id || 
         request.auth.uid == resource.data.user_id);
      allow write: if request.auth != null && 
        request.auth.uid == resource.data.user_id;
    }
    
    // Game states - users can manage their own game state
    match /game_states/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Mandala grids - users can manage their own grids
    match /mandala_grids/{gridId} {
      allow read, write: if request.auth != null && request.auth.uid == resource.data.uid;
    }
  }
}
"""

def get_collection_schema(collection_name: str) -> Dict[str, Any]:
    """Get the schema definition for a collection"""
    schemas = {
        "users": {
            "required_fields": ["uid", "email", "display_name", "created_at"],
            "indexed_fields": ["email", "last_active", "player_level"],
            "ttl_field": None
        },
        "tasks": {
            "required_fields": ["task_id", "uid", "task_type", "title", "status", "created_at"],
            "indexed_fields": ["uid", "status", "due_date", "task_type", "mandala_cell_id"],
            "ttl_field": None
        },
        "mood_logs": {
            "required_fields": ["uid", "log_date", "mood_score"],
            "indexed_fields": ["uid", "log_date"],
            "ttl_field": None
        },
        "story_states": {
            "required_fields": ["uid", "node_id", "unlocked_at"],
            "indexed_fields": ["uid", "unlocked_at", "read_flag"],
            "ttl_field": None
        },
        "story_nodes": {
            "required_fields": ["node_id", "chapter_type", "node_type", "title", "content"],
            "indexed_fields": ["chapter_type", "node_type"],
            "ttl_field": None
        },
        "guardian_links": {
            "required_fields": ["guardian_id", "user_id", "permission_level", "created_at"],
            "indexed_fields": ["guardian_id", "user_id", "permission_level", "approved_by_user"],
            "ttl_field": None
        }
    }
    
    return schemas.get(collection_name, {})

def initialize_collections(db_client):
    """Initialize Firestore collections with proper structure"""
    
    # Create initial documents to establish collections
    initial_data = {
        "users": {
            "uid": "system",
            "email": "system@therapeutic-gamification.app",
            "display_name": "System User",
            "player_level": 1,
            "yu_level": 1,
            "total_xp": 0,
            "created_at": datetime.utcnow(),
            "last_active": datetime.utcnow(),
            "adhd_profile": {},
            "therapeutic_goals": []
        },
        "story_nodes": {
            "node_id": "welcome_node",
            "chapter_type": "self_discipline",
            "node_type": "opening",
            "title": "Welcome to Your Journey",
            "content": "Your therapeutic adventure begins here...",
            "estimated_read_time": 2,
            "therapeutic_tags": ["welcome", "introduction"],
            "unlock_conditions": []
        }
    }
    
    for collection_name, data in initial_data.items():
        try:
            doc_ref = db_client.collection(collection_name).document("system_init")
            doc_ref.set(data)
            print(f"Initialized collection: {collection_name}")
        except Exception as e:
            print(f"Error initializing collection {collection_name}: {e}")

# Multi-region configuration
MULTI_REGION_CONFIG = {
    "primary_region": "us-central1",
    "secondary_regions": ["asia-northeast1", "europe-west1"],
    "replication_settings": {
        "users": "multi_region",
        "tasks": "multi_region", 
        "mood_logs": "multi_region",
        "story_states": "multi_region",
        "story_nodes": "global",  # Read-heavy, can be globally replicated
        "story_edges": "global"
    }
}