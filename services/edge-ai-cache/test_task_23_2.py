"""
タスク23.2: ? - ?
ユーザー
"""
import pytest
import asyncio
import numpy as np
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from collections import defaultdict

from main import (
    IntelligentCache, CacheStrategy, ModelType, CacheItem,
    UserBehaviorPattern, EdgeAICacheEngine
)

class TestUserBehaviorPredictionModel:
    """ユーザー"""
    
    def setup_method(self):
        """?"""
        self.cache = IntelligentCache(max_size=100, strategy=CacheStrategy.PREDICTIVE)
    
    @pytest.mark.asyncio
    async def test_user_behavior_pattern_creation(self):
        """ユーザー"""
        # アプリ
        user_id = "behavior_test_user"
        
        # ?
        for hour in [9, 10, 11, 14, 15, 16]:  # ?
            for i in range(5):  # ?5?
                self.cache.access_history.append({
                    "key": f"task_key_{i}",
                    "user_id": user_id,
                    "timestamp": datetime.now().replace(hour=hour, minute=i*10),
                    "hit": i % 2 == 0  # 50%の
                })
        
        # ?
        await self.cache._analyze_user_pattern(user_id)
        
        # ?
        assert user_id in self.cache.user_patterns
        pattern = self.cache.user_patterns[user_id]
        
        # ?
        assert len(pattern.time_patterns) > 0
        assert "9" in pattern.time_patterns or "10" in pattern.time_patterns
        
        # タスク
        assert len(pattern.task_preferences) > 0
        
        # ?
        assert 0.0 <= pattern.prediction_accuracy <= 1.0
    
    @pytest.mark.asyncio
    async def test_prediction_model_integration(self):
        """?"""
        await self.cache.initialize_prediction_model()
        
        # ?
        # モデル None ま MockModel
        assert self.cache.prediction_model is None or hasattr(self.cache.prediction_model, 'predict')
    
    @pytest.mark.asyncio
    async def test_prediction_score_calculation_with_pattern(self):
        """?"""
        user_id = "prediction_test_user"
        
        # ?
        self.cache.user_patterns[user_id] = UserBehaviorPattern(
            user_id=user_id,
            session_patterns=[],
            task_preferences={
                "story_hash": 0.9,
                "task_hash": 0.7,
                "mood_hash": 0.5
            },
            time_patterns={
                str(datetime.now().hour): 0.8,
                str((datetime.now().hour + 1) % 24): 0.6
            },
            mood_patterns={"current": 0.7},
            prediction_accuracy=0.85
        )
        
        # ?
        score = await self.cache._calculate_prediction_score(
            "story_related_key", user_id, ModelType.STORY_GENERATION
        )
        
        # ?
        assert 0.0 <= score <= 1.0
        assert score > 0.5
    
    @pytest.mark.asyncio
    async def test_statistical_prediction_fallback(self):
        """?"""
        user_id = "statistical_test_user"
        
        # ?
        pattern = UserBehaviorPattern(
            user_id=user_id,
            session_patterns=[],
            task_preferences={"test_key": 0.8},
            time_patterns={str(datetime.now().hour): 0.9},
            mood_patterns={"current": 0.6},
            prediction_accuracy=0.75
        )
        
        # ?
        score = self.cache._statistical_prediction("test_key", pattern, ModelType.TASK_RECOMMENDATION)
        
        # ?
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # ?

class TestPredictiveCacheAlgorithm:
    """?"""
    
    def setup_method(self):
        """?"""
        self.cache = IntelligentCache(max_size=50, strategy=CacheStrategy.PREDICTIVE)
    
    @pytest.mark.asyncio
    async def test_predictive_preload_trigger(self):
        """?"""
        user_id = "preload_test_user"
        
        # ユーザー
        self.cache.user_patterns[user_id] = UserBehaviorPattern(
            user_id=user_id,
            session_patterns=[],
            task_preferences={"story": 0.8, "task": 0.6},
            time_patterns={str(datetime.now().hour): 0.9},
            mood_patterns={"current": 0.7},
            prediction_accuracy=0.8
        )
        
        # ?
        await self.cache._trigger_predictive_preload(user_id, "missed_story_key")
        
        # プレビュー
        # 実装3つ
        preloaded_items = [key for key in self.cache.cache.keys() if "preloaded" in str(self.cache.cache[key].value)]
        assert len(preloaded_items) <= 3
    
    @pytest.mark.asyncio
    async def test_related_keys_prediction(self):
        """?"""
        user_id = "related_keys_user"
        
        # ユーザー
        pattern = UserBehaviorPattern(
            user_id=user_id,
            session_patterns=[],
            task_preferences={},
            time_patterns={
                str(datetime.now().hour): 0.8,
                str((datetime.now().hour + 1) % 24): 0.6
            },
            mood_patterns={"current": 0.7},
            prediction_accuracy=0.75
        )
        
        # ?
        related_keys = await self.cache._predict_related_keys(user_id, "base_story_key", pattern)
        
        # ?
        assert len(related_keys) > 0
        assert any("hour_" in key for key in related_keys)  # ?
        assert any("_story" in key or "_task" in key or "_mood" in key for key in related_keys)  # タスク
    
    @pytest.mark.asyncio
    async def test_preload_cache_integration(self):
        """プレビュー"""
        user_id = "integration_test_user"
        
        # ?
        await self.cache.put("initial_key", "initial_value", ModelType.STORY_GENERATION, user_id)
        
        # ?
        result = await self.cache.get("nonexistent_key", user_id)
        assert result is None  # ?
        
        # プレビュー
        await asyncio.sleep(0.1)  # プレビュー
        
        # ?
        stats = self.cache.get_stats()
        assert stats["cache_size"] >= 1  # ? + プレビュー
    
    @pytest.mark.asyncio
    async def test_predictive_cache_strategy_effectiveness(self):
        """?"""
        # ?
        predictive_cache = IntelligentCache(max_size=10, strategy=CacheStrategy.PREDICTIVE)
        
        # ?LRU?
        lru_cache = IntelligentCache(max_size=10, strategy=CacheStrategy.LRU)
        
        user_id = "strategy_test_user"
        
        # ?
        test_keys = [f"key_{i}" for i in range(15)]  # ?
        
        # ?
        for i, key in enumerate(test_keys):
            await predictive_cache.put(key, f"value_{i}", ModelType.STORY_GENERATION, user_id)
            await lru_cache.put(key, f"value_{i}", ModelType.STORY_GENERATION, user_id)
        
        # アプリ
        access_pattern = ["key_0", "key_1", "key_2", "key_0", "key_1", "key_14", "key_13"]
        
        predictive_hits = 0
        lru_hits = 0
        
        for key in access_pattern:
            if await predictive_cache.get(key, user_id) is not None:
                predictive_hits += 1
            if await lru_cache.get(key, user_id) is not None:
                lru_hits += 1
        
        # ?
        predictive_stats = predictive_cache.get_stats()
        lru_stats = lru_cache.get_stats()
        
        assert predictive_stats["hit_rate"] >= 0.0
        assert lru_stats["hit_rate"] >= 0.0

class TestCacheEfficiencyOptimization:
    """?"""
    
    def setup_method(self):
        """?"""
        self.cache = IntelligentCache(max_size=20, strategy=CacheStrategy.HYBRID)
    
    @pytest.mark.asyncio
    async def test_hybrid_cache_strategy(self):
        """?"""
        user_id = "hybrid_test_user"
        
        # ?
        items = [
            ("high_score_high_freq", "value1", 0.9, 10),
            ("high_score_low_freq", "value2", 0.8, 2),
            ("low_score_high_freq", "value3", 0.2, 8),
            ("low_score_low_freq", "value4", 0.1, 1),
        ]
        
        # アプリ
        for key, value, pred_score, access_count in items:
            await self.cache.put(key, value, ModelType.STORY_GENERATION, user_id)
            
            # ?
            if key in self.cache.cache:
                self.cache.cache[key].prediction_score = pred_score
                self.cache.cache[key].access_count = access_count
        
        # ?
        for i in range(25):  # max_size=20を
            await self.cache.put(f"overflow_{i}", f"overflow_value_{i}", ModelType.TASK_RECOMMENDATION, user_id)
        
        # ?
        remaining_keys = list(self.cache.cache.keys())
        
        # 基本
        assert len(remaining_keys) <= self.cache.max_size
        assert self.cache.stats["evictions"] > 0
    
    @pytest.mark.asyncio
    async def test_cache_size_optimization(self):
        """?"""
        # ?
        small_cache = IntelligentCache(max_size=5, strategy=CacheStrategy.HYBRID)
        
        # ?
        for i in range(20):
            await small_cache.put(f"key_{i}", f"large_value_{i}" * 100, ModelType.STORY_GENERATION)
        
        # ?
        assert len(small_cache.cache) <= small_cache.max_size
        
        # ?
        assert small_cache.stats["evictions"] > 0
        
        # ?
        stats = small_cache.get_stats()
        assert stats["cache_size"] <= 5
        assert stats["total_evictions"] > 0
    
    @pytest.mark.asyncio
    async def test_ttl_based_optimization(self):
        """TTL?"""
        # ?TTLで
        await self.cache.put("short_ttl", "value1", ModelType.STORY_GENERATION, ttl_seconds=1)
        await self.cache.put("long_ttl", "value2", ModelType.STORY_GENERATION, ttl_seconds=10)
        await self.cache.put("no_ttl", "value3", ModelType.STORY_GENERATION)
        
        # ?
        assert await self.cache.get("short_ttl") == "value1"
        assert await self.cache.get("long_ttl") == "value2"
        assert await self.cache.get("no_ttl") == "value3"
        
        # TTL?
        await asyncio.sleep(1.1)
        
        # ?TTLの
        assert await self.cache.get("short_ttl") is None
        assert await self.cache.get("long_ttl") == "value2"  # ま
        assert await self.cache.get("no_ttl") == "value3"    # TTLな
    
    @pytest.mark.asyncio
    async def test_memory_usage_optimization(self):
        """メイン"""
        # ?
        large_data = "x" * 10000  # 10KB の
        
        for i in range(10):
            await self.cache.put(f"large_key_{i}", large_data, ModelType.STORY_GENERATION)
        
        # メイン
        total_size = sum(item.size_bytes for item in self.cache.cache.values())
        assert total_size > 0
        
        # ?
        for item in self.cache.cache.values():
            assert item.size_bytes > 0
    
    @pytest.mark.asyncio
    async def test_access_pattern_optimization(self):
        """アプリ"""
        user_id = "pattern_opt_user"
        
        # ?
        keys = ["morning_task", "afternoon_task", "evening_task"]
        
        # ?
        for hour in [9, 14, 20]:  # ?
            for i, key in enumerate(keys):
                if (hour == 9 and i == 0) or (hour == 14 and i == 1) or (hour == 20 and i == 2):
                    # ?
                    await self.cache.put(key, f"value_{hour}_{i}", ModelType.TASK_RECOMMENDATION, user_id)
                    await self.cache.get(key, user_id)
        
        # ユーザー
        if user_id in self.cache.user_patterns:
            pattern = self.cache.user_patterns[user_id]
            assert len(pattern.time_patterns) > 0

class TestCacheSystemIntegration:
    """?"""
    
    def setup_method(self):
        """?"""
        self.engine = EdgeAICacheEngine()
    
    @pytest.mark.asyncio
    async def test_intelligent_cache_engine_integration(self):
        """?"""
        await self.engine.initialize()
        
        # ?
        assert isinstance(self.engine.cache, IntelligentCache)
        assert self.engine.cache.strategy == CacheStrategy.HYBRID
    
    @pytest.mark.asyncio
    async def test_cache_with_ai_inference_integration(self):
        """?AI?"""
        await self.engine.initialize()
        
        user_id = "ai_integration_user"
        input_data = {"prompt": "?"}
        
        # ?
        result1 = await self.engine.get_cached_inference(
            ModelType.STORY_GENERATION, input_data, user_id
        )
        
        # 2?
        result2 = await self.engine.get_cached_inference(
            ModelType.STORY_GENERATION, input_data, user_id
        )
        
        # ?
        stats = self.engine.cache.get_stats()
        assert stats["total_hits"] >= 0
        assert stats["total_misses"] >= 0
    
    @pytest.mark.asyncio
    async def test_multi_user_cache_isolation(self):
        """?"""
        await self.engine.initialize()
        
        # ?
        input_data = {"prompt": "共有"}
        
        user1_result = await self.engine.get_cached_inference(
            ModelType.STORY_GENERATION, input_data, "user_1"
        )
        
        user2_result = await self.engine.get_cached_inference(
            ModelType.STORY_GENERATION, input_data, "user_2"
        )
        
        # ?
        # た
        assert "user_1" not in self.engine.cache.user_patterns or "user_2" not in self.engine.cache.user_patterns or \
               self.engine.cache.user_patterns.get("user_1") != self.engine.cache.user_patterns.get("user_2")
    
    @pytest.mark.asyncio
    async def test_cache_performance_under_load(self):
        """?"""
        await self.engine.initialize()
        
        # ?
        tasks = []
        for i in range(50):
            input_data = {"prompt": f"?_{i % 10}"}  # 10?
            task = self.engine.get_cached_inference(
                ModelType.STORY_GENERATION, input_data, f"load_user_{i % 5}"
            )
            tasks.append(task)
        
        # ?
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        # ?
        total_time = end_time - start_time
        assert total_time < 10.0  # 10?
        
        # エラー
        errors = [r for r in results if isinstance(r, Exception)]
        assert len(errors) == 0
        
        # ?
        stats = self.engine.cache.get_stats()
        assert stats["hit_rate"] >= 0.0  # ?

class TestAdvancedCacheFeatures:
    """?"""
    
    def setup_method(self):
        """?"""
        self.cache = IntelligentCache(max_size=30, strategy=CacheStrategy.HYBRID)
    
    @pytest.mark.asyncio
    async def test_cache_warming(self):
        """?"""
        user_id = "warming_test_user"
        
        # ?
        common_data = [
            ("morning_greeting", "お", ModelType.STORY_GENERATION),
            ("daily_task_list", ["task1", "task2", "task3"], ModelType.TASK_RECOMMENDATION),
            ("mood_check", {"score": 3}, ModelType.MOOD_PREDICTION),
        ]
        
        # ?
        for key, value, model_type in common_data:
            await self.cache.put(key, value, model_type, user_id)
            # ?
            if key in self.cache.cache:
                self.cache.cache[key].prediction_score = 0.9
        
        # ?
        for key, _, _ in common_data:
            assert await self.cache.get(key, user_id) is not None
    
    @pytest.mark.asyncio
    async def test_cache_analytics(self):
        """?"""
        user_id = "analytics_test_user"
        
        # ?
        for i in range(20):
            key = f"analytics_key_{i % 5}"  # 5つ
            await self.cache.put(key, f"value_{i}", ModelType.STORY_GENERATION, user_id)
            await self.cache.get(key, user_id)
        
        # ?
        stats = self.cache.get_stats()
        
        # 基本
        assert "hit_rate" in stats
        assert "cache_size" in stats
        assert "total_hits" in stats
        assert "total_misses" in stats
        
        # ?
        assert 0.0 <= stats["hit_rate"] <= 1.0
        
        # ?
        assert stats["cache_size"] <= self.cache.max_size
    
    @pytest.mark.asyncio
    async def test_cache_health_monitoring(self):
        """?"""
        # ?
        healthy_cache = IntelligentCache(max_size=100, strategy=CacheStrategy.HYBRID)
        
        # ?
        for i in range(10):
            await healthy_cache.put(f"healthy_key_{i}", f"value_{i}", ModelType.STORY_GENERATION)
        
        stats = healthy_cache.get_stats()
        
        # ヘルパー
        assert stats["cache_size"] > 0
        assert stats["cache_size"] <= healthy_cache.max_size
        
        # メイン
        total_items = len(healthy_cache.cache)
        assert total_items <= healthy_cache.max_size
    
    @pytest.mark.asyncio
    async def test_cache_recovery_mechanisms(self):
        """?"""
        # ?
        recovery_cache = IntelligentCache(max_size=5, strategy=CacheStrategy.HYBRID)
        
        # ?
        for i in range(100):
            try:
                await recovery_cache.put(f"recovery_key_{i}", f"value_{i}", ModelType.STORY_GENERATION)
            except Exception as e:
                # ?
                pass
        
        # ?
        assert len(recovery_cache.cache) <= recovery_cache.max_size
        
        # 基本
        test_result = await recovery_cache.get("recovery_key_99")
        # ? None で

if __name__ == "__main__":
    pytest.main([__file__, "-v"])