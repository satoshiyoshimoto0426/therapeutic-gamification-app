"""
Edge AI Cache Service ?
"""
import asyncio
import json
import numpy as np
from datetime import datetime
from main import EdgeAICacheEngine, IntelligentCache, CacheStrategy, ModelType

async def test_edge_ai_cache():
    """Edge AI ?"""
    print("=== Edge AI Cache Service ? ===")
    
    # エラー
    engine = EdgeAICacheEngine()
    await engine.initialize()
    print("? Edge AI エラー")
    
    # ?
    print("\n=== ? ===")
    cache = engine.cache
    
    # デフォルト
    await cache.put("test_story", "?...", ModelType.STORY_GENERATION, "user_001")
    await cache.put("test_task", {"type": "routine", "difficulty": 3}, ModelType.TASK_RECOMMENDATION, "user_001")
    await cache.put("test_mood", {"score": 4, "energy": 3}, ModelType.MOOD_PREDICTION, "user_001")
    
    print("? ?")
    
    # デフォルト
    story = await cache.get("test_story", "user_001")
    task = await cache.get("test_task", "user_001")
    mood = await cache.get("test_mood", "user_001")
    
    print(f"? ストーリー: {story}")
    print(f"? タスク: {task}")
    print(f"? 気分: {mood}")
    
    # ?
    stats = cache.get_stats()
    print(f"\n=== ? ===")
    print(f"?: {stats['cache_size']}")
    print(f"?: {stats['hit_rate']:.3f}")
    print(f"?: {stats['total_hits']}")
    print(f"?: {stats['total_misses']}")
    print(f"?: {stats['strategy']}")
    
    # AI?
    print("\n=== AI? ===")
    
    # ストーリー
    story_input = {"prompt": "勇", "length": 100}
    story_result = await engine.get_cached_inference(ModelType.STORY_GENERATION, story_input, "user_001")
    print(f"? ストーリー: {story_result}")
    
    # タスク
    task_input = {"user_mood": 4, "time_of_day": "morning", "difficulty_preference": 3}
    task_result = await engine.get_cached_inference(ModelType.TASK_RECOMMENDATION, task_input, "user_001")
    print(f"? タスク: {task_result}")
    
    # 気分
    mood_input = {"recent_tasks": [3, 4, 2], "sleep_hours": 7, "weather": "sunny"}
    mood_result = await engine.get_cached_inference(ModelType.MOOD_PREDICTION, mood_input, "user_001")
    print(f"? 気分: {mood_result}")
    
    # ?
    print("\n=== ? ===")
    story_result2 = await engine.get_cached_inference(ModelType.STORY_GENERATION, story_input, "user_001")
    print(f"? 2?: {story_result2}")
    
    # ?
    updated_stats = cache.get_stats()
    print(f"? ?: {updated_stats['hit_rate']:.3f}")
    print(f"? ?: {updated_stats['total_hits']}")
    
    # ?
    print("\n=== ? ===")
    
    # ?
    operations = [
        {
            "type": "task_completion",
            "task_id": "task_001",
            "user_id": "user_001",
            "xp_gained": 50
        },
        {
            "type": "mood_update",
            "user_id": "user_001",
            "mood_score": 4,
            "energy_level": 3
        },
        {
            "type": "story_progress",
            "user_id": "user_001",
            "story_id": "story_001",
            "chapter": 2
        }
    ]
    
    for op in operations:
        await engine.add_to_offline_queue(op)
    
    print(f"? ?: {len(operations)}?")
    print(f"? ?: {len(engine.offline_queue)}")
    
    # ?
    sync_result = await engine.sync_offline_operations()
    print(f"? ?: {sync_result}")
    
    # ユーザー
    print("\n=== ユーザー ===")
    
    # アプリ
    for i in range(30):
        cache.access_history.append({
            "key": f"pattern_key_{i % 5}",
            "user_id": "user_001",
            "timestamp": datetime.now(),
            "hit": i % 3 == 0  # 33%の
        })
    
    # ?
    await cache._analyze_user_pattern("user_001")
    
    if "user_001" in cache.user_patterns:
        pattern = cache.user_patterns["user_001"]
        print(f"? ユーザー")
        print(f"  - ?: {pattern.prediction_accuracy:.3f}")
        print(f"  - ?: {len(pattern.time_patterns)}")
        print(f"  - タスク: {len(pattern.task_preferences)}")
    
    # ?
    print("\n=== ? ===")
    
    # ?
    prediction_score = await cache._calculate_prediction_score(
        "predictive_key", "user_001", ModelType.STORY_GENERATION
    )
    print(f"? ?: {prediction_score:.3f}")
    
    # ?
    related_keys = await cache._predict_related_keys(
        "user_001", "base_story_key", cache.user_patterns.get("user_001")
    )
    print(f"? ?: {related_keys}")
    
    # ?
    print("\n=== ? ===")
    
    strategies = [CacheStrategy.LRU, CacheStrategy.LFU, CacheStrategy.PREDICTIVE, CacheStrategy.HYBRID]
    
    for strategy in strategies:
        test_cache = IntelligentCache(max_size=5, strategy=strategy)
        
        # ?
        for i in range(7):  # ?
            await test_cache.put(f"strategy_key_{i}", f"value_{i}", ModelType.USER_BEHAVIOR)
        
        stats = test_cache.get_stats()
        print(f"? {strategy.value}?: ?={stats['cache_size']}, ?={stats['total_evictions']}")
    
    # ?
    print("\n=== ? ===")
    
    import time
    
    # ?
    start_time = time.time()
    
    for i in range(100):
        key = f"perf_key_{i}"
        value = f"performance_test_value_{i}" * 10  # ?
        await cache.put(key, value, ModelType.USER_BEHAVIOR, "perf_user")
    
    put_time = time.time() - start_time
    print(f"? 100?PUT?: {put_time:.3f}?")
    
    start_time = time.time()
    
    hit_count = 0
    for i in range(100):
        key = f"perf_key_{i}"
        result = await cache.get(key, "perf_user")
        if result is not None:
            hit_count += 1
    
    get_time = time.time() - start_time
    print(f"? 100?GET?: {get_time:.3f}?")
    print(f"? ?: {hit_count}/100")
    
    # ?
    print("\n=== ? ===")
    final_stats = cache.get_stats()
    print(f"?: {final_stats['cache_size']}")
    print(f"?: {final_stats['hit_rate']:.3f}")
    print(f"ユーザー: {final_stats['user_patterns_count']}")
    print(f"?: {final_stats['total_evictions']}")
    
    print("\n=== ? ===")
    return True

def test_api_endpoints():
    """API エラー"""
    print("\n=== API エラー ===")
    
    from fastapi.testclient import TestClient
    from main import app
    
    client = TestClient(app)
    
    # ヘルパー
    response = client.get("/edge-ai/health")
    assert response.status_code == 200
    print("? GET /edge-ai/health")
    
    # ?
    response = client.get("/edge-ai/cache/stats")
    assert response.status_code == 200
    print("? GET /edge-ai/cache/stats")
    
    # モデル
    response = client.get("/edge-ai/models/status")
    assert response.status_code == 200
    print("? GET /edge-ai/models/status")
    
    # ?
    operation = {
        "type": "task_completion",
        "task_id": "api_test_task",
        "user_id": "api_test_user"
    }
    response = client.post("/edge-ai/offline/add", json=operation)
    assert response.status_code == 200
    print("? POST /edge-ai/offline/add")
    
    # ?
    response = client.post("/edge-ai/offline/sync")
    assert response.status_code == 200
    print("? POST /edge-ai/offline/sync")
    
    print("? ?APIエラー")

if __name__ == "__main__":
    # ?
    asyncio.run(test_edge_ai_cache())
    
    # API ?
    test_api_endpoints()
    
    print("\n? Edge AI Cache Service ?")