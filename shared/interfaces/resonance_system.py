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
    """共鳴タイプ"""
    HARMONY = "harmony"           # 調和共鳴
    GROWTH = "growth"            # 成長共鳴
    BREAKTHROUGH = "breakthrough" # 突破共鳴
    WISDOM = "wisdom"            # 知恵共鳴


class ResonanceIntensity(str, Enum):
    """共鳴強度"""
    GENTLE = "gentle"     # 穏やか
    MODERATE = "moderate" # 中程度
    STRONG = "strong"     # 強い
    INTENSE = "intense"   # 激しい


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


class ResonanceEventManager:
    """共鳴イベント管理"""
    
    def __init__(self):
        self.resonance_history: List[ResonanceEvent] = []
        self.conditions = ResonanceCondition()
        
        # 共鳴タイプ別の設定
        self.resonance_configs = {
            ResonanceType.HARMONY: {
                "base_xp": 50,
                "crystal_bonus": 10,
                "message": "ユウとの心が調和し、穏やかな共鳴が生まれました。"
            },
            ResonanceType.GROWTH: {
                "base_xp": 75,
                "crystal_bonus": 15,
                "message": "ユウと共に成長の共鳴を感じています。"
            },
            ResonanceType.BREAKTHROUGH: {
                "base_xp": 100,
                "crystal_bonus": 20,
                "message": "ユウとの強い絆が新たな突破口を開きました。"
            },
            ResonanceType.WISDOM: {
                "base_xp": 125,
                "crystal_bonus": 25,
                "message": "ユウの深い知恵があなたの心に響いています。"
            }
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
        if player_level <= yu_level:
            return False, None
        
        # クールダウンチェック
        if self._is_in_cooldown():
            return False, None
        
        # 共鳴タイプ決定
        resonance_type = self._determine_resonance_type(player_level, yu_level, level_difference)

        return True, resonance_type

    def meets_conditions(self, intensity: float, synergy_count: int, last_event_at: str | None) -> bool:
        threshold = 0.7
        if intensity < threshold:
            return False
        if synergy_count <= 0:
            return False
        if last_event_at:
            try:
                t = datetime.fromisoformat(last_event_at)
                if datetime.now() - t < timedelta(minutes=60):
                    return False
            except Exception:
                pass
        return True
    
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
                return ResonanceType.WISDOM
            elif level_difference >= 10:
                return ResonanceType.BREAKTHROUGH
            else:
                return ResonanceType.GROWTH
        
        # ユウがプレイヤーより高レベルの場合
        else:
            if level_difference >= 15:
                return ResonanceType.WISDOM
            elif level_difference >= 10:
                return ResonanceType.HARMONY
            else:
                return ResonanceType.GROWTH
    
    def _calculate_intensity(self, level_difference: int) -> ResonanceIntensity:
        """共鳴強度計算"""
        if level_difference >= 18:
            return ResonanceIntensity.INTENSE
        elif level_difference >= 12:
            return ResonanceIntensity.STRONG
        elif level_difference >= 8:
            return ResonanceIntensity.MODERATE
        else:
            return ResonanceIntensity.GENTLE
    
    def _get_intensity_multiplier(self, intensity: ResonanceIntensity) -> float:
        """強度倍率取得"""
        multipliers = {
            ResonanceIntensity.GENTLE: 1.0,
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
            ResonanceType.HARMONY: [CrystalAttribute.EMPATHY, CrystalAttribute.RESILIENCE],
            ResonanceType.GROWTH: [CrystalAttribute.CURIOSITY, CrystalAttribute.COURAGE],
            ResonanceType.BREAKTHROUGH: [CrystalAttribute.CREATIVITY, CrystalAttribute.SELF_DISCIPLINE],
            ResonanceType.WISDOM: [CrystalAttribute.WISDOM, CrystalAttribute.COMMUNICATION]
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
            ResonanceType.HARMONY: "調和の証獲得",
            ResonanceType.GROWTH: "成長の印獲得",
            ResonanceType.BREAKTHROUGH: "突破の勲章獲得",
            ResonanceType.WISDOM: "知恵の宝珠獲得"
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
            ResonanceIntensity.GENTLE: "この穏やかな瞬間を大切にしてください。",
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
        if player_level >= 10 and resonance_type == ResonanceType.BREAKTHROUGH:
            return "special_chapter_breakthrough"
        elif player_level >= 20 and resonance_type == ResonanceType.WISDOM:
            return "wisdom_path_unlock"
        
        return None