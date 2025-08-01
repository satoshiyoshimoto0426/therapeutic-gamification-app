"""
Task 24.2 ?: ?
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import json

# ?
from feedback_analysis import (
    FeedbackAnalysisEngine, FeedbackCategory, FeedbackPriority,
    SentimentType, FeedbackItem
)
from main import AlphaPlaytestEngine, FeedbackType

class TestFeedbackAnalysisIntegration:
    """?"""
    
    @pytest.fixture
    def feedback_engine(self):
        """?"""
        return FeedbackAnalysisEngine()
    
    @pytest.fixture
    def playtest_engine(self):
        """プレビュー"""
        engine = AlphaPlaytestEngine()
        engine.max_test_users = 10
        return engine
    
    @pytest.mark.asyncio
    async def test_feedback_submission_and_analysis(self, feedback_engine):
        """?"""
        
        # 1. ?
        positive_feedback = await feedback_engine.submit_feedback(
            user_id="user_001",
            category=FeedbackCategory.USABILITY,
            title="使用",
            content="こ",
            rating=5,
            device_info={"platform": "iOS", "version": "14.0"},
            app_version="1.0.0"
        )
        
        # 2. 基本
        assert positive_feedback.feedback_id is not None
        assert positive_feedback.user_id == "user_001"
        assert positive_feedback.category == FeedbackCategory.USABILITY
        assert positive_feedback.rating == 5
        assert positive_feedback.processed
        
        # 3. ?
        sentiment = positive_feedback.sentiment_analysis
        assert sentiment is not None
        assert sentiment.overall_score > 0  # ?
        assert sentiment.sentiment_type in [SentimentType.POSITIVE, SentimentType.VERY_POSITIVE]
        assert len(sentiment.positive_keywords) > 0
        
        # 4. ?
        assert "ui_navigation" in positive_feedback.themes
        assert len(positive_feedback.keywords) > 0
        
        # 5. ?
        assert positive_feedback.priority == FeedbackPriority.LOW  # ?5?
    
    @pytest.mark.asyncio
    async def test_negative_feedback_analysis(self, feedback_engine):
        """?"""
        
        # 1. ?
        negative_feedback = await feedback_engine.submit_feedback(
            user_id="user_002",
            category=FeedbackCategory.BUG_REPORT,
            title="アプリ",
            content="アプリ",
            rating=1
        )
        
        # 2. ?
        sentiment = negative_feedback.sentiment_analysis
        assert sentiment.overall_score < 0  # ?
        assert sentiment.sentiment_type in [SentimentType.NEGATIVE, SentimentType.VERY_NEGATIVE]
        assert len(sentiment.negative_keywords) > 0
        
        # 3. ?
        assert negative_feedback.priority == FeedbackPriority.CRITICAL
        
        # 4. ?
        assert "performance" in negative_feedback.themes or "bug_report" in negative_feedback.themes
    
    @pytest.mark.asyncio
    async def test_theme_analysis_generation(self, feedback_engine):
        """?"""
        
        # 1. ?
        feedback_data = [
            {
                "user_id": "user_001",
                "category": FeedbackCategory.USABILITY,
                "title": "?",
                "content": "メイン",
                "rating": 2
            },
            {
                "user_id": "user_002",
                "category": FeedbackCategory.USABILITY,
                "title": "UI?",
                "content": "?",
                "rating": 3
            },
            {
                "user_id": "user_003",
                "category": FeedbackCategory.PERFORMANCE,
                "title": "?",
                "content": "アプリ",
                "rating": 2
            },
            {
                "user_id": "user_004",
                "category": FeedbackCategory.THERAPEUTIC_EFFECT,
                "title": "?",
                "content": "こ",
                "rating": 5
            }
        ]
        
        for data in feedback_data:
            await feedback_engine.submit_feedback(**data)
        
        # 2. ?
        theme_analyses = await feedback_engine.generate_theme_analysis(days=30)
        
        # 3. ?
        assert len(theme_analyses) > 0
        
        # UI/?
        ui_theme = next((t for t in theme_analyses if t.theme == "ui_navigation"), None)
        assert ui_theme is not None
        assert ui_theme.frequency >= 2  # 2?
        assert ui_theme.user_count >= 2  # 2?
        assert ui_theme.sentiment_score < 0  # ?
        
        # ?
        perf_theme = next((t for t in theme_analyses if t.theme == "performance"), None)
        assert perf_theme is not None
        assert perf_theme.frequency >= 1
        
        # 治療
        therapeutic_theme = next((t for t in theme_analyses if t.theme == "therapeutic_effectiveness"), None)
        assert therapeutic_theme is not None
        assert therapeutic_theme.sentiment_score > 0  # ?
    
    @pytest.mark.asyncio
    async def test_improvement_suggestions_generation(self, feedback_engine):
        """?"""
        
        # 1. ?
        problem_feedback = [
            {
                "user_id": f"user_{i}",
                "category": FeedbackCategory.USABILITY,
                "title": "?",
                "content": "メイン",
                "rating": 2
            }
            for i in range(5)  # 5?
        ]
        
        for feedback in problem_feedback:
            await feedback_engine.submit_feedback(**feedback)
        
        # 2. ?
        theme_analyses = await feedback_engine.generate_theme_analysis(days=30)
        
        # 3. ?
        suggestions = await feedback_engine.generate_improvement_suggestions(theme_analyses)
        
        # 4. ?
        assert len(suggestions) > 0
        
        # UI/?
        ui_suggestions = [s for s in suggestions if s["theme"] == "ui_navigation"]
        assert len(ui_suggestions) > 0
        
        ui_suggestion = ui_suggestions[0]
        assert ui_suggestion["urgency"] in ["?", "?"]  # ?
        assert ui_suggestion["affected_users"] == 5
        assert ui_suggestion["frequency"] >= 5
        assert "?" in ui_suggestion["suggestion"]
        assert ui_suggestion["sentiment_score"] < 0
    
    @pytest.mark.asyncio
    async def test_feedback_statistics_calculation(self, feedback_engine):
        """?"""
        
        # 1. ?
        feedback_samples = [
            # バリデーション
            {
                "category": FeedbackCategory.BUG_REPORT,
                "title": "エラー",
                "content": "エラー",
                "rating": 1
            },
            # ?
            {
                "category": FeedbackCategory.FEATURE_REQUEST,
                "title": "?",
                "content": "こ",
                "rating": 4
            },
            # ユーザー
            {
                "category": FeedbackCategory.USABILITY,
                "title": "使用",
                "content": "も",
                "rating": 3
            },
            # 治療
            {
                "category": FeedbackCategory.THERAPEUTIC_EFFECT,
                "title": "?",
                "content": "と",
                "rating": 5
            }
        ]
        
        for i, feedback_data in enumerate(feedback_samples):
            await feedback_engine.submit_feedback(
                user_id=f"stats_user_{i}",
                **feedback_data
            )
        
        # 2. ?
        stats = feedback_engine.get_feedback_statistics(days=30)
        
        # 3. ?
        assert stats["total_feedback"] == 4
        assert stats["unique_users"] == 4
        
        statistics = stats["statistics"]
        
        # カスタム
        category_dist = statistics["category_distribution"]
        assert category_dist["bug_report"] == 1
        assert category_dist["feature_request"] == 1
        assert category_dist["usability"] == 1
        assert category_dist["therapeutic_effect"] == 1
        
        # ?
        priority_dist = statistics["priority_distribution"]
        assert priority_dist["high"] >= 1  # バリデーション
        assert priority_dist["medium"] >= 1  # ?
        assert priority_dist["low"] >= 1   # 治療5?
        
        # ?
        rating_dist = statistics["rating_distribution"]
        assert rating_dist[1] == 1  # 1つ
        assert rating_dist[3] == 1  # 3つ
        assert rating_dist[4] == 1  # 4つ
        assert rating_dist[5] == 1  # 5つ
        
        # ?
        assert statistics["average_rating"] == 3.25  # (1+3+4+5)/4
        
        # ?
        assert statistics["processing_rate"] == 1.0  # ?
    
    @pytest.mark.asyncio
    async def test_feedback_status_management(self, feedback_engine):
        """?"""
        
        # 1. ?
        feedback = await feedback_engine.submit_feedback(
            user_id="status_user",
            category=FeedbackCategory.BUG_REPORT,
            title="バリデーション",
            content="バリデーション",
            rating=2
        )
        
        # 2. ?
        assert feedback.status == "open"
        assert feedback.assigned_to is None
        assert feedback.resolution is None
        
        # 3. ?
        updated_feedback = await feedback_engine.update_feedback_status(
            feedback.feedback_id,
            status="in_progress",
            assigned_to="developer_001"
        )
        
        assert updated_feedback is not None
        assert updated_feedback.status == "in_progress"
        assert updated_feedback.assigned_to == "developer_001"
        
        # 4. ?
        resolved_feedback = await feedback_engine.update_feedback_status(
            feedback.feedback_id,
            status="resolved",
            resolution="バリデーション"
        )
        
        assert resolved_feedback.status == "resolved"
        assert resolved_feedback.resolution is not None
        assert "?" in resolved_feedback.resolution
    
    @pytest.mark.asyncio
    async def test_high_priority_feedback_filtering(self, feedback_engine):
        """?"""
        
        # 1. ?
        feedback_data = [
            # ?
            {
                "category": FeedbackCategory.BUG_REPORT,
                "title": "?",
                "content": "アプリ",
                "rating": 1
            },
            # ?
            {
                "category": FeedbackCategory.BUG_REPORT,
                "title": "エラー",
                "content": "エラー",
                "rating": 2
            },
            # ?
            {
                "category": FeedbackCategory.USABILITY,
                "title": "?",
                "content": "使用",
                "rating": 3
            },
            # ?
            {
                "category": FeedbackCategory.GENERAL,
                "title": "?",
                "content": "?",
                "rating": 4
            }
        ]
        
        submitted_feedback = []
        for i, data in enumerate(feedback_data):
            feedback = await feedback_engine.submit_feedback(
                user_id=f"priority_user_{i}",
                **data
            )
            submitted_feedback.append(feedback)
        
        # 2. ?
        high_priority = feedback_engine.get_high_priority_feedback()
        
        # 3. ?
        assert len(high_priority) >= 2  # ?
        
        # ?
        for feedback in high_priority:
            assert feedback.priority in [FeedbackPriority.HIGH, FeedbackPriority.CRITICAL]
            assert feedback.status in ["open", "in_progress"]
        
        # ?
        critical_feedback = [fb for fb in high_priority if fb.priority == FeedbackPriority.CRITICAL]
        assert len(critical_feedback) >= 1
    
    @pytest.mark.asyncio
    async def test_user_feedback_history(self, feedback_engine):
        """ユーザー"""
        
        # 1. ?
        user_id = "history_user"
        feedback_history = [
            {
                "category": FeedbackCategory.USABILITY,
                "title": "?",
                "content": "使用",
                "rating": 3
            },
            {
                "category": FeedbackCategory.FEATURE_REQUEST,
                "title": "?",
                "content": "こ",
                "rating": 4
            },
            {
                "category": FeedbackCategory.THERAPEUTIC_EFFECT,
                "title": "?",
                "content": "?",
                "rating": 5
            }
        ]
        
        for feedback_data in feedback_history:
            await feedback_engine.submit_feedback(user_id=user_id, **feedback_data)
            await asyncio.sleep(0.01)  # ?
        
        # 2. ユーザー
        user_feedback = feedback_engine.get_feedback_by_user(user_id)
        
        # 3. ?
        assert len(user_feedback) == 3
        
        # ?
        for feedback in user_feedback:
            assert feedback.user_id == user_id
        
        # ?
        timestamps = [fb.created_at for fb in user_feedback]
        assert timestamps == sorted(timestamps)
        
        # ?
        ratings = [fb.rating for fb in user_feedback]
        assert ratings == [3, 4, 5]  # ?
    
    @pytest.mark.asyncio
    async def test_feedback_export_report(self, feedback_engine):
        """?"""
        
        # 1. ?
        sample_feedback = [
            {
                "user_id": "export_user_1",
                "category": FeedbackCategory.BUG_REPORT,
                "title": "バリデーション",
                "content": "バリデーション",
                "rating": 2
            },
            {
                "user_id": "export_user_2",
                "category": FeedbackCategory.USABILITY,
                "title": "UI?",
                "content": "UIを",
                "rating": 3
            }
        ]
        
        for feedback_data in sample_feedback:
            await feedback_engine.submit_feedback(**feedback_data)
        
        # 2. レベル
        report_json = feedback_engine.export_feedback_report(format="json")
        
        # 3. ?
        assert report_json is not None
        
        # JSON?
        report_data = json.loads(report_json)
        
        # 基本
        assert "generated_at" in report_data
        assert "summary" in report_data
        assert "theme_analysis" in report_data
        assert "high_priority_items" in report_data
        assert "recent_feedback" in report_data
        
        # ?
        summary = report_data["summary"]
        assert summary["total_feedback"] >= 2
        assert summary["unique_users"] >= 2
        
        # ?
        recent_feedback = report_data["recent_feedback"]
        assert len(recent_feedback) >= 2
        
        for feedback in recent_feedback:
            assert "feedback_id" in feedback
            assert "category" in feedback
            assert "title" in feedback
            assert "rating" in feedback
            assert "priority" in feedback
            assert "status" in feedback
            assert "created_at" in feedback

if __name__ == "__main__":
    pytest.main([__file__, "-v"])