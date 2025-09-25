#!/usr/bin/env python3
"""
Auto-Deployment System 基本機能テスト

システムの基本的な機能が正常に動作するかを確認します。
"""

import asyncio
import sys
import os

# パスの設定
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_imports():
    """基本的なインポートテスト"""
    print("🔍 インポートテスト開始...")
    
    try:
        from config import Environment, DeploymentStrategy, DeploymentConfig
        print("✅ config モジュール: OK")
        
        from exceptions import DeploymentError, PreDeploymentError
        print("✅ exceptions モジュール: OK")
        
        from orchestrator import DeploymentOrchestrator, DeploymentStatus
        print("✅ orchestrator モジュール: OK")
        
        print("✅ 全てのインポートが成功しました")
        return True
        
    except Exception as e:
        print(f"❌ インポートエラー: {e}")
        return False

def test_config_creation():
    """設定作成テスト"""
    print("\n🔍 設定作成テスト開始...")
    
    try:
        from config import Environment, DeploymentConfig, default_config_manager
        
        # 各環境の設定を作成
        for env in Environment:
            config = default_config_manager.get_config(env)
            print(f"✅ {env.value} 環境設定: OK")
            
            # 基本的な設定値を確認
            assert config.environment == env
            assert config.cloud_config.project_id is not None
            assert config.cloud_config.region is not None
            
        print("✅ 設定作成テストが成功しました")
        return True
        
    except Exception as e:
        print(f"❌ 設定作成エラー: {e}")
        return False

async def test_orchestrator_creation():
    """オーケストレータ作成テスト"""
    print("\n🔍 オーケストレータ作成テスト開始...")
    
    try:
        from orchestrator import DeploymentOrchestrator
        from config import Environment, default_config_manager
        
        # オーケストレータを作成
        config = default_config_manager.get_config(Environment.DEVELOPMENT)
        orchestrator = DeploymentOrchestrator(config)
        
        print("✅ オーケストレータ作成: OK")
        
        # 基本的なプロパティを確認
        assert orchestrator.config is not None
        assert len(orchestrator.deployment_steps) > 0
        
        print("✅ オーケストレータ作成テストが成功しました")
        return True
        
    except Exception as e:
        print(f"❌ オーケストレータ作成エラー: {e}")
        return False

def test_cli_import():
    """CLI インポートテスト"""
    print("\n🔍 CLI インポートテスト開始...")
    
    try:
        from cli import cli, CLIColors
        print("✅ CLI インポート: OK")
        
        # CLIコマンドが存在することを確認
        assert cli is not None
        assert hasattr(CLIColors, 'GREEN')
        
        print("✅ CLI インポートテストが成功しました")
        return True
        
    except Exception as e:
        print(f"❌ CLI インポートエラー: {e}")
        return False

async def main():
    """メインテスト実行"""
    print("🚀 Auto-Deployment System 基本機能テスト開始")
    print("=" * 60)
    
    tests = [
        ("インポートテスト", test_imports),
        ("設定作成テスト", test_config_creation),
        ("オーケストレータ作成テスト", test_orchestrator_creation),
        ("CLI インポートテスト", test_cli_import),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} で予期しないエラー: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 テスト結果: {passed}/{total} 成功")
    
    if passed == total:
        print("🎉 全てのテストが成功しました！")
        return True
    else:
        print("⚠️  一部のテストが失敗しました")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)