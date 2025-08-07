from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict

class LevelCalculator:
    @staticmethod
    def calculate_xp_for_level(level: int) -> int:
        if level <= 1:
            return 0
        return int(round(100 * ((level - 1) ** 1.5)))

    @staticmethod
    def get_level_from_xp(xp: int) -> int:
        lvl = 1
        while LevelCalculator.calculate_xp_for_level(lvl + 1) <= xp:
            lvl += 1
        return lvl

    @staticmethod
    def calculate_level_up_rewards(old_level: int, new_level: int) -> List[str]:
        return [f"レベル{lvl}到達おめでとう！" for lvl in range(old_level + 1, new_level + 1)]

class PlayerLevelManager:
    def __init__(self, initial_xp: int = 0):
        self.total_xp = initial_xp
        self.level_history: List[Dict] = []
        self.level_progression = self._snapshot()

    def _snapshot(self):
        lvl = LevelCalculator.get_level_from_xp(self.total_xp)
        cur_xp = self.total_xp
        xp_cur = LevelCalculator.calculate_xp_for_level(lvl)
        xp_next = LevelCalculator.calculate_xp_for_level(lvl + 1)
        need = max(1, xp_next - xp_cur)
        progress = ((cur_xp - xp_cur) / need) * 100 if cur_xp >= xp_cur else 0.0
        return {
            "current_level": lvl,
            "current_xp": cur_xp,
            "xp_for_current_level": xp_cur,
            "xp_for_next_level": xp_next,
            "progress_percentage": progress,
        }

    def add_xp(self, amount: int, reason: str):
        old_level = LevelCalculator.get_level_from_xp(self.total_xp)
        self.total_xp += amount
        new_level = LevelCalculator.get_level_from_xp(self.total_xp)
        rewards = LevelCalculator.calculate_level_up_rewards(old_level, new_level) if new_level > old_level else []
        self.level_history.append({"added": amount, "reason": reason, "level_up": new_level > old_level})
        self.level_progression = self._snapshot()
        return {
            "xp_added": amount,
            "old_level": old_level,
            "new_level": new_level,
            "level_up": new_level > old_level,
            "rewards": rewards,
        }

    def get_xp_breakdown(self):
        return {"total_xp": self.total_xp, "history": list(self.level_history)}

    def simulate_xp_addition(self, amount: int):
        temp = self.total_xp + amount
        return {"new_level": LevelCalculator.get_level_from_xp(temp), "new_xp": temp}

class YuLevelManager:
    def __init__(self, initial_level: int = 1):
        self.current_level = initial_level
        self.personality_traits = {"wisdom": 0.5, "courage": 0.5, "kindness": 0.5}

    def grow_naturally(self, player_level: int, days_passed: int):
        old = self.current_level
        growth = False
        if days_passed >= 5 and player_level >= self.current_level:
            self.current_level += 1
            growth = True
        return {
            "old_level": old,
            "new_level": self.current_level,
            "growth_occurred": growth,
            "description": "明るく元気なユウは、あなたの冒険を楽しみにしています。",
        }

    def grow_from_interaction(self, interaction: str, player_level: int):
        old = self.current_level
        growth = False
        if interaction in {"story_choice", "task_completion", "crystal_resonance", "emotional_support"}:
            if player_level >= self.current_level:
                self.current_level += 1
                growth = True
        return {
            "old_level": old,
            "new_level": self.current_level,
            "growth_occurred": growth,
            "description": "明るく元気なユウは、あなたの冒険を楽しみにしています。",
        }

class LevelSystemManager:
    def __init__(self, player_xp: int, yu_level: int):
        self.player_manager = PlayerLevelManager(player_xp)
        self.yu_manager = YuLevelManager(yu_level)
        self.system_events: List[str] = []

    def add_player_xp(self, amount: int, reason: str):
        p = self.player_manager.add_xp(amount, reason)
        y = self.yu_manager.grow_naturally(self.player_manager.level_progression["current_level"], days_passed=1)
        evt = f"xp_added:{amount}"
        self.system_events.append(evt)
        return {"player": p, "yu": y, "system_event": evt}

    def trigger_yu_interaction(self, interaction: str):
        return self.yu_manager.grow_from_interaction(interaction, self.player_manager.level_progression["current_level"])

    def get_system_status(self):
        p = self.player_manager.level_progression
        return {
            "player": {"level": p["current_level"], "xp": self.player_manager.total_xp, "progression": p},
            "yu": {"level": self.yu_manager.current_level, "personality": "cheerful", "description": "明るく元気なユウは、あなたの冒険を楽しみにしています。"},
            "level_difference": abs(p["current_level"] - self.yu_manager.current_level),
            "recent_events": list(self.system_events)[-5:],
        }
