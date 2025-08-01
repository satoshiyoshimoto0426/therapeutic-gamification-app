"""
Game state repository for player progression, XP, and crystal system
Handles core game mechanics, leveling, and crystal growth tracking
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from google.cloud import firestore

from .base_repository import BaseRepository
from ..interfaces.core_types import (
    GameState, ChapterType, CrystalAttribute, CrystalState, 
    CrystalGrowthRecord, CrystalGrowthEvent, UserCrystalSystem
)
from ..utils.exceptions import ValidationError, NotFoundError


class GameStateRepository(BaseRepository[GameState]):
    """Repository for game state and crystal system data"""
    
    def __init__(self, db_client: firestore.Client):
        super().__init__(db_client, "game_states")
    
    def _to_entity(self, doc_data: Dict[str, Any], doc_id: str = None) -> GameState:
        """Convert Firestore document to GameState entity"""
        return GameState(
            player_level=doc_data["player_level"],
            yu_level=doc_data["yu_level"],
            current_chapter=ChapterType(doc_data["current_chapter"]),
            crystal_gauges={
                ChapterType(k): v for k, v in doc_data["crystal_gauges"].items()
            },
            total_xp=doc_data["total_xp"],
            last_resonance_event=doc_data.get("last_resonance_event")
        )
    
    def _to_document(self, entity: GameState) -> Dict[str, Any]:
        """Convert GameState entity to Firestore document"""
        return {
            "player_level": entity.player_level,
            "yu_level": entity.yu_level,
            "current_chapter": entity.current_chapter.value,
            "crystal_gauges": {
                k.value: v for k, v in entity.crystal_gauges.items()
            },
            "total_xp": entity.total_xp,
            "last_resonance_event": entity.last_resonance_event
        }
    
    async def get_user_game_state(self, uid: str) -> Optional[GameState]:
        """Get user's game state"""
        try:
            doc_ref = self.collection_ref.document(uid)
            doc = doc_ref.get()
            
            if not doc.exists:
                return None
            
            return self._to_entity(doc.to_dict(), doc.id)
            
        except Exception as e:
            self.logger.error(f"Failed to get game state for user {uid}: {str(e)}")
            raise
    
    async def create_initial_game_state(self, uid: str) -> str:
        """Create initial game state for new user"""
        try:
            # Check if game state already exists
            existing = await self.get_user_game_state(uid)
            if existing:
                raise ValidationError("Game state already exists for user")
            
            # Initialize crystal gauges
            crystal_gauges = {chapter: 0 for chapter in ChapterType}
            
            game_state = GameState(
                player_level=1,
                yu_level=1,
                current_chapter=ChapterType.SELF_DISCIPLINE,
                crystal_gauges=crystal_gauges,
                total_xp=0,
                last_resonance_event=None
            )
            
            # Use uid as document ID for easy lookup
            doc_data = self._to_document(game_state)
            doc_data["uid"] = uid
            
            doc_ref = self.collection_ref.document(uid)
            doc_ref.set(doc_data)
            
            self.logger.info(f"Created initial game state for user {uid}")
            return uid
            
        except Exception as e:
            self.logger.error(f"Failed to create initial game state for user {uid}: {str(e)}")
            raise
    
    async def add_xp(self, uid: str, xp_amount: int, source: str = "task_completion") -> Dict[str, Any]:
        """Add XP and handle level ups"""
        try:
            game_state = await self.get_user_game_state(uid)
            if not game_state:
                raise NotFoundError(f"Game state not found for user {uid}")
            
            old_level = game_state.player_level
            old_yu_level = game_state.yu_level
            
            # Add XP
            game_state.total_xp += xp_amount
            
            # Calculate new levels
            new_player_level = self._calculate_level_from_xp(game_state.total_xp)
            new_yu_level = self._calculate_yu_level_from_player_level(new_player_level)
            
            game_state.player_level = new_player_level
            game_state.yu_level = new_yu_level
            
            # Update in database
            updates = {
                "total_xp": game_state.total_xp,
                "player_level": game_state.player_level,
                "yu_level": game_state.yu_level
            }
            
            await self.update(uid, updates)
            
            # Prepare response
            level_ups = []
            if new_player_level > old_level:
                level_ups.append({
                    "type": "player_level",
                    "old_level": old_level,
                    "new_level": new_player_level
                })
            
            if new_yu_level > old_yu_level:
                level_ups.append({
                    "type": "yu_level",
                    "old_level": old_yu_level,
                    "new_level": new_yu_level
                })
            
            result = {
                "xp_added": xp_amount,
                "total_xp": game_state.total_xp,
                "current_level": new_player_level,
                "current_yu_level": new_yu_level,
                "level_ups": level_ups,
                "source": source
            }
            
            self.logger.info(f"Added {xp_amount} XP to user {uid}, new level: {new_player_level}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to add XP for user {uid}: {str(e)}")
            raise
    
    def _calculate_level_from_xp(self, total_xp: int) -> int:
        """Calculate player level from total XP"""
        # Progressive XP requirements: level n requires n*100 XP
        # Level 1: 0-99 XP, Level 2: 100-299 XP, Level 3: 300-599 XP, etc.
        
        if total_xp < 100:
            return 1
        
        level = 1
        xp_needed = 0
        
        while xp_needed <= total_xp:
            level += 1
            xp_needed += level * 100
        
        return level - 1
    
    def _calculate_yu_level_from_player_level(self, player_level: int) -> int:
        """Calculate Yu level from player level (Yu levels up every 5 player levels)"""
        return min(100, (player_level - 1) // 5 + 1)
    
    async def update_crystal_gauge(self, uid: str, chapter: ChapterType, 
                                 growth_amount: int, event_type: CrystalGrowthEvent,
                                 context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Update crystal gauge and record growth event"""
        try:
            game_state = await self.get_user_game_state(uid)
            if not game_state:
                raise NotFoundError(f"Game state not found for user {uid}")
            
            if context is None:
                context = {}
            
            # Get current crystal value
            current_value = game_state.crystal_gauges.get(chapter, 0)
            
            # Calculate new value (max 100)
            new_value = min(100, current_value + growth_amount)
            actual_growth = new_value - current_value
            
            if actual_growth <= 0:
                return {
                    "growth_applied": 0,
                    "current_value": current_value,
                    "milestone_reached": False
                }
            
            # Update crystal gauge
            game_state.crystal_gauges[chapter] = new_value
            
            # Check for milestone rewards
            milestone_reached = self._check_crystal_milestone(current_value, new_value)
            
            # Update in database
            updates = {
                f"crystal_gauges.{chapter.value}": new_value
            }
            
            await self.update(uid, updates)
            
            # Record growth event
            await self._record_crystal_growth(uid, chapter, event_type, actual_growth, context)
            
            result = {
                "growth_applied": actual_growth,
                "current_value": new_value,
                "milestone_reached": milestone_reached,
                "chapter": chapter.value,
                "event_type": event_type.value
            }
            
            self.logger.info(f"Updated crystal {chapter.value} for user {uid}: +{actual_growth} -> {new_value}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to update crystal gauge for user {uid}: {str(e)}")
            raise
    
    def _check_crystal_milestone(self, old_value: int, new_value: int) -> bool:
        """Check if a crystal milestone was reached"""
        milestones = [25, 50, 75, 100]
        
        for milestone in milestones:
            if old_value < milestone <= new_value:
                return True
        
        return False
    
    async def _record_crystal_growth(self, uid: str, chapter: ChapterType, 
                                   event_type: CrystalGrowthEvent, growth_amount: int,
                                   context: Dict[str, Any]) -> None:
        """Record crystal growth event in separate collection"""
        try:
            growth_record = {
                "uid": uid,
                "attribute": chapter.value,
                "event_type": event_type.value,
                "growth_amount": growth_amount,
                "trigger_context": context,
                "created_at": datetime.utcnow()
            }
            
            # Store in crystal_growth_logs collection
            growth_collection = self.db.collection("crystal_growth_logs")
            growth_collection.add(growth_record)
            
        except Exception as e:
            self.logger.error(f"Failed to record crystal growth for user {uid}: {str(e)}")
            # Don't raise - this is supplementary logging
    
    async def calculate_resonance_level(self, uid: str) -> Dict[str, Any]:
        """Calculate resonance level based on crystal balance"""
        try:
            game_state = await self.get_user_game_state(uid)
            if not game_state:
                raise NotFoundError(f"Game state not found for user {uid}")
            
            crystal_values = list(game_state.crystal_gauges.values())
            
            if not crystal_values:
                return {"resonance_level": 0, "balance_score": 0}
            
            # Calculate balance (lower standard deviation = better balance)
            mean_value = sum(crystal_values) / len(crystal_values)
            variance = sum((x - mean_value) ** 2 for x in crystal_values) / len(crystal_values)
            std_dev = variance ** 0.5
            
            # Balance score (0-100, higher is better)
            max_possible_std = 50  # Maximum possible standard deviation
            balance_score = max(0, 100 - (std_dev / max_possible_std * 100))
            
            # Resonance level (0-10 based on balance and overall progress)
            overall_progress = mean_value
            resonance_level = min(10, int((balance_score * 0.6 + overall_progress * 0.4) / 10))
            
            # Check for resonance events
            resonance_event_triggered = False
            if balance_score > 80 and overall_progress > 60:
                # Check if enough time has passed since last resonance event
                if (not game_state.last_resonance_event or 
                    datetime.utcnow() - game_state.last_resonance_event > timedelta(days=1)):
                    
                    resonance_event_triggered = True
                    
                    # Update last resonance event time
                    await self.update(uid, {"last_resonance_event": datetime.utcnow()})
            
            result = {
                "resonance_level": resonance_level,
                "balance_score": round(balance_score, 2),
                "overall_progress": round(overall_progress, 2),
                "crystal_values": {k.value: v for k, v in game_state.crystal_gauges.items()},
                "resonance_event_triggered": resonance_event_triggered
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to calculate resonance level for user {uid}: {str(e)}")
            raise
    
    async def get_level_progress(self, uid: str) -> Dict[str, Any]:
        """Get detailed level progression information"""
        try:
            game_state = await self.get_user_game_state(uid)
            if not game_state:
                raise NotFoundError(f"Game state not found for user {uid}")
            
            current_level = game_state.player_level
            current_xp = game_state.total_xp
            
            # Calculate XP needed for current level
            xp_for_current_level = self._calculate_xp_for_level(current_level)
            xp_for_next_level = self._calculate_xp_for_level(current_level + 1)
            
            # Progress within current level
            xp_in_current_level = current_xp - xp_for_current_level
            xp_needed_for_next = xp_for_next_level - current_xp
            level_progress_percentage = (xp_in_current_level / (xp_for_next_level - xp_for_current_level)) * 100
            
            return {
                "current_level": current_level,
                "current_yu_level": game_state.yu_level,
                "total_xp": current_xp,
                "xp_in_current_level": xp_in_current_level,
                "xp_needed_for_next": xp_needed_for_next,
                "level_progress_percentage": round(level_progress_percentage, 2),
                "next_level": current_level + 1,
                "next_yu_level_at": (current_level // 5 + 1) * 5 + 1
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get level progress for user {uid}: {str(e)}")
            raise
    
    def _calculate_xp_for_level(self, level: int) -> int:
        """Calculate total XP needed to reach a specific level"""
        if level <= 1:
            return 0
        
        total_xp = 0
        for l in range(2, level + 1):
            total_xp += l * 100
        
        return total_xp
    
    async def get_crystal_growth_history(self, uid: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get crystal growth history for specified period"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            growth_collection = self.db.collection("crystal_growth_logs")
            query = (growth_collection
                    .where("uid", "==", uid)
                    .where("created_at", ">=", start_date)
                    .where("created_at", "<=", end_date)
                    .order_by("created_at", direction=firestore.Query.DESCENDING))
            
            docs = query.get()
            
            history = []
            for doc in docs:
                data = doc.to_dict()
                history.append({
                    "attribute": data["attribute"],
                    "event_type": data["event_type"],
                    "growth_amount": data["growth_amount"],
                    "trigger_context": data.get("trigger_context", {}),
                    "created_at": data["created_at"]
                })
            
            return history
            
        except Exception as e:
            self.logger.error(f"Failed to get crystal growth history for user {uid}: {str(e)}")
            raise
    
    async def update_current_chapter(self, uid: str, new_chapter: ChapterType) -> bool:
        """Update user's current chapter"""
        try:
            game_state = await self.get_user_game_state(uid)
            if not game_state:
                raise NotFoundError(f"Game state not found for user {uid}")
            
            # Validate chapter transition (could add logic here)
            game_state.current_chapter = new_chapter
            
            updates = {"current_chapter": new_chapter.value}
            result = await self.update(uid, updates)
            
            self.logger.info(f"Updated current chapter for user {uid} to {new_chapter.value}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to update current chapter for user {uid}: {str(e)}")
            raise
    
    async def get_leaderboard(self, limit: int = 10, metric: str = "total_xp") -> List[Dict[str, Any]]:
        """Get leaderboard data"""
        try:
            if metric == "total_xp":
                query = (self.collection_ref
                        .order_by("total_xp", direction=firestore.Query.DESCENDING)
                        .limit(limit))
            elif metric == "player_level":
                query = (self.collection_ref
                        .order_by("player_level", direction=firestore.Query.DESCENDING)
                        .order_by("total_xp", direction=firestore.Query.DESCENDING)
                        .limit(limit))
            else:
                raise ValidationError(f"Invalid leaderboard metric: {metric}")
            
            docs = query.get()
            
            leaderboard = []
            for i, doc in enumerate(docs):
                data = doc.to_dict()
                leaderboard.append({
                    "rank": i + 1,
                    "uid": doc.id,
                    "player_level": data["player_level"],
                    "yu_level": data["yu_level"],
                    "total_xp": data["total_xp"],
                    "current_chapter": data["current_chapter"]
                })
            
            return leaderboard
            
        except Exception as e:
            self.logger.error(f"Failed to get leaderboard: {str(e)}")
            raise