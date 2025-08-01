"""
システムAPI?
Simple API test for core game engine
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi.testclient import TestClient
from main import app

def test_api():
    """基本API?"""
    client = TestClient(app)
    
    print("=== Core Game API Test ===")
    
    # 1. ヘルパー
    response = client.get("/health")
    print(f"1. Health check: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Service: {data['service']}")
        print(f"   Status: {data['status']}")
    
    # 2. XP?
    xp_request = {
        "uid": "test_user_simple",
        "xp_amount": 150,
        "source": "simple_test"
    }
    
    response = client.post("/xp/add", json=xp_request)
    print(f"2. XP add: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   XP added: {data['xp_added']}")
        print(f"   Level: {data['old_level']} ? {data['new_level']}")
        print(f"   Level up: {data['level_up']}")
        
        if data.get('resonance_event'):
            resonance = data['resonance_event']
            print(f"   Resonance: {resonance['type']} (+{resonance['bonus_xp']} XP)")
    
    # 3. レベル
    progress_request = {"uid": "test_user_simple"}
    response = client.post("/level/progress", json=progress_request)
    print(f"3. Level progress: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        player = data['data']['player']
        print(f"   Current level: {player['current_level']}")
        print(f"   Progress: {player['progress_percentage']:.1f}%")
    
    # 4. システム
    status_request = {"uid": "test_user_simple"}
    response = client.post("/system/status", json=status_request)
    print(f"4. System status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        status = data['data']
        print(f"   Player Level: {status['player_level']}")
        print(f"   Yu Level: {status['yu_level']}")
        print(f"   Resonance available: {status['resonance_available']}")
    
    print("=== API Test Completed ===")

if __name__ == "__main__":
    test_api()