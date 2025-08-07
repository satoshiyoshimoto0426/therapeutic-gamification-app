"""
Resonance System Interface

共鳴イベントシステムのインターフェース定義
Requirements: 4.4, 4.5
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel, Field
import uuid
from .core_types import CrystalAttribute


class ResonanceType(str, Enum):
    """Types of resonance events."""

    LEVEL_SYNC = "level_sync"
    CRYSTAL_HARMONY = "crystal_harmony"
    EMOTIONAL_BOND = "emotional_bond"
    WISDOM_SHARING = "wisdom_sharing"


class ResonanceIntensity(str, Enum):
    """Intensity levels for resonance events."""

    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    INTENSE = "intense"


class ResonanceEvent(BaseModel):
    """共鳴イベント"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    resonance_type: ResonanceType
    intensity: ResonanceIntensity
    player_level: int
    yu_level: int
    level_difference: int
    bonus_xp: int
    crystal_bonuses: Dict[CrystalAttribute, int] = {}
    special_rewards: List[str] = []
    therapeutic_message: str = ""
    story_unlock: Optional[str] = None
    triggered_at: datetime = Field(default_factory=datetime.utcnow)


class ResonanceCondition(BaseModel):
    """共鳴発生条件"""
    min_level_difference: int = 5
    max_level_difference: int = 20
    cooldown_hours: int = 24
    required_player_level: int = 1


class ResonanceCalculator:
    """Utility calculations for resonance mechanics."""

    INTENSITY_THRESHOLDS = {
        ResonanceIntensity.WEAK: (0, 7),
        ResonanceIntensity.MODERATE: (8, 12),
        ResonanceIntensity.STRONG: (13, 20),
        ResonanceIntensity.INTENSE: (21, 10**6),
    }

    INTENSITY_MULTIPLIERS = {
        ResonanceIntensity.WEAK: 1.5,
        ResonanceIntensity.MODERATE: 2.0,
        ResonanceIntensity.STRONG: 3.0,
        ResonanceIntensity.INTENSE: 4.0,
    }

    BASE_BONUS_PER_LEVEL = 50

    @staticmethod
    def calculate_resonance_intensity(level_difference: int) -> ResonanceIntensity:
        for intensity, (low, high) in ResonanceCalculator.INTENSITY_THRESHOLDS.items():
            if low <= level_difference <= high:
                return intensity
        return ResonanceIntensity.WEAK

    @staticmethod
    def calculate_bonus_xp(
        level_difference: int,
        player_level: int,
        resonance_type: ResonanceType,
    ) -> int:
        base = level_difference * ResonanceCalculator.BASE_BONUS_PER_LEVEL
        intensity = ResonanceCalculator.calculate_resonance_intensity(level_difference)
        intensity_mult = ResonanceCalculator.INTENSITY_MULTIPLIERS[intensity]
        level_mult = 1.0 + (player_level * 0.05)
        type_mult = {
            ResonanceType.LEVEL_SYNC: 1.0,
            ResonanceType.CRYSTAL_HARMONY: 1.2,
            ResonanceType.EMOTIONAL_BOND: 0.8,
            ResonanceType.WISDOM_SHARING: 1.1,
        }.get(resonance_type, 1.0)
        bonus = int(base * intensity_mult * level_mult * type_mult)
        return max(100, bonus)

    @staticmethod
    def calculate_crystal_bonuses(
        resonance_type: ResonanceType,
        intensity: ResonanceIntensity,
        player_level: int,
    ) -> Dict[CrystalAttribute, int]:
        base = {
            ResonanceIntensity.WEAK: 5,
            ResonanceIntensity.MODERATE: 8,
            ResonanceIntensity.STRONG: 12,
            ResonanceIntensity.INTENSE: 18,
        }[intensity]

        if resonance_type == ResonanceType.LEVEL_SYNC:
            return {attr: base // 2 for attr in CrystalAttribute}
        if resonance_type == ResonanceType.CRYSTAL_HARMONY:
            return {
                CrystalAttribute.WISDOM: base,
                CrystalAttribute.EMPATHY: base,
                CrystalAttribute.RESILIENCE: base // 2,
            }
        if resonance_type == ResonanceType.EMOTIONAL_BOND:
            return {
                CrystalAttribute.EMPATHY: base,
                CrystalAttribute.COMMUNICATION: base,
                CrystalAttribute.COURAGE: base // 2,
            }
        if resonance_type == ResonanceType.WISDOM_SHARING:
            return {
                CrystalAttribute.WISDOM: base,
                CrystalAttribute.CURIOSITY: base,
                CrystalAttribute.CREATIVITY: base // 2,
            }
        return {}

    @staticmethod
    def generate_therapeutic_message(
        resonance_type: ResonanceType,
        intensity: ResonanceIntensity,
        player_level: int,
        yu_level: int,
    ) -> str:
        intensity_desc = {
            ResonanceIntensity.WEAK: "穏やかな",
            ResonanceIntensity.MODERATE: "心地よい",
            ResonanceIntensity.STRONG: "力強い",
            ResonanceIntensity.INTENSE: "深い",
        }[intensity]

        messages = {
            ResonanceType.LEVEL_SYNC: f"{intensity_desc}調和が生まれました。",
            ResonanceType.CRYSTAL_HARMONY: f"{intensity_desc}成長を感じます。",
            ResonanceType.EMOTIONAL_BOND: f"{intensity_desc}共有の絆が力になります。",
            ResonanceType.WISDOM_SHARING: f"{intensity_desc}知恵を分かち合いました。",
        }
        return messages.get(resonance_type, "共鳴が起こりました。")


class ResonanceEventManager:
    """共鳴イベント管理"""
    
    def __init__(self):
        self.resonance_history: List[ResonanceEvent] = []
        self.conditions = ResonanceCondition()
        
        # 共鳴タイプ別の設定
        self.resonance_configs = {
            ResonanceType.LEVEL_SYNC: {
                "base_xp": 50,
                "crystal_bonus": 10,
                "message": "ユウとの心が調和し、穏やかな共鳴が生まれました。",
            },
            ResonanceType.CRYSTAL_HARMONY: {
                "base_xp": 75,
                "crystal_bonus": 15,
                "message": "ユウと共に成長の共鳴を感じています。",
            },
            ResonanceType.EMOTIONAL_BOND: {
                "base_xp": 100,
                "crystal_bonus": 20,
                "message": "ユウとの強い絆が新たな突破口を開きました。",
            },
            ResonanceType.WISDOM_SHARING: {
                "base_xp": 125,
                "crystal_bonus": 25,
                "message": "ユウの深い知恵があなたの心に響いています。",
            },
        }

    def check_resonance_conditions(
        self, 
        player_level: int, 
        yu_level: int
    ) -> Tuple[bool, Optional[ResonanceType]]:
        """共鳴発生条件チェック"""
        level_difference = abs(player_level - yu_level)
        
        # レベル差チェック
        if level_difference < self.conditions.min_level_difference:
            return False, None
        
        if level_difference > self.conditions.max_level_difference:
            return False, None
        
        # プレイヤーレベルチェック
        if player_level < self.conditions.required_player_level:
            return False, None
        
        # クールダウンチェック
        if self._is_in_cooldown():
            return False, None
        
        # 共鳴タイプ決定
        resonance_type = self._determine_resonance_type(player_level, yu_level, level_difference)
        
        return True, resonance_type
    
    def trigger_resonance_event(
        self,
        player_level: int,
        yu_level: int,
        resonance_type: ResonanceType
    ) -> ResonanceEvent:
        """共鳴イベント発生"""
        level_difference = abs(player_level - yu_level)
        intensity = self._calculate_intensity(level_difference)
        
        # ボーナスXP計算
        config = self.resonance_configs[resonance_type]
        base_xp = config["base_xp"]
        intensity_multiplier = self._get_intensity_multiplier(intensity)
        bonus_xp = int(base_xp * intensity_multiplier)
        
        # クリスタルボーナス計算
        crystal_bonuses = self._calculate_crystal_bonuses(
            resonance_type, 
            intensity, 
            config["crystal_bonus"]
        )
        
        # 特別報酬生成
        special_rewards = self._generate_special_rewards(resonance_type, intensity, level_difference)
        
        # 治療的メッセージ生成
        therapeutic_message = self._generate_therapeutic_message(resonance_type, intensity)
        
        # ストーリーアンロック判定
        story_unlock = self._check_story_unlock(player_level, resonance_type)
        
        # 共鳴イベント作成
        event = ResonanceEvent(
            resonance_type=resonance_type,
            intensity=intensity,
            player_level=player_level,
            yu_level=yu_level,
            level_difference=level_difference,
            bonus_xp=bonus_xp,
            crystal_bonuses=crystal_bonuses,
            special_rewards=special_rewards,
            therapeutic_message=therapeutic_message,
            story_unlock=story_unlock
        )
        
        # 履歴に追加
        self.resonance_history.append(event)
        
        return event
    
    def get_resonance_statistics(self) -> Dict[str, Any]:
        """共鳴統計取得"""
        total_events = len(self.resonance_history)
        
        if total_events == 0:
            return {
                "total_events": 0,
                "last_event": None,
                "type_distribution": {},
                "total_bonus_xp": 0,
                "average_bonus_xp": 0
            }
        
        # タイプ別分布
        type_distribution = {}
        total_bonus_xp = 0
        
        for event in self.resonance_history:
            event_type = event.resonance_type.value
            type_distribution[event_type] = type_distribution.get(event_type, 0) + 1
            total_bonus_xp += event.bonus_xp
        
        return {
            "total_events": total_events,
            "last_event": self.resonance_history[-1].triggered_at,
            "type_distribution": type_distribution,
            "total_bonus_xp": total_bonus_xp,
            "average_bonus_xp": total_bonus_xp / total_events
        }
    
    def simulate_resonance_probability(
        self, 
        player_level: int, 
        yu_level: int, 
        days_ahead: int = 7
    ) -> Dict[str, Any]:
        """共鳴確率シミュレーション"""
        level_difference = abs(player_level - yu_level)
        
        # 基本確率計算
        if level_difference < self.conditions.min_level_difference:
            base_probability = 0.0
        elif level_difference >= self.conditions.max_level_difference:
            base_probability = 0.1
        else:
            # レベル差に基づく確率（5-20の範囲で線形増加）
            normalized_diff = (level_difference - 5) / 15
            base_probability = 0.3 + (normalized_diff * 0.4)  # 0.3-0.7の範囲
        
        # クールダウン考慮
        if self._is_in_cooldown():
            current_probability = 0.0
        else:
            current_probability = base_probability
        
        # 将来予測
        future_probabilities = []
        for day in range(1, days_ahead + 1):
            # 簡単な予測モデル（実際はより複雑になる）
            daily_prob = base_probability * (1 - 0.1 * day)  # 時間経過で少し減少
            future_probabilities.append({
                "day": day,
                "probability": max(0.0, daily_prob)
            })
        
        return {
            "current_probability": current_probability,
            "base_probability": base_probability,
            "level_difference": level_difference,
            "in_cooldown": self._is_in_cooldown(),
            "future_predictions": future_probabilities
        }
    
    # プライベートメソッド
    
    def _is_in_cooldown(self) -> bool:
        """クールダウン中かチェック"""
        if not self.resonance_history:
            return False
        
        last_event = self.resonance_history[-1]
        cooldown_end = last_event.triggered_at + timedelta(hours=self.conditions.cooldown_hours)
        
        return datetime.utcnow() < cooldown_end
    
    def _determine_resonance_type(
        self, 
        player_level: int, 
        yu_level: int, 
        level_difference: int
    ) -> ResonanceType:
        """共鳴タイプ決定"""
        # プレイヤーがユウより高レベルの場合
        if player_level > yu_level:
            if level_difference >= 15:
                return ResonanceType.WISDOM_SHARING
            elif level_difference >= 10:
                return ResonanceType.EMOTIONAL_BOND
            else:
                return ResonanceType.CRYSTAL_HARMONY
        
        # ユウがプレイヤーより高レベルの場合
        else:
            if level_difference >= 15:
                return ResonanceType.WISDOM_SHARING
            elif level_difference >= 10:
                return ResonanceType.LEVEL_SYNC
            else:
                return ResonanceType.CRYSTAL_HARMONY
    
    def _calculate_intensity(self, level_difference: int) -> ResonanceIntensity:
        """共鳴強度計算"""
        if level_difference >= 18:
            return ResonanceIntensity.INTENSE
        elif level_difference >= 12:
            return ResonanceIntensity.STRONG
        elif level_difference >= 8:
            return ResonanceIntensity.MODERATE
        else:
            return ResonanceIntensity.WEAK
    
    def _get_intensity_multiplier(self, intensity: ResonanceIntensity) -> float:
        """強度倍率取得"""
        multipliers = {
            ResonanceIntensity.WEAK: 1.0,
            ResonanceIntensity.MODERATE: 1.2,
            ResonanceIntensity.STRONG: 1.5,
            ResonanceIntensity.INTENSE: 2.0
        }
        return multipliers.get(intensity, 1.0)
    
    def _calculate_crystal_bonuses(
        self, 
        resonance_type: ResonanceType, 
        intensity: ResonanceIntensity,
        base_bonus: int
    ) -> Dict[CrystalAttribute, int]:
        """クリスタルボーナス計算"""
        intensity_multiplier = self._get_intensity_multiplier(intensity)
        bonus_amount = int(base_bonus * intensity_multiplier)
        
        # 共鳴タイプに基づく属性選択
        type_attributes = {
            ResonanceType.LEVEL_SYNC: [CrystalAttribute.EMPATHY, CrystalAttribute.RESILIENCE],
            ResonanceType.CRYSTAL_HARMONY: [CrystalAttribute.CURIOSITY, CrystalAttribute.COURAGE],
            ResonanceType.EMOTIONAL_BOND: [CrystalAttribute.CREATIVITY, CrystalAttribute.SELF_DISCIPLINE],
            ResonanceType.WISDOM_SHARING: [CrystalAttribute.WISDOM, CrystalAttribute.COMMUNICATION]
        }
        
        attributes = type_attributes.get(resonance_type, [CrystalAttribute.SELF_DISCIPLINE])
        
        return {attr: bonus_amount for attr in attributes}
    
    def _generate_special_rewards(
        self, 
        resonance_type: ResonanceType, 
        intensity: ResonanceIntensity,
        level_difference: int
    ) -> List[str]:
        """特別報酬生成"""
        rewards = []
        
        # 強度に基づく報酬
        if intensity == ResonanceIntensity.INTENSE:
            rewards.append("レジェンダリーアイテム獲得")
        elif intensity == ResonanceIntensity.STRONG:
            rewards.append("レアアイテム獲得")
        
        # レベル差に基づく報酬
        if level_difference >= 15:
            rewards.append("特別なストーリー分岐アンロック")
        
        # タイプ別報酬
        type_rewards = {
            ResonanceType.LEVEL_SYNC: "調和の証獲得",
            ResonanceType.CRYSTAL_HARMONY: "成長の印獲得",
            ResonanceType.EMOTIONAL_BOND: "突破の勲章獲得",
            ResonanceType.WISDOM_SHARING: "知恵の宝珠獲得"
        }
        
        if resonance_type in type_rewards:
            rewards.append(type_rewards[resonance_type])
        
        return rewards
    
    def _generate_therapeutic_message(
        self, 
        resonance_type: ResonanceType, 
        intensity: ResonanceIntensity
    ) -> str:
        """治療的メッセージ生成"""
        base_message = self.resonance_configs[resonance_type]["message"]
        
        # 強度に基づくメッセージ拡張
        intensity_additions = {
            ResonanceIntensity.WEAK: "この穏やかな瞬間を大切にしてください。",
            ResonanceIntensity.MODERATE: "あなたの努力が実を結んでいます。",
            ResonanceIntensity.STRONG: "素晴らしい成長を遂げていますね。",
            ResonanceIntensity.INTENSE: "あなたの変化は本当に驚くべきものです。"
        }
        
        addition = intensity_additions.get(intensity, "")
        
        return f"{base_message} {addition}".strip()
    
    def _check_story_unlock(
        self, 
        player_level: int, 
        resonance_type: ResonanceType
    ) -> Optional[str]:
        """ストーリーアンロック判定"""
        # 特定条件でストーリーアンロック
        if player_level >= 10 and resonance_type == ResonanceType.EMOTIONAL_BOND:
            return "special_chapter_breakthrough"
        elif player_level >= 20 and resonance_type == ResonanceType.WISDOM_SHARING:
            return "wisdom_path_unlock"
        
        return None