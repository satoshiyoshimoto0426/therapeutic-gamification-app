"""
Firestore database initialization and setup utilities
Handles collection creation, security rules deployment, and initial data seeding
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from .firestore_collections import (
    COLLECTION_SCHEMAS, 
    FIRESTORE_SECURITY_RULES,
    CrystalAttribute,
    TaskType,
    TaskStatus
)
from .firestore_indexes import FIRESTORE_INDEXES, generate_firestore_indexes_json

class FirestoreSetup:
    """Firestore database setup and initialization"""
    
    def __init__(self, project_id: str = None):
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT')
        self.db = firestore.Client(project=self.project_id)
        
    def initialize_database(self) -> Dict[str, Any]:
        """Initialize Firestore database with collections and initial data"""
        results = {
            "collections_created": [],
            "initial_data_seeded": [],
            "indexes_configured": False,
            "security_rules_ready": False,
            "errors": []
        }
        
        try:
            # Create collections with initial documents
            self._create_collections(results)
            
            # Seed initial data
            self._seed_initial_data(results)
            
            # Generate index configuration file
            self._generate_index_config(results)
            
            # Generate security rules file
            self._generate_security_rules(results)
            
            print("? Firestore database initialization completed successfully")
            
        except Exception as e:
            results["errors"].append(f"Database initialization failed: {str(e)}")
            print(f"? Database initialization failed: {str(e)}")
            
        return results
    
    def _create_collections(self, results: Dict[str, Any]):
        """Create Firestore collections with proper structure"""
        
        for collection_name, schema in COLLECTION_SCHEMAS.items():
            try:
                # Create a system document to establish the collection
                system_doc_data = self._generate_system_document(collection_name, schema)
                
                doc_ref = self.db.collection(collection_name).document("_system_init")
                doc_ref.set(system_doc_data)
                
                results["collections_created"].append(collection_name)
                print(f"? Created collection: {collection_name}")
                
            except Exception as e:
                error_msg = f"Failed to create collection {collection_name}: {str(e)}"
                results["errors"].append(error_msg)
                print(f"? {error_msg}")
    
    def _generate_system_document(self, collection_name: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate system initialization document for each collection"""
        
        base_doc = {
            "_system": True,
            "_created_at": datetime.utcnow(),
            "_schema_version": "1.0",
            "_description": schema.get("description", "")
        }
        
        # Collection-specific system documents
        if collection_name == "user_profiles":
            return {
                **base_doc,
                "uid": "_system",
                "email": "system@therapeutic-gamification.app",
                "display_name": "System User",
                "created_at": datetime.utcnow(),
                "last_active": datetime.utcnow(),
                "player_level": 1,
                "yu_level": 1,
                "total_xp": 0,
                "crystal_gauges": {attr.value: 0 for attr in CrystalAttribute}
            }
            
        elif collection_name == "story_nodes":
            return {
                **base_doc,
                "node_id": "_welcome_node",
                "chapter_type": CrystalAttribute.SELF_DISCIPLINE.value,
                "node_type": "opening",
                "title": "Welcome to Your Therapeutic Journey",
                "content": "Your adventure in self-discovery and growth begins here...",
                "therapeutic_elements": ["welcome", "introduction", "motivation"],
                "estimated_read_time": 3
            }
            
        elif collection_name == "story_edges":
            return {
                **base_doc,
                "edge_id": "_welcome_edge",
                "from_node": "_welcome_node",
                "to_node": "_first_choice",
                "choice_text": "I'm ready to begin my journey",
                "created_at": datetime.utcnow(),
                "xp_reward": 10
            }
            
        elif collection_name == "tasks":
            return {
                **base_doc,
                "task_id": "_welcome_task",
                "uid": "_system",
                "task_type": TaskType.ROUTINE.value,
                "title": "Welcome Task",
                "description": "Complete your profile setup",
                "difficulty": 1,
                "status": TaskStatus.COMPLETED.value,
                "created_at": datetime.utcnow(),
                "completed_at": datetime.utcnow(),
                "xp_earned": 10
            }
            
        else:
            # Generic system document
            return base_doc
    
    def _seed_initial_data(self, results: Dict[str, Any]):
        """Seed initial data for story content and system configuration"""
        
        try:
            # Seed story nodes for each crystal attribute
            self._seed_story_nodes(results)
            
            # Seed story edges for basic navigation
            self._seed_story_edges(results)
            
            # Seed system configuration
            self._seed_system_config(results)
            
        except Exception as e:
            error_msg = f"Failed to seed initial data: {str(e)}"
            results["errors"].append(error_msg)
            print(f"? {error_msg}")
    
    def _seed_story_nodes(self, results: Dict[str, Any]):
        """Seed initial story nodes for each crystal attribute"""
        
        story_nodes = [
            {
                "node_id": f"{attr.value}_opening",
                "chapter_type": attr.value,
                "node_type": "opening",
                "title": f"{attr.value.replace('_', ' ').title()} Journey Begins",
                "content": f"Welcome to your {attr.value.replace('_', ' ')} development chapter...",
                "therapeutic_elements": [attr.value, "introduction"],
                "estimated_read_time": 5,
                "unlock_conditions": [],
                "therapeutic_tags": [attr.value, "opening", "motivation"]
            }
            for attr in CrystalAttribute
        ]
        
        batch = self.db.batch()
        for node in story_nodes:
            doc_ref = self.db.collection("story_nodes").document(node["node_id"])
            batch.set(doc_ref, node)
        
        batch.commit()
        results["initial_data_seeded"].append("story_nodes")
        print("? Seeded initial story nodes")
    
    def _seed_story_edges(self, results: Dict[str, Any]):
        """Seed initial story edges for navigation"""
        
        story_edges = []
        for attr in CrystalAttribute:
            story_edges.extend([
                {
                    "edge_id": f"{attr.value}_choice_1",
                    "from_node": f"{attr.value}_opening",
                    "to_node": f"{attr.value}_task_1",
                    "choice_text": "I want to take action",
                    "created_at": datetime.utcnow(),
                    "xp_reward": 25,
                    "habit_tag": f"{attr.value}_basic",
                    "therapeutic_outcome": "action_orientation"
                },
                {
                    "edge_id": f"{attr.value}_choice_2",
                    "from_node": f"{attr.value}_opening", 
                    "to_node": f"{attr.value}_reflection_1",
                    "choice_text": "I want to reflect first",
                    "created_at": datetime.utcnow(),
                    "xp_reward": 15,
                    "therapeutic_outcome": "self_awareness"
                }
            ])
        
        batch = self.db.batch()
        for edge in story_edges:
            doc_ref = self.db.collection("story_edges").document(edge["edge_id"])
            batch.set(doc_ref, edge)
        
        batch.commit()
        results["initial_data_seeded"].append("story_edges")
        print("? Seeded initial story edges")
    
    def _seed_system_config(self, results: Dict[str, Any]):
        """Seed system configuration documents"""
        
        system_configs = [
            {
                "collection": "system_config",
                "document": "app_settings",
                "data": {
                    "app_version": "1.0.0",
                    "maintenance_mode": False,
                    "max_daily_tasks": 16,
                    "xp_base_multiplier": 10,
                    "resonance_level_threshold": 5,
                    "safety_f1_target": 0.98,
                    "api_timeout_seconds": 3.5,
                    "updated_at": datetime.utcnow()
                }
            },
            {
                "collection": "system_config",
                "document": "crystal_attributes",
                "data": {
                    "attributes": [attr.value for attr in CrystalAttribute],
                    "max_gauge_value": 100,
                    "chapter_unlock_threshold": 100,
                    "updated_at": datetime.utcnow()
                }
            },
            {
                "collection": "system_config",
                "document": "task_types",
                "data": {
                    "types": [task_type.value for task_type in TaskType],
                    "difficulty_range": [1, 5],
                    "xp_calculation_formula": "difficulty * mood_coefficient * adhd_assist * base_multiplier",
                    "updated_at": datetime.utcnow()
                }
            }
        ]
        
        for config in system_configs:
            doc_ref = self.db.collection(config["collection"]).document(config["document"])
            doc_ref.set(config["data"])
        
        results["initial_data_seeded"].append("system_config")
        print("? Seeded system configuration")
    
    def _generate_index_config(self, results: Dict[str, Any]):
        """Generate firestore.indexes.json file"""
        
        try:
            indexes_config = generate_firestore_indexes_json()
            
            # Write to file for Firebase CLI deployment
            os.makedirs("firebase_config", exist_ok=True)
            with open("firebase_config/firestore.indexes.json", "w") as f:
                json.dump(indexes_config, f, indent=2)
            
            results["indexes_configured"] = True
            print("? Generated firestore.indexes.json")
            
        except Exception as e:
            error_msg = f"Failed to generate index config: {str(e)}"
            results["errors"].append(error_msg)
            print(f"? {error_msg}")
    
    def _generate_security_rules(self, results: Dict[str, Any]):
        """Generate firestore.rules file"""
        
        try:
            os.makedirs("firebase_config", exist_ok=True)
            with open("firebase_config/firestore.rules", "w") as f:
                f.write(FIRESTORE_SECURITY_RULES)
            
            results["security_rules_ready"] = True
            print("? Generated firestore.rules")
            
        except Exception as e:
            error_msg = f"Failed to generate security rules: {str(e)}"
            results["errors"].append(error_msg)
            print(f"? {error_msg}")
    
    def verify_setup(self) -> Dict[str, Any]:
        """Verify database setup and configuration"""
        
        verification_results = {
            "collections_exist": [],
            "indexes_needed": [],
            "data_integrity_issues": [],
            "performance_warnings": []
        }
        
        try:
            # Check if collections exist
            for collection_name in COLLECTION_SCHEMAS.keys():
                try:
                    docs = self.db.collection(collection_name).limit(1).get()
                    if docs:
                        verification_results["collections_exist"].append(collection_name)
                except Exception:
                    verification_results["data_integrity_issues"].append(
                        f"Collection {collection_name} not accessible"
                    )
            
            # Check for missing indexes (simplified check)
            for index in FIRESTORE_INDEXES:
                collection = index["collectionGroup"]
                fields = [field["fieldPath"] for field in index["fields"]]
                
                # This is a simplified check - in production, use Firebase Admin SDK
                # to actually verify index existence
                verification_results["indexes_needed"].append({
                    "collection": collection,
                    "fields": fields
                })
            
            print("? Database verification completed")
            
        except Exception as e:
            verification_results["data_integrity_issues"].append(
                f"Verification failed: {str(e)}"
            )
            print(f"? Database verification failed: {str(e)}")
        
        return verification_results
    
    def cleanup_test_data(self):
        """Clean up test and system initialization data"""
        
        try:
            collections_to_clean = COLLECTION_SCHEMAS.keys()
            
            for collection_name in collections_to_clean:
                # Delete system initialization documents
                system_docs = self.db.collection(collection_name).where(
                    filter=FieldFilter("_system", "==", True)
                ).get()
                
                batch = self.db.batch()
                for doc in system_docs:
                    batch.delete(doc.reference)
                
                if system_docs:
                    batch.commit()
                    print(f"? Cleaned up system docs in {collection_name}")
            
        except Exception as e:
            print(f"? Cleanup failed: {str(e)}")

def main():
    """Main setup function"""
    print("? Starting Firestore database setup...")
    
    setup = FirestoreSetup()
    
    # Initialize database
    results = setup.initialize_database()
    
    # Print results
    print("\n? Setup Results:")
    print(f"Collections created: {len(results['collections_created'])}")
    print(f"Initial data seeded: {len(results['initial_data_seeded'])}")
    print(f"Indexes configured: {results['indexes_configured']}")
    print(f"Security rules ready: {results['security_rules_ready']}")
    
    if results["errors"]:
        print(f"\n?  Errors encountered: {len(results['errors'])}")
        for error in results["errors"]:
            print(f"  - {error}")
    
    # Verify setup
    print("\n? Verifying setup...")
    verification = setup.verify_setup()
    
    print(f"Collections verified: {len(verification['collections_exist'])}")
    print(f"Indexes needed: {len(verification['indexes_needed'])}")
    
    if verification["data_integrity_issues"]:
        print(f"\n?  Data integrity issues: {len(verification['data_integrity_issues'])}")
        for issue in verification["data_integrity_issues"]:
            print(f"  - {issue}")
    
    print("\n? Firestore setup completed!")
    print("\nNext steps:")
    print("1. Deploy indexes: firebase deploy --only firestore:indexes")
    print("2. Deploy security rules: firebase deploy --only firestore:rules")
    print("3. Run integration tests to verify functionality")

if __name__ == "__main__":
    main()