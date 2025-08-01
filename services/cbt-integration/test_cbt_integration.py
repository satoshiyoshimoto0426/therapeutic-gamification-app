"""
CBT Integration Service ?

?
- バリデーションABCモデル1タスク
- ?45?
- 治療
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import json

# ?
from main import app, cbt_engine, CBTTriggerType

client = TestClient(app)

class TestCBTIntegrationEngine:
    """CBT?"""
    
    async def test_battle_victory_abc_trigger(self):
        """バリデーションABCモデル"""
        user_id = "victory_test_user"
        context = {
            "battle_result": {
                "enemy_type": "?",
                "victory_type": "complete",
                "tasks_completed": 3,
                "xp_gained": 150
            },
            "event_description": "?"
        }
        
        result = await cbt_engine.trigger_cbt_intervention(
            CBTTriggerType.BATTLE_VICTORY, user_id, context
        )
        
        assert result["success"] is True
        assert result["trigger_type"] == "battle_victory"
        assert "abc_prompt" in result
        assert result["abc_prompt"] is not None
        
        # ABCプレビュー
        abc_prompt = result["abc_prompt"]
        assert "?" in abc_prompt["title"]
        assert "prompts" in abc_prompt
        assert "activating_event" in abc_prompt["prompts"]
        assert "belief" in abc_prompt["prompts"]
        assert "consequence" in abc_prompt["prompts"]
        
        print("? バリデーションABCモデル")
        return result["session_id"]
    
    async def test_abc_entry_submission(self):
        """ABCエラー"""
        # ま
        session_id = await self.test_battle_victory_abc_trigger()
        
        abc_data = {
            "activating_event": "?",
            "belief": "や",
            "consequence": "?"
        }
        
        result = await cbt_engine.submit_abc_entry(session_id, abc_data)
        
        assert result["success"] is True
        assert "entry_id" in result
        assert "rational_response" in result
        assert "thought_pattern_analysis" in result
        assert result["completion_reward"]["xp"] == 25
        
        # ?
        analysis = result["thought_pattern_analysis"]
        assert "detected_patterns" in analysis
        assert "cognitive_flexibility_score" in analysis
        
        print("? ABCエラー")
        return result["entry_id"]
    
    async def test_battle_defeat_micro_intervention(self):
        """バリデーション"""
        user_id = "defeat_test_user"
        context = {
            "battle_result": {
                "enemy_type": "?",
                "defeat_type": "overwhelming",
                "attempts": 3
            },
            "event_description": "?"
        }
        
        result = await cbt_engine.trigger_cbt_intervention(
            CBTTriggerType.BATTLE_DEFEAT, user_id, context
        )
        
        assert result["success"] is True
        assert result["trigger_type"] == "battle_defeat"
        assert len(result["suggested_interventions"]) > 0
        
        # ?45?
        for intervention in result["suggested_interventions"]:
            assert intervention["duration_seconds"] <= 45
            assert "video_url" in intervention
            assert "technique" in intervention
        
        # ?overwhelming defeat?
        breathing_interventions = [
            i for i in result["suggested_interventions"] 
            if i["technique"] == "breathing"
        ]
        assert len(breathing_interventions) > 0
        
        print(f"? バリデーション: {len(result['suggested_interventions'])}?")
        return result["session_id"]
    
    async def test_intervention_completion(self):
        """?"""
        # ま
        session_id = await self.test_battle_defeat_micro_intervention()
        
        # ?
        session = cbt_engine.cbt_sessions[session_id]
        intervention_id = session.interventions_suggested[0]
        effectiveness_rating = 4  # 5?4
        
        result = await cbt_engine.complete_intervention(
            session_id, intervention_id, effectiveness_rating
        )
        
        assert result["success"] is True
        assert result["effectiveness_rating"] == 4
        assert "session_summary" in result
        assert "therapeutic_progress" in result
        
        # ?
        summary = result["session_summary"]
        assert summary["total_interventions"] == 1
        assert summary["session_duration_minutes"] >= 0
        
        print("? ?")
    
    async def test_negative_thought_intervention(self):
        """?"""
        user_id = "negative_thought_user"
        context = {
            "thought_content": "?",
            "mood_rating": 2,
            "trigger_situation": "タスク"
        }
        
        result = await cbt_engine.trigger_cbt_intervention(
            CBTTriggerType.NEGATIVE_THOUGHT, user_id, context
        )
        
        assert result["success"] is True
        assert len(result["suggested_interventions"]) > 0
        
        # ?
        thought_stop_interventions = [
            i for i in result["suggested_interventions"]
            if "thought_stop" in i["technique"] or "thought_stopping" in i["technique"]
        ]
        assert len(thought_stop_interventions) > 0
        
        print("? ?")
    
    async def test_thought_pattern_detection(self):
        """?"""
        # ?
        abc_entry_data = {
            "activating_event": "プレビュー",
            "belief": "?",
            "consequence": "?"
        }
        
        # ?ABCエラー
        from main import ABCModelEntry
        abc_entry = ABCModelEntry(
            entry_id="test_entry",
            user_id="pattern_test_user",
            trigger_event="プレビュー",
            activating_event=abc_entry_data["activating_event"],
            belief=abc_entry_data["belief"],
            consequence=abc_entry_data["consequence"],
            created_at=datetime.now(),
            therapeutic_context="test"
        )
        
        analysis = await cbt_engine._analyze_thought_patterns(abc_entry)
        
        assert "detected_patterns" in analysis
        assert len(analysis["detected_patterns"]) > 0
        
        # ?
        pattern_names = [p["pattern_name"] for p in analysis["detected_patterns"]]
        assert "?" in pattern_names
        
        print(f"? ?: {len(analysis['detected_patterns'])}?")
    
    async def test_user_cbt_history(self):
        """ユーザーCBT?"""
        user_id = "history_test_user"
        
        # ?CBT?
        for i in range(3):
            context = {"test_session": i}
            await cbt_engine.trigger_cbt_intervention(
                CBTTriggerType.BATTLE_VICTORY, user_id, context
            )
        
        # ?
        history = await cbt_engine.get_user_cbt_history(user_id, days=30)
        
        assert history["user_id"] == user_id
        assert history["summary"]["total_cbt_sessions"] >= 3
        assert "cognitive_progress" in history
        assert "recent_abc_entries" in history
        
        # ?
        progress = history["cognitive_progress"]
        assert 1 <= progress["awareness_level"] <= 5
        assert 1 <= progress["coping_skills"] <= 5
        assert 1 <= progress["thought_flexibility"] <= 5
        
        print(f"? ユーザーCBT?: {history['summary']['total_cbt_sessions']}?")

class TestTherapeuticSafety:
    """治療"""
    
    def test_intervention_duration_limits(self):
        """?"""
        for intervention in cbt_engine.micro_interventions:
            assert intervention.duration_seconds <= 45, f"? {intervention.intervention_id} が45?"
        
        print(f"? ?: ?{len(cbt_engine.micro_interventions)}?45?")
    
    def test_therapeutic_technique_coverage(self):
        """治療"""
        techniques = set()
        for intervention in cbt_engine.micro_interventions:
            techniques.add(intervention.therapeutic_technique)
        
        # ?
        expected_techniques = ["breathing", "reframing", "grounding", "self_compassion"]
        for technique in expected_techniques:
            assert any(technique in t for t in techniques), f"治療 {technique} が"
        
        print(f"? 治療: {len(techniques)}?")
    
    def test_thought_pattern_comprehensiveness(self):
        """?"""
        pattern_types = set()
        for pattern in cbt_engine.thought_patterns:
            pattern_types.add(pattern.cognitive_distortion_type)
        
        # ?
        expected_distortions = ["dichotomous_thinking", "catastrophizing", "mind_reading", "should_statements"]
        for distortion in expected_distortions:
            assert distortion in pattern_types, f"? {distortion} が"
        
        print(f"? ?: {len(pattern_types)}?")
    
    async def test_rational_response_generation(self):
        """?"""
        test_beliefs = [
            "?",
            "?",
            "や"
        ]
        
        for belief in test_beliefs:
            from main import ABCModelEntry
            abc_entry = ABCModelEntry(
                entry_id="test",
                user_id="test_user",
                trigger_event="test",
                activating_event="test",
                belief=belief,
                consequence="test",
                created_at=datetime.now(),
                therapeutic_context="test"
            )
            
            rational_response = await cbt_engine._generate_rational_response(abc_entry)
            
            assert len(rational_response) > 0
            assert isinstance(rational_response, str)
        
        print("? ?")

class TestAPIEndpoints:
    """APIエラー"""
    
    def test_trigger_cbt_intervention_endpoint(self):
        """CBT?"""
        request_data = {
            "trigger_type": "battle_victory",
            "user_id": "api_test_user",
            "context": {
                "battle_result": {
                    "enemy_type": "?",
                    "victory_type": "complete"
                }
            }
        }
        
        response = client.post("/cbt/trigger", params={
            "trigger_type": request_data["trigger_type"],
            "user_id": request_data["user_id"]
        }, json=request_data["context"])
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "session_id" in data
        assert "abc_prompt" in data
        
        print("? CBT?")
    
    def test_list_interventions_endpoint(self):
        """?"""
        response = client.get("/cbt/interventions")
        
        assert response.status_code == 200
        data = response.json()
        assert "interventions" in data
        assert "total_count" in data
        assert data["max_duration_seconds"] == 45
        assert data["total_count"] > 0
        
        print(f"? ?: {data['total_count']}?")
    
    def test_list_thought_patterns_endpoint(self):
        """?"""
        response = client.get("/cbt/thought-patterns")
        
        assert response.status_code == 200
        data = response.json()
        assert "thought_patterns" in data
        assert "total_count" in data
        assert data["total_count"] > 0
        
        print(f"? ?: {data['total_count']}?")
    
    def test_cbt_analytics_endpoint(self):
        """CBT?"""
        response = client.get("/cbt/analytics")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_cbt_sessions" in data
        assert "total_abc_entries" in data
        assert "trigger_type_distribution" in data
        assert "therapeutic_outcomes" in data
        
        print("? CBT?")
    
    def test_user_history_endpoint(self):
        """ユーザー"""
        user_id = "api_history_user"
        
        response = client.get(f"/cbt/user/{user_id}/history?days=30")
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user_id
        assert "summary" in data
        assert "cognitive_progress" in data
        
        print("? ユーザー")

def run_all_tests():
    """?"""
    print("CBT Integration Service ?")
    print("=" * 50)
    
    # 基本
    engine_tests = TestCBTIntegrationEngine()
    
    async def run_async_engine_tests():
        await engine_tests.test_battle_victory_abc_trigger()
        await engine_tests.test_abc_entry_submission()
        await engine_tests.test_battle_defeat_micro_intervention()
        await engine_tests.test_intervention_completion()
        await engine_tests.test_negative_thought_intervention()
        await engine_tests.test_thought_pattern_detection()
        await engine_tests.test_user_cbt_history()
    
    asyncio.run(run_async_engine_tests())
    
    # 治療
    safety_tests = TestTherapeuticSafety()
    safety_tests.test_intervention_duration_limits()
    safety_tests.test_therapeutic_technique_coverage()
    safety_tests.test_thought_pattern_comprehensiveness()
    
    async def run_async_safety_tests():
        await safety_tests.test_rational_response_generation()
    
    asyncio.run(run_async_safety_tests())
    
    # APIエラー
    api_tests = TestAPIEndpoints()
    api_tests.test_trigger_cbt_intervention_endpoint()
    api_tests.test_list_interventions_endpoint()
    api_tests.test_list_thought_patterns_endpoint()
    api_tests.test_cbt_analytics_endpoint()
    api_tests.test_user_history_endpoint()
    
    print("\n" + "=" * 50)
    print("? CBT Integration Service ?")
    print("\n?:")
    print("- バリデーションABCモデル1タスク ?")
    print("- ?45? ?")
    print("- 治療 ?")
    print("- ? ?")
    print("- CBT? ?")

if __name__ == "__main__":
    run_all_tests()