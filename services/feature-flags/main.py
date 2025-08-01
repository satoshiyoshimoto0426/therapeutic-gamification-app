"""
Feature Flag Service - A/B?Kill-Switch基本

?
- LaunchDarkly?A/B TestとKill-Switchを
- 治療
- リスト
"""

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
from enum import Enum
import logging
import uuid
import json
import hashlib

# 共有
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../shared'))

app = FastAPI(title="Feature Flag Service", version="1.0.0")
logger = logging.getLogger(__name__)

class FlagType(Enum):
    BOOLEAN = "boolean"           # ON/OFF?
    STRING = "string"             # 文字
    NUMBER = "number"             # ?
    JSON = "json"                 # JSON設定
    PERCENTAGE = "percentage"     # ?

class TargetingRule(BaseModel):
    rule_id: str
    name: str
    conditions: List[Dict[str, Any]]  # ユーザー
    percentage: float  # 0.0-1.0
    value: Any  # ?
    priority: int  # ?

class FeatureFlag(BaseModel):
    flag_key: str
    name: str
    description: str
    flag_type: FlagType
    default_value: Any
    enabled: bool
    targeting_rules: List[TargetingRule]
    kill_switch_active: bool = False
    created_at: datetime
    updated_at: datetime
    tags: List[str] = []
    therapeutic_safety_level: str = "low"  # low, medium, high, critical

class UserContext(BaseModel):
    user_id: str
    attributes: Dict[str, Any]  # age, adhd_level, therapeutic_state, etc.
    session_id: Optional[str] = None
    timestamp: datetime = datetime.now()

class FlagEvaluation(BaseModel):
    flag_key: str
    value: Any
    variation_id: Optional[str] = None
    reason: str
    rule_matched: Optional[str] = None
    user_id: str
    timestamp: datetime

class ABTestConfig(BaseModel):
    test_id: str
    name: str
    description: str
    flag_key: str
    variations: List[Dict[str, Any]]  # [{"id": "control", "value": false}, {"id": "treatment", "value": true}]
    traffic_allocation: Dict[str, float]  # {"control": 0.5, "treatment": 0.5}
    targeting_rules: List[TargetingRule]
    start_date: datetime
    end_date: Optional[datetime] = None
    therapeutic_safety_check: bool = True

class FeatureFlagEngine:
    def __init__(self):
        self.flags = {}  # 実装Redis/Firestoreを
        self.ab_tests = {}
        self.evaluations_log = []  # ?
        self.kill_switches = {}  # ?
        
        # 治療
        self.safety_thresholds = {
            "critical": {"max_rollout_per_hour": 0.01, "require_approval": True},
            "high": {"max_rollout_per_hour": 0.05, "require_approval": True},
            "medium": {"max_rollout_per_hour": 0.20, "require_approval": False},
            "low": {"max_rollout_per_hour": 1.0, "require_approval": False}
        }
        
        self._initialize_default_flags()
    
    def _initialize_default_flags(self):
        """デフォルト"""
        default_flags = [
            # Daily Trio?
            FeatureFlag(
                flag_key="daily_trio_enabled",
                name="Daily Trio?",
                description="1?3つ",
                flag_type=FlagType.BOOLEAN,
                default_value=True,
                enabled=True,
                targeting_rules=[],
                therapeutic_safety_level="medium",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                tags=["core_feature", "adhd_support"]
            ),
            
            # Self-Efficacy Gauge?
            FeatureFlag(
                flag_key="self_efficacy_gauge_enabled",
                name="自動",
                description="21?",
                flag_type=FlagType.BOOLEAN,
                default_value=True,
                enabled=True,
                targeting_rules=[],
                therapeutic_safety_level="high",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                tags=["core_feature", "habit_formation"]
            ),
            
            # Micro Rewards?
            FeatureFlag(
                flag_key="micro_rewards_enabled",
                name="?",
                description="3?",
                flag_type=FlagType.BOOLEAN,
                default_value=True,
                enabled=True,
                targeting_rules=[],
                therapeutic_safety_level="medium",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                tags=["core_feature", "engagement"]
            ),
            
            # リスト
            FeatureFlag(
                flag_key="recovery_boost_multiplier",
                name="リスト",
                description="?XP?",
                flag_type=FlagType.NUMBER,
                default_value=1.2,
                enabled=True,
                targeting_rules=[],
                therapeutic_safety_level="low",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                tags=["engagement", "retention"]
            ),
            
            # ?
            FeatureFlag(
                flag_key="new_cbt_integration",
                name="CBT?",
                description="?",
                flag_type=FlagType.BOOLEAN,
                default_value=False,
                enabled=True,
                targeting_rules=[
                    TargetingRule(
                        rule_id="beta_users",
                        name="?",
                        conditions=[{"attribute": "user_type", "operator": "equals", "value": "beta"}],
                        percentage=1.0,
                        value=True,
                        priority=1
                    )
                ],
                therapeutic_safety_level="critical",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                tags=["experimental", "cbt", "therapy"]
            ),
            
            # ?
            FeatureFlag(
                flag_key="ai_response_timeout",
                name="AI?",
                description="GPT-4o?",
                flag_type=FlagType.NUMBER,
                default_value=3.5,
                enabled=True,
                targeting_rules=[],
                therapeutic_safety_level="medium",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                tags=["performance", "ai"]
            )
        ]
        
        for flag in default_flags:
            self.flags[flag.flag_key] = flag
    
    async def evaluate_flag(self, flag_key: str, user_context: UserContext, default_value: Any = None) -> FlagEvaluation:
        """?"""
        try:
            # ?
            if flag_key not in self.flags:
                return FlagEvaluation(
                    flag_key=flag_key,
                    value=default_value,
                    reason="flag_not_found",
                    user_id=user_context.user_id,
                    timestamp=datetime.now()
                )
            
            flag = self.flags[flag_key]
            
            # Kill Switch ?
            if flag.kill_switch_active:
                return FlagEvaluation(
                    flag_key=flag_key,
                    value=flag.default_value,
                    reason="kill_switch_active",
                    user_id=user_context.user_id,
                    timestamp=datetime.now()
                )
            
            # ?
            if not flag.enabled:
                return FlagEvaluation(
                    flag_key=flag_key,
                    value=flag.default_value,
                    reason="flag_disabled",
                    user_id=user_context.user_id,
                    timestamp=datetime.now()
                )
            
            # タスク
            for rule in sorted(flag.targeting_rules, key=lambda r: r.priority):
                if await self._evaluate_targeting_rule(rule, user_context):
                    # ?
                    if self._is_user_in_percentage(user_context.user_id, flag_key, rule.percentage):
                        evaluation = FlagEvaluation(
                            flag_key=flag_key,
                            value=rule.value,
                            variation_id=rule.rule_id,
                            reason="targeting_rule_match",
                            rule_matched=rule.name,
                            user_id=user_context.user_id,
                            timestamp=datetime.now()
                        )
                        
                        # ?
                        self.evaluations_log.append(evaluation)
                        return evaluation
            
            # デフォルト
            evaluation = FlagEvaluation(
                flag_key=flag_key,
                value=flag.default_value,
                reason="default_value",
                user_id=user_context.user_id,
                timestamp=datetime.now()
            )
            
            self.evaluations_log.append(evaluation)
            return evaluation
            
        except Exception as e:
            logger.error(f"Flag evaluation failed for {flag_key}: {e}")
            return FlagEvaluation(
                flag_key=flag_key,
                value=default_value or False,
                reason="evaluation_error",
                user_id=user_context.user_id,
                timestamp=datetime.now()
            )
    
    async def _evaluate_targeting_rule(self, rule: TargetingRule, user_context: UserContext) -> bool:
        """タスク"""
        for condition in rule.conditions:
            attribute = condition.get("attribute")
            operator = condition.get("operator")
            expected_value = condition.get("value")
            
            if attribute not in user_context.attributes:
                return False
            
            actual_value = user_context.attributes[attribute]
            
            if operator == "equals" and actual_value != expected_value:
                return False
            elif operator == "not_equals" and actual_value == expected_value:
                return False
            elif operator == "greater_than" and actual_value <= expected_value:
                return False
            elif operator == "less_than" and actual_value >= expected_value:
                return False
            elif operator == "contains" and expected_value not in str(actual_value):
                return False
            elif operator == "in" and actual_value not in expected_value:
                return False
        
        return True
    
    def _is_user_in_percentage(self, user_id: str, flag_key: str, percentage: float) -> bool:
        """ユーザー"""
        # ユーザーIDと
        hash_input = f"{user_id}:{flag_key}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        user_percentage = (hash_value % 10000) / 10000.0
        
        return user_percentage < percentage
    
    async def create_ab_test(self, ab_test: ABTestConfig) -> Dict[str, Any]:
        """A/B?"""
        try:
            # 治療
            if ab_test.therapeutic_safety_check:
                safety_result = await self._therapeutic_safety_check(ab_test)
                if not safety_result["approved"]:
                    raise HTTPException(
                        status_code=400,
                        detail=f"治療: {safety_result['reason']}"
                    )
            
            # A/B?
            targeting_rules = []
            
            for variation_id, allocation in ab_test.traffic_allocation.items():
                variation = next((v for v in ab_test.variations if v["id"] == variation_id), None)
                if variation:
                    targeting_rules.append(TargetingRule(
                        rule_id=f"{ab_test.test_id}_{variation_id}",
                        name=f"{ab_test.name} - {variation_id}",
                        conditions=[],  # A/B?
                        percentage=allocation,
                        value=variation["value"],
                        priority=len(targeting_rules) + 1
                    ))
            
            flag = FeatureFlag(
                flag_key=ab_test.flag_key,
                name=f"A/B Test: {ab_test.name}",
                description=ab_test.description,
                flag_type=FlagType.BOOLEAN,  # 基本boolean
                default_value=ab_test.variations[0]["value"],  # ?
                enabled=True,
                targeting_rules=targeting_rules,
                therapeutic_safety_level="high",  # A/B?
                created_at=datetime.now(),
                updated_at=datetime.now(),
                tags=["ab_test", ab_test.test_id]
            )
            
            self.flags[ab_test.flag_key] = flag
            self.ab_tests[ab_test.test_id] = ab_test
            
            return {
                "success": True,
                "test_id": ab_test.test_id,
                "flag_key": ab_test.flag_key,
                "message": "A/B?"
            }
            
        except Exception as e:
            logger.error(f"A/B test creation failed: {e}")
            raise HTTPException(status_code=500, detail="A/B?")
    
    async def _therapeutic_safety_check(self, ab_test: ABTestConfig) -> Dict[str, Any]:
        """治療"""
        # 基本
        checks = []
        
        # 1. ?
        total_allocation = sum(ab_test.traffic_allocation.values())
        if abs(total_allocation - 1.0) > 0.01:
            checks.append("?100%で")
        
        # 2. ?
        max_single_allocation = max(ab_test.traffic_allocation.values())
        if max_single_allocation > 0.5:  # 50%?
            checks.append("?50%を")
        
        # 3. ?
        if ab_test.end_date and ab_test.end_date < ab_test.start_date:
            checks.append("終")
        
        # 4. ?
        if ab_test.flag_key in self.flags:
            checks.append("?")
        
        return {
            "approved": len(checks) == 0,
            "reason": "; ".join(checks) if checks else "安全",
            "checks_performed": ["traffic_allocation", "gradual_rollout", "date_validation", "flag_uniqueness"]
        }
    
    async def activate_kill_switch(self, flag_key: str, reason: str, activated_by: str) -> Dict[str, Any]:
        """?Kill Switch発"""
        try:
            if flag_key not in self.flags:
                raise HTTPException(status_code=404, detail="?")
            
            flag = self.flags[flag_key]
            flag.kill_switch_active = True
            flag.updated_at = datetime.now()
            
            # Kill Switch?
            kill_switch_record = {
                "flag_key": flag_key,
                "reason": reason,
                "activated_by": activated_by,
                "activated_at": datetime.now(),
                "previous_state": flag.enabled
            }
            
            self.kill_switches[flag_key] = kill_switch_record
            
            logger.warning(f"Kill switch activated for {flag_key}: {reason}")
            
            return {
                "success": True,
                "flag_key": flag_key,
                "message": f"Kill Switchが: {reason}",
                "activated_at": kill_switch_record["activated_at"].isoformat()
            }
            
        except Exception as e:
            logger.error(f"Kill switch activation failed: {e}")
            raise HTTPException(status_code=500, detail="Kill Switch発")
    
    async def deactivate_kill_switch(self, flag_key: str, deactivated_by: str) -> Dict[str, Any]:
        """Kill Switch?"""
        try:
            if flag_key not in self.flags:
                raise HTTPException(status_code=404, detail="?")
            
            flag = self.flags[flag_key]
            flag.kill_switch_active = False
            flag.updated_at = datetime.now()
            
            # Kill Switch?
            if flag_key in self.kill_switches:
                self.kill_switches[flag_key]["deactivated_by"] = deactivated_by
                self.kill_switches[flag_key]["deactivated_at"] = datetime.now()
            
            logger.info(f"Kill switch deactivated for {flag_key}")
            
            return {
                "success": True,
                "flag_key": flag_key,
                "message": "Kill Switchが",
                "deactivated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Kill switch deactivation failed: {e}")
            raise HTTPException(status_code=500, detail="Kill Switch?")
    
    async def get_flag_analytics(self, flag_key: str, hours: int = 24) -> Dict[str, Any]:
        """?"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # ?
        relevant_evaluations = [
            eval for eval in self.evaluations_log
            if eval.flag_key == flag_key and eval.timestamp > cutoff_time
        ]
        
        if not relevant_evaluations:
            return {
                "flag_key": flag_key,
                "period_hours": hours,
                "total_evaluations": 0,
                "unique_users": 0,
                "value_distribution": {},
                "reason_distribution": {}
            }
        
        # ?
        unique_users = len(set(eval.user_id for eval in relevant_evaluations))
        
        value_distribution = {}
        reason_distribution = {}
        
        for eval in relevant_evaluations:
            # ?
            value_key = str(eval.value)
            value_distribution[value_key] = value_distribution.get(value_key, 0) + 1
            
            # 理
            reason_distribution[eval.reason] = reason_distribution.get(eval.reason, 0) + 1
        
        return {
            "flag_key": flag_key,
            "period_hours": hours,
            "total_evaluations": len(relevant_evaluations),
            "unique_users": unique_users,
            "value_distribution": value_distribution,
            "reason_distribution": reason_distribution,
            "kill_switch_active": self.flags[flag_key].kill_switch_active if flag_key in self.flags else False
        }

# ?
feature_flag_engine = FeatureFlagEngine()

# APIエラー

@app.post("/flags/evaluate")
async def evaluate_flag(flag_key: str, user_context: UserContext, default_value: Any = None):
    """?"""
    return await feature_flag_engine.evaluate_flag(flag_key, user_context, default_value)

@app.post("/flags/evaluate-batch")
async def evaluate_flags_batch(flag_keys: List[str], user_context: UserContext):
    """?"""
    results = {}
    
    for flag_key in flag_keys:
        evaluation = await feature_flag_engine.evaluate_flag(flag_key, user_context)
        results[flag_key] = evaluation
    
    return {
        "user_id": user_context.user_id,
        "evaluations": results,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/flags")
async def list_flags():
    """?"""
    return {
        "flags": list(feature_flag_engine.flags.values()),
        "total_count": len(feature_flag_engine.flags)
    }

@app.get("/flags/{flag_key}")
async def get_flag(flag_key: str):
    """?"""
    if flag_key not in feature_flag_engine.flags:
        raise HTTPException(status_code=404, detail="?")
    
    return feature_flag_engine.flags[flag_key]

@app.post("/ab-tests")
async def create_ab_test(ab_test: ABTestConfig):
    """A/B?"""
    return await feature_flag_engine.create_ab_test(ab_test)

@app.get("/ab-tests")
async def list_ab_tests():
    """A/B?"""
    return {
        "ab_tests": list(feature_flag_engine.ab_tests.values()),
        "total_count": len(feature_flag_engine.ab_tests)
    }

@app.post("/flags/{flag_key}/kill-switch/activate")
async def activate_kill_switch(flag_key: str, reason: str, activated_by: str):
    """Kill Switch発"""
    return await feature_flag_engine.activate_kill_switch(flag_key, reason, activated_by)

@app.post("/flags/{flag_key}/kill-switch/deactivate")
async def deactivate_kill_switch(flag_key: str, deactivated_by: str):
    """Kill Switch?"""
    return await feature_flag_engine.deactivate_kill_switch(flag_key, deactivated_by)

@app.get("/flags/{flag_key}/analytics")
async def get_flag_analytics(flag_key: str, hours: int = 24):
    """?"""
    return await feature_flag_engine.get_flag_analytics(flag_key, hours)

@app.get("/health")
async def health_check():
    """ヘルパー"""
    return {
        "status": "healthy",
        "total_flags": len(feature_flag_engine.flags),
        "active_kill_switches": len([k for k, v in feature_flag_engine.kill_switches.items() if "deactivated_at" not in v]),
        "total_evaluations": len(feature_flag_engine.evaluations_log),
        "timestamp": datetime.now().isoformat()
    }

# 治療
@app.get("/therapeutic-safety/dashboard")
async def therapeutic_safety_dashboard():
    """治療"""
    safety_summary = {
        "critical_flags": [],
        "high_risk_flags": [],
        "active_kill_switches": [],
        "recent_safety_events": []
    }
    
    for flag_key, flag in feature_flag_engine.flags.items():
        if flag.therapeutic_safety_level == "critical":
            safety_summary["critical_flags"].append({
                "flag_key": flag_key,
                "enabled": flag.enabled,
                "kill_switch_active": flag.kill_switch_active
            })
        elif flag.therapeutic_safety_level == "high":
            safety_summary["high_risk_flags"].append({
                "flag_key": flag_key,
                "enabled": flag.enabled,
                "kill_switch_active": flag.kill_switch_active
            })
    
    # アプリKill Switch
    for flag_key, kill_switch in feature_flag_engine.kill_switches.items():
        if "deactivated_at" not in kill_switch:
            safety_summary["active_kill_switches"].append({
                "flag_key": flag_key,
                "reason": kill_switch["reason"],
                "activated_at": kill_switch["activated_at"].isoformat()
            })
    
    return safety_summary

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8011)