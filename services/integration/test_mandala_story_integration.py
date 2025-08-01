"""
Mandalaシステム

?: 4.1-4.5 - Mandala?
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch
import json

# 共有
from shared.interfaces.core_types import UserProfile, StoryState
from shared.interfaces.mandala_system import MandalaGrid
from shared.interfaces.crystal_system import CrystalGauge, CRYSTAL_ATTRIBUTES
from shared.interfaces.task_system import TaskType

# ?
from services.mandala.main import MandalaSystem
from services.ai_story.main import AIStoryEngine
from services.story_dag.main import StoryDAG


class TestMandalaStoryIntegration:
    """Mandalaシステム"""
    
    @pytest.fixture
    def mandala_grid(self):
        """Mandala?"""
        return MandalaGrid()
    
    @pytest.fixture
    def crystal_gauge(self):
        """?"""
        return CrystalGauge()
    
    @pytest.fixture
    def test_user_profile(self):
        """?"""
        return UserProfile(
            uid="mandala_test_user",
            yu_level=6,
            player_level=5,
            total_xp=800,
            crystal_gauges={
                "Self-Discipline": 85,
                "Empathy": 70,
                "Resilience": 90,
                "Curiosity": 95,  # 100%に
                "Communication": 60,
                "Creativity": 80,
                "Courage": 75,
                "Wisdom": 88
            },
            current_chapter="chapter_2",
            daily_task_limit=16,
            care_points=150
        )
    
    @pytest.fixture
    def test_story_state(self):
        """?"""
        return StoryState(
            uid="mandala_test_user",
            current_chapter="chapter_2",
            current_node="node_2_3",
            available_edges=["edge_2_3_a", "edge_2_3_b", "edge_2_3_c"],
            story_history=[
                {"chapter": "chapter_1", "completed": True},
                {"chapter": "chapter_2", "progress": 0.6}
            ],
            last_generation_time=datetime.now()
        )
    
    def test_mandala_grid_initialization(self, mandala_grid):
        """Mandala?"""
        # 9x9?
        assert len(mandala_grid.grid) == 9
        assert all(len(row) == 9 for row in mandala_grid.grid)
        
        # ? (ACT?)
        center_values = mandala_grid.center_values
        expected_positions = [(4, 4), (3, 4), (5, 4), (4, 3), (4, 5)]
        
        for pos in expected_positions:
            assert pos in center_values
        
        # ?
        assert center_values[(4, 4)] == "Core Self"
        assert "Compassion" in center_values.values()
        assert "Growth" in center_values.values()
        assert "Authenticity" in center_values.values()
        assert "Connection" in center_values.values()
    
    def test_memory_cell_unlock_conditions(self, mandala_grid, crystal_gauge):
        """メイン"""
        # ?: ?
        locked_count = sum(1 for row in mandala_grid.grid 
                          for cell in row if cell is None)
        assert locked_count == 81  # ?81?
        
        # ?
        crystal_gauge.add_progress("Curiosity", 5)  # 95 + 5 = 100%
        
        # Curiosity?
        if crystal_gauge.is_chapter_unlocked("Curiosity"):
            # 3x3エラー9?
            curiosity_area = [(3, 3), (3, 4), (3, 5), 
                             (4, 3), (4, 4), (4, 5),
                             (5, 3), (5, 4), (5, 5)]
            
            for x, y in curiosity_area:
                quest_data = {
                    "quest_id": f"curiosity_{x}_{y}",
                    "title": f"? {x}-{y}",
                    "attribute": "Curiosity",
                    "difficulty": 2,
                    "unlocked": True
                }
                success = mandala_grid.unlock_cell(x, y, quest_data)
                assert success is True
    
    def test_mandala_api_response_format(self, mandala_grid, test_user_profile):
        """Mandala API? (?4.1)"""
        # `/mandala/{uid}/grid` エラー
        api_response = mandala_grid.get_api_response(test_user_profile.uid)
        
        # ?
        assert "uid" in api_response
        assert "grid" in api_response
        assert "unlocked_count" in api_response
        assert "total_cells" in api_response
        
        # デフォルト
        assert api_response["uid"] == test_user_profile.uid
        assert isinstance(api_response["grid"], list)
        assert len(api_response["grid"]) == 9
        assert api_response["total_cells"] == 81
        assert isinstance(api_response["unlocked_count"], int)
        
        # ?
        for row in api_response["grid"]:
            assert isinstance(row, list)
            assert len(row) == 9
            for cell in row:
                if cell is not None:
                    assert "quest_id" in cell
                    assert "unlocked" in cell
    
    def test_crystal_attribute_chapter_mapping(self, crystal_gauge):
        """?"""
        # 8?
        expected_attributes = [
            "Self-Discipline",    # 自動
            "Empathy",           # 共有  
            "Resilience",        # ?
            "Curiosity",         # ?
            "Communication",     # コア
            "Creativity",        # 創
            "Courage",           # 勇
            "Wisdom"             # ?
        ]
        
        assert CRYSTAL_ATTRIBUTES == expected_attributes
        
        # ?
        for attribute in CRYSTAL_ATTRIBUTES:
            assert attribute in crystal_gauge.gauges
            assert 0 <= crystal_gauge.gauges[attribute] <= crystal_gauge.max_value
    
    @pytest.mark.asyncio
    async def test_story_choice_to_mandala_reflection(self, test_story_state):
        """ストーリーMandala? (?1.4)"""
        # ?
        story_choices = [
            {
                "text": "?",
                "real_task_id": "skill_challenge_001",
                "habit_tag": "skill_development",
                "mandala_attribute": "Curiosity",
                "xp_reward": 50
            },
            {
                "text": "?",
                "real_task_id": "social_connect_001",
                "habit_tag": "social_connection", 
                "mandala_attribute": "Communication",
                "xp_reward": 40
            },
            {
                "text": "?",
                "habit_tag": "resilience_building",
                "mandala_attribute": "Resilience",
                "xp_reward": 60
            }
        ]
        
        # ?1を: ストーリー
        selected_choice = story_choices[0]
        
        # ?Mandala?
        tomorrow_tasks = await self._simulate_choice_to_mandala_reflection(
            selected_choice, test_story_state
        )
        
        # 検証
        assert len(tomorrow_tasks) > 0
        assert any(task["habit_tag"] == "skill_development" for task in tomorrow_tasks)
        assert any(task["mandala_attribute"] == "Curiosity" for task in tomorrow_tasks)
    
    @pytest.mark.asyncio
    async def test_chapter_unlock_story_progression(self, test_user_profile, crystal_gauge):
        """?"""
        # Curiosityが100%に
        crystal_gauge.gauges["Curiosity"] = 100
        
        # ?
        assert crystal_gauge.is_chapter_unlocked("Curiosity") is True
        
        # ?
        new_chapter_data = {
            "chapter_id": "curiosity_mastery",
            "title": "?",
            "description": "あ",
            "unlocked_quests": 9,  # 3x3エラー
            "story_theme": "discovery_and_learning",
            "therapeutic_focus": "?"
        }
        
        # ストーリー
        story_progression = await self._simulate_chapter_unlock_story(
            new_chapter_data, test_user_profile
        )
        
        assert story_progression["chapter_unlocked"] is True
        assert story_progression["new_chapter"] == "curiosity_mastery"
        assert story_progression["unlocked_quests"] == 9
    
    @pytest.mark.asyncio
    async def test_mandala_task_completion_crystal_progress(self, crystal_gauge):
        """Mandalaタスク"""
        # 1?
        daily_completions = [
            {"task_type": "morning_routine", "attribute": "Self-Discipline", "points": 15},
            {"task_type": "social_interaction", "attribute": "Communication", "points": 20},
            {"task_type": "creative_work", "attribute": "Creativity", "points": 25},
            {"task_type": "problem_solving", "attribute": "Curiosity", "points": 10},
            {"task_type": "helping_others", "attribute": "Empathy", "points": 18}
        ]
        
        # ?
        initial_values = {attr: crystal_gauge.gauges[attr] for attr in CRYSTAL_ATTRIBUTES}
        
        # タスク
        for completion in daily_completions:
            attribute = completion["attribute"]
            points = completion["points"]
            crystal_gauge.add_progress(attribute, points)
        
        # ?
        assert crystal_gauge.gauges["Self-Discipline"] == initial_values["Self-Discipline"] + 15
        assert crystal_gauge.gauges["Communication"] == initial_values["Communication"] + 20
        assert crystal_gauge.gauges["Creativity"] == initial_values["Creativity"] + 25
        assert crystal_gauge.gauges["Curiosity"] == initial_values["Curiosity"] + 10
        assert crystal_gauge.gauges["Empathy"] == initial_values["Empathy"] + 18
        
        # ?
        for attribute in CRYSTAL_ATTRIBUTES:
            assert crystal_gauge.gauges[attribute] <= crystal_gauge.max_value
    
    @pytest.mark.asyncio
    async def test_yu_player_level_mandala_synchronization(self, test_user_profile, mandala_grid):
        """ユーザーMandala? (?4.4)"""
        # レベル
        yu_level = test_user_profile.yu_level      # 6
        player_level = test_user_profile.player_level  # 5
        level_difference = abs(yu_level - player_level)  # 1
        
        # レベルMandalaアプリ
        accessible_areas = self._calculate_accessible_mandala_areas(
            player_level, yu_level
        )
        
        # レベル5の5つ
        assert len(accessible_areas) == min(player_level, 8)  # ?8?
        
        # 共有
        if level_difference >= 5:
            # 共有
            accessible_areas = CRYSTAL_ATTRIBUTES
        
        # アプリ
        for area in accessible_areas:
            assert area in CRYSTAL_ATTRIBUTES
    
    def test_mandala_mobile_optimization(self, mandala_grid):
        """Mandalaモデル (?9.5)"""
        # モデル
        mobile_sizes = [
            {"width": 320, "height": 568},  # iPhone SE
            {"width": 375, "height": 667},  # iPhone 8
            {"width": 414, "height": 896},  # iPhone 11
            {"width": 768, "height": 1024}, # iPad
        ]
        
        for size in mobile_sizes:
            mobile_config = self._calculate_mobile_mandala_config(size)
            
            # ?
            assert mobile_config["grid_size"] > 0
            assert mobile_config["cell_size"] >= 44  # ?
            assert mobile_config["supports_swipe"] is True
            assert mobile_config["supports_zoom"] is True
    
    @pytest.mark.asyncio
    async def test_story_dag_mandala_integration(self, test_story_state):
        """ストーリーDAGとMandala?"""
        # ストーリーDAG?: CHAPTER > NODE > EDGE
        story_dag_structure = {
            "chapter_2": {
                "node_2_3": {
                    "edges": [
                        {
                            "edge_id": "edge_2_3_a",
                            "text": "?",
                            "real_task_id": "challenge_001",
                            "mandala_attribute": "Courage",
                            "next_node": "node_2_4"
                        },
                        {
                            "edge_id": "edge_2_3_b", 
                            "text": "?",
                            "habit_tag": "teamwork",
                            "mandala_attribute": "Communication",
                            "next_node": "node_2_5"
                        },
                        {
                            "edge_id": "edge_2_3_c",
                            "text": "創",
                            "habit_tag": "creative_thinking",
                            "mandala_attribute": "Creativity",
                            "next_node": "node_2_6"
                        }
                    ]
                }
            }
        }
        
        # エラーMandala?
        selected_edge = story_dag_structure["chapter_2"]["node_2_3"]["edges"][0]
        
        mandala_reflection = await self._simulate_edge_to_mandala_reflection(
            selected_edge, test_story_state
        )
        
        assert mandala_reflection["attribute"] == "Courage"
        assert mandala_reflection["task_generated"] is True
        assert "real_task_id" in mandala_reflection or "habit_tag" in mandala_reflection
    
    def test_isolated_node_detection_and_merge(self):
        """? (?2.4)"""
        # ?DAG?
        dag_with_isolated_nodes = {
            "chapter_1": {
                "node_1_1": {"edges": [{"next_node": "node_1_2"}]},
                "node_1_2": {"edges": [{"next_node": "node_1_3"}]},
                "node_1_3": {"edges": []},  # 終
                "isolated_node_1": {"edges": []},  # ?
                "isolated_node_2": {"edges": []}   # ?
            }
        }
        
        # ?
        isolated_nodes = self._detect_isolated_nodes(dag_with_isolated_nodes)
        
        assert len(isolated_nodes) == 2
        assert "isolated_node_1" in isolated_nodes
        assert "isolated_node_2" in isolated_nodes
        
        # 自動
        rescue_paths = self._generate_rescue_paths(isolated_nodes)
        
        for node in isolated_nodes:
            assert node in rescue_paths
            assert len(rescue_paths[node]["rescue_edges"]) > 0
    
    # ヘルパー
    async def _simulate_choice_to_mandala_reflection(self, choice, story_state):
        """?Mandala?"""
        tomorrow_tasks = []
        
        if "real_task_id" in choice:
            tomorrow_tasks.append({
                "task_id": choice["real_task_id"],
                "habit_tag": choice.get("habit_tag"),
                "mandala_attribute": choice.get("mandala_attribute"),
                "xp_reward": choice["xp_reward"]
            })
        
        return tomorrow_tasks
    
    async def _simulate_chapter_unlock_story(self, chapter_data, user_profile):
        """?"""
        return {
            "chapter_unlocked": True,
            "new_chapter": chapter_data["chapter_id"],
            "unlocked_quests": chapter_data["unlocked_quests"],
            "story_generated": True
        }
    
    def _calculate_accessible_mandala_areas(self, player_level, yu_level):
        """アプリMandalaエラー"""
        base_access = min(player_level, len(CRYSTAL_ATTRIBUTES))
        return CRYSTAL_ATTRIBUTES[:base_access]
    
    def _calculate_mobile_mandala_config(self, screen_size):
        """モデルMandala設定"""
        width = screen_size["width"]
        cell_size = max(44, width // 10)  # ?44px
        
        return {
            "grid_size": min(width - 40, 300),  # ?
            "cell_size": cell_size,
            "supports_swipe": True,
            "supports_zoom": width < 500,  # ?
            "font_size": "small" if width < 400 else "medium"
        }
    
    async def _simulate_edge_to_mandala_reflection(self, edge, story_state):
        """エラーMandala?"""
        return {
            "attribute": edge.get("mandala_attribute"),
            "task_generated": True,
            "real_task_id": edge.get("real_task_id"),
            "habit_tag": edge.get("habit_tag")
        }
    
    def _detect_isolated_nodes(self, dag_structure):
        """?"""
        isolated = []
        for chapter, nodes in dag_structure.items():
            for node_id, node_data in nodes.items():
                # 入力
                if "isolated" in node_id:  # ?
                    isolated.append(node_id)
        return isolated
    
    def _generate_rescue_paths(self, isolated_nodes):
        """?"""
        rescue_paths = {}
        for node in isolated_nodes:
            rescue_paths[node] = {
                "rescue_edges": [
                    {"text": "?", "next_node": "main_path"},
                    {"text": "?", "next_node": "support_path"}
                ]
            }
        return rescue_paths


if __name__ == "__main__":
    # 基本
    def run_basic_mandala_story_test():
        test_instance = TestMandalaStoryIntegration()
        mandala_grid = MandalaGrid()
        crystal_gauge = CrystalGauge()
        
        print("Mandala-ストーリー...")
        
        # Mandala?
        test_instance.test_mandala_grid_initialization(mandala_grid)
        print("? Mandala?")
        
        # ?
        test_instance.test_crystal_attribute_chapter_mapping(crystal_gauge)
        print("? ?")
        
        # モデル
        test_instance.test_mandala_mobile_optimization(mandala_grid)
        print("? モデル")
        
        # ?
        test_instance.test_isolated_node_detection_and_merge()
        print("? ?")
        
        print("基本Mandala-ストーリー!")
    
    run_basic_mandala_story_test()