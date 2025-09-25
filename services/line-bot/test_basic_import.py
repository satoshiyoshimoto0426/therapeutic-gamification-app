#!/usr/bin/env python3
"""
LINE Bot サービスの基本インポートテスト
"""

def test_basic_imports():
    """基本的なインポートのテスト"""
    try:
        from fastapi import FastAPI
        print("✅ FastAPI import: OK")
        
        from linebot import LineBotApi, WebhookHandler
        print("✅ LINE Bot API import: OK")
        
        from linebot.models import MessageEvent, TextMessage, TextSendMessage
        print("✅ LINE Bot basic models import: OK")
        
        # FlexMessage関連は optional として扱う
        try:
            from linebot.models import FlexMessage
            print("✅ FlexMessage import: OK")
        except ImportError:
            print("⚠️  FlexMessage import: Not available (will use fallback)")
        
        print("✅ LINE Bot service basic imports: All OK")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

if __name__ == "__main__":
    success = test_basic_imports()
    exit(0 if success else 1)