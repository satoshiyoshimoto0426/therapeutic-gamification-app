"""
Unit tests for Story DAG Management System
Tests story node/edge management, DAG validation, and user progression
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import sys
import os

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from interfaces.core_types import ChapterType

class TestStoryNodeManagement:
    """Test story node creation and management"""
    
    @pytest.mark.asyncio
    async def test_create_story_node(self):
        """Test creating a new story node"""
        from main import create_story_node, db, StoryDatabase
        from interfaces.core_types import NodeType
        
        # Reset database
        db.__dict__.update(StoryDatabase().__dict__)
        
        mock_user = {"uid": "test_user_123", "email": "test@example.com"}
        
        # First create a chapter
        chapter_id = list(db.chapters.keys())[0]  # Use existing sample chapter
        
        node_data = {
            "chapter_id": chapter_id,
            "node_type": "opening",
            "title": "The Beginning",
            "content": "Your journey starts here...",
            "estimated_read_time": 3,
            "therapeutic_tags": ["motivation", "goal_setting"],
            "unlock_conditions": [],
            "companion_effects": {"yu": 5},
            "mood_effects": {"confidence": 0.1},
            "ending_flags": {"hero_path": True}
        }
        
        result = await create_story_node(
            node_data=node_data,
            current_user=mock_user
        )
        
        # Verify node creation
        assert "node_id" in result
        assert result["message"] == "Story node created successfully"
        
        node_id = result["node_id"]
        assert node_id in db.nodes
        
        node = db.nodes[node_id]
        assert node.title == "The Beginning"
        assert node.chapter_id == chapter_id
        assert node.node_type == NodeType.OPENING
        assert node.companion_effects["yu"] == 5
        assert node.ending_flags["hero_path"] == True

    @pytest.mark.asyncio
    async def test_get_story_node(self):
        """Test retrieving a story node"""
        from main import create_story_node, get_story_node, db, StoryDatabase
        
        # Reset database
        db.__dict__.update(StoryDatabase().__dict__)
        
        mock_user = {"uid": "test_user_123", "email": "test@example.com"}
        
        # Create a node first
        chapter_id = list(db.chapters.keys())[0]  # Use existing sample chapter
        node_data = {
            "chapter_id": chapter_id,
            "node_type": "opening",
            "title": "Test Node",
            "content": "Test content"
        }
        
        create_result = await create_story_node(
            node_data=node_data,
            current_user=mock_user
        )
        node_id = create_result["node_id"]
        
        # Retrieve the node
        retrieved_node = await get_story_node(
            node_id=node_id,
            current_user=mock_user
        )
        
        assert retrieved_node.node_id == node_id
        assert retrieved_node.title == "Test Node"

    @pytest.mark.asyncio
    async def test_list_story_nodes(self):
        """Test listing story nodes with filtering"""
        from main import create_story_node, list_story_nodes, db, StoryDatabase
        
        # Reset database
        db.__dict__.update(StoryDatabase().__dict__)
        
        mock_user = {"uid": "test_user_123", "email": "test@example.com"}
        
        # Get existing chapter
        chapter_id = list(db.chapters.keys())[0]  # Use existing sample chapter
        
        # Create multiple nodes
        nodes_data = [
            {
                "chapter_id": chapter_id,
                "node_type": "opening",
                "title": "Opening 1",
                "content": "Content 1"
            },
            {
                "chapter_id": chapter_id,
                "node_type": "challenge",
                "title": "Challenge 1",
                "content": "Content 2"
            },
            {
                "chapter_id": chapter_id,
                "node_type": "opening",
                "title": "Opening 2",
                "content": "Content 3"
            }
        ]
        
        for node_data in nodes_data:
            await create_story_node(node_data=node_data, current_user=mock_user)
        
        # Test listing all nodes
        all_nodes = await list_story_nodes(current_user=mock_user)
        assert all_nodes["total_count"] >= 3
        
        # Test filtering by chapter
        chapter_nodes = await list_story_nodes(
            chapter=ChapterType.SELF_DISCIPLINE,
            current_user=mock_user
        )
        assert len([n for n in chapter_nodes["nodes"] if n.chapter_type == ChapterType.SELF_DISCIPLINE]) == 2

class TestStoryEdgeManagement:
    """Test story edge creation and management"""
    
    @pytest.mark.asyncio
    async def test_create_story_edge(self):
        """Test creating a story edge"""
        from main import create_story_node, create_story_edge, db, StoryDatabase
        
        # Reset database
        db.__dict__.update(StoryDatabase().__dict__)
        
        mock_user = {"uid": "test_user_123", "email": "test@example.com"}
        
        # Create two nodes first
        node1_data = {
            "chapter_type": "self_discipline",
            "node_type": "opening",
            "title": "Start",
            "content": "Beginning"
        }
        
        node2_data = {
            "chapter_type": "self_discipline",
            "node_type": "challenge",
            "title": "First Challenge",
            "content": "Your first test"
        }
        
        node1_result = await create_story_node(node_data=node1_data, current_user=mock_user)
        node2_result = await create_story_node(node_data=node2_data, current_user=mock_user)
        
        node1_id = node1_result["node_id"]
        node2_id = node2_result["node_id"]
        
        # Create edge
        edge_data = {
            "from_node_id": node1_id,
            "to_node_id": node2_id,
            "choice_text": "Accept the challenge",
            "real_task_id": "morning_routine_task",
            "probability": 0.8,
            "therapeutic_weight": 1.2,
            "companion_requirements": {"yu": 10},
            "achievement_rewards": ["first_step"],
            "ending_influence": {"hero_path": 0.5}
        }
        
        result = await create_story_edge(
            edge_data=edge_data,
            current_user=mock_user
        )
        
        # Verify edge creation
        assert "edge_id" in result
        assert result["message"] == "Story edge created successfully"
        
        edge_id = result["edge_id"]
        assert edge_id in db.edges
        
        edge = db.edges[edge_id]
        assert edge.from_node_id == node1_id
        assert edge.to_node_id == node2_id
        assert edge.choice_text == "Accept the challenge"
        assert edge.real_task_id == "morning_routine_task"
        assert edge.ending_influence["hero_path"] == 0.5

    @pytest.mark.asyncio
    async def test_prevent_invalid_edges(self):
        """Test prevention of edges to non-existent nodes"""
        from main import create_story_edge, db, StoryDatabase
        
        # Reset database
        db.__dict__.update(StoryDatabase().__dict__)
        
        mock_user = {"uid": "test_user_123", "email": "test@example.com"}
        
        edge_data = {
            "from_node_id": "non_existent_1",
            "to_node_id": "non_existent_2",
            "choice_text": "Invalid choice"
        }
        
        with pytest.raises(Exception) as exc_info:
            await create_story_edge(edge_data=edge_data, current_user=mock_user)
        
        assert "From node does not exist" in str(exc_info.value)

class TestDAGValidation:
    """Test DAG structure validation"""
    
    @pytest.mark.asyncio
    async def test_cycle_detection(self):
        """Test cycle detection in DAG"""
        from main import create_story_node, create_story_edge, validate_dag, db, StoryDatabase
        
        # Reset database
        db.__dict__.update(StoryDatabase().__dict__)
        
        mock_user = {"uid": "test_user_123", "email": "test@example.com"}
        
        # Get existing chapter
        chapter_id = list(db.chapters.keys())[0]
        
        # Create three nodes
        nodes_data = [
            {"chapter_id": chapter_id, "node_type": "opening", "title": "A", "content": "Node A"},
            {"chapter_id": chapter_id, "node_type": "challenge", "title": "B", "content": "Node B"},
            {"chapter_id": chapter_id, "node_type": "resolution", "title": "C", "content": "Node C"}
        ]
        
        node_ids = []
        for node_data in nodes_data:
            result = await create_story_node(node_data=node_data, current_user=mock_user)
            node_ids.append(result["node_id"])
        
        # Create edges A->B, B->C (valid)
        await create_story_edge({
            "from_node_id": node_ids[0],
            "to_node_id": node_ids[1],
            "choice_text": "Go to B"
        }, current_user=mock_user)
        
        await create_story_edge({
            "from_node_id": node_ids[1],
            "to_node_id": node_ids[2],
            "choice_text": "Go to C"
        }, current_user=mock_user)
        
        # Validate (should be valid)
        validation = await validate_dag(current_user=mock_user)
        assert validation["is_valid"] == True
        assert validation["has_cycles"] == False
        
        # Try to create cycle C->A (should fail)
        with pytest.raises(Exception) as exc_info:
            await create_story_edge({
                "from_node_id": node_ids[2],
                "to_node_id": node_ids[0],
                "choice_text": "Back to A"
            }, current_user=mock_user)
        
        assert "cycle" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_isolated_node_detection(self):
        """Test detection of isolated nodes"""
        from main import create_story_node, validate_dag, db, StoryDatabase
        
        # Reset database
        db.__dict__.update(StoryDatabase().__dict__)
        
        mock_user = {"uid": "test_user_123", "email": "test@example.com"}
        
        # Get existing chapter
        chapter_id = list(db.chapters.keys())[0]
        
        # Create isolated node
        node_data = {
            "chapter_id": chapter_id,
            "node_type": "opening",
            "title": "Isolated",
            "content": "No connections"
        }
        
        result = await create_story_node(node_data=node_data, current_user=mock_user)
        node_id = result["node_id"]
        
        # Validate
        validation = await validate_dag(current_user=mock_user)
        assert node_id in validation["isolated_nodes"]

    @pytest.mark.asyncio
    async def test_auto_merge_isolated_nodes(self):
        """Test automatic merging of isolated nodes"""
        from main import create_story_node, create_story_edge, auto_merge_dag_nodes, validate_dag, db, StoryDatabase
        
        # Reset database
        db.__dict__.update(StoryDatabase().__dict__)
        
        mock_user = {"uid": "test_user_123", "email": "test@example.com"}
        
        # Get existing chapter
        chapter_id = list(db.chapters.keys())[0]
        
        # Create a connected node
        connected_node_data = {
            "chapter_id": chapter_id,
            "node_type": "choice",
            "title": "Connected Node",
            "content": "This node has connections",
            "therapeutic_tags": ["exploration", "discovery"]
        }
        
        connected_result = await create_story_node(node_data=connected_node_data, current_user=mock_user)
        connected_node_id = connected_result["node_id"]
        
        # Create isolated node with similar therapeutic tags
        isolated_node_data = {
            "chapter_id": chapter_id,
            "node_type": "opening",
            "title": "Isolated Discovery",
            "content": "This node was isolated",
            "therapeutic_tags": ["discovery", "growth"]
        }
        
        isolated_result = await create_story_node(node_data=isolated_node_data, current_user=mock_user)
        isolated_node_id = isolated_result["node_id"]
        
        # Verify node is isolated
        validation_before = await validate_dag(current_user=mock_user)
        assert isolated_node_id in validation_before["isolated_nodes"]
        
        # Auto-merge isolated nodes
        merge_result = await auto_merge_dag_nodes(chapter_id=chapter_id, current_user=mock_user)
        
        assert merge_result["merge_result"]["merged_count"] >= 1
        assert len(merge_result["merge_result"]["merge_details"]) >= 1
        
        # Verify node is no longer isolated
        validation_after = await validate_dag(current_user=mock_user)
        assert isolated_node_id not in validation_after["isolated_nodes"]
        
        # Verify rescue edge was created
        merge_detail = merge_result["merge_result"]["merge_details"][0]
        assert merge_detail["isolated_node"] == isolated_node_id
        assert merge_detail["method"] == "auto_rescue_path"
        assert merge_detail["rescue_edge"] in db.edges

class TestUserStoryProgression:
    """Test user story state and progression"""
    
    @pytest.mark.asyncio
    async def test_get_user_story_state(self):
        """Test getting user story state"""
        from main import get_user_story_state, db, StoryDatabase
        
        # Reset database
        db.__dict__.update(StoryDatabase().__dict__)
        
        mock_user = {"uid": "test_user_123", "email": "test@example.com"}
        
        # Get initial state (should create new)
        state = await get_user_story_state(
            uid="test_user_123",
            current_user=mock_user
        )
        
        assert state.uid == "test_user_123"
        assert state.current_node_id == ""
        assert len(state.unlocked_nodes) == 0
        assert len(state.choice_history) == 0

    @pytest.mark.asyncio
    async def test_story_progression(self):
        """Test user story progression"""
        from main import (create_story_node, create_story_edge, progress_story, 
                         get_user_story_state, db, StoryDatabase)
        
        # Reset database
        db.__dict__.update(StoryDatabase().__dict__)
        
        mock_user = {"uid": "test_user_123", "email": "test@example.com"}
        
        # Create story structure
        node1_result = await create_story_node({
            "chapter_type": "self_discipline",
            "node_type": "opening",
            "title": "Start",
            "content": "Beginning",
            "companion_effects": {"yu": 5},
            "ending_flags": {"started": True}
        }, current_user=mock_user)
        
        node2_result = await create_story_node({
            "chapter_type": "self_discipline",
            "node_type": "challenge",
            "title": "Challenge",
            "content": "First test",
            "companion_effects": {"yu": 10}
        }, current_user=mock_user)
        
        edge_result = await create_story_edge({
            "from_node_id": node1_result["node_id"],
            "to_node_id": node2_result["node_id"],
            "choice_text": "Accept challenge",
            "ending_influence": {"hero_path": 0.3}
        }, current_user=mock_user)
        
        # Set initial state
        db.user_states["test_user_123"] = await get_user_story_state(
            uid="test_user_123",
            current_user=mock_user
        )
        db.user_states["test_user_123"].current_node_id = node1_result["node_id"]
        
        # Progress story
        progress_result = await progress_story(
            uid="test_user_123",
            progress_data={"edge_id": edge_result["edge_id"]},
            current_user=mock_user
        )
        
        assert progress_result["message"] == "Story progressed successfully"
        
        # Check updated state
        updated_state = db.user_states["test_user_123"]
        assert updated_state.current_node_id == node2_result["node_id"]
        assert node2_result["node_id"] in updated_state.unlocked_nodes
        assert node1_result["node_id"] in updated_state.completed_nodes
        assert len(updated_state.choice_history) == 1
        assert updated_state.companion_relationships["yu"] == 10
        assert updated_state.ending_scores["hero_path"] == 0.3

class TestCompanionSystem:
    """Test companion relationship system"""
    
    @pytest.mark.asyncio
    async def test_list_companions(self):
        """Test listing available companions"""
        from main import list_companions, db, StoryDatabase
        
        # Reset database
        db.__dict__.update(StoryDatabase().__dict__)
        
        mock_user = {"uid": "test_user_123", "email": "test@example.com"}
        
        result = await list_companions(current_user=mock_user)
        
        assert "companions" in result
        assert len(result["companions"]) >= 2  # yu and mentor
        
        # Check yu companion
        yu_companion = next((c for c in result["companions"] if c.companion_id == "yu"), None)
        assert yu_companion is not None
        assert yu_companion.name == "Yu"

    @pytest.mark.asyncio
    async def test_companion_relationships(self):
        """Test companion relationship tracking"""
        from main import get_companion_relationships, db, StoryDatabase, UserStoryState
        
        # Reset database
        db.__dict__.update(StoryDatabase().__dict__)
        
        mock_user = {"uid": "test_user_123", "email": "test@example.com"}
        
        # Create user state with companion relationships
        user_state = UserStoryState(
            uid="test_user_123",
            current_node_id="test_node",
            last_updated=datetime.utcnow()
        )
        user_state.companion_relationships = {"yu": 25, "mentor": 10}
        db.user_states["test_user_123"] = user_state
        
        result = await get_companion_relationships(
            uid="test_user_123",
            current_user=mock_user
        )
        
        assert "relationships" in result
        assert "yu" in result["relationships"]
        assert result["relationships"]["yu"]["relationship_level"] == 25
        assert result["relationships"]["yu"]["relationship_percentage"] == 25.0  # 25/100 * 100

class TestStoryAnalytics:
    """Test story analytics and insights"""
    
    @pytest.mark.asyncio
    async def test_story_path_analytics(self):
        """Test story path analysis"""
        from main import analyze_story_paths, db, StoryDatabase, UserStoryState
        
        # Reset database
        db.__dict__.update(StoryDatabase().__dict__)
        
        mock_user = {"uid": "test_user_123", "email": "test@example.com"}
        
        # Create sample user states with choice history
        user1 = UserStoryState(
            uid="user1",
            current_node_id="node1",
            last_updated=datetime.utcnow()
        )
        user1.choice_history = [{"edge_id": "edge1"}, {"edge_id": "edge2"}]
        user1.ending_scores = {"hero_path": 0.8, "wisdom_path": 0.2}
        
        user2 = UserStoryState(
            uid="user2",
            current_node_id="node2",
            last_updated=datetime.utcnow()
        )
        user2.choice_history = [{"edge_id": "edge1"}, {"edge_id": "edge3"}]
        user2.ending_scores = {"hero_path": 0.3, "wisdom_path": 0.7}
        
        db.user_states["user1"] = user1
        db.user_states["user2"] = user2
        
        result = await analyze_story_paths(current_user=mock_user)
        
        assert "popular_choices" in result
        assert "ending_trends" in result
        assert result["total_users"] == 2
        assert result["popular_choices"]["edge1"] == 2  # Both users chose edge1
        assert "hero_path" in result["ending_trends"]
        assert "wisdom_path" in result["ending_trends"]

class TestStoryNavigation:
    """Test story navigation and state management"""
    
    @pytest.mark.asyncio
    async def test_get_available_choices(self):
        """Test getting available choices for user's current position"""
        from main import (create_story_node, create_story_edge, get_available_choices, 
                         get_user_story_state, db, StoryDatabase)
        
        # Reset database
        db.__dict__.update(StoryDatabase().__dict__)
        
        mock_user = {"uid": "test_user_123", "email": "test@example.com"}
        
        # Get existing chapter
        chapter_id = list(db.chapters.keys())[0]
        
        # Create story structure
        start_node = await create_story_node({
            "chapter_id": chapter_id,
            "node_type": "choice",
            "title": "The Crossroads",
            "content": "Two paths diverge before you...",
            "therapeutic_tags": ["decision_making"]
        }, current_user=mock_user)
        
        path1_node = await create_story_node({
            "chapter_id": chapter_id,
            "node_type": "challenge",
            "title": "Path of Courage",
            "content": "Face your fears head-on",
            "estimated_read_time": 5
        }, current_user=mock_user)
        
        path2_node = await create_story_node({
            "chapter_id": chapter_id,
            "node_type": "reflection",
            "title": "Path of Wisdom",
            "content": "Contemplate the deeper meaning",
            "estimated_read_time": 3
        }, current_user=mock_user)
        
        # Create edges with different requirements
        edge1 = await create_story_edge({
            "from_node_id": start_node["node_id"],
            "to_node_id": path1_node["node_id"],
            "choice_text": "Take the courageous path",
            "real_task_id": "courage_task",
            "probability": 0.8,
            "therapeutic_weight": 1.2,
            "companion_requirements": {"yu": 10}
        }, current_user=mock_user)
        
        edge2 = await create_story_edge({
            "from_node_id": start_node["node_id"],
            "to_node_id": path2_node["node_id"],
            "choice_text": "Take the contemplative path",
            "habit_tag": "reflection",
            "probability": 0.9,
            "therapeutic_weight": 1.0
        }, current_user=mock_user)
        
        # Set up user state
        user_state = await get_user_story_state(uid="test_user_123", current_user=mock_user)
        user_state.current_node_id = start_node["node_id"]
        user_state.companion_relationships = {"yu": 15}  # Meets requirement for edge1
        db.user_states["test_user_123"] = user_state
        
        # Get available choices
        choices_result = await get_available_choices(
            uid="test_user_123",
            current_user=mock_user
        )
        
        assert "current_node" in choices_result
        assert "choices" in choices_result
        assert choices_result["current_node"]["title"] == "The Crossroads"
        assert len(choices_result["choices"]) == 2
        
        # Check choice details
        courage_choice = next((c for c in choices_result["choices"] if c["choice_text"] == "Take the courageous path"), None)
        assert courage_choice is not None
        assert courage_choice["can_choose"] == True  # Yu relationship meets requirement
        assert courage_choice["real_task_id"] == "courage_task"
        
        wisdom_choice = next((c for c in choices_result["choices"] if c["choice_text"] == "Take the contemplative path"), None)
        assert wisdom_choice is not None
        assert wisdom_choice["can_choose"] == True
        assert wisdom_choice["habit_tag"] == "reflection"

    @pytest.mark.asyncio
    async def test_get_story_path(self):
        """Test getting user's complete story path"""
        from main import (create_story_node, create_story_edge, progress_story, 
                         get_story_path, get_user_story_state, db, StoryDatabase)
        
        # Reset database
        db.__dict__.update(StoryDatabase().__dict__)
        
        mock_user = {"uid": "test_user_123", "email": "test@example.com"}
        
        # Get existing chapter
        chapter_id = list(db.chapters.keys())[0]
        
        # Create story progression
        node1 = await create_story_node({
            "chapter_id": chapter_id,
            "node_type": "opening",
            "title": "Beginning",
            "content": "Your journey starts"
        }, current_user=mock_user)
        
        node2 = await create_story_node({
            "chapter_id": chapter_id,
            "node_type": "challenge",
            "title": "First Challenge",
            "content": "Your first test"
        }, current_user=mock_user)
        
        edge1 = await create_story_edge({
            "from_node_id": node1["node_id"],
            "to_node_id": node2["node_id"],
            "choice_text": "Accept the challenge"
        }, current_user=mock_user)
        
        # Set up user state and progress
        user_state = await get_user_story_state(uid="test_user_123", current_user=mock_user)
        user_state.current_node_id = node1["node_id"]
        user_state.unlocked_chapters = [chapter_id]
        db.user_states["test_user_123"] = user_state
        
        # Progress through story
        await progress_story(
            uid="test_user_123",
            progress_data={"edge_id": edge1["edge_id"]},
            current_user=mock_user
        )
        
        # Get story path
        path_result = await get_story_path(
            uid="test_user_123",
            current_user=mock_user
        )
        
        assert "story_path" in path_result
        assert "progression" in path_result
        assert "current_position" in path_result
        
        # Check story path
        assert len(path_result["story_path"]) == 1
        path_step = path_result["story_path"][0]
        assert path_step["choice_text"] == "Accept the challenge"
        assert path_step["from_node"]["title"] == "Beginning"
        assert path_step["to_node"]["title"] == "First Challenge"
        
        # Check progression
        progression = path_result["progression"]
        assert progression["unlocked_chapters"] == 1
        assert progression["completed_nodes"] == 1
        assert progression["completion_percentage"] > 0

    @pytest.mark.asyncio
    async def test_get_chapter_structure(self):
        """Test getting complete chapter structure"""
        from main import (create_story_node, create_story_edge, get_chapter_structure, 
                         db, StoryDatabase)
        
        # Reset database
        db.__dict__.update(StoryDatabase().__dict__)
        
        mock_user = {"uid": "test_user_123", "email": "test@example.com"}
        
        # Get existing chapter
        chapter_id = list(db.chapters.keys())[0]
        
        # Create additional nodes in the chapter
        opening_node = await create_story_node({
            "chapter_id": chapter_id,
            "node_type": "opening",
            "title": "Chapter Opening",
            "content": "The chapter begins",
            "therapeutic_tags": ["motivation"]
        }, current_user=mock_user)
        
        choice_node = await create_story_node({
            "chapter_id": chapter_id,
            "node_type": "choice",
            "title": "Important Decision",
            "content": "Choose your path",
            "therapeutic_tags": ["decision_making"]
        }, current_user=mock_user)
        
        ending_node = await create_story_node({
            "chapter_id": chapter_id,
            "node_type": "ending",
            "title": "Chapter Conclusion",
            "content": "The chapter ends",
            "therapeutic_tags": ["achievement"]
        }, current_user=mock_user)
        
        # Create edges
        await create_story_edge({
            "from_node_id": opening_node["node_id"],
            "to_node_id": choice_node["node_id"],
            "choice_text": "Continue forward"
        }, current_user=mock_user)
        
        await create_story_edge({
            "from_node_id": choice_node["node_id"],
            "to_node_id": ending_node["node_id"],
            "choice_text": "Reach the conclusion"
        }, current_user=mock_user)
        
        # Get chapter structure
        structure_result = await get_chapter_structure(
            chapter_id=chapter_id,
            current_user=mock_user
        )
        
        assert "chapter" in structure_result
        assert "nodes" in structure_result
        assert "edges" in structure_result
        assert "structure_stats" in structure_result
        
        # Check chapter info
        chapter_info = structure_result["chapter"]
        assert chapter_info["chapter_id"] == chapter_id
        
        # Check nodes (should include existing sample nodes plus new ones)
        nodes = structure_result["nodes"]
        assert len(nodes) >= 3  # At least our 3 new nodes
        
        # Find our created nodes
        opening_found = any(n["title"] == "Chapter Opening" for n in nodes)
        choice_found = any(n["title"] == "Important Decision" for n in nodes)
        ending_found = any(n["title"] == "Chapter Conclusion" for n in nodes)
        
        assert opening_found
        assert choice_found
        assert ending_found
        
        # Check edges
        edges = structure_result["edges"]
        assert len(edges) >= 2  # At least our 2 new edges
        
        # Check structure stats
        stats = structure_result["structure_stats"]
        assert stats["total_nodes"] >= 3
        assert stats["total_edges"] >= 2
        assert stats["opening_nodes"] >= 1
        assert stats["choice_nodes"] >= 1
        assert stats["ending_nodes"] >= 1

if __name__ == "__main__":
    pytest.main([__file__, "-v"])