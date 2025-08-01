"""
ADHD support repository for managing ADHD-specific settings and cognitive load reduction
Handles Pomodoro settings, break reminders, and accessibility preferences
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from google.cloud import firestore

from .base_repository import BaseRepository
from ..utils.exceptions import ValidationError, NotFoundError


class ADHDSupportSettings:
    """ADHD support settings data class"""
    
    def __init__(self, uid: str, **kwargs):
        self.uid = uid
        self.pomodoro_enabled = kwargs.get("pomodoro_enabled", True)
        self.pomodoro_work_duration = kwargs.get("pomodoro_work_duration", 25)  # minutes
        self.pomodoro_break_duration = kwargs.get("pomodoro_break_duration", 5)  # minutes
        self.pomodoro_long_break_duration = kwargs.get("pomodoro_long_break_duration", 15)  # minutes
        self.pomodoro_sessions_until_long_break = kwargs.get("pomodoro_sessions_until_long_break", 4)
        
        self.break_reminders = kwargs.get("break_reminders", True)
        self.break_reminder_interval = kwargs.get("break_reminder_interval", 30)  # minutes
        
        self.daily_task_limit = kwargs.get("daily_task_limit", 16)
        self.task_buffer_extensions = kwargs.get("task_buffer_extensions", 2)  # per day
        self.buffer_extensions_used = kwargs.get("buffer_extensions_used", 0)
        
        # Cognitive load reduction settings
        self.cognitive_load_settings = kwargs.get("cognitive_load_settings", {
            "reduce_animations": False,
            "simplified_ui": False,
            "high_contrast": False,
            "larger_fonts": False,
            "reduced_distractions": True
        })
        
        # Time perception aids
        self.time_perception_aids = kwargs.get("time_perception_aids", {
            "visual_timers": True,
            "progress_indicators": True,
            "time_estimates": True,
            "deadline_warnings": True
        })
        
        # Notification preferences
        self.notification_schedule = kwargs.get("notification_schedule", {
            "enabled": True,
            "quiet_hours_start": "22:00",
            "quiet_hours_end": "08:00",
            "weekend_reduced": True
        })
        
        self.updated_at = kwargs.get("updated_at", datetime.utcnow())


class ADHDSupportRepository(BaseRepository[ADHDSupportSettings]):
    """Repository for ADHD support settings"""
    
    def __init__(self, db_client: firestore.Client):
        super().__init__(db_client, "adhd_support_settings")
    
    def _to_entity(self, doc_data: Dict[str, Any], doc_id: str = None) -> ADHDSupportSettings:
        """Convert Firestore document to ADHDSupportSettings entity"""
        return ADHDSupportSettings(
            uid=doc_data["uid"],
            pomodoro_enabled=doc_data.get("pomodoro_enabled", True),
            pomodoro_work_duration=doc_data.get("pomodoro_work_duration", 25),
            pomodoro_break_duration=doc_data.get("pomodoro_break_duration", 5),
            pomodoro_long_break_duration=doc_data.get("pomodoro_long_break_duration", 15),
            pomodoro_sessions_until_long_break=doc_data.get("pomodoro_sessions_until_long_break", 4),
            break_reminders=doc_data.get("break_reminders", True),
            break_reminder_interval=doc_data.get("break_reminder_interval", 30),
            daily_task_limit=doc_data.get("daily_task_limit", 16),
            task_buffer_extensions=doc_data.get("task_buffer_extensions", 2),
            buffer_extensions_used=doc_data.get("buffer_extensions_used", 0),
            cognitive_load_settings=doc_data.get("cognitive_load_settings", {}),
            time_perception_aids=doc_data.get("time_perception_aids", {}),
            notification_schedule=doc_data.get("notification_schedule", {}),
            updated_at=doc_data.get("updated_at", datetime.utcnow())
        )
    
    def _to_document(self, entity: ADHDSupportSettings) -> Dict[str, Any]:
        """Convert ADHDSupportSettings entity to Firestore document"""
        return {
            "uid": entity.uid,
            "pomodoro_enabled": entity.pomodoro_enabled,
            "pomodoro_work_duration": entity.pomodoro_work_duration,
            "pomodoro_break_duration": entity.pomodoro_break_duration,
            "pomodoro_long_break_duration": entity.pomodoro_long_break_duration,
            "pomodoro_sessions_until_long_break": entity.pomodoro_sessions_until_long_break,
            "break_reminders": entity.break_reminders,
            "break_reminder_interval": entity.break_reminder_interval,
            "daily_task_limit": entity.daily_task_limit,
            "task_buffer_extensions": entity.task_buffer_extensions,
            "buffer_extensions_used": entity.buffer_extensions_used,
            "cognitive_load_settings": entity.cognitive_load_settings,
            "time_perception_aids": entity.time_perception_aids,
            "notification_schedule": entity.notification_schedule,
            "updated_at": entity.updated_at
        }
    
    async def get_user_settings(self, uid: str) -> Optional[ADHDSupportSettings]:
        """Get ADHD support settings for user"""
        try:
            doc_ref = self.collection_ref.document(uid)
            doc = doc_ref.get()
            
            if not doc.exists:
                return None
            
            return self._to_entity(doc.to_dict(), doc.id)
            
        except Exception as e:
            self.logger.error(f"Failed to get ADHD settings for user {uid}: {str(e)}")
            raise
    
    async def create_default_settings(self, uid: str) -> str:
        """Create default ADHD support settings for new user"""
        try:
            # Check if settings already exist
            existing = await self.get_user_settings(uid)
            if existing:
                raise ValidationError("ADHD settings already exist for user")
            
            settings = ADHDSupportSettings(uid=uid)
            
            # Use uid as document ID for easy lookup
            doc_data = self._to_document(settings)
            
            doc_ref = self.collection_ref.document(uid)
            doc_ref.set(doc_data)
            
            self.logger.info(f"Created default ADHD settings for user {uid}")
            return uid
            
        except Exception as e:
            self.logger.error(f"Failed to create default ADHD settings for user {uid}: {str(e)}")
            raise
    
    async def update_pomodoro_settings(self, uid: str, pomodoro_settings: Dict[str, Any]) -> bool:
        """Update Pomodoro-specific settings"""
        try:
            # Validate settings
            valid_keys = {
                "pomodoro_enabled", "pomodoro_work_duration", "pomodoro_break_duration",
                "pomodoro_long_break_duration", "pomodoro_sessions_until_long_break"
            }
            
            updates = {}
            for key, value in pomodoro_settings.items():
                if key not in valid_keys:
                    raise ValidationError(f"Invalid Pomodoro setting: {key}")
                
                # Validate ranges
                if key == "pomodoro_work_duration" and not (5 <= value <= 60):
                    raise ValidationError("Work duration must be between 5-60 minutes")
                elif key == "pomodoro_break_duration" and not (1 <= value <= 30):
                    raise ValidationError("Break duration must be between 1-30 minutes")
                elif key == "pomodoro_long_break_duration" and not (5 <= value <= 60):
                    raise ValidationError("Long break duration must be between 5-60 minutes")
                elif key == "pomodoro_sessions_until_long_break" and not (2 <= value <= 8):
                    raise ValidationError("Sessions until long break must be between 2-8")
                
                updates[key] = value
            
            updates["updated_at"] = datetime.utcnow()
            
            result = await self.update(uid, updates)
            
            if result:
                self.logger.info(f"Updated Pomodoro settings for user {uid}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to update Pomodoro settings for user {uid}: {str(e)}")
            raise
    
    async def update_cognitive_load_settings(self, uid: str, cognitive_settings: Dict[str, Any]) -> bool:
        """Update cognitive load reduction settings"""
        try:
            valid_keys = {
                "reduce_animations", "simplified_ui", "high_contrast", 
                "larger_fonts", "reduced_distractions"
            }
            
            # Get current settings
            current_settings = await self.get_user_settings(uid)
            if not current_settings:
                raise NotFoundError(f"ADHD settings not found for user {uid}")
            
            # Update cognitive load settings
            new_cognitive_settings = current_settings.cognitive_load_settings.copy()
            
            for key, value in cognitive_settings.items():
                if key not in valid_keys:
                    raise ValidationError(f"Invalid cognitive load setting: {key}")
                
                if not isinstance(value, bool):
                    raise ValidationError(f"Cognitive load setting {key} must be boolean")
                
                new_cognitive_settings[key] = value
            
            updates = {
                "cognitive_load_settings": new_cognitive_settings,
                "updated_at": datetime.utcnow()
            }
            
            result = await self.update(uid, updates)
            
            if result:
                self.logger.info(f"Updated cognitive load settings for user {uid}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to update cognitive load settings for user {uid}: {str(e)}")
            raise
    
    async def update_daily_task_limit(self, uid: str, new_limit: int) -> bool:
        """Update daily task limit with validation"""
        try:
            if not (1 <= new_limit <= 20):
                raise ValidationError("Daily task limit must be between 1-20")
            
            updates = {
                "daily_task_limit": new_limit,
                "updated_at": datetime.utcnow()
            }
            
            result = await self.update(uid, updates)
            
            if result:
                self.logger.info(f"Updated daily task limit for user {uid} to {new_limit}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to update daily task limit for user {uid}: {str(e)}")
            raise
    
    async def use_buffer_extension(self, uid: str) -> Dict[str, Any]:
        """Use one buffer extension for the day"""
        try:
            settings = await self.get_user_settings(uid)
            if not settings:
                raise NotFoundError(f"ADHD settings not found for user {uid}")
            
            # Check if extensions are available
            if settings.buffer_extensions_used >= settings.task_buffer_extensions:
                return {
                    "success": False,
                    "reason": "no_extensions_remaining",
                    "extensions_used": settings.buffer_extensions_used,
                    "extensions_available": settings.task_buffer_extensions
                }
            
            # Use extension
            new_used_count = settings.buffer_extensions_used + 1
            
            updates = {
                "buffer_extensions_used": new_used_count,
                "updated_at": datetime.utcnow()
            }
            
            await self.update(uid, updates)
            
            # Log the extension usage
            await self._log_buffer_extension_usage(uid)
            
            result = {
                "success": True,
                "extensions_used": new_used_count,
                "extensions_remaining": settings.task_buffer_extensions - new_used_count,
                "new_task_limit": settings.daily_task_limit + 1
            }
            
            self.logger.info(f"Used buffer extension for user {uid}: {new_used_count}/{settings.task_buffer_extensions}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to use buffer extension for user {uid}: {str(e)}")
            raise
    
    async def _log_buffer_extension_usage(self, uid: str) -> None:
        """Log buffer extension usage"""
        try:
            usage_log = {
                "uid": uid,
                "used_at": datetime.utcnow(),
                "date": datetime.utcnow().date()
            }
            
            # Store in buffer_extension_logs collection
            logs_collection = self.db.collection("buffer_extension_logs")
            logs_collection.add(usage_log)
            
        except Exception as e:
            self.logger.error(f"Failed to log buffer extension usage for user {uid}: {str(e)}")
            # Don't raise - this is supplementary logging
    
    async def reset_daily_counters(self, uid: str) -> bool:
        """Reset daily counters (called by daily cron job)"""
        try:
            updates = {
                "buffer_extensions_used": 0,
                "updated_at": datetime.utcnow()
            }
            
            result = await self.update(uid, updates)
            
            if result:
                self.logger.info(f"Reset daily counters for user {uid}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to reset daily counters for user {uid}: {str(e)}")
            raise
    
    async def get_effective_task_limit(self, uid: str) -> int:
        """Get effective daily task limit including used extensions"""
        try:
            settings = await self.get_user_settings(uid)
            if not settings:
                return 16  # Default limit
            
            # Base limit + used extensions
            effective_limit = settings.daily_task_limit + settings.buffer_extensions_used
            
            return effective_limit
            
        except Exception as e:
            self.logger.error(f"Failed to get effective task limit for user {uid}: {str(e)}")
            return 16  # Safe default
    
    async def get_pomodoro_session_data(self, uid: str) -> Dict[str, Any]:
        """Get Pomodoro session configuration data"""
        try:
            settings = await self.get_user_settings(uid)
            if not settings:
                # Return default Pomodoro settings
                return {
                    "enabled": True,
                    "work_duration": 25,
                    "break_duration": 5,
                    "long_break_duration": 15,
                    "sessions_until_long_break": 4
                }
            
            return {
                "enabled": settings.pomodoro_enabled,
                "work_duration": settings.pomodoro_work_duration,
                "break_duration": settings.pomodoro_break_duration,
                "long_break_duration": settings.pomodoro_long_break_duration,
                "sessions_until_long_break": settings.pomodoro_sessions_until_long_break
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get Pomodoro session data for user {uid}: {str(e)}")
            raise
    
    async def update_time_perception_aids(self, uid: str, time_aids: Dict[str, Any]) -> bool:
        """Update time perception aid settings"""
        try:
            valid_keys = {
                "visual_timers", "progress_indicators", "time_estimates", "deadline_warnings"
            }
            
            # Get current settings
            current_settings = await self.get_user_settings(uid)
            if not current_settings:
                raise NotFoundError(f"ADHD settings not found for user {uid}")
            
            # Update time perception aids
            new_time_aids = current_settings.time_perception_aids.copy()
            
            for key, value in time_aids.items():
                if key not in valid_keys:
                    raise ValidationError(f"Invalid time perception aid setting: {key}")
                
                if not isinstance(value, bool):
                    raise ValidationError(f"Time perception aid setting {key} must be boolean")
                
                new_time_aids[key] = value
            
            updates = {
                "time_perception_aids": new_time_aids,
                "updated_at": datetime.utcnow()
            }
            
            result = await self.update(uid, updates)
            
            if result:
                self.logger.info(f"Updated time perception aids for user {uid}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to update time perception aids for user {uid}: {str(e)}")
            raise
    
    async def get_accessibility_preferences(self, uid: str) -> Dict[str, Any]:
        """Get accessibility preferences for UI rendering"""
        try:
            settings = await self.get_user_settings(uid)
            if not settings:
                # Return default accessibility settings
                return {
                    "reduce_animations": False,
                    "simplified_ui": False,
                    "high_contrast": False,
                    "larger_fonts": False,
                    "reduced_distractions": True,
                    "visual_timers": True,
                    "progress_indicators": True,
                    "time_estimates": True,
                    "deadline_warnings": True
                }
            
            # Combine cognitive load and time perception settings
            accessibility_prefs = settings.cognitive_load_settings.copy()
            accessibility_prefs.update(settings.time_perception_aids)
            
            return accessibility_prefs
            
        except Exception as e:
            self.logger.error(f"Failed to get accessibility preferences for user {uid}: {str(e)}")
            raise
    
    async def get_adhd_analytics(self, uid: str, days: int = 30) -> Dict[str, Any]:
        """Get ADHD support analytics"""
        try:
            settings = await self.get_user_settings(uid)
            if not settings:
                return {"error": "Settings not found"}
            
            # Get buffer extension usage history
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            logs_collection = self.db.collection("buffer_extension_logs")
            query = (logs_collection
                    .where("uid", "==", uid)
                    .where("used_at", ">=", start_date)
                    .where("used_at", "<=", end_date))
            
            extension_docs = query.get()
            
            # Calculate analytics
            total_extensions_used = len(extension_docs)
            days_with_extensions = len(set(doc.to_dict()["date"] for doc in extension_docs))
            
            analytics = {
                "current_settings": {
                    "daily_task_limit": settings.daily_task_limit,
                    "buffer_extensions_available": settings.task_buffer_extensions,
                    "pomodoro_enabled": settings.pomodoro_enabled,
                    "break_reminders": settings.break_reminders
                },
                "usage_stats": {
                    "total_extensions_used_period": total_extensions_used,
                    "days_with_extensions": days_with_extensions,
                    "average_extensions_per_day": total_extensions_used / days if days > 0 else 0,
                    "extensions_used_today": settings.buffer_extensions_used,
                    "extensions_remaining_today": settings.task_buffer_extensions - settings.buffer_extensions_used
                },
                "accessibility_settings": settings.cognitive_load_settings,
                "time_perception_aids": settings.time_perception_aids
            }
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Failed to get ADHD analytics for user {uid}: {str(e)}")
            raise