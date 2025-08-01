#!/usr/bin/env python3
"""
治療的ゲーミフィケーションアプリ - 機能テスト
UNICODE問題を回避した動作確認版
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import uvicorn
import threading
import time
import subprocess
import sys

# データモデル
class UserProfile(BaseModel):
    uid: str
    yu_level: int = 1
    player_level: int = 1
    total_xp: int = 0
    crystal_gauges: Dict[str, int] = {}

class TaskCompletion(BaseModel):
    task_id: str
    uid: str
    difficulty: int
    mood_coefficient: float = 1.0
    adhd_assist: float = 1.0

class XPResponse(BaseModel):
    xp_earned: int
    new_total_xp: int
    level_up: bool
    new_level: int

# 複数のサービスを作成
def create_core_game_service():
    app = FastAPI(title="Core Game Engine", version="1.0.0")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # インメモリデータストア
    users = {}
    
    @app.get("/")
    async def root():
        return {"message": "Core Game Engine is running!", "status": "ok"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "service": "core-game"}
    
    @app.post("/api/xp/calculate", response_model=XPResponse)
    async def calculate_xp(task: TaskCompletion):
        # XP計算: difficulty × mood_coefficient × adhd_assist
        xp_earned = int(task.difficulty * 10 * task.mood_coefficient * task.adhd_assist)
        
        # ユーザー情報取得または作成
        if task.uid not in users:
            users[task.uid] = UserProfile(uid=task.uid)
        
        user = users[task.uid]
        old_level = user.player_level
        user.total_xp += xp_earned
        
        # レベル計算（簡単な式）
        new_level = int((user.total_xp / 100) ** 0.5) + 1
        level_up = new_level > old_level
        user.player_level = new_level
        
        return XPResponse(
            xp_earned=xp_earned,
            new_total_xp=user.total_xp,
            level_up=level_up,
            new_level=new_level
        )
    
    @app.get("/api/user/{uid}")
    async def get_user(uid: str):
        if uid not in users:
            users[uid] = UserProfile(uid=uid)
        return users[uid]
    
    return app

def create_auth_service():
    app = FastAPI(title="Authentication Service", version="1.0.0")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root():
        return {"message": "Auth Service is running!", "status": "ok"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "service": "auth"}
    
    @app.post("/api/login")
    async def login(credentials: dict):
        return {
            "token": "mock_jwt_token",
            "user_id": "user_123",
            "expires_in": 3600
        }
    
    return app

def create_task_service():
    app = FastAPI(title="Task Management Service", version="1.0.0")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    tasks = {}
    
    @app.get("/")
    async def root():
        return {"message": "Task Management Service is running!", "status": "ok"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "service": "task-management"}
    
    @app.get("/api/tasks/{uid}")
    async def get_tasks(uid: str):
        return {
            "uid": uid,
            "tasks": [
                {"id": "task_1", "type": "routine", "description": "朝の運動", "difficulty": 2},
                {"id": "task_2", "type": "social", "description": "友人との会話", "difficulty": 3},
                {"id": "task_3", "type": "skill_up", "description": "新しいスキル学習", "difficulty": 4}
            ]
        }
    
    @app.post("/api/tasks/{uid}/complete")
    async def complete_task(uid: str, task_data: dict):
        return {
            "success": True,
            "message": "Task completed successfully",
            "xp_earned": task_data.get("difficulty", 1) * 10
        }
    
    return app

def run_service(app, port):
    """サービスを指定ポートで実行"""
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

def main():
    print("🎮 治療的ゲーミフィケーションアプリ - 機能テスト版")
    print("="*60)
    
    services = [
        ("Core Game", create_core_game_service(), 8001),
        ("Auth", create_auth_service(), 8002),
        ("Task Management", create_task_service(), 8003)
    ]
    
    threads = []
    
    try:
        # 各サービスを別スレッドで起動
        for name, app, port in services:
            print(f"🚀 {name} サービス起動中... (ポート: {port})")
            thread = threading.Thread(
                target=run_service, 
                args=(app, port),
                daemon=True
            )
            thread.start()
            threads.append((name, thread, port))
            time.sleep(1)
        
        print("\n✅ 全サービス起動完了!")
        print("\n🌐 アクセス可能なエンドポイント:")
        
        for name, thread, port in threads:
            print(f"  • {name}: http://localhost:{port}")
            print(f"    - Health: http://localhost:{port}/health")
            print(f"    - API Docs: http://localhost:{port}/docs")
        
        print("\n📋 テスト用API呼び出し例:")
        print("  curl http://localhost:8001/health")
        print("  curl http://localhost:8002/api/login -X POST -d '{}'")
        print("  curl http://localhost:8003/api/tasks/user123")
        
        print("\n⚠️ 終了するには Ctrl+C を押してください")
        print("="*60)
        
        # メインスレッドを維持
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 サービス停止中...")
        print("🎯 停止完了")

if __name__ == "__main__":
    main()