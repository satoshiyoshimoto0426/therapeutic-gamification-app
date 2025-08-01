"""
?
?
"""
import re
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel, Field
from collections import Counter, defaultdict
import statistics
import logging
import asyncio
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class FeedbackCategory(Enum):
    """?"""
    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request"
    USABILITY = "usability"
    THERAPEUTIC_EFFECT = "therapeutic_effect"
    PERFORMANCE = "performance"
    ACCESSIBILITY = "accessibility"
    CONTENT = "content"
    GENERAL = "general"

class FeedbackPriority(Enum):
    """?"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SentimentType(Enum):
    """?"""
    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"

@dataclass
class ThemeAnalysis:
    """?"""
    theme: str
    frequency: int
    sentiment_score: float
    related_keywords: List[str]
    user_count: int

@dataclass
class SentimentAnalysis:
    """?"""
    overall_score: float
    sentiment_type: SentimentType
    confidence: float
    positive_keywords: List[str]
    negative_keywords: List[str]

class FeedbackItem(BaseModel):
    """?"""
    feedback_id: str = Field(default_factory=lambda: f"fb_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    user_id: str
    category: FeedbackCategory
    title: str
    content: str
    rating: Optional[int] = Field(None, ge=1, le=5)
    priority: FeedbackPriority = FeedbackPriority.MEDIUM
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # ?
    sentiment_analysis: Optional[SentimentAnalysis] = None
    themes: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    
    # ?
    processed: bool = False
    assigned_to: Optional[str] = None
    status: str = "open"  # open, in_progress, resolved, closed
    resolution: Optional[str] = None
    
    # メイン
    device_info: Optional[Dict[str, Any]] = None
    app_version: Optional[str] = None
    user_context: Optional[Dict[str, Any]] = None

class FeedbackAnalysisEngine:
    """?"""
    
    def __init__(self):
        self.feedback_items: List[FeedbackItem] = []
        self.theme_patterns = self._initialize_theme_patterns()
        self.sentiment_keywords = self._initialize_sentiment_keywords()
        self.improvement_templates = self._initialize_improvement_templates()
        
    def _initialize_theme_patterns(self) -> Dict[str, List[str]]:
        """?"""
        return {
            "ui_navigation": [
                r"?", r"メイン", r"?", r"?", r"?",
                r"タスク", r"?", r"リスト", r"?", r"使用"
            ],
            "performance": [
                r"?", r"?", r"?", r"?", r"?", r"?",
                r"?", r"?", r"?", r"?"
            ],
            "therapeutic_effectiveness": [
                r"?", r"?", r"気分", r"モデル", r"や",
                r"?", r"?", r"治療", r"?", r"成"
            ],
            "gamification": [
                r"ゲーム", r"レベル", r"XP", r"?", r"?", r"?",
                r"バリデーション", r"?", r"?", r"?"
            ],
            "accessibility": [
                r"?", r"?", r"文字", r"?", r"コア",
                r"?", r"?", r"アプリ", r"?"
            ],
            "content_quality": [
                r"内部", r"コア", r"ストーリー", r"文字", r"?",
                r"?", r"?", r"理", r"?"
            ],
            "mobile_experience": [
                r"ストーリー", r"モデル", r"タスク", r"ストーリー", r"?",
                r"?", r"レベル", r"?", r"?"
            ],
            "data_privacy": [
                r"プレビュー", r"?", r"デフォルト", r"安全", r"?",
                r"?", r"?", r"共有"
            ]
        }
    
    def _initialize_sentiment_keywords(self) -> Dict[str, List[str]]:
        """?"""
        return {
            "very_positive": [
                "?", "?", "?", "?", "?", "?",
                "?", "?", "?", "?"
            ],
            "positive": [
                "?", "い", "?", "使用", "?", "?",
                "?", "?", "?", "?", "?", "?"
            ],
            "negative": [
                "?", "だ", "?", "?", "使用", "?",
                "?", "エラー", "バリデーション", "?", "?", "?"
            ],
            "very_negative": [
                "?", "?", "使用", "?", "?",
                "?", "?", "?", "ストーリー", "?"
            ]
        }
    
    def _initialize_improvement_templates(self) -> Dict[str, List[str]]:
        """?"""
        return {
            "ui_navigation": [
                "?",
                "メイン",
                "ユーザー",
                "?"
            ],
            "performance": [
                "?",
                "?",
                "メイン",
                "レベル"
            ],
            "therapeutic_effectiveness": [
                "治療",
                "ユーザー",
                "モデル",
                "?"
            ],
            "accessibility": [
                "アプリ",
                "?",
                "?",
                "?"
            ]
        }
    
    async def submit_feedback(self, user_id: str, category: FeedbackCategory,
                            title: str, content: str, rating: Optional[int] = None,
                            device_info: Optional[Dict] = None,
                            app_version: Optional[str] = None) -> FeedbackItem:
        """?"""
        
        feedback = FeedbackItem(
            user_id=user_id,
            category=category,
            title=title,
            content=content,
            rating=rating,
            device_info=device_info,
            app_version=app_version
        )
        
        # 自動
        await self._analyze_feedback(feedback)
        
        # ?
        feedback.priority = self._determine_priority(feedback)
        
        self.feedback_items.append(feedback)
        
        logger.info(f"Feedback submitted: {feedback.feedback_id} by {user_id}")
        return feedback
    
    async def _analyze_feedback(self, feedback: FeedbackItem):
        """?"""
        
        # ?
        feedback.sentiment_analysis = await self._perform_sentiment_analysis(feedback.content)
        
        # ?
        feedback.themes = await self._extract_themes(feedback.content, feedback.category)
        
        # ?
        feedback.keywords = await self._extract_keywords(feedback.content)
        
        feedback.processed = True
        feedback.updated_at = datetime.now()
    
    async def _perform_sentiment_analysis(self, text: str) -> SentimentAnalysis:
        """?"""
        text_lower = text.lower()
        
        # ?
        sentiment_scores = {
            "very_positive": 2,
            "positive": 1,
            "negative": -1,
            "very_negative": -2
        }
        
        total_score = 0
        total_words = 0
        positive_keywords = []
        negative_keywords = []
        
        for sentiment_type, keywords in self.sentiment_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    total_score += sentiment_scores[sentiment_type]
                    total_words += 1
                    
                    if sentiment_scores[sentiment_type] > 0:
                        positive_keywords.append(keyword)
                    else:
                        negative_keywords.append(keyword)
        
        # ?-1か1の
        normalized_score = total_score / max(total_words, 1) if total_words > 0 else 0
        normalized_score = max(-1, min(1, normalized_score))
        
        # ?
        if normalized_score >= 0.6:
            sentiment_type = SentimentType.VERY_POSITIVE
        elif normalized_score >= 0.2:
            sentiment_type = SentimentType.POSITIVE
        elif normalized_score <= -0.6:
            sentiment_type = SentimentType.VERY_NEGATIVE
        elif normalized_score <= -0.2:
            sentiment_type = SentimentType.NEGATIVE
        else:
            sentiment_type = SentimentType.NEUTRAL
        
        # 信頼
        confidence = min(1.0, total_words / 5)  # 5?
        
        return SentimentAnalysis(
            overall_score=normalized_score,
            sentiment_type=sentiment_type,
            confidence=confidence,
            positive_keywords=positive_keywords,
            negative_keywords=negative_keywords
        )
    
    async def _extract_themes(self, text: str, category: FeedbackCategory) -> List[str]:
        """?"""
        text_lower = text.lower()
        detected_themes = []
        
        for theme, patterns in self.theme_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    detected_themes.append(theme)
                    break
        
        # カスタム
        category_themes = {
            FeedbackCategory.BUG_REPORT: ["bug_report"],
            FeedbackCategory.FEATURE_REQUEST: ["feature_request"],
            FeedbackCategory.USABILITY: ["ui_navigation"],
            FeedbackCategory.THERAPEUTIC_EFFECT: ["therapeutic_effectiveness"],
            FeedbackCategory.PERFORMANCE: ["performance"],
            FeedbackCategory.ACCESSIBILITY: ["accessibility"]
        }
        
        if category in category_themes:
            detected_themes.extend(category_themes[category])
        
        return list(set(detected_themes))  # ?
    
    async def _extract_keywords(self, text: str) -> List[str]:
        """?"""
        # ?
        
        # ストーリー
        stop_words = {
            "の", "に", "は", "を", "が", "で", "と", "か", "ま",
            "で", "で", "だ", "で", "ま", "し", "す",
            "こ", "?", "あ", "こ", "?", "あ"
        }
        
        # ?
        words = re.findall(r'[?-ん-?-?a-zA-Z0-9]+', text)
        
        # ?
        keywords = [
            word for word in words
            if len(word) >= 2 and word not in stop_words
        ]
        
        # ?
        word_counts = Counter(keywords)
        return [word for word, count in word_counts.most_common(10)]
    
    def _determine_priority(self, feedback: FeedbackItem) -> FeedbackPriority:
        """?"""
        
        # ?
        critical_keywords = ["?", "?", "使用", "デフォルト", "?"]
        if any(keyword in feedback.content for keyword in critical_keywords):
            return FeedbackPriority.CRITICAL
        
        # ?
        if (feedback.category == FeedbackCategory.BUG_REPORT or
            feedback.rating and feedback.rating <= 2 or
            feedback.sentiment_analysis and feedback.sentiment_analysis.overall_score <= -0.5):
            return FeedbackPriority.HIGH
        
        # ?
        if (feedback.category in [FeedbackCategory.USABILITY, FeedbackCategory.PERFORMANCE] and
            feedback.rating and feedback.rating == 3):
            return FeedbackPriority.MEDIUM
        
        # ?
        if feedback.category == FeedbackCategory.FEATURE_REQUEST:
            return FeedbackPriority.MEDIUM
        
        # ?4?
        if feedback.rating and feedback.rating >= 4:
            return FeedbackPriority.LOW
        
        return FeedbackPriority.MEDIUM  # デフォルト
    
    async def generate_theme_analysis(self, days: int = 30) -> List[ThemeAnalysis]:
        """?"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_feedback = [
            fb for fb in self.feedback_items
            if fb.created_at >= cutoff_date
        ]
        
        # ?
        theme_stats = defaultdict(lambda: {
            "frequency": 0,
            "sentiment_scores": [],
            "keywords": [],
            "users": set()
        })
        
        for feedback in recent_feedback:
            for theme in feedback.themes:
                stats = theme_stats[theme]
                stats["frequency"] += 1
                stats["users"].add(feedback.user_id)
                stats["keywords"].extend(feedback.keywords)
                
                if feedback.sentiment_analysis:
                    stats["sentiment_scores"].append(feedback.sentiment_analysis.overall_score)
        
        # ?
        theme_analyses = []
        for theme, stats in theme_stats.items():
            avg_sentiment = statistics.mean(stats["sentiment_scores"]) if stats["sentiment_scores"] else 0
            
            # ?
            keyword_counts = Counter(stats["keywords"])
            related_keywords = [kw for kw, count in keyword_counts.most_common(5)]
            
            analysis = ThemeAnalysis(
                theme=theme,
                frequency=stats["frequency"],
                sentiment_score=avg_sentiment,
                related_keywords=related_keywords,
                user_count=len(stats["users"])
            )
            theme_analyses.append(analysis)
        
        # ?
        theme_analyses.sort(key=lambda x: x.frequency, reverse=True)
        return theme_analyses
    
    async def generate_improvement_suggestions(self, theme_analyses: List[ThemeAnalysis]) -> List[Dict[str, Any]]:
        """?"""
        suggestions = []
        
        for analysis in theme_analyses[:10]:  # ?10?
            theme = analysis.theme
            
            # 基本
            base_suggestions = self.improvement_templates.get(theme, [
                f"{theme}に"
            ])
            
            # ?
            if analysis.sentiment_score <= -0.5:
                urgency = "?"
                impact = "ユーザー"
            elif analysis.sentiment_score <= -0.2:
                urgency = "?"
                impact = "ユーザー"
            else:
                urgency = "?"
                impact = "?"
            
            # ?
            for suggestion_text in base_suggestions:
                suggestion = {
                    "theme": theme,
                    "suggestion": suggestion_text,
                    "urgency": urgency,
                    "impact": impact,
                    "affected_users": analysis.user_count,
                    "frequency": analysis.frequency,
                    "sentiment_score": analysis.sentiment_score,
                    "related_keywords": analysis.related_keywords,
                    "generated_at": datetime.now().isoformat()
                }
                suggestions.append(suggestion)
        
        return suggestions
    
    def get_feedback_statistics(self, days: int = 30) -> Dict[str, Any]:
        """?"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_feedback = [
            fb for fb in self.feedback_items
            if fb.created_at >= cutoff_date
        ]
        
        if not recent_feedback:
            return {
                "total_feedback": 0,
                "period_days": days,
                "statistics": {}
            }
        
        # 基本
        total_feedback = len(recent_feedback)
        unique_users = len(set(fb.user_id for fb in recent_feedback))
        
        # カスタム
        category_dist = Counter(fb.category.value for fb in recent_feedback)
        
        # ?
        priority_dist = Counter(fb.priority.value for fb in recent_feedback)
        
        # ?
        ratings = [fb.rating for fb in recent_feedback if fb.rating is not None]
        rating_dist = Counter(ratings) if ratings else {}
        avg_rating = statistics.mean(ratings) if ratings else None
        
        # ?
        sentiment_scores = [
            fb.sentiment_analysis.overall_score
            for fb in recent_feedback
            if fb.sentiment_analysis
        ]
        avg_sentiment = statistics.mean(sentiment_scores) if sentiment_scores else None
        
        sentiment_types = [
            fb.sentiment_analysis.sentiment_type.value
            for fb in recent_feedback
            if fb.sentiment_analysis
        ]
        sentiment_dist = Counter(sentiment_types)
        
        # ?
        status_dist = Counter(fb.status for fb in recent_feedback)
        processed_count = len([fb for fb in recent_feedback if fb.processed])
        processing_rate = processed_count / total_feedback if total_feedback > 0 else 0
        
        return {
            "total_feedback": total_feedback,
            "unique_users": unique_users,
            "period_days": days,
            "statistics": {
                "category_distribution": dict(category_dist),
                "priority_distribution": dict(priority_dist),
                "rating_distribution": dict(rating_dist),
                "average_rating": avg_rating,
                "sentiment_distribution": dict(sentiment_dist),
                "average_sentiment": avg_sentiment,
                "status_distribution": dict(status_dist),
                "processing_rate": processing_rate
            }
        }
    
    def get_feedback_by_user(self, user_id: str) -> List[FeedbackItem]:
        """ユーザー"""
        return [fb for fb in self.feedback_items if fb.user_id == user_id]
    
    def get_feedback_by_category(self, category: FeedbackCategory) -> List[FeedbackItem]:
        """カスタム"""
        return [fb for fb in self.feedback_items if fb.category == category]
    
    def get_high_priority_feedback(self) -> List[FeedbackItem]:
        """?"""
        return [
            fb for fb in self.feedback_items
            if fb.priority in [FeedbackPriority.HIGH, FeedbackPriority.CRITICAL]
            and fb.status in ["open", "in_progress"]
        ]
    
    async def update_feedback_status(self, feedback_id: str, status: str,
                                   assigned_to: Optional[str] = None,
                                   resolution: Optional[str] = None) -> Optional[FeedbackItem]:
        """?"""
        for feedback in self.feedback_items:
            if feedback.feedback_id == feedback_id:
                feedback.status = status
                feedback.updated_at = datetime.now()
                
                if assigned_to:
                    feedback.assigned_to = assigned_to
                
                if resolution:
                    feedback.resolution = resolution
                
                logger.info(f"Feedback {feedback_id} status updated to {status}")
                return feedback
        
        return None
    
    def export_feedback_report(self, format: str = "json") -> str:
        """?"""
        
        # ?
        stats = self.get_feedback_statistics()
        
        # ?
        theme_counts = defaultdict(int)
        for feedback in self.feedback_items:
            for theme in feedback.themes:
                theme_counts[theme] += 1
        
        report_data = {
            "generated_at": datetime.now().isoformat(),
            "summary": stats,
            "theme_analysis": dict(theme_counts),
            "high_priority_items": len(self.get_high_priority_feedback()),
            "recent_feedback": [
                {
                    "feedback_id": fb.feedback_id,
                    "category": fb.category.value,
                    "title": fb.title,
                    "rating": fb.rating,
                    "priority": fb.priority.value,
                    "status": fb.status,
                    "created_at": fb.created_at.isoformat(),
                    "sentiment_score": fb.sentiment_analysis.overall_score if fb.sentiment_analysis else None,
                    "themes": fb.themes
                }
                for fb in sorted(self.feedback_items, key=lambda x: x.created_at, reverse=True)[:50]
            ]
        }
        
        if format == "json":
            return json.dumps(report_data, indent=2, ensure_ascii=False)
        else:
            return json.dumps(report_data, indent=2, ensure_ascii=False)

# ?
feedback_engine = FeedbackAnalysisEngine()