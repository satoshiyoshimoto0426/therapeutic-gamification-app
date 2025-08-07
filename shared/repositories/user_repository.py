"""
User profile repository implementation
Handles user data, game states, and crystal progression
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from .base_repository import CachedRepository
from ..interfaces.core_types import User
from ..config.firestore_collections import CrystalAttribute

@dataclass
class UserProfile:
    uid: str
    email: str
    display_name: str
    created_at: datetime
    last_active: datetime
    player_level: int
    yu_level: int
    total_xp: int
    crystal_gauges: Dict[str, int]
    adhd_profile: Dict[str, Any] = None
    therapeutic_goals: List[str] = None
    guardian_links: List[str] = None
    care_points: int = 0
    subscription_status: str = "free"
    preferences: Dict[str, Any] = None

class UserRepository(CachedRepository[UserProfile]):
    """Repository for user profiles and game states"""
    
    def __init__(self, db_client, cache_ttl_seconds: int = 600):  # 10 minutes cache
        super().__init__(db_client, "user_profiles", cache_ttl_seconds)
    
    def _to_entity(self, doc_data: Dict[str, Any], doc_id: str = None) -> UserProfile:
        """Convert Firestore document to UserProfile entity"""
        return UserProfile(
            uid=doc_data.get("uid", doc_id),
            email=doc_data["email"],
            display_name=doc_data["display_name"],
            created_at=doc_data["created_at"],
            last_active=doc_data["last_active"],
            player_level=doc_data["player_level"],
            yu_level=doc_data["yu_level"],
            total_xp=doc_data["total_xp"],
            crystal_gauges=doc_data["crystal_gauges"],
            adhd_profile=doc_data.get("adhd_profile", {}),
            therapeutic_goals=doc_data.get("therapeutic_goals", []),
            guardian_links=doc_data.get("guardian_links", []),
            care_points=doc_data.get("care_points", 0),
            subscription_status=doc_data.get("subscription_status", "free"),
            preferences=doc_data.get("preferences", {})
        )
    
    def _to_document(self, entity: UserProfile) -> Dict[str, Any]:
        """Convert UserProfile entity to Firestore document"""
        return {
            "uid": entity.uid,
            "email": entity.email,
            "display_name": entity.display_name,
            "created_at": entity.created_at,
            "last_active": entity.last_active,
            "player_level": entity.player_level,
            "yu_level": entity.yu_level,
            "total_xp": entity.total_xp,
            "crystal_gauges": entity.crystal_gauges,
            "adhd_profile": entity.adhd_profile or {},
            "therapeutic_goals": entity.therapeutic_goals or [],
            "guardian_links": entity.guardian_links or [],
            "care_points": entity.care_points,
            "subscription_status": entity.subscription_status,
            "preferences": entity.preferences or {}
        }
    
    async def get_by_email(self, email: str) -> Optional[UserProfile]:
        """Get user by email address"""
        users = await self.find_by_field("email", email, limit=1)
        return users[0] if users else None
    
    async def update_last_active(self, uid: str) -> bool:
        """Update user's last active timestamp"""
        return await self.update(uid, {"last_active": datetime.utcnow()})
    
    async def add_xp(self, uid: str, xp_amount: int, source: str = "task") -> Dict[str, Any]:
        """Add XP to user and handle level progression"""
        user = await self.get_by_id(uid)
        if not user:
            raise ValueError(f"User {uid} not found")
        
        # Calculate new XP and level
        new_total_xp = user.total_xp + xp_amount
        new_player_level = self._calculate_level(new_total_xp)
        
        # Check for level up
        level_up = new_player_level > user.player_level
        
        # Check for resonance event
        resonance_event = abs(user.yu_level - new_player_level) >= 5
        
        updates = {
            "total_xp": new_total_xp,
            "player_level": new_player_level,
            "last_active": datetime.utcnow()
        }
        
        await self.update(uid, updates)
        
        return {
            "xp_added": xp_amount,
            "new_total_xp": new_total_xp,
            "new_level": new_player_level,
            "level_up": level_up,
            "resonance_event": resonance_event,
            "source": source
        }
    
    async def update_crystal_gauge(self, uid: str, attribute: str, points: int) -> Dict[str, Any]:
        """Update crystal gauge for specific attribute"""
        user = await self.get_by_id(uid)
        if not user:
            raise ValueError(f"User {uid} not found")
        
        if attribute not in [attr.value for attr in CrystalAttribute]:
            raise ValueError(f"Invalid crystal attribute: {attribute}")
        
        current_gauges = user.crystal_gauges.copy()
        current_value = current_gauges.get(attribute, 0)
        new_value = min(100, current_value + points)  # Cap at 100
        current_gauges[attribute] = new_value

        chapter_unlocked = new_value >= 100 and current_value < 100

        await self.update(uid, {"crystal_gauges": current_gauges})

        return {
            "attribute": attribute,
            "points_added": new_value - current_value,
            "new_value": new_value,
            "chapter_unlocked": chapter_unlocked,
        }
    
    async def get_leaderboard(self, limit: int = 100, metric: str = "total_xp") -> List[Dict[str, Any]]:
        """Get user leaderboard by specified metric"""
        # Use pagination for better performance
        result = await self.find_with_pagination(
            order_by=metric,
            order_direction="desc",
            page_size=limit
        )
        
        leaderboard = []
        for i, user in enumerate(result["data"]):
            leaderboard.append({
                "rank": i + 1,
                "uid": user.uid,
                "display_name": user.display_name,
                "player_level": user.player_level,
                "total_xp": user.total_xp,
                "metric_value": getattr(user, metric, 0)
            })
        
        return leaderboard
    
    async def get_users_by_level_range(self, min_level: int, max_level: int) -> List[UserProfile]:
        """Get users within a level range"""
        return await self.find_by_multiple_fields({
            "player_level": {"operator": ">=", "value": min_level}
        })
    
    async def get_inactive_users(self, days_inactive: int = 7) -> List[UserProfile]:
        """Get users who haven't been active for specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_inactive)
        return await self.find_by_date_range(
            "last_active",
            datetime.min,
            cutoff_date
        )
    
    async def update_adhd_profile(self, uid: str, adhd_data: Dict[str, Any]) -> bool:
        """Update user's ADHD profile settings"""
        return await self.update(uid, {"adhd_profile": adhd_data})
    
    async def add_therapeutic_goal(self, uid: str, goal: str) -> bool:
        """Add therapeutic goal to user profile"""
        user = await self.get_by_id(uid)
        if not user:
            return False
        
        goals = user.therapeutic_goals or []
        if goal not in goals:
            goals.append(goal)
            return await self.update(uid, {"therapeutic_goals": goals})
        
        return True
    
    async def update_care_points(self, uid: str, points_change: int) -> Dict[str, Any]:
        """Update user's care points balance"""
        user = await self.get_by_id(uid)
        if not user:
            raise ValueError(f"User {uid} not found")
        
        new_balance = max(0, user.care_points + points_change)
        await self.update(uid, {"care_points": new_balance})
        
        return {
            "previous_balance": user.care_points,
            "change": points_change,
            "new_balance": new_balance
        }
    
    async def get_crystal_progress_summary(self, uid: str) -> Dict[str, Any]:
        """Get summary of user's crystal progression"""
        user = await self.get_by_id(uid)
        if not user:
            return {}
        
        crystal_summary = {}
        total_progress = 0
        unlocked_chapters = 0
        
        for attr in CrystalAttribute:
            attr_value = attr.value
            gauge_value = user.crystal_gauges.get(attr_value, 0)
            
            crystal_summary[attr_value] = {
                "current_value": gauge_value,
                "max_value": 100,
                "percentage": gauge_value,
                "chapter_unlocked": gauge_value >= 100
            }
            
            total_progress += gauge_value
            if gauge_value >= 100:
                unlocked_chapters += 1
        
        return {
            "crystals": crystal_summary,
            "total_progress": total_progress,
            "max_total_progress": 800,  # 8 attributes * 100
            "overall_percentage": (total_progress / 800) * 100,
            "unlocked_chapters": unlocked_chapters,
            "total_chapters": len(CrystalAttribute)
        }
    
    def _calculate_level(self, total_xp: int) -> int:
        """Calculate level from total XP using exponential progression"""
        from ..interfaces.level_system import LevelCalculator
        return LevelCalculator.get_level_from_xp(total_xp)
    
    def _calculate_xp_for_next_level(self, current_level: int) -> int:
        """Calculate XP needed for next level"""
        return (2 ** current_level - 1) * 100
    
    async def get_user_statistics(self, uid: str) -> Dict[str, Any]:
        """Get comprehensive user statistics"""
        user = await self.get_by_id(uid)
        if not user:
            return {}
        
        crystal_progress = await self.get_crystal_progress_summary(uid)
        xp_for_next_level = self._calculate_xp_for_next_level(user.player_level)
        current_level_xp = self._calculate_xp_for_next_level(user.player_level - 1) if user.player_level > 1 else 0
        
        return {
            "basic_info": {
                "uid": user.uid,
                "display_name": user.display_name,
                "player_level": user.player_level,
                "yu_level": user.yu_level,
                "total_xp": user.total_xp,
                "care_points": user.care_points
            },
            "progression": {
                "current_level_progress": user.total_xp - current_level_xp,
                "xp_for_next_level": xp_for_next_level - user.total_xp,
                "level_progress_percentage": ((user.total_xp - current_level_xp) / (xp_for_next_level - current_level_xp)) * 100
            },
            "crystal_progress": crystal_progress,
            "account_info": {
                "created_at": user.created_at,
                "last_active": user.last_active,
                "subscription_status": user.subscription_status,
                "days_since_creation": (datetime.utcnow() - user.created_at).days
            },
            "therapeutic_info": {
                "goals_count": len(user.therapeutic_goals or []),
                "adhd_profile_configured": bool(user.adhd_profile),
                "guardian_links_count": len(user.guardian_links or [])
            }
        }