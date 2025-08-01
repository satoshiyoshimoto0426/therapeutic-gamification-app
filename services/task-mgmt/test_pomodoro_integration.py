"""
Pomodoro?ADHD支援

Requirements: 3.2, 5.3
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

from pomodoro_integration import (
    PomodoroIntegrationService, PomodoroSession, PomodoroSessionStatus,
    BreakType, WorkSession, ADHDSupportMetrics
)


class TestPomodoroIntegrationService:
    """Pomodoro?"""
    
    @pytest.fixture
    def service(self):
        """?"""
        return PomodoroIntegrationService()
    
    @pytest.fixture
    def sample_uid(self):
        """?ID"""
        return "test_user_123"
    
    @pytest.fixture
    def sample_task_id(self):
        """?ID"""
        return "task_test_123"
    
    @pytest.mark.asyncio
    async def test_start_pomodoro_session(self, service, sample_uid, sample_task_id):
        """Pomodoro?"""
        # ?
        session = await service.start_pomodoro_session(
            uid=sample_uid,
            task_id=sample_task_id,
            duration=25,
            focus_music_enabled=True
        )
        
        # 検証
        assert session.uid == sample_uid
        assert session.task_id == sample_task_id
        assert session.planned_duration == 25
        assert session.status == PomodoroSessionStatus.ACTIVE
        assert session.focus_music_enabled is True
        assert session.started_at is not None
        assert session.session_id in service.pomodoro_sessions
        
        # ?
        assert sample_uid in service.work_sessions
        work_session = service.work_sessions[sample_uid]
        assert session.session_id in work_session.pomodoro_sessions
    
    @pytest.mark.asyncio
    async def test_complete_pomodoro_session(self, service, sample_uid, sample_task_id):
        """Pomodoro?"""
        # ?
        session = await service.start_pomodoro_session(
            uid=sample_uid,
            task_id=sample_task_id,
            duration=25
        )
        
        # ?
        completed_session = await service.complete_pomodoro_session(
            session_id=session.session_id,
            actual_duration=23,
            notes="?"
        )
        
        # 検証
        assert completed_session.status == PomodoroSessionStatus.COMPLETED
        assert completed_session.actual_duration == 23
        assert completed_session.notes == "?"
        assert completed_session.completed_at is not None
        
        # ADHD支援
        assert sample_uid in service.adhd_metrics
        metrics = service.adhd_metrics[sample_uid]
        assert metrics.total_pomodoro_sessions == 1
        assert metrics.successful_sessions == 1
    
    @pytest.mark.asyncio
    async def test_start_and_complete_break(self, service, sample_uid, sample_task_id):
        """?"""
        # ?
        session = await service.start_pomodoro_session(sample_uid, sample_task_id)
        await service.complete_pomodoro_session(session.session_id)
        
        # ?
        break_session = await service.start_break(
            session_id=session.session_id,
            break_type=BreakType.SHORT
        )
        
        # 検証
        assert break_session.status == PomodoroSessionStatus.BREAK
        assert break_session.break_type == BreakType.SHORT
        assert break_session.break_duration == 5
        assert break_session.break_started_at is not None
        
        # ?
        completed_break = await service.complete_break(session.session_id)
        assert completed_break.status == PomodoroSessionStatus.COMPLETED
        assert completed_break.break_completed_at is not None
    
    @pytest.mark.asyncio
    async def test_cancel_session(self, service, sample_uid, sample_task_id):
        """?"""
        # ?
        session = await service.start_pomodoro_session(sample_uid, sample_task_id)
        
        # ?
        cancelled_session = await service.cancel_session(
            session_id=session.session_id,
            reason="?"
        )
        
        # 検証
        assert cancelled_session.status == PomodoroSessionStatus.CANCELLED
        assert "?" in cancelled_session.notes
    
    def test_calculate_adhd_assist_multiplier_no_data(self, service, sample_uid):
        """ADHD支援"""
        multiplier = service.calculate_adhd_assist_multiplier(sample_uid)
        assert multiplier == 1.0
    
    def test_calculate_adhd_assist_multiplier_with_data(self, service, sample_uid):
        """ADHD支援"""
        # ?
        service.adhd_metrics[sample_uid] = ADHDSupportMetrics(
            uid=sample_uid,
            total_pomodoro_sessions=20,
            successful_sessions=18,
            usage_frequency_score=0.8,  # ?
            break_compliance_rate=0.9   # ?
        )
        
        multiplier = service.calculate_adhd_assist_multiplier(sample_uid)
        
        # 検証1.0 + 0.8*0.2 + 0.9*0.1 + 0.9*0.1 = 1.34 -> 1.3に
        assert 1.2 <= multiplier <= 1.3
    
    @pytest.mark.asyncio
    async def test_check_continuous_work_time_no_session(self, service, sample_uid):
        """?"""
        result = await service.check_continuous_work_time(sample_uid)
        
        assert result["continuous_minutes"] == 0
        assert result["needs_break"] is False
        assert result["break_suggestion"] is None
    
    @pytest.mark.asyncio
    async def test_check_continuous_work_time_needs_break(self, service, sample_uid, sample_task_id):
        """?"""
        # 60?
        past_time = datetime.utcnow() - timedelta(minutes=65)
        service.work_sessions[sample_uid] = WorkSession(
            uid=sample_uid,
            start_time=past_time,
            is_active=True
        )
        
        result = await service.check_continuous_work_time(sample_uid)
        
        assert result["continuous_minutes"] >= 60
        assert result["needs_break"] is True
        assert result["break_suggestion"] is not None
        assert result["break_suggestion"]["type"] == "first_suggestion"
    
    @pytest.mark.asyncio
    async def test_handle_break_refusal_first_time(self, service, sample_uid):
        """?"""
        # ?
        service.work_sessions[sample_uid] = WorkSession(
            uid=sample_uid,
            start_time=datetime.utcnow() - timedelta(minutes=65),
            is_active=True
        )
        
        result = await service.handle_break_refusal(sample_uid)
        
        assert result["refusal_count"] == 1
        assert result["show_mother_concern"] is False
        assert result["mandatory_break_required"] is False
    
    @pytest.mark.asyncio
    async def test_handle_break_refusal_second_time(self, service, sample_uid):
        """?2?"""
        # ?1?
        service.work_sessions[sample_uid] = WorkSession(
            uid=sample_uid,
            start_time=datetime.utcnow() - timedelta(minutes=65),
            break_refusal_count=1,
            is_active=True
        )
        
        result = await service.handle_break_refusal(sample_uid)
        
        assert result["refusal_count"] == 2
        assert result["show_mother_concern"] is True
        assert result["mandatory_break_required"] is True
        assert "お" in result["narrative"]
    
    @pytest.mark.asyncio
    async def test_get_user_pomodoro_statistics(self, service, sample_uid, sample_task_id):
        """Pomodoro?"""
        # ?
        session1 = await service.start_pomodoro_session(sample_uid, sample_task_id, 25)
        await service.complete_pomodoro_session(session1.session_id, 25)
        
        session2 = await service.start_pomodoro_session(sample_uid, sample_task_id, 25)
        await service.cancel_session(session2.session_id, "?")
        
        # ?
        stats = await service.get_user_pomodoro_statistics(sample_uid, 30)
        
        # 検証
        assert stats["total_sessions"] == 2
        assert stats["completed_sessions"] == 1
        assert stats["cancelled_sessions"] == 1
        assert stats["completion_rate"] == 0.5
        assert stats["average_focus_duration"] == 25
        assert "adhd_assist_multiplier" in stats
    
    @pytest.mark.asyncio
    async def test_work_session_management(self, service, sample_uid, sample_task_id):
        """?"""
        # ?Pomodoro?
        session1 = await service.start_pomodoro_session(sample_uid, sample_task_id)
        
        # ?
        assert sample_uid in service.work_sessions
        work_session = service.work_sessions[sample_uid]
        assert len(work_session.pomodoro_sessions) == 1
        
        # 2?Pomodoro?
        session2 = await service.start_pomodoro_session(sample_uid, sample_task_id)
        
        # ?
        work_session = service.work_sessions[sample_uid]
        assert len(work_session.pomodoro_sessions) == 2
    
    def test_mother_concern_narrative_generation(self, service, sample_uid):
        """?"""
        narrative = service._generate_mother_concern_narrative(sample_uid)
        
        assert isinstance(narrative, str)
        assert len(narrative) > 0
        assert "お" in narrative
        assert any(keyword in narrative for keyword in ["?", "?", "?"])
    
    @pytest.mark.asyncio
    async def test_adhd_metrics_update(self, service, sample_uid, sample_task_id):
        """ADHD支援"""
        # ?
        session = await service.start_pomodoro_session(sample_uid, sample_task_id)
        await service.complete_pomodoro_session(session.session_id)
        
        # メイン
        metrics = service.adhd_metrics[sample_uid]
        assert metrics.total_pomodoro_sessions == 1
        assert metrics.successful_sessions == 1
        assert metrics.usage_frequency_score > 0
        assert metrics.last_updated is not None
    
    @pytest.mark.asyncio
    async def test_break_suggestion_types(self, service, sample_uid):
        """?"""
        # ?
        service.work_sessions[sample_uid] = WorkSession(
            uid=sample_uid,
            start_time=datetime.utcnow() - timedelta(minutes=30),
            is_active=True
        )
        
        suggestion = await service._generate_break_suggestion(sample_uid, service.work_sessions[sample_uid])
        assert suggestion["type"] == "first_suggestion"
        assert suggestion["is_mandatory"] is False
        
        # 1?
        service.work_sessions[sample_uid].break_refusal_count = 1
        suggestion = await service._generate_break_suggestion(sample_uid, service.work_sessions[sample_uid])
        assert suggestion["type"] == "gentle_reminder"
        
        # 2?
        service.work_sessions[sample_uid].break_refusal_count = 2
        suggestion = await service._generate_break_suggestion(sample_uid, service.work_sessions[sample_uid])
        assert suggestion["type"] == "mother_concern"
        assert suggestion["is_mandatory"] is True


class TestPomodoroModels:
    """Pomodoroモデル"""
    
    def test_pomodoro_session_creation(self):
        """Pomodoro?"""
        session = PomodoroSession(
            session_id="test_session",
            uid="test_user",
            task_id="test_task",
            planned_duration=25
        )
        
        assert session.session_id == "test_session"
        assert session.status == PomodoroSessionStatus.PENDING
        assert session.planned_duration == 25
        assert session.break_duration == 5
        assert session.interruption_count == 0
    
    def test_work_session_creation(self):
        """?"""
        work_session = WorkSession(
            uid="test_user",
            start_time=datetime.utcnow()
        )
        
        assert work_session.uid == "test_user"
        assert work_session.total_duration == 0
        assert work_session.pomodoro_sessions == []
        assert work_session.break_suggestions_count == 0
        assert work_session.break_refusal_count == 0
        assert work_session.is_active is True
    
    def test_adhd_support_metrics_creation(self):
        """ADHD支援"""
        metrics = ADHDSupportMetrics(uid="test_user")
        
        assert metrics.uid == "test_user"
        assert metrics.total_pomodoro_sessions == 0
        assert metrics.successful_sessions == 0
        assert metrics.break_compliance_rate == 0.0
        assert metrics.average_focus_duration == 0.0
        assert metrics.usage_frequency_score == 0.0
        assert metrics.last_updated is not None


class TestPomodoroEnums:
    """Pomodoro?"""
    
    def test_pomodoro_session_status_enum(self):
        """Pomodoro?"""
        assert PomodoroSessionStatus.PENDING == "pending"
        assert PomodoroSessionStatus.ACTIVE == "active"
        assert PomodoroSessionStatus.BREAK == "break"
        assert PomodoroSessionStatus.COMPLETED == "completed"
        assert PomodoroSessionStatus.CANCELLED == "cancelled"
    
    def test_break_type_enum(self):
        """?"""
        assert BreakType.SHORT == "short"
        assert BreakType.LONG == "long"
        assert BreakType.MANDATORY == "mandatory"


if __name__ == "__main__":
    # ?
    pytest.main([__file__, "-v"])