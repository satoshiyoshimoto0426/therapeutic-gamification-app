"""
Story management repository implementation
Handles story nodes, edges, and user story progression
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from google.cloud import firestore

from .base_repository import BaseRepository
from ..interfaces.core_types import StoryNode, StoryEdge, StoryState, ChapterType
from ..utils.exceptions import ValidationError, NotFoundError


class StoryNode:
    """Story node data class"""
    
    def __init__(self, **kwargs):
        self.node_id = kwargs["node_id"]
        self.chapter_type = kwargs["chapter_type"]
        self.node_type = kwargs.get("node_type", "narrative")
        self.title = kwargs["title"]
        self.content = kwargs["content"]
        self.therapeutic_elements = kwargs.get("therapeutic_elements", [])
        self.estimated_read_time = kwargs.get("estimated_read_time", 3)
        self.unlock_conditions = kwargs.get("unlock_conditions", [])
        self.created_at = kwargs.get("created_at", datetime.utcnow())


class StoryEdge:
    """Story edge data class"""
    
    def __init__(self, **kwargs):
        self.edge_id = kwargs["edge_id"]
        self.from_node = kwargs["from_node"]
        self.to_node = kwargs["to_node"]
        self.choice_text = kwargs["choice_text"]
        self.real_task_id = kwargs.get("real_task_id")
        self.habit_tag = kwargs.get("habit_tag")
        self.xp_reward = kwargs.get("xp_reward", 0)
        self.conditions = kwargs.get("conditions", [])
        self.therapeutic_impact = kwargs.get("therapeutic_impact", {})


class StoryState:
    """User story state data class"""
    
    def __init__(self, **kwargs):
        self.uid = kwargs["uid"]
        self.current_chapter = kwargs["current_chapter"]
        self.current_node = kwargs["current_node"]
        self.visited_nodes = kwargs.get("visited_nodes", [])
        self.available_edges = kwargs.get("available_edges", [])
        self.story_history = kwargs.get("story_history", [])
        self.last_story_time = kwargs.get("last_story_time")
        self.chapter_progress = kwargs.get("chapter_progress", 0.0)
        self.updated_at = kwargs.get("updated_at", datetime.utcnow())


class StoryNodeRepository(BaseRepository[StoryNode]):
    """Repository for story nodes"""
    
    def __init__(self, db_client: firestore.Client):
        super().__init__(db_client, "story_nodes")
    
    def _to_entity(self, doc_data: Dict[str, Any], doc_id: str = None) -> StoryNode:
        """Convert Firestore document to StoryNode entity"""
        return StoryNode(
            node_id=doc_data.get("node_id", doc_id),
            chapter_type=doc_data["chapter_type"],
            node_type=doc_data.get("node_type", "narrative"),
            title=doc_data["title"],
            content=doc_data["content"],
            therapeutic_elements=doc_data.get("therapeutic_elements", []),
            estimated_read_time=doc_data.get("estimated_read_time", 3),
            unlock_conditions=doc_data.get("unlock_conditions", []),
            created_at=doc_data.get("created_at", datetime.utcnow())
        )
    
    def _to_document(self, entity: StoryNode) -> Dict[str, Any]:
        """Convert StoryNode entity to Firestore document"""
        return {
            "node_id": entity.node_id,
            "chapter_type": entity.chapter_type,
            "node_type": entity.node_type,
            "title": entity.title,
            "content": entity.content,
            "therapeutic_elements": entity.therapeutic_elements,
            "estimated_read_time": entity.estimated_read_time,
            "unlock_conditions": entity.unlock_conditions,
            "created_at": entity.created_at
        }
    
    async def get_nodes_by_chapter(self, chapter_type: str) -> List[StoryNode]:
        """Get all story nodes for a specific chapter"""
        try:
            return await self.find_by_field("chapter_type", chapter_type)
        except Exception as e:
            self.logger.error(f"Failed to get nodes for chapter {chapter_type}: {str(e)}")
            raise


class StoryEdgeRepository(BaseRepository[StoryEdge]):
    """Repository for story edges"""
    
    def __init__(self, db_client: firestore.Client):
        super().__init__(db_client, "story_edges")
    
    def _to_entity(self, doc_data: Dict[str, Any], doc_id: str = None) -> StoryEdge:
        """Convert Firestore document to StoryEdge entity"""
        return StoryEdge(
            edge_id=doc_data.get("edge_id", doc_id),
            from_node=doc_data["from_node"],
            to_node=doc_data["to_node"],
            choice_text=doc_data["choice_text"],
            real_task_id=doc_data.get("real_task_id"),
            habit_tag=doc_data.get("habit_tag"),
            xp_reward=doc_data.get("xp_reward", 0),
            conditions=doc_data.get("conditions", []),
            therapeutic_impact=doc_data.get("therapeutic_impact", {})
        )
    
    def _to_document(self, entity: StoryEdge) -> Dict[str, Any]:
        """Convert StoryEdge entity to Firestore document"""
        return {
            "edge_id": entity.edge_id,
            "from_node": entity.from_node,
            "to_node": entity.to_node,
            "choice_text": entity.choice_text,
            "real_task_id": entity.real_task_id,
            "habit_tag": entity.habit_tag,
            "xp_reward": entity.xp_reward,
            "conditions": entity.conditions,
            "therapeutic_impact": entity.therapeutic_impact
        }
    
    async def get_edges_from_node(self, node_id: str) -> List[StoryEdge]:
        """Get all edges from a specific node"""
        try:
            return await self.find_by_field("from_node", node_id)
        except Exception as e:
            self.logger.error(f"Failed to get edges from node {node_id}: {str(e)}")
            raise


class StoryStateRepository(BaseRepository[StoryState]):
    """Repository for user story states"""
    
    def __init__(self, db_client: firestore.Client):
        super().__init__(db_client, "story_states")
    
    def _to_entity(self, doc_data: Dict[str, Any], doc_id: str = None) -> StoryState:
        """Convert Firestore document to StoryState entity"""
        return StoryState(
            uid=doc_data.get("uid", doc_id),
            current_chapter=doc_data["current_chapter"],
            current_node=doc_data["current_node"],
            visited_nodes=doc_data.get("visited_nodes", []),
            available_edges=doc_data.get("available_edges", []),
            story_history=doc_data.get("story_history", []),
            last_story_time=doc_data.get("last_story_time"),
            chapter_progress=doc_data.get("chapter_progress", 0.0),
            updated_at=doc_data.get("updated_at", datetime.utcnow())
        )
    
    def _to_document(self, entity: StoryState) -> Dict[str, Any]:
        """Convert StoryState entity to Firestore document"""
        return {
            "uid": entity.uid,
            "current_chapter": entity.current_chapter,
            "current_node": entity.current_node,
            "visited_nodes": entity.visited_nodes,
            "available_edges": entity.available_edges,
            "story_history": entity.story_history,
            "last_story_time": entity.last_story_time,
            "chapter_progress": entity.chapter_progress,
            "updated_at": entity.updated_at
        }
    
    async def advance_story(self, uid: str, chosen_edge_id: str) -> Dict[str, Any]:
        """Advance user's story by choosing an edge"""
        try:
            # Implementation would go here
            return {
                "success": True,
                "new_node": "next_node_id",
                "xp_earned": 50
            }
        except Exception as e:
            self.logger.error(f"Failed to advance story for user {uid}: {str(e)}")
            raise
    
    async def get_story_progress_summary(self, uid: str) -> Dict[str, Any]:
        """Get comprehensive story progress summary"""
        try:
            # Implementation would go here
            return {
                "current_chapter": "chapter_1",
                "progress_percentage": 25.0,
                "nodes_visited": 5
            }
        except Exception as e:
            self.logger.error(f"Failed to get story progress for user {uid}: {str(e)}")
            raise