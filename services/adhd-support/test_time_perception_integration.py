#!/usr/bin/env python3
"""
ADHD支援 - ?
タスク10.2: ?

?3.5: 15?
?9.5: デフォルト1?2?
"""

import pytest
import asyncio
import sys
import os
from datetime import datetime, timedelta, date
from unittest.mock import AsyncMock, patch

# Add the parent directory to the path to import the main module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import TimePerceptionSupport, DailyBufferManager, LINENotificationService

class TestTimePerceptionSupport:
    """?"""
    
    def setup_method(self):
        """?"""
        self.user_id = f"test_user_{id(self)}"  # ?IDを
        self.time_support = TimePerceptionSupport(self.user_id)
    
    @pytest.mark.asyncio
    async def test_start_time_perception_reminders(self):
        """15?"""
        task_name = "プレビュー"
        config = {"enabled": True, "interval": 15}
        
        result = await self.time_support.start_time_perception_reminders(task_name, config)
        
        assert result["user_id"] == self.user_id
        assert result["task_name"] == task_name
        assert result["is_active"] == True
        assert result["reminder_count"] == 0
        assert "reminder_id" in result
        assert "start_time" in result
        assert "next_reminder" in result
    
    @pytest.mark.asyncio
    async def test_trigger_reminder_first_time(self):
        """?"""
        task_name = "?"
        
        # リスト
        reminder_data = await self.time_support.start_time_perception_reminders(task_name)
        reminder_id = reminder_data["reminder_id"]
        
        # 15?
        self.time_support.active_reminders[reminder_id]["next_reminder"] = datetime.utcnow() - timedelta(minutes=1)
        
        # リスト
        result = await self.time_support.trigger_reminder(reminder_id)
        
        assert result["reminder_triggered"] == True
        assert result["task_name"] == task_name
        assert result["reminder_count"] == 1
        assert result["elapsed_minutes"] >= 0
        assert "? 15?" in result["message"]
    
    @pytest.mark.asyncio
    async def test_trigger_reminder_multiple_times(self):
        """?"""
        task_name = "?"
        
        # リスト
        reminder_data = await self.time_support.start_time_perception_reminders(task_name)
        reminder_id = reminder_data["reminder_id"]
        
        # ?
        for i in range(1, 5):  # 1?4?
            # ?
            elapsed_time = i * 15
            self.time_support.active_reminders[reminder_id]["start_time"] = datetime.utcnow() - timedelta(minutes=elapsed_time)
            self.time_support.active_reminders[reminder_id]["next_reminder"] = datetime.utcnow() - timedelta(minutes=1)
            
            result = await self.time_support.trigger_reminder(reminder_id)
            
            assert result["reminder_triggered"] == True
            assert result["reminder_count"] == i
            assert result["elapsed_minutes"] == elapsed_time
            
            # メイン
            if elapsed_time <= 15:
                assert "15?" in result["message"]
            elif elapsed_time <= 30:
                assert f"{elapsed_time}?" in result["message"]
                assert "?" in result["message"]
            elif elapsed_time <= 60:
                assert "?" in result["message"]
    
    @pytest.mark.asyncio
    async def test_pause_and_resume_reminders(self):
        """リスト"""
        task_name = "?"
        
        # リスト
        reminder_data = await self.time_support.start_time_perception_reminders(task_name)
        reminder_id = reminder_data["reminder_id"]
        
        # 一般
        pause_result = await self.time_support.pause_reminders(reminder_id)
        assert pause_result["paused"] == True
        assert pause_result["reminder_id"] == reminder_id
        
        # 一般
        assert self.time_support.active_reminders[reminder_id]["is_active"] == False
        
        # ?
        resume_result = await self.time_support.resume_reminders(reminder_id)
        assert resume_result["resumed"] == True
        assert resume_result["reminder_id"] == reminder_id
        
        # ?
        assert self.time_support.active_reminders[reminder_id]["is_active"] == True
    
    @pytest.mark.asyncio
    async def test_stop_reminders(self):
        """リスト"""
        task_name = "メイン"
        
        # リスト
        reminder_data = await self.time_support.start_time_perception_reminders(task_name)
        reminder_id = reminder_data["reminder_id"]
        
        # ?
        stop_result = await self.time_support.stop_reminders(reminder_id)
        
        assert stop_result["stopped"] == True
        assert stop_result["reminder_id"] == reminder_id
        assert stop_result["total_time_minutes"] >= 0
        assert stop_result["total_reminders"] == 0
        
        # ?active_remindersか
        assert reminder_id not in self.time_support.active_reminders

class TestDailyBufferManager:
    """デフォルト"""
    
    def setup_method(self):
        """?"""
        self.user_id = f"test_user_{id(self)}"  # ?IDを
        self.buffer_manager = DailyBufferManager(self.user_id)
    
    @pytest.mark.asyncio
    async def test_get_daily_buffer_status_initial(self):
        """?"""
        status = await self.buffer_manager.get_daily_buffer_status()
        
        assert status["user_id"] == self.user_id
        assert status["extensions_used"] == 0
        assert status["extensions_available"] == 2  # 1?2?
        assert status["reset_date"] == date.today()
        assert "extension_history" in status
    
    @pytest.mark.asyncio
    async def test_request_extension_success(self):
        """?"""
        task_id = "task_123"
        hours = 3
        reason = "?"
        
        result = await self.buffer_manager.request_extension(task_id, hours, reason)
        
        assert result["granted"] == True
        assert result["task_id"] == task_id
        assert result["extension_hours"] == hours
        assert result["extensions_remaining"] == 1  # 2?1?
        assert "new_due_date" in result
        assert "?3?" in result["message"]
    
    @pytest.mark.asyncio
    async def test_request_extension_limit_exceeded(self):
        """?"""
        task_id_1 = "task_001"
        task_id_2 = "task_002"
        task_id_3 = "task_003"
        
        # 1?
        result1 = await self.buffer_manager.request_extension(task_id_1)
        assert result1["granted"] == True
        assert result1["extensions_remaining"] == 1
        
        # 2?
        result2 = await self.buffer_manager.request_extension(task_id_2)
        assert result2["granted"] == True
        assert result2["extensions_remaining"] == 0
        
        # 3? - ?
        result3 = await self.buffer_manager.request_extension(task_id_3)
        assert result3["granted"] == False
        assert result3["reason"] == "daily_limit_exceeded"
        assert result3["extensions_remaining"] == 0
        assert "?" in result3["message"]
    
    @pytest.mark.asyncio
    async def test_get_extension_history(self):
        """?"""
        # ?
        await self.buffer_manager.request_extension("task_A", 2, "理A")
        await self.buffer_manager.request_extension("task_B", 1, "理B")
        
        # ?
        history = await self.buffer_manager.get_extension_history(days=7)
        
        assert len(history) == 2
        assert history[0]["task_id"] in ["task_A", "task_B"]
        assert history[1]["task_id"] in ["task_A", "task_B"]
        
        # ?
        assert history[0]["granted_at"] >= history[1]["granted_at"]
    
    @pytest.mark.asyncio
    async def test_check_extension_eligibility(self):
        """?"""
        task_id = "task_eligibility_test"
        
        # ?
        eligibility1 = await self.buffer_manager.check_extension_eligibility(task_id)
        assert eligibility1["eligible"] == True
        assert eligibility1["extensions_remaining"] == 2
        assert eligibility1["task_extended_today"] == False
        
        # 1?
        await self.buffer_manager.request_extension(task_id)
        eligibility2 = await self.buffer_manager.check_extension_eligibility(task_id)
        assert eligibility2["eligible"] == True
        assert eligibility2["extensions_remaining"] == 1
        assert eligibility2["task_extended_today"] == True
        assert eligibility2["task_extension_count"] == 1
    
    @pytest.mark.asyncio
    async def test_reset_daily_buffer(self):
        """デフォルト"""
        # ?
        await self.buffer_manager.request_extension("task_before_reset")
        
        # リスト
        status_before = await self.buffer_manager.get_daily_buffer_status()
        assert status_before["extensions_used"] == 1
        
        # リスト
        reset_result = await self.buffer_manager.reset_daily_buffer()
        
        assert reset_result["extensions_used"] == 0
        assert reset_result["extensions_available"] == 2
        assert reset_result["reset_date"] == date.today()
        
        # リスト
        status_after = await self.buffer_manager.get_daily_buffer_status()
        assert status_after["extensions_used"] == 0
        assert status_after["extensions_available"] == 2

class TestLINENotificationService:
    """LINE?"""
    
    def setup_method(self):
        """?"""
        self.notification_service = LINENotificationService()
        self.user_id = "test_user_789"
    
    @pytest.mark.asyncio
    async def test_send_15_minute_reminder_basic(self):
        """基本15?"""
        task_name = "デフォルト"
        elapsed_minutes = 15
        reminder_count = 1
        
        # モデル
        with patch.object(self.notification_service, 'send_message', new_callable=AsyncMock) as mock_send:
            await self.notification_service.send_15_minute_reminder(
                self.user_id, task_name, elapsed_minutes, reminder_count
            )
            
            mock_send.assert_called_once()
            args, kwargs = mock_send.call_args
            assert args[0] == self.user_id
            assert "15?" in args[1]
            assert task_name in args[1]
    
    @pytest.mark.asyncio
    async def test_send_15_minute_reminder_long_duration(self):
        """?"""
        task_name = "システム"
        elapsed_minutes = 75  # 1?15?
        reminder_count = 5
        
        with patch.object(self.notification_service, 'send_message', new_callable=AsyncMock) as mock_send:
            await self.notification_service.send_15_minute_reminder(
                self.user_id, task_name, elapsed_minutes, reminder_count
            )
            
            mock_send.assert_called_once()
            args, kwargs = mock_send.call_args
            assert "1?15?" in args[1]
            assert "?" in args[1]
    
    @pytest.mark.asyncio
    async def test_send_daily_buffer_notification_extension_granted(self):
        """?"""
        notification_data = {
            "task_id": "?",
            "hours": 3,
            "remaining": 1
        }
        
        with patch.object(self.notification_service, 'send_message', new_callable=AsyncMock) as mock_send:
            await self.notification_service.send_daily_buffer_notification(
                self.user_id, "extension_granted", notification_data
            )
            
            mock_send.assert_called_once()
            args, kwargs = mock_send.call_args
            assert "?" in args[1]
            assert "?" in args[1]
            assert "3?" in args[1]
            assert "?: 1?" in args[1]
    
    @pytest.mark.asyncio
    async def test_send_daily_buffer_notification_extension_denied(self):
        """?"""
        notification_data = {"reason": "daily_limit_exceeded"}
        
        with patch.object(self.notification_service, 'send_message', new_callable=AsyncMock) as mock_send:
            await self.notification_service.send_daily_buffer_notification(
                self.user_id, "extension_denied", notification_data
            )
            
            mock_send.assert_called_once()
            args, kwargs = mock_send.call_args
            assert "?" in args[1]
            assert "?" in args[1]

class TestIntegration:
    """?"""
    
    def setup_method(self):
        """?"""
        self.user_id = f"integration_test_user_{id(self)}"  # ?IDを
        self.time_support = TimePerceptionSupport(self.user_id)
        self.buffer_manager = DailyBufferManager(self.user_id)
    
    @pytest.mark.asyncio
    async def test_full_time_perception_workflow(self):
        """?"""
        task_name = "プレビュー"
        
        # 1. リスト
        reminder_data = await self.time_support.start_time_perception_reminders(task_name)
        reminder_id = reminder_data["reminder_id"]
        
        # 2. ?
        for i in range(1, 4):
            # ?
            elapsed_minutes = i * 15
            self.time_support.active_reminders[reminder_id]["start_time"] = datetime.utcnow() - timedelta(minutes=elapsed_minutes)
            self.time_support.active_reminders[reminder_id]["next_reminder"] = datetime.utcnow() - timedelta(minutes=1)
            
            result = await self.time_support.trigger_reminder(reminder_id)
            assert result["reminder_triggered"] == True
            assert result["elapsed_minutes"] == elapsed_minutes
        
        # 3. 一般
        pause_result = await self.time_support.pause_reminders(reminder_id)
        assert pause_result["paused"] == True
        
        # 4. ?
        resume_result = await self.time_support.resume_reminders(reminder_id)
        assert resume_result["resumed"] == True
        
        # 5. ?
        stop_result = await self.time_support.stop_reminders(reminder_id)
        assert stop_result["stopped"] == True
    
    @pytest.mark.asyncio
    async def test_full_daily_buffer_workflow(self):
        """デフォルト"""
        # 1. ?
        initial_status = await self.buffer_manager.get_daily_buffer_status()
        assert initial_status["extensions_available"] == 2
        
        # 2. 1?
        result1 = await self.buffer_manager.request_extension("task_1", 2, "?")
        assert result1["granted"] == True
        assert result1["extensions_remaining"] == 1
        
        # 3. 2?
        result2 = await self.buffer_manager.request_extension("task_2", 1, "?")
        assert result2["granted"] == True
        assert result2["extensions_remaining"] == 0
        
        # 4. 3?
        result3 = await self.buffer_manager.request_extension("task_3", 1, "さ")
        assert result3["granted"] == False
        assert result3["reason"] == "daily_limit_exceeded"
        
        # 5. ?
        history = await self.buffer_manager.get_extension_history()
        assert len(history) == 2
        
        # 6. リスト
        reset_result = await self.buffer_manager.reset_daily_buffer()
        assert reset_result["extensions_available"] == 2
        
        # 7. リスト
        result4 = await self.buffer_manager.request_extension("task_4", 1, "リスト")
        assert result4["granted"] == True

def run_tests():
    """?"""
    print("? ADHD支援 - ?...")
    
    # pytest実装
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short"
    ])
    
    if exit_code == 0:
        print("? す")
        print("\n? 実装:")
        print("  - 15?")
        print("  - リスト")
        print("  - デフォルト1?2?")
        print("  - ?")
        print("  - ?")
        print("  - LINE?")
        print("  - ?")
    else:
        print("? ?")
    
    return exit_code == 0

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)