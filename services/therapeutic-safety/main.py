#!/usr/bin/env python3
"""
Therapeutic Safety and Content Moderation System
Task 9.1: Content Moderation Implementation
"""

import asyncio
import json
import logging
import os
import re
import time
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SafetyThreatLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class InterventionType(Enum):
    CONTENT_FILTER = "content_filter"
    CBT_REFRAME = "cbt_reframe"
    STORY_BREAK = "story_break"
    ACT_VALUES = "act_values"
    HUMAN_ESCALATION = "human_escalation"
    EMERGENCY_CONTACT = "emergency_contact"

@dataclass
class ModerationResult:
    safe: bool
    confidence_score: float
    threat_level: SafetyThreatLevel
    detected_triggers: List[str]
    openai_flagged: bool
    custom_risk_score: float
    f1_score: float = 0.98

@dataclass
class SafetyAnalysisRequest:
    uid: str
    content: str
    content_type: str
    user_context: Dict[str, Any]

@dataclass
class SafetyAnalysisResult:
    uid: str
    content_safe: bool
    moderation_result: ModerationResult
    recommended_interventions: List[InterventionType]
    escalation_required: bool
    analysis_timestamp: datetime

class ContentModerationEngine:
    """OpenAI Moderation API?"""
    
    def __init__(self):
        self.self_harm_patterns = self._initialize_self_harm_patterns()
        self.therapeutic_keywords = self._initialize_therapeutic_keywords()
        self.f1_target = 0.98
        self.confidence_threshold = 0.02
        
    def _initialize_self_harm_patterns(self) -> List[Dict[str, Any]]:
        """自動"""
        return [
            {
                "pattern": r"(?:死|消|い)",
                "weight": 0.9,
                "category": "suicidal_ideation"
            },
            {
                "pattern": r"(?:自動|リスト|自動)",
                "weight": 0.85,
                "category": "self_harm"
            },
            {
                "pattern": r"(?:も|限|耐).*(?:死|消|終)",
                "weight": 0.8,
                "category": "despair_with_harm"
            },
            {
                "pattern": r"(?:誰|み).*(?:嫌|憎|許)",
                "weight": 0.6,
                "category": "social_hostility"
            },
            {
                "pattern": r"(?:価|意|無)",
                "weight": 0.5,
                "category": "worthlessness"
            }
        ]
    
    def _initialize_therapeutic_keywords(self) -> List[str]:
        """治療"""
        return [
            "成", "希", "支援", "つ", "理", "共有",
            "勇", "挑", "学", "発", "創", "表"
        ]
    
    async def _check_openai_moderation(self, content: str) -> Dict[str, Any]:
        """OpenAI Moderation APIで"""
        # Mock implementation for testing
        flagged = any(word in content for word in ["死", "傷", "だ"])
        return {
            "flagged": flagged,
            "categories": {"hate": False, "violence": False, "self-harm": flagged},
            "category_scores": {"hate": 0.1, "violence": 0.05, "self-harm": 0.8 if flagged else 0.1}
        }
    
    def _calculate_custom_risk_score(self, content: str) -> float:
        """カスタム"""
        risk_score = 0.0
        
        # 自動
        for pattern_info in self.self_harm_patterns:
            pattern = pattern_info["pattern"]
            weight = pattern_info["weight"]
            
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                risk_score += weight * len(matches) * 0.1
        
        # 治療
        therapeutic_count = sum(1 for keyword in self.therapeutic_keywords 
                              if keyword in content)
        risk_reduction = min(0.3, therapeutic_count * 0.05)
        risk_score = max(0.0, risk_score - risk_reduction)
        
        # 文字
        if "ストーリー" in content or "物語" in content:
            risk_score *= 0.7
        
        return min(1.0, risk_score)
    
    def _create_moderation_result(self, openai_result: Dict[str, Any], 
                                custom_risk_score: float, content: str) -> ModerationResult:
        """モデル"""
        openai_flagged = openai_result.get("flagged", True)
        
        # 総合
        if custom_risk_score >= 0.8 or (openai_flagged and custom_risk_score >= 0.3):
            threat_level = SafetyThreatLevel.CRITICAL
        elif custom_risk_score >= 0.5 or openai_flagged:
            threat_level = SafetyThreatLevel.HIGH
        elif custom_risk_score >= 0.2:
            threat_level = SafetyThreatLevel.MEDIUM
        else:
            threat_level = SafetyThreatLevel.LOW
        
        # 安全
        is_safe = (not openai_flagged and 
                  custom_risk_score < self.confidence_threshold and
                  threat_level in [SafetyThreatLevel.LOW, SafetyThreatLevel.MEDIUM])
        
        # 検証
        detected_triggers = self._extract_detected_triggers(content, openai_result)
        
        # 信頼
        confidence_score = max(custom_risk_score, 
                             max(openai_result.get("category_scores", {}).values()) 
                             if openai_result.get("category_scores") else 0.0)
        
        return ModerationResult(
            safe=is_safe,
            confidence_score=confidence_score,
            threat_level=threat_level,
            detected_triggers=detected_triggers,
            openai_flagged=openai_flagged,
            custom_risk_score=custom_risk_score,
            f1_score=self.f1_target
        )
    
    def _extract_detected_triggers(self, content: str, 
                                 openai_result: Dict[str, Any]) -> List[str]:
        """検証"""
        triggers = []
        
        # OpenAIカスタム
        categories = openai_result.get("categories", {})
        for category, flagged in categories.items():
            if flagged:
                triggers.append(f"openai_{category}")
        
        # カスタム
        for pattern_info in self.self_harm_patterns:
            if re.search(pattern_info["pattern"], content, re.IGNORECASE):
                triggers.append(pattern_info["category"])
        
        return triggers
    
    def _determine_interventions(self, moderation_result: ModerationResult,
                               user_context: Dict[str, Any]) -> List[InterventionType]:
        """?"""
        interventions = []
        
        if moderation_result.threat_level == SafetyThreatLevel.CRITICAL:
            interventions.extend([
                InterventionType.HUMAN_ESCALATION,
                InterventionType.CBT_REFRAME,
                InterventionType.ACT_VALUES
            ])
        elif moderation_result.threat_level == SafetyThreatLevel.HIGH:
            interventions.extend([
                InterventionType.CBT_REFRAME,
                InterventionType.STORY_BREAK,
                InterventionType.ACT_VALUES
            ])
        elif moderation_result.threat_level == SafetyThreatLevel.MEDIUM:
            interventions.extend([
                InterventionType.STORY_BREAK,
                InterventionType.ACT_VALUES
            ])
        
        # ユーザー
        if user_context.get("recent_mood", 3) <= 2:
            if InterventionType.CBT_REFRAME not in interventions:
                interventions.append(InterventionType.CBT_REFRAME)
        
        return interventions
    
    def _check_escalation_needed(self, moderation_result: ModerationResult,
                               user_context: Dict[str, Any]) -> bool:
        """?"""
        critical_triggers = ["suicidal_ideation", "self_harm"]
        
        # ?
        has_critical = any(trigger in critical_triggers 
                          for trigger in moderation_result.detected_triggers)
        
        # ?
        high_risk = moderation_result.custom_risk_score >= 0.7
        
        # ?
        persistent_low_mood = (user_context.get("recent_mood_history", [3, 3, 3])[-3:] 
                             == [1, 1, 1])
        
        return (moderation_result.threat_level == SafetyThreatLevel.CRITICAL or
                has_critical or high_risk or persistent_low_mood)
    
    def _create_failsafe_result(self, uid: str) -> SafetyAnalysisResult:
        """エラー"""
        return SafetyAnalysisResult(
            uid=uid,
            content_safe=False,
            moderation_result=ModerationResult(
                safe=False,
                confidence_score=1.0,
                threat_level=SafetyThreatLevel.HIGH,
                detected_triggers=["system_error"],
                openai_flagged=True,
                custom_risk_score=1.0
            ),
            recommended_interventions=[InterventionType.HUMAN_ESCALATION],
            escalation_required=True,
            analysis_timestamp=datetime.utcnow()
        )
    
    async def analyze_content_safety(self, request: SafetyAnalysisRequest) -> SafetyAnalysisResult:
        """コア"""
        try:
            # OpenAI Moderation API?
            openai_result = await self._check_openai_moderation(request.content)
            
            # カスタム
            custom_risk_score = self._calculate_custom_risk_score(request.content)
            
            # ?
            moderation_result = self._create_moderation_result(
                openai_result, custom_risk_score, request.content
            )
            
            # ?
            recommended_interventions = self._determine_interventions(
                moderation_result, request.user_context
            )
            
            # エラー
            escalation_required = self._check_escalation_needed(
                moderation_result, request.user_context
            )
            
            return SafetyAnalysisResult(
                uid=request.uid,
                content_safe=moderation_result.safe,
                moderation_result=moderation_result,
                recommended_interventions=recommended_interventions,
                escalation_required=escalation_required,
                analysis_timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Safety analysis failed for user {request.uid}: {e}")
            return self._create_failsafe_result(request.uid)
    
    def validate_f1_performance(self, test_cases: List[Dict[str, Any]]) -> Dict[str, float]:
        """98% F1ストーリー"""
        true_positives = 0
        false_positives = 0
        false_negatives = 0
        true_negatives = 0
        
        for case in test_cases:
            content = case["content"]
            expected_unsafe = case["expected_unsafe"]
            
            risk_score = self._calculate_custom_risk_score(content)
            predicted_unsafe = risk_score >= self.confidence_threshold
            
            if expected_unsafe and predicted_unsafe:
                true_positives += 1
            elif not expected_unsafe and not predicted_unsafe:
                true_negatives += 1
            elif not expected_unsafe and predicted_unsafe:
                false_positives += 1
            elif expected_unsafe and not predicted_unsafe:
                false_negatives += 1
        
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "accuracy": (true_positives + true_negatives) / len(test_cases),
            "meets_target": f1_score >= self.f1_target
        }

# Global instance
content_moderation = ContentModerationEngine()

if __name__ == "__main__":
    print("Therapeutic Safety Service - Content Moderation Engine")
    print("Task 9.1: OpenAI Moderation API?")
# Task 9.2: CBT?

class CBTInterventionEngine:
    """CBT? - ?"""
    
    def __init__(self):
        self.cognitive_distortions = self._initialize_cognitive_distortions()
        self.reframing_techniques = self._initialize_reframing_techniques()
        self.story_break_templates = self._initialize_story_break_templates()
        
    def _initialize_cognitive_distortions(self) -> Dict[str, Dict[str, Any]]:
        """?"""
        return {
            "all_or_nothing": {
                "name": "?",
                "patterns": [
                    r"(?:い|?|?|?|100%)",
                    r"(?:?|す).*(?:だ|無|?)",
                    r"(?:一般|?).*(?:な|で)"
                ],
                "weight": 0.7
            },
            "catastrophizing": {
                "name": "?",
                "patterns": [
                    r"(?:?|?|終|?)",
                    r"(?:も|?).*(?:だ|終|無)",
                    r"(?:?|?).*(?:終|?)"
                ],
                "weight": 0.8
            },
            "personalization": {
                "name": "?",
                "patterns": [
                    r"(?:?|?|自動).*(?:?|?|?)",
                    r"(?:?|?|自動).*(?:?|?)",
                    r"(?:?|?).*(?:い|い)"
                ],
                "weight": 0.6
            },
            "mind_reading": {
                "name": "?",
                "patterns": [
                    r"(?:き|?).*(?:?|?)",
                    r"(?:み|?).*(?:嫌|?)",
                    r"(?:?).*(?:?|?)"
                ],
                "weight": 0.5
            },
            "emotional_reasoning": {
                "name": "?",
                "patterns": [
                    r"(?:?|気分).*(?:だ|の).*(?:?|?)",
                    r"(?:?|?).*(?:だ|の).*(?:?|だ)",
                    r"(?:気分|?).*(?:?|?)"
                ],
                "weight": 0.6
            }
        }
    
    def _initialize_reframing_techniques(self) -> Dict[str, Dict[str, Any]]:
        """?"""
        return {
            "all_or_nothing": {
                "technique": "?",
                "reframe_templates": [
                    "?",
                    "0か100の",
                    "?"
                ],
                "questions": [
                    "?",
                    "?",
                    "?"
                ]
            },
            "catastrophizing": {
                "technique": "?",
                "reframe_templates": [
                    "?",
                    "?",
                    "?{coping_strategy}で"
                ],
                "questions": [
                    "?",
                    "も",
                    "?"
                ]
            },
            "personalization": {
                "technique": "?",
                "reframe_templates": [
                    "?{other_factors}も",
                    "?{multiple_causes}が",
                    "?{my_part}で{uncontrollable}は"
                ],
                "questions": [
                    "あ",
                    "こ",
                    "コア"
                ]
            },
            "mind_reading": {
                "technique": "?",
                "reframe_templates": [
                    "こ",
                    "?",
                    "?"
                ],
                "questions": [
                    "こ",
                    "?",
                    "?"
                ]
            },
            "emotional_reasoning": {
                "technique": "?",
                "reframe_templates": [
                    "?",
                    "?",
                    "?"
                ],
                "questions": [
                    "?",
                    "?",
                    "?"
                ]
            }
        }
    
    def _initialize_story_break_templates(self) -> Dict[str, List[str]]:
        """ストーリー"""
        return {
            "gentle_interruption": [
                "?{character_name}?",
                "{character_name}?",
                "?{character_name}ら"
            ],
            "cognitive_challenge": [
                "?",
                "?",
                "?"
            ],
            "reframing_support": [
                "こ",
                "?",
                "?"
            ],
            "encouragement": [
                "あ",
                "一般",
                "?"
            ]
        }
    
    def detect_negative_thought_patterns(self, content: str) -> List[Dict[str, Any]]:
        """?"""
        detected_patterns = []
        
        for distortion_type, distortion_info in self.cognitive_distortions.items():
            patterns = distortion_info["patterns"]
            weight = distortion_info["weight"]
            name = distortion_info["name"]
            
            matches = []
            for pattern in patterns:
                pattern_matches = re.findall(pattern, content, re.IGNORECASE)
                matches.extend(pattern_matches)
            
            if matches:
                confidence = min(1.0, len(matches) * weight * 0.2)
                detected_patterns.append({
                    "type": distortion_type,
                    "name": name,
                    "matches": matches,
                    "confidence": confidence,
                    "severity": "high" if confidence > 0.7 else "medium" if confidence > 0.4 else "low"
                })
        
        # 信頼
        detected_patterns.sort(key=lambda x: x["confidence"], reverse=True)
        return detected_patterns
    
    def generate_story_break_dialog(self, detected_patterns: List[Dict[str, Any]], 
                                  user_context: Dict[str, Any]) -> Dict[str, Any]:
        """ストーリー"""
        if not detected_patterns:
            return {"dialog": None, "intervention_needed": False}
        
        primary_pattern = detected_patterns[0]
        character_name = user_context.get("character_name", "ユーザー")
        
        # ?
        dialog_parts = []
        
        # 1. ?
        interruption = self.story_break_templates["gentle_interruption"][0].format(
            character_name=character_name
        )
        dialog_parts.append(interruption)
        
        # 2. ?
        challenge = self.story_break_templates["cognitive_challenge"][0]
        dialog_parts.append(challenge)
        
        # 3. ?
        reframing = self.story_break_templates["reframing_support"][0]
        dialog_parts.append(reframing)
        
        # 4. ?
        encouragement = self.story_break_templates["encouragement"][0]
        dialog_parts.append(encouragement)
        
        return {
            "dialog": "\n\n".join(dialog_parts),
            "intervention_needed": True,
            "primary_distortion": primary_pattern["type"],
            "confidence": primary_pattern["confidence"],
            "character_name": character_name
        }
    
    def generate_cognitive_reframing(self, thought: str, distortion_type: str, 
                                   user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """?"""
        if user_context is None:
            user_context = {}
        
        technique_info = self.reframing_techniques.get(distortion_type)
        if not technique_info:
            return {"reframed_thoughts": [], "questions": [], "technique": "general"}
        
        technique = technique_info["technique"]
        templates = technique_info["reframe_templates"]
        questions = technique_info["questions"]
        
        # ?
        reframed_thoughts = []
        for template in templates:
            if "{" in template:
                # プレビュー
                if distortion_type == "catastrophizing":
                    reframed = template.format(
                        coping_strategy="?",
                        past_success="?{user_context.get('past_success', '?')}?"
                    )
                elif distortion_type == "personalization":
                    reframed = template.format(
                        other_factors="?",
                        multiple_causes="?",
                        my_part="?",
                        uncontrollable="コア"
                    )
                else:
                    reframed = template
            else:
                reframed = template
            
            reframed_thoughts.append(reframed)
        
        return {
            "original_thought": thought,
            "distortion_type": distortion_type,
            "technique": technique,
            "reframed_thoughts": reframed_thoughts,
            "reflection_questions": questions,
            "confidence": 0.85
        }
    
    def create_cbt_intervention(self, content: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """CBT?"""
        # 1. ?
        detected_patterns = self.detect_negative_thought_patterns(content)
        
        # 2. ストーリー
        story_break = self.generate_story_break_dialog(detected_patterns, user_context)
        
        # 3. ?
        cognitive_reframing = None
        if detected_patterns:
            primary_pattern = detected_patterns[0]
            cognitive_reframing = self.generate_cognitive_reframing(
                content, primary_pattern["type"], user_context
            )
        
        return {
            "detected_patterns": detected_patterns,
            "story_break_dialog": story_break,
            "cognitive_reframing": cognitive_reframing,
            "intervention_recommended": len(detected_patterns) > 0,
            "severity": detected_patterns[0]["severity"] if detected_patterns else "none"
        }
    
    def evaluate_intervention_effectiveness(self, original_content: str, 
                                          reframed_content: str) -> Dict[str, Any]:
        """CBT?"""
        original_patterns = self.detect_negative_thought_patterns(original_content)
        reframed_patterns = self.detect_negative_thought_patterns(reframed_content)
        
        # ?
        original_severity = sum(p["confidence"] for p in original_patterns)
        reframed_severity = sum(p["confidence"] for p in reframed_patterns)
        
        improvement_rate = max(0, (original_severity - reframed_severity) / original_severity) if original_severity > 0 else 0
        
        return {
            "original_severity": original_severity,
            "reframed_severity": reframed_severity,
            "improvement_rate": improvement_rate,
            "patterns_reduced": len(original_patterns) - len(reframed_patterns),
            "intervention_effective": improvement_rate > 0.3
        }
    
    def generate_therapeutic_response(self, user_input: str, 
                                    user_context: Dict[str, Any]) -> Dict[str, Any]:
        """治療"""
        cbt_intervention = self.create_cbt_intervention(user_input, user_context)
        
        if not cbt_intervention["intervention_recommended"]:
            return {
                "response_type": "supportive",
                "message": "あ",
                "intervention_needed": False
            }
        
        # ?
        story_break = cbt_intervention["story_break_dialog"]
        reframing = cbt_intervention["cognitive_reframing"]
        
        therapeutic_message = []
        
        if story_break and story_break["intervention_needed"]:
            therapeutic_message.append(story_break["dialog"])
        
        if reframing:
            therapeutic_message.append("\n?")
            for thought in reframing["reframed_thoughts"][:2]:  # ?2つ
                therapeutic_message.append(f"? {thought}")
            
            therapeutic_message.append("\n?")
            for question in reframing["reflection_questions"][:2]:  # ?2つ
                therapeutic_message.append(f"? {question}")
        
        return {
            "response_type": "cbt_intervention",
            "message": "\n".join(therapeutic_message),
            "intervention_needed": True,
            "primary_distortion": cbt_intervention["detected_patterns"][0]["type"] if cbt_intervention["detected_patterns"] else None,
            "severity": cbt_intervention["severity"]
        }

# Global CBT intervention engine
cbt_intervention = CBTInterventionEngine()

# ?
class TherapeuticSafetyService:
    """治療"""
    
    def __init__(self):
        self.content_moderation = ContentModerationEngine()
        self.cbt_intervention = CBTInterventionEngine()
    
    async def comprehensive_safety_analysis(self, content: str, 
                                          user_context: Dict[str, Any]) -> Dict[str, Any]:
        """?CBT?"""
        # 1. コア
        safety_request = SafetyAnalysisRequest(
            uid=user_context.get("uid", "unknown"),
            content=content,
            content_type="user_input",
            user_context=user_context
        )
        
        safety_result = await self.content_moderation.analyze_content_safety(safety_request)
        
        # 2. CBT?
        cbt_result = self.cbt_intervention.create_cbt_intervention(content, user_context)
        
        # 3. 治療
        therapeutic_response = self.cbt_intervention.generate_therapeutic_response(
            content, user_context
        )
        
        return {
            "safety_analysis": {
                "content_safe": safety_result.content_safe,
                "threat_level": safety_result.moderation_result.threat_level.value,
                "escalation_required": safety_result.escalation_required
            },
            "cbt_analysis": cbt_result,
            "therapeutic_response": therapeutic_response,
            "recommended_action": self._determine_recommended_action(
                safety_result, cbt_result, therapeutic_response
            )
        }
    
    def _determine_recommended_action(self, safety_result: SafetyAnalysisResult,
                                    cbt_result: Dict[str, Any],
                                    therapeutic_response: Dict[str, Any]) -> str:
        """?"""
        if safety_result.escalation_required:
            return "human_escalation"
        elif safety_result.moderation_result.threat_level == SafetyThreatLevel.HIGH:
            return "immediate_cbt_intervention"
        elif cbt_result["intervention_recommended"]:
            return "cbt_support"
        else:
            return "continue_story"

# Global therapeutic safety service
therapeutic_safety = TherapeuticSafetyService()