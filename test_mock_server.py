"""
パフォーマンステスト用モックサーバー
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import time
import random
from datetime import datetime
from typing import Dict, Any

app = FastAPI(title="MVP Performance Test Mock Server")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 簡単なメモリ内データストア
users_data = {}
tasks_data = {}

@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/user/{user_id}/dashboard")
async def get_user_dashboard(user_id: str):
    """ユーザーダッシュボード"""
    # 軽い処理遅延をシミュレート
    import asyncio
    await asyncio.sleep(random.uniform(0.05, 0.15))
    
    return {
        "user_id": user_id,
        "level": random.randint(1, 10),
        "xp": random.randint(100, 2000),
        "crystal_progress": {
            "Self-Discipline": random.randint(0, 100),
            "Empathy": random.randint(0, 100),
            "Resilience": random.randint(0, 100)
        },
        "active_tasks": random.randint(0, 5),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/user/{user_id}/tasks")
async def get_user_tasks(user_id: str):
    """ユーザータスク一覧"""
    import asyncio
    await asyncio.sleep(random.uniform(0.02, 0.1))
    
    tasks = []
    for i in range(random.randint(1, 8)):
        tasks.append({
            "id": f"task_{i}",
            "type": random.choice(["routine", "one_shot", "skill_up", "social"]),
            "difficulty": random.randint(1, 5),
            "description": f"テストタスク {i}",
            "completed": random.choice([True, False])
        })
    
    return {
        "user_id": user_id,
        "tasks": tasks,
        "total_count": len(tasks),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/user/{user_id}/mandala")
async def get_user_mandala(user_id: str):
    """ユーザーMandala"""
    import asyncio
    await asyncio.sleep(random.uniform(0.05, 0.2))
    
    # 9x9グリッドをシミュレート
    grid = []
    for i in range(9):
        row = []
        for j in range(9):
            if random.random() > 0.7:  # 30%の確率でアンロック
                row.append({
                    "unlocked": True,
                    "content": f"セル({i},{j})",
                    "xp_reward": random.randint(10, 50)
                })
            else:
                row.append({"unlocked": False})
        grid.append(row)
    
    return {
        "user_id": user_id,
        "grid": grid,
        "unlocked_count": sum(1 for row in grid for cell in row if cell.get("unlocked", False)),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/user/{user_id}/story")
async def get_user_story(user_id: str):
    """ユーザーストーリー"""
    # ストーリー生成の重い処理をシミュレート
    await asyncio.sleep(random.uniform(0.5, 1.5))
    
    return {
        "user_id": user_id,
        "current_chapter": "Self-Discipline",
        "story_text": "テストストーリーコンテンツ...",
        "choices": [
            {"id": 1, "text": "選択肢1", "xp_reward": 25},
            {"id": 2, "text": "選択肢2", "xp_reward": 30}
        ],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/performance/metrics")
async def get_performance_metrics():
    """パフォーマンスメトリクス"""
    await asyncio.sleep(random.uniform(0.02, 0.1))
    
    return {
        "cpu_usage": random.uniform(10, 60),
        "memory_usage": random.uniform(30, 70),
        "active_connections": random.randint(5, 50),
        "requests_per_second": random.uniform(10, 100),
        "avg_response_time": random.uniform(0.1, 0.8),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/user/{user_id}/tasks")
async def create_task(user_id: str, task_data: Dict[str, Any]):
    """タスク作成"""
    await asyncio.sleep(random.uniform(0.1, 0.3))
    
    task_id = f"task_{random.randint(1000, 9999)}"
    return {
        "task_id": task_id,
        "user_id": user_id,
        "created": True,
        "timestamp": datetime.now().isoformat()
    }

@app.put("/api/user/{user_id}/tasks/{task_id}/complete")
async def complete_task(user_id: str, task_id: str):
    """タスク完了"""
    await asyncio.sleep(random.uniform(0.05, 0.2))
    
    xp_earned = random.randint(10, 100)
    return {
        "task_id": task_id,
        "user_id": user_id,
        "completed": True,
        "xp_earned": xp_earned,
        "timestamp": datetime.now().isoformat()
    }

# 重い処理をシミュレートするエンドポイント
@app.get("/api/heavy/computation")
async def heavy_computation():
    """重い計算処理のシミュレート"""
    # 意図的に重い処理
    await asyncio.sleep(random.uniform(2, 4))
    
    return {
        "result": "heavy computation completed",
        "computation_time": random.uniform(2, 4),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import asyncio
    
    print("パフォーマンステスト用モックサーバー起動中...")
    print("URL: http://localhost:8001")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )