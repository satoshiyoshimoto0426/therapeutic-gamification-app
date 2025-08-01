"""
Mood tracking repository for daily mood logs and XP coefficient calculation
Handles mood data storage, retrieval, and analytics
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from google.cloud import firestore

from .base_repository import BaseRepository
from ..interfaces.core_types import MoodLog
from ..utils.exceptions import ValidationError, NotFoundError


class MoodRepository(BaseRepository[MoodLog]):
    """Repository for mood tracking data"""
    
    def __init__(self, db_client: firestore.Client):
        super().__init__(db_client, "mood_logs")
    
    def _to_entity(self, doc_data: Dict[str, Any], doc_id: str = None) -> MoodLog:
        """Convert Firestore document to MoodLog entity"""
        return MoodLog(
            uid=doc_data["uid"],
            log_date=doc_data["log_date"],
            mood_score=doc_data["mood_score"],
            notes=doc_data.get("notes", ""),
            context_tags=doc_data.get("context_tags", []),
            calculated_coefficient=doc_data["calculated_coefficient"]
        )
    
    def _to_document(self, entity: MoodLog) -> Dict[str, Any]:
        """Convert MoodLog entity to Firestore document"""
        return {
            "uid": entity.uid,
            "log_date": entity.log_date,
            "mood_score": entity.mood_score,
            "notes": entity.notes,
            "context_tags": entity.context_tags,
            "calculated_coefficient": entity.calculated_coefficient
        }
    
    async def get_mood_for_date(self, uid: str, date: datetime) -> Optional[MoodLog]:
        """Get mood log for specific date"""
        try:
            # Query by uid and date (assuming date is stored as date, not datetime)
            date_only = date.date() if isinstance(date, datetime) else date
            
            query = self.collection_ref.where("uid", "==", uid).where("log_date", "==", date_only)
            docs = query.get()
            
            if not docs:
                return None
            
            # Should only be one document per user per date
            doc = docs[0]
            return self._to_entity(doc.to_dict(), doc.id)
            
        except Exception as e:
            self.logger.error(f"Failed to get mood for date {date} for user {uid}: {str(e)}")
            raise
    
    async def get_mood_history(self, uid: str, days: int = 30) -> List[MoodLog]:
        """Get mood history for specified number of days"""
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            query = (self.collection_ref
                    .where("uid", "==", uid)
                    .where("log_date", ">=", start_date)
                    .where("log_date", "<=", end_date)
                    .order_by("log_date", direction=firestore.Query.DESCENDING))
            
            docs = query.get()
            return [self._to_entity(doc.to_dict(), doc.id) for doc in docs]
            
        except Exception as e:
            self.logger.error(f"Failed to get mood history for user {uid}: {str(e)}")
            raise
    
    async def get_current_mood_coefficient(self, uid: str) -> float:
        """Get current mood coefficient for XP calculation"""
        try:
            # Get today's mood
            today_mood = await self.get_mood_for_date(uid, datetime.now())
            
            if today_mood:
                return today_mood.calculated_coefficient
            
            # If no mood today, get most recent mood within last 3 days
            recent_moods = await self.get_mood_history(uid, days=3)
            
            if recent_moods:
                return recent_moods[0].calculated_coefficient
            
            # Default coefficient if no recent mood data
            return 1.0
            
        except Exception as e:
            self.logger.error(f"Failed to get current mood coefficient for user {uid}: {str(e)}")
            return 1.0  # Safe default
    
    async def calculate_mood_coefficient(self, mood_score: int) -> float:
        """Calculate mood coefficient from mood score (1-5 scale)"""
        if not 1 <= mood_score <= 5:
            raise ValidationError("Mood score must be between 1 and 5")
        
        # Formula: 0.6 + (mood_score * 0.15)
        # Results: 1->0.75, 2->0.9, 3->1.05, 4->1.2, 5->1.35
        # Clamped to 0.8-1.2 range for balance
        coefficient = 0.6 + (mood_score * 0.15)
        return max(0.8, min(1.2, coefficient))
    
    async def create_mood_log(self, uid: str, mood_score: int, notes: str = "", 
                            context_tags: List[str] = None) -> str:
        """Create new mood log with calculated coefficient"""
        try:
            if context_tags is None:
                context_tags = []
            
            # Check if mood already exists for today
            today = datetime.now().date()
            existing_mood = await self.get_mood_for_date(uid, today)
            
            if existing_mood:
                raise ValidationError("Mood log already exists for today")
            
            # Calculate coefficient
            coefficient = await self.calculate_mood_coefficient(mood_score)
            
            mood_log = MoodLog(
                uid=uid,
                log_date=today,
                mood_score=mood_score,
                notes=notes,
                context_tags=context_tags,
                calculated_coefficient=coefficient
            )
            
            return await self.create(mood_log)
            
        except Exception as e:
            self.logger.error(f"Failed to create mood log for user {uid}: {str(e)}")
            raise
    
    async def update_mood_log(self, uid: str, date: datetime, mood_score: int, 
                            notes: str = None, context_tags: List[str] = None) -> bool:
        """Update existing mood log"""
        try:
            existing_mood = await self.get_mood_for_date(uid, date)
            
            if not existing_mood:
                raise NotFoundError(f"No mood log found for date {date}")
            
            updates = {}
            
            if mood_score is not None:
                if not 1 <= mood_score <= 5:
                    raise ValidationError("Mood score must be between 1 and 5")
                updates["mood_score"] = mood_score
                updates["calculated_coefficient"] = await self.calculate_mood_coefficient(mood_score)
            
            if notes is not None:
                updates["notes"] = notes
            
            if context_tags is not None:
                updates["context_tags"] = context_tags
            
            # Find document ID for update
            date_only = date.date() if isinstance(date, datetime) else date
            query = self.collection_ref.where("uid", "==", uid).where("log_date", "==", date_only)
            docs = query.get()
            
            if docs:
                doc_id = docs[0].id
                return await self.update(doc_id, updates)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to update mood log for user {uid}: {str(e)}")
            raise
    
    async def get_mood_analytics(self, uid: str, days: int = 30) -> Dict[str, Any]:
        """Get mood analytics for specified period"""
        try:
            mood_history = await self.get_mood_history(uid, days)
            
            if not mood_history:
                return {
                    "average_mood": 0,
                    "mood_trend": "no_data",
                    "total_logs": 0,
                    "streak_days": 0,
                    "coefficient_average": 1.0
                }
            
            # Calculate analytics
            mood_scores = [mood.mood_score for mood in mood_history]
            coefficients = [mood.calculated_coefficient for mood in mood_history]
            
            average_mood = sum(mood_scores) / len(mood_scores)
            average_coefficient = sum(coefficients) / len(coefficients)
            
            # Calculate trend (simple: compare first half vs second half)
            if len(mood_scores) >= 4:
                mid_point = len(mood_scores) // 2
                first_half_avg = sum(mood_scores[:mid_point]) / mid_point
                second_half_avg = sum(mood_scores[mid_point:]) / (len(mood_scores) - mid_point)
                
                if second_half_avg > first_half_avg + 0.3:
                    trend = "improving"
                elif second_half_avg < first_half_avg - 0.3:
                    trend = "declining"
                else:
                    trend = "stable"
            else:
                trend = "insufficient_data"
            
            # Calculate streak (consecutive days with logs)
            streak_days = 0
            current_date = datetime.now().date()
            
            for i in range(days):
                check_date = current_date - timedelta(days=i)
                has_log = any(mood.log_date == check_date for mood in mood_history)
                
                if has_log:
                    streak_days += 1
                else:
                    break
            
            return {
                "average_mood": round(average_mood, 2),
                "mood_trend": trend,
                "total_logs": len(mood_history),
                "streak_days": streak_days,
                "coefficient_average": round(average_coefficient, 3),
                "mood_distribution": {
                    str(i): mood_scores.count(i) for i in range(1, 6)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get mood analytics for user {uid}: {str(e)}")
            raise
    
    async def get_weekly_mood_summary(self, uid: str) -> Dict[str, Any]:
        """Get weekly mood summary for dashboard"""
        try:
            # Get last 7 days
            mood_history = await self.get_mood_history(uid, days=7)
            
            # Group by day of week
            weekly_data = {}
            today = datetime.now().date()
            
            for i in range(7):
                date = today - timedelta(days=i)
                day_name = date.strftime("%A")
                
                mood_for_day = next((mood for mood in mood_history if mood.log_date == date), None)
                
                weekly_data[day_name] = {
                    "date": date.isoformat(),
                    "mood_score": mood_for_day.mood_score if mood_for_day else None,
                    "coefficient": mood_for_day.calculated_coefficient if mood_for_day else None,
                    "has_log": mood_for_day is not None
                }
            
            # Calculate weekly stats
            logged_days = [data for data in weekly_data.values() if data["has_log"]]
            
            if logged_days:
                avg_mood = sum(data["mood_score"] for data in logged_days) / len(logged_days)
                avg_coefficient = sum(data["coefficient"] for data in logged_days) / len(logged_days)
            else:
                avg_mood = 0
                avg_coefficient = 1.0
            
            return {
                "weekly_data": weekly_data,
                "days_logged": len(logged_days),
                "average_mood": round(avg_mood, 2),
                "average_coefficient": round(avg_coefficient, 3),
                "completion_rate": len(logged_days) / 7 * 100
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get weekly mood summary for user {uid}: {str(e)}")
            raise
    
    async def delete_mood_log(self, uid: str, date: datetime) -> bool:
        """Delete mood log for specific date"""
        try:
            date_only = date.date() if isinstance(date, datetime) else date
            query = self.collection_ref.where("uid", "==", uid).where("log_date", "==", date_only)
            docs = query.get()
            
            if docs:
                doc_id = docs[0].id
                return await self.delete(doc_id)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to delete mood log for user {uid}: {str(e)}")
            raise