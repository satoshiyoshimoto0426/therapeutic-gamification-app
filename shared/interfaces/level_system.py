"""
Level System Interface

レベルシステムのインターフェース定義
Requirements: 4.4, 4.5
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel
import math


class LevelProgression(BaseModel):
    """レベル進行情報"""
    current_level: int
    current_xp: int
    xp_for_current_level: int
    xp_for_next_level: int
    xp_needed_for_next: int
    progress_percentage: float


class YuPersonality(str, Enum):
    """ユウの性格タイプ"""
    CHEERFUL = "cheerful"       # 明るい
    CALM = "calm"              # 落ち着いた
    ENERGETIC = "energetic"    # エネルギッシュ
    WISE = "wise"              # 賢い
    SUPPORTIVE = "supportive"  # 支援的


class LevelCalculator:
    """レベル計算機"""
    
    @staticmethod
    def calculate_level(total_xp: int) -> int:
        """総XPからレベルを計算"""
        if total_xp <= 0:
            return 1
        return int(math.log2(total_xp / 100 + 1)) + 1
    
    @staticmethod
    def xp_for_level(level: int) -> int:
        """指定レベルに必要な総XP"""
        if level <= 1:
            return 0
        return (2 ** (level - 1) - 1) * 100
    
    @staticmethod
    def xp_for_next_level(current_level: int) -> int:
        """次のレベルに必要な総XP"""
        return LevelCalculator.xp_for_level(current_level + 1)
    
    @staticmethod
    def get_level_progression(total_xp: int) -> LevelProgression:
        """レベル進行情報を取得"""
        current_level = LevelCalculator.calculate_level(total_xp)
        xp_for_current = LevelCalculator.xp_for_level(current_level)
        xp_for_next = LevelCalculator.xp_for_next_level(current_level)
        xp_needed = xp_for_next - total_xp
        
        # 進行率計算
        if xp_for_next > xp_for_current:
            progress = (total_xp - xp_for_current) / (xp_for_next - xp_for_current)
        else:
            progress = 1.0
        
        return LevelProgression(
            current_level=current_level,
            current_xp=total_xp,
            xp_for_current_level=xp_for_current,
            xp_for_next_level=xp_for_next,
            xp_needed_for_next=max(0, xp_needed),
            progress_percentage=min(100.0, progress * 100)
        )


class PlayerLevelManager:
    """プレイヤーレベル管理"""
    
    def __init__(self, initial_xp: int = 0):
        self.total_xp = initial_xp
        self.level_progression = LevelCalculator.get_level_progression(initial_xp)
    
    def add_xp(self, xp_amount: int, source: str = "unknown") -> Dict[str, Any]:
        """XP追加"""
        old_level = self.level_progression.current_level
        self.total_xp += xp_amount
        self.level_progression = LevelCalculator.get_level_progression(self.total_xp)
        new_level = self.level_progression.current_level
        
        level_up = new_level > old_level
        rewards = []
        
        if level_up:
            rewards = self._generate_level_up_rewards(new_level)
        
        return {
            "old_level": old_level,
            "new_level": new_level,
            "level_up": level_up,
            "xp_added": xp_amount,
            "total_xp": self.total_xp,
            "rewards": rewards,
            "source": source
        }
    
    def _generate_level_up_rewards(self, level: int) -> List[str]:
        """レベルアップ報酬生成"""
        rewards = [f"レベル{level}到達おめでとう！"]
        
        # 特定レベルでの特別報酬
        if level % 5 == 0:
            rewards.append("特別なアチーブメント獲得")
        if level % 10 == 0:
            rewards.append("新しい機能がアンロックされました")
        
        return rewards


class YuLevelManager:
    """ユウレベル管理"""
    
    def __init__(self, initial_level: int = 1):
        self.level = initial_level
        self.personality = self._determine_personality(initial_level)
        self.description = self._generate_description()
    
    def update_level(self, player_level: int) -> Dict[str, Any]:
        """プレイヤーレベルに基づいてユウのレベル更新"""
        old_level = self.level
        
        # ユウはプレイヤーより少し遅れて成長
        if player_level >= 5:
            self.level = max(1, player_level - 2)
        elif player_level >= 3:
            self.level = max(1, player_level - 1)
        else:
            self.level = 1
        
        growth_occurred = self.level > old_level
        
        if growth_occurred:
            self.personality = self._determine_personality(self.level)
            self.description = self._generate_description()
        
        return {
            "old_level": old_level,
            "new_level": self.level,
            "growth_occurred": growth_occurred,
            "personality": self.personality.value,
            "description": self.description
        }
    
    def _determine_personality(self, level: int) -> YuPersonality:
        """レベルに基づく性格決定"""
        if level >= 20:
            return YuPersonality.WISE
        elif level >= 15:
            return YuPersonality.SUPPORTIVE
        elif level >= 10:
            return YuPersonality.CALM
        elif level >= 5:
            return YuPersonality.ENERGETIC
        else:
            return YuPersonality.CHEERFUL
    
    def _generate_description(self) -> str:
        """性格に基づく説明生成"""
        descriptions = {
            YuPersonality.CHEERFUL: "明るく元気なユウは、あなたの冒険を楽しみにしています。",
            YuPersonality.ENERGETIC: "エネルギッシュなユウは、新しい挑戦に積極的です。",
            YuPersonality.CALM: "落ち着いたユウは、あなたの成長を静かに見守っています。",
            YuPersonality.SUPPORTIVE: "支援的なユウは、あなたの努力を理解し、励ましてくれます。",
            YuPersonality.WISE: "賢いユウは、深い洞察であなたを導いてくれます。"
        }
        return descriptions.get(self.personality, "ユウはあなたと一緒に成長しています。")


class LevelSystemManager:
    """レベルシステム統合管理"""
    
    def __init__(self, player_xp: int = 0, yu_level: int = 1):
        self.player_manager = PlayerLevelManager(player_xp)
        self.yu_manager = YuLevelManager(yu_level)
    
    def add_player_xp(self, xp_amount: int, source: str = "unknown") -> Dict[str, Any]:
        """プレイヤーXP追加と連動処理"""
        # プレイヤーXP追加
        player_result = self.player_manager.add_xp(xp_amount, source)
        
        # ユウレベル更新
        yu_result = self.yu_manager.update_level(player_result["new_level"])
        
        return {
            "player": player_result,
            "yu": yu_result
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """システム全体の状態取得"""
        player_level = self.player_manager.level_progression.current_level
        yu_level = self.yu_manager.level
        
        return {
            "player": {
                "level": player_level,
                "xp": self.player_manager.total_xp,
                "progression": self.player_manager.level_progression.dict()
            },
            "yu": {
                "level": yu_level,
                "personality": self.yu_manager.personality.value,
                "description": self.yu_manager.description
            },
            "level_difference": abs(player_level - yu_level)
        }