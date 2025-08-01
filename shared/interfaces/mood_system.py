"""
Mood System Interface

気分追跡システムのインターフェース定義
Requirements: 5.4
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta, date
from enum import Enum
from pydantic import BaseModel, Field
import uuid


class MoodLevel(int, Enum):
    """気分レベル（1-5スケール）"""
    VERY_LOW = 1      # とても低い
    LOW = 2           # 低い
    NEUTRAL = 3       # 普通
    HIGH = 4          # 高い
    VERY_HIGH = 5     # とても高い


class MoodCategory(str, Enum):
    """気分カテゴリ"""
    ENERGY = "energy"           # エネルギー
    MOTIVATION = "motivation"   # やる気
    FOCUS = "focus"            # 集中力
    ANXIETY = "anxiety"        # 不安
    STRESS = "stress"          # ストレス
    SATISFACTION = "satisfaction" # 満足感


class MoodTrigger(str, Enum):
    """気分トリガー"""
    TASK_COMPLETION = "task_completion"     # タスク完了
    SOCIAL_INTERACTION = "social_interaction" # 社会的交流
    PHYSICAL_ACTIVITY = "physical_activity"   # 身体活動
    REST = "rest"                           # 休息
    CREATIVE_WORK = "creative_work"         # 創作活動
    LEARNING = "learning"                   # 学習
    REFLECTION = "reflection"               # 振り返り


class MoodTrend(str, Enum):
    """気分トレンド"""
    IMPROVING = "improving"     # 改善中
    STABLE = "stable"          # 安定
    DECLINING = "declining"    # 悪化中
    FLUCTUATING = "fluctuating" # 変動中


class MoodEntry(BaseModel):
    """気分エントリ"""
    entry_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    uid: str
    log_date: datetime = Field(default_factory=datetime.utcnow)
    mood_score: MoodLevel
    category_scores: Dict[MoodCategory, MoodLevel] = {}
    notes: str = ""
    context_tags: List[str] = []
    triggers: List[MoodTrigger] = []
    calculated_coefficient: float = 0.0
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.calculated_coefficient == 0.0:
            self.calculated_coefficient = self._calculate_coefficient()
    
    def _calculate_coefficient(self) -> float:
        """XP係数計算（0.8-1.2の範囲）"""
        # 基本係数: 1-5 -> 0.8-1.2
        base_coefficient = 0.8 + (self.mood_score.value - 1) * 0.1
        
        # カテゴリ別調整
        if self.category_scores:
            category_avg = sum(score.value for score in self.category_scores.values()) / len(self.category_scores)
            category_adjustment = (category_avg - 3) * 0.05  # -0.1 to +0.1
            base_coefficient += category_adjustment
        
        # 0.8-1.2の範囲に制限
        return max(0.8, min(1.2, base_coefficient))


class MoodAnalysis(BaseModel):
    """気分分析結果"""
    uid: str
    analysis_period: int  # 日数
    average_mood: float
    mood_trend: MoodTrend
    trend_strength: float  # 0.0-1.0
    stability_score: float  # 0.0-1.0
    improvement_rate: float  # 日あたりの改善率
    category_analysis: Dict[MoodCategory, Dict[str, float]] = {}
    trigger_effectiveness: Dict[MoodTrigger, float] = {}
    recommendations: List[str] = []


class MoodInsight(BaseModel):
    """気分インサイト"""
    insight_type: str
    title: str
    description: str
    confidence: float  # 0.0-1.0
    actionable_suggestions: List[str] = []
    related_data: Dict[str, Any] = {}


class MoodTrackingSystem:
    """気分追跡システム"""
    
    def __init__(self):
        # 実際の実装ではFirestoreを使用
        self.mood_entries: Dict[str, List[MoodEntry]] = {}  # uid -> entries
        self.mood_cache: Dict[str, Dict[str, float]] = {}   # uid -> date -> coefficient
    
    def log_mood(
        self,
        uid: str,
        mood_score: MoodLevel,
        category_scores: Optional[Dict[MoodCategory, MoodLevel]] = None,
        notes: str = "",
        context_tags: List[str] = None,
        triggers: List[MoodTrigger] = None
    ) -> MoodEntry:
        """気分ログ記録"""
        try:
            entry = MoodEntry(
                uid=uid,
                mood_score=mood_score,
                category_scores=category_scores or {},
                notes=notes,
                context_tags=context_tags or [],
                triggers=triggers or []
            )
            
            # ストレージに保存
            if uid not in self.mood_entries:
                self.mood_entries[uid] = []
            
            self.mood_entries[uid].append(entry)
            
            # キャッシュ更新
            self._update_coefficient_cache(uid, entry)
            
            return entry
            
        except Exception as e:
            raise ValueError(f"Failed to log mood: {str(e)}")
    
    def get_mood_coefficient(self, uid: str, target_date: Optional[date] = None) -> float:
        """指定日の気分係数取得"""
        if target_date is None:
            target_date = date.today()
        
        date_str = target_date.isoformat()
        
        # キャッシュから取得
        if uid in self.mood_cache and date_str in self.mood_cache[uid]:
            return self.mood_cache[uid][date_str]
        
        # 当日のエントリを検索
        if uid in self.mood_entries:
            today_entries = [
                entry for entry in self.mood_entries[uid]
                if entry.log_date.date() == target_date
            ]
            
            if today_entries:
                # 最新のエントリを使用
                latest_entry = max(today_entries, key=lambda e: e.log_date)
                return latest_entry.calculated_coefficient
        
        # デフォルト係数（普通の気分）
        return 1.0
    
    def get_mood_history(
        self,
        uid: str,
        days: int = 30
    ) -> List[MoodEntry]:
        """気分履歴取得"""
        if uid not in self.mood_entries:
            return []
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        return [
            entry for entry in self.mood_entries[uid]
            if entry.log_date >= cutoff_date
        ]
    
    def analyze_mood_trends(
        self,
        uid: str,
        days: int = 30
    ) -> MoodAnalysis:
        """気分トレンド分析"""
        history = self.get_mood_history(uid, days)
        
        if not history:
            return MoodAnalysis(
                uid=uid,
                analysis_period=days,
                average_mood=3.0,
                mood_trend=MoodTrend.STABLE,
                trend_strength=0.0,
                stability_score=1.0,
                improvement_rate=0.0
            )
        
        # 基本統計
        mood_scores = [entry.mood_score.value for entry in history]
        average_mood = sum(mood_scores) / len(mood_scores)
        
        # トレンド計算
        trend, trend_strength = self._calculate_trend(mood_scores)
        
        # 安定性スコア計算
        stability_score = self._calculate_stability(mood_scores)
        
        # 改善率計算
        improvement_rate = self._calculate_improvement_rate(mood_scores, days)
        
        # カテゴリ別分析
        category_analysis = self._analyze_categories(history)
        
        # トリガー効果分析
        trigger_effectiveness = self._analyze_triggers(history)
        
        # 推奨事項生成
        recommendations = self._generate_recommendations(
            average_mood, trend, category_analysis, trigger_effectiveness
        )
        
        return MoodAnalysis(
            uid=uid,
            analysis_period=days,
            average_mood=average_mood,
            mood_trend=trend,
            trend_strength=trend_strength,
            stability_score=stability_score,
            improvement_rate=improvement_rate,
            category_analysis=category_analysis,
            trigger_effectiveness=trigger_effectiveness,
            recommendations=recommendations
        )
    
    def generate_mood_insights(
        self,
        uid: str,
        days: int = 30
    ) -> List[MoodInsight]:
        """気分インサイト生成"""
        analysis = self.analyze_mood_trends(uid, days)
        insights = []
        
        # トレンドインサイト
        if analysis.trend_strength > 0.6:
            if analysis.mood_trend == MoodTrend.IMPROVING:
                insights.append(MoodInsight(
                    insight_type="trend_positive",
                    title="気分が改善傾向にあります",
                    description=f"過去{days}日間で気分が着実に改善しています。",
                    confidence=analysis.trend_strength,
                    actionable_suggestions=[
                        "現在の良い習慣を継続しましょう",
                        "改善要因を振り返って記録しておきましょう"
                    ]
                ))
            elif analysis.mood_trend == MoodTrend.DECLINING:
                insights.append(MoodInsight(
                    insight_type="trend_negative",
                    title="気分の低下が見られます",
                    description=f"過去{days}日間で気分の低下傾向があります。",
                    confidence=analysis.trend_strength,
                    actionable_suggestions=[
                        "ストレス要因を特定してみましょう",
                        "リラックスできる活動を増やしてみましょう",
                        "必要に応じて専門家に相談することを検討してください"
                    ]
                ))
        
        # 安定性インサイト
        if analysis.stability_score < 0.4:
            insights.append(MoodInsight(
                insight_type="stability_low",
                title="気分の変動が大きいようです",
                description="気分の波が大きく、安定性が低い状態です。",
                confidence=1.0 - analysis.stability_score,
                actionable_suggestions=[
                    "規則正しい生活リズムを心がけましょう",
                    "気分の変動要因を記録してパターンを見つけましょう",
                    "ストレス管理技術を学んでみましょう"
                ]
            ))
        
        # トリガー効果インサイト
        best_trigger = max(analysis.trigger_effectiveness.items(), 
                          key=lambda x: x[1], default=(None, 0))
        
        if best_trigger[0] and best_trigger[1] > 0.3:
            insights.append(MoodInsight(
                insight_type="trigger_effective",
                title=f"{best_trigger[0].value}が気分改善に効果的です",
                description=f"この活動が気分向上に最も効果的であることが分かりました。",
                confidence=best_trigger[1],
                actionable_suggestions=[
                    f"{best_trigger[0].value}の頻度を増やしてみましょう",
                    "効果的な活動を定期的にスケジュールに組み込みましょう"
                ]
            ))
        
        return insights
    
    # プライベートメソッド
    
    def _update_coefficient_cache(self, uid: str, entry: MoodEntry):
        """係数キャッシュ更新"""
        if uid not in self.mood_cache:
            self.mood_cache[uid] = {}
        
        date_str = entry.log_date.date().isoformat()
        self.mood_cache[uid][date_str] = entry.calculated_coefficient
    
    def _calculate_trend(self, mood_scores: List[int]) -> Tuple[MoodTrend, float]:
        """トレンド計算"""
        if len(mood_scores) < 3:
            return MoodTrend.STABLE, 0.0
        
        # 線形回帰による傾き計算
        n = len(mood_scores)
        x_mean = (n - 1) / 2
        y_mean = sum(mood_scores) / n
        
        numerator = sum((i - x_mean) * (score - y_mean) for i, score in enumerate(mood_scores))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return MoodTrend.STABLE, 0.0
        
        slope = numerator / denominator
        
        # トレンド判定
        if abs(slope) < 0.05:
            return MoodTrend.STABLE, abs(slope) / 0.05
        elif slope > 0:
            return MoodTrend.IMPROVING, min(1.0, abs(slope) / 0.2)
        else:
            return MoodTrend.DECLINING, min(1.0, abs(slope) / 0.2)
    
    def _calculate_stability(self, mood_scores: List[int]) -> float:
        """安定性スコア計算"""
        if len(mood_scores) < 2:
            return 1.0
        
        # 標準偏差ベースの安定性
        mean_score = sum(mood_scores) / len(mood_scores)
        variance = sum((score - mean_score) ** 2 for score in mood_scores) / len(mood_scores)
        std_dev = variance ** 0.5
        
        # 0-1スケールに正規化（標準偏差が大きいほど安定性が低い）
        return max(0.0, 1.0 - (std_dev / 2.0))
    
    def _calculate_improvement_rate(self, mood_scores: List[int], days: int) -> float:
        """改善率計算"""
        if len(mood_scores) < 2:
            return 0.0
        
        first_half = mood_scores[:len(mood_scores)//2]
        second_half = mood_scores[len(mood_scores)//2:]
        
        if not first_half or not second_half:
            return 0.0
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        return (second_avg - first_avg) / days
    
    def _analyze_categories(self, history: List[MoodEntry]) -> Dict[MoodCategory, Dict[str, float]]:
        """カテゴリ別分析"""
        category_data = {}
        
        for category in MoodCategory:
            scores = []
            for entry in history:
                if category in entry.category_scores:
                    scores.append(entry.category_scores[category].value)
            
            if scores:
                category_data[category] = {
                    "average": sum(scores) / len(scores),
                    "trend": self._calculate_trend(scores)[1],
                    "stability": self._calculate_stability(scores)
                }
        
        return category_data
    
    def _analyze_triggers(self, history: List[MoodEntry]) -> Dict[MoodTrigger, float]:
        """トリガー効果分析"""
        trigger_effects = {}
        
        for trigger in MoodTrigger:
            with_trigger = []
            without_trigger = []
            
            for entry in history:
                if trigger in entry.triggers:
                    with_trigger.append(entry.mood_score.value)
                else:
                    without_trigger.append(entry.mood_score.value)
            
            if with_trigger and without_trigger:
                avg_with = sum(with_trigger) / len(with_trigger)
                avg_without = sum(without_trigger) / len(without_trigger)
                effect = (avg_with - avg_without) / 4.0  # 0-1スケールに正規化
                trigger_effects[trigger] = max(0.0, effect)
        
        return trigger_effects
    
    def _generate_recommendations(
        self,
        average_mood: float,
        trend: MoodTrend,
        category_analysis: Dict[MoodCategory, Dict[str, float]],
        trigger_effectiveness: Dict[MoodTrigger, float]
    ) -> List[str]:
        """推奨事項生成"""
        recommendations = []
        
        # 平均気分に基づく推奨
        if average_mood < 2.5:
            recommendations.append("気分が低めです。セルフケアを重視しましょう。")
        elif average_mood > 4.0:
            recommendations.append("良い気分を維持できています。現在の習慣を継続しましょう。")
        
        # トレンドに基づく推奨
        if trend == MoodTrend.DECLINING:
            recommendations.append("気分の低下が見られます。ストレス要因を見直してみましょう。")
        elif trend == MoodTrend.IMPROVING:
            recommendations.append("気分が改善しています。良い変化を続けましょう。")
        
        # 効果的なトリガーの推奨
        if trigger_effectiveness:
            best_trigger = max(trigger_effectiveness.items(), key=lambda x: x[1])
            if best_trigger[1] > 0.2:
                recommendations.append(f"{best_trigger[0].value}が効果的です。頻度を増やしてみましょう。")
        
        return recommendations


# グローバルインスタンス
mood_tracking_system = MoodTrackingSystem()