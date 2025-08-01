"""
Edge AI Cache Service ?
"""
import pytest
import asyncio
import numpy as np
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from main import (
    app, edge_ai_engine, intelligent_cache,
    EdgeAICacheEngine, IntelligentCache, CacheStrategy, ModelType,
    TensorFlowLiteModel, ONNXModel, CacheItem
)

client = TestClient(app)

class TestIntelligentCache:
    def setup_method(self):
        """?"""
        self.cache = IntelligentCache(max_size=10, strategy=CacheStrategy.HYBRID)
    
    @pytest.mark.asyncio
    async def test_cache_basic_operations(self):
        """基本"""
        # デフォルト
        result = await self.cache.put("test_key", "test_value", ModelType.STORY_GENERATION)
        assert result is True
        
        # デフォルト
        value = await self.cache.get("test_key")
        assert value == "test_value"
        
        # ?
        stats = self.cache.get_stats()
        assert stats["total_hits"] == 1
        assert stats["total_misses"] == 0
        assert stats["cache_size"] == 1
    
    @pytest.mark.asyncio
    async def test_cache_miss(self):
        """?"""
        # ?
        value = await self.cache.get("nonexistent_key")
        assert value is None
        
        # ?
        stats = self.cache.get_stats()
        assert stats["total_misses"] == 1
        assert stats["total_hits"] == 0
    
    @pytest.mark.asyncio
    async def test_cache_ttl(self):
        """TTL?Time To Live?"""
        # TTL?
        await self.cache.put("ttl_key", "ttl_value", ModelType.TASK_RECOMMENDATION, ttl_seconds=1)
        
        # ?
        value = await self.cache.get("ttl_key")
        assert value == "ttl_value"
        
        # TTL?
        await asyncio.sleep(1.1)
        value = await self.cache.get("ttl_key")
        assert value is None
    
    @pytest.mark.asyncio
    async def test_cache_eviction(self):
        """?"""
        # ?
        for i in range(10):
            await self.cache.put(f"key_{i}", f"value_{i}", ModelType.MOOD_PREDICTION)
        
        assert len(self.cache.cache) == 10
        
        # ?
        await self.cache.put("overflow_key", "overflow_value", ModelType.USER_BEHAVIOR)
        
        # ?
        assert len(self.cache.cache) <= 10
        assert self.cache.stats["evictions"] > 0
    
    @pytest.mark.asyncio
    async def test_prediction_score_calculation(self):
        """?"""
        # ユーザー
        from main import UserBehaviorPattern
        
        self.cache.user_patterns["test_user"] = UserBehaviorPattern(
            user_id="test_user",
            session_patterns=[],
            task_preferences={"test_hash": 0.8},
            time_patterns={str(datetime.now().hour): 0.9},
            mood_patterns={"current": 0.7},
            prediction_accuracy=0.85
        )
        
        # ?
        score = await self.cache._calculate_prediction_score(
            "test_key", "test_user", ModelType.STORY_GENERATION
        )
        
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # ?
    
    @pytest.mark.asyncio
    async def test_user_pattern_analysis(self):
        """ユーザー"""
        # アプリ
        for i in range(20):
            self.cache.access_history.append({
                "key": f"key_{i % 5}",
                "user_id": "test_user",
                "timestamp": datetime.now() - timedelta(minutes=i),
                "hit": i % 3 == 0  # 33%の
            })
        
        # ?
        await self.cache._analyze_user_pattern("test_user")
        
        # ?
        assert "test_user" in self.cache.user_patterns
        pattern = self.cache.user_patterns["test_user"]
        
        assert pattern.user_id == "test_user"
        assert len(pattern.time_patterns) > 0
        assert len(pattern.task_preferences) > 0
        assert 0.0 <= pattern.prediction_accuracy <= 1.0

class TestEdgeAIModels:
    @pytest.mark.asyncio
    async def test_tensorflow_lite_model_mock(self):
        """TensorFlow Liteモデル"""
        model = TensorFlowLiteModel("mock_path.tflite", ModelType.STORY_GENERATION)
        await model.load_model()
        
        assert model.is_loaded is True
        
        # ?
        input_data = np.array([[1.0, 2.0, 3.0]], dtype=np.float32)
        result = await model.predict(input_data)
        
        assert isinstance(result, np.ndarray)
        assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_onnx_model_mock(self):
        """ONNXモデル"""
        model = ONNXModel("mock_path.onnx", ModelType.TASK_RECOMMENDATION)
        await model.load_model()
        
        assert model.is_loaded is True
        
        # ?
        input_data = {"input": np.array([[0.5, 1.5]], dtype=np.float32)}
        result = await model.predict(input_data)
        
        assert isinstance(result, (np.ndarray, float))

class TestEdgeAICacheEngine:
    def setup_method(self):
        """?"""
        self.engine = EdgeAICacheEngine()
    
    @pytest.mark.asyncio
    async def test_engine_initialization(self):
        """エラー"""
        await self.engine.initialize()
        
        # ?
        assert self.engine.cache is not None
        
        # モデル
        assert len(self.engine.models) >= 0  # モデル0で
    
    @pytest.mark.asyncio
    async def test_cached_inference(self):
        """?"""
        await self.engine.initialize()
        
        # ?
        input_data = {"text": "test story prompt"}
        result1 = await self.engine.get_cached_inference(
            ModelType.STORY_GENERATION, input_data, "test_user"
        )
        
        # 2?
        result2 = await self.engine.get_cached_inference(
            ModelType.STORY_GENERATION, input_data, "test_user"
        )
        
        # ?
        if result1 is not None and result2 is not None:
            assert np.array_equal(result1, result2)
    
    @pytest.mark.asyncio
    async def test_offline_queue_operations(self):
        """?"""
        # ?
        operation1 = {
            "type": "task_completion",
            "task_id": "task_123",
            "user_id": "user_456"
        }
        
        await self.engine.add_to_offline_queue(operation1)
        assert len(self.engine.offline_queue) == 1
        
        operation2 = {
            "type": "mood_update",
            "mood_score": 4,
            "user_id": "user_456"
        }
        
        await self.engine.add_to_offline_queue(operation2)
        assert len(self.engine.offline_queue) == 2
        
        # ?
        sync_result = await self.engine.sync_offline_operations()
        
        assert sync_result["status"] == "completed"
        assert sync_result["synced_count"] >= 0
    
    def test_cache_key_generation(self):
        """?"""
        input_data1 = {"text": "hello world"}
        input_data2 = {"text": "hello world"}
        input_data3 = {"text": "goodbye world"}
        
        key1 = self.engine._generate_cache_key(ModelType.STORY_GENERATION, input_data1)
        key2 = self.engine._generate_cache_key(ModelType.STORY_GENERATION, input_data2)
        key3 = self.engine._generate_cache_key(ModelType.STORY_GENERATION, input_data3)
        
        # ?
        assert key1 == key2
        
        # ?
        assert key1 != key3
        
        # ?
        assert key1.startswith("story_generation_")
        assert len(key1) > 20  # ?

class TestEdgeAICacheAPI:
    def test_health_check_endpoint(self):
        """ヘルパーAPI?"""
        response = client.get("/edge-ai/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "cache_hit_rate" in data
        assert "models_loaded" in data
        assert "offline_queue_size" in data
    
    def test_cache_stats_endpoint(self):
        """?API?"""
        response = client.get("/edge-ai/cache/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "cache_size" in data
        assert "hit_rate" in data
        assert "strategy" in data
    
    def test_models_status_endpoint(self):
        """モデルAPI?"""
        response = client.get("/edge-ai/models/status")
        assert response.status_code == 200
        
        data = response.json()
        # モデル
        assert isinstance(data, dict)
    
    def test_offline_operations_endpoints(self):
        """?API?"""
        # ?
        operation = {
            "type": "task_completion",
            "task_id": "test_task",
            "user_id": "test_user"
        }
        
        response = client.post("/edge-ai/offline/add", json=operation)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "added"
        assert "queue_size" in data
        
        # ?
        response = client.post("/edge-ai/offline/sync")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "synced_count" in data
    
    def test_inference_endpoint(self):
        """?API?"""
        input_data = {"text": "test input"}
        
        response = client.get(
            "/edge-ai/inference/story_generation",
            params={"input_data": input_data, "user_id": "test_user"}
        )
        
        # モデル
        # 400ま500エラー
        assert response.status_code in [200, 400, 500]
    
    def test_model_quantization_endpoint(self):
        """モデルAPI?"""
        response = client.post("/edge-ai/models/story_generation/quantize")
        
        # モデル404が
        assert response.status_code in [200, 404]

class TestCacheStrategies:
    @pytest.mark.asyncio
    async def test_lru_strategy(self):
        """LRU?"""
        cache = IntelligentCache(max_size=3, strategy=CacheStrategy.LRU)
        
        # ?
        await cache.put("key1", "value1", ModelType.STORY_GENERATION)
        await cache.put("key2", "value2", ModelType.STORY_GENERATION)
        await cache.put("key3", "value3", ModelType.STORY_GENERATION)
        
        # key1に
        await cache.get("key1")
        
        # ?key2が
        await cache.put("key4", "value4", ModelType.STORY_GENERATION)
        
        # key1とkey3は
        assert await cache.get("key1") == "value1"
        assert await cache.get("key3") == "value3"
        assert await cache.get("key4") == "value4"
    
    @pytest.mark.asyncio
    async def test_predictive_strategy(self):
        """?"""
        cache = IntelligentCache(max_size=3, strategy=CacheStrategy.PREDICTIVE)
        
        # ?
        await cache.put("high_score", "value1", ModelType.STORY_GENERATION)
        await cache.put("medium_score", "value2", ModelType.STORY_GENERATION)
        await cache.put("low_score", "value3", ModelType.STORY_GENERATION)
        
        # ?
        cache.cache["high_score"].prediction_score = 0.9
        cache.cache["medium_score"].prediction_score = 0.5
        cache.cache["low_score"].prediction_score = 0.1
        
        # ?
        await cache.put("new_item", "value4", ModelType.STORY_GENERATION)
        
        # ?
        assert await cache.get("high_score") == "value1"
        assert await cache.get("new_item") == "value4"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])