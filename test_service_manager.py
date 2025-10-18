"""
サービスマネージャーのテスト
"""

import time
import json
from local_service_manager import LocalServiceManager, ServiceStatus


def test_config_loading():
    """設定ファイルの読み込みテスト"""
    print("=" * 60)
    print("テスト1: 設定ファイルの読み込み")
    print("=" * 60)
    
    try:
        manager = LocalServiceManager()
        
        print(f"✓ 設定ファイルを読み込みました")
        print(f"  サービス数: {len(manager.services)}")
        print(f"  フロントエンド: {'あり' if manager.frontend_info else 'なし'}")
        
        print("\n登録されているサービス:")
        for service_name, service_info in manager.services.items():
            config = service_info.config
            print(f"  - {config.display_name} ({service_name})")
            print(f"    ポート: {config.port}")
            print(f"    必須: {'はい' if config.required else 'いいえ'}")
        
        return True
        
    except Exception as e:
        print(f"✗ エラー: {e}")
        return False


def test_service_status():
    """サービス状態の取得テスト"""
    print("\n" + "=" * 60)
    print("テスト2: サービス状態の取得")
    print("=" * 60)
    
    try:
        manager = LocalServiceManager()
        
        # 全サービスの状態を取得
        statuses = manager.get_all_services_status()
        
        print(f"✓ サービス状態を取得しました")
        print(f"  サービス数: {len(statuses)}")
        
        for service_name, status in statuses.items():
            print(f"\n  {service_name}:")
            print(f"    表示名: {status.get('display_name')}")
            print(f"    状態: {status.get('status')}")
            print(f"    ポート: {status.get('port')}")
        
        return True
        
    except Exception as e:
        print(f"✗ エラー: {e}")
        return False


def test_single_service_start_stop():
    """個別サービスの起動・停止テスト"""
    print("\n" + "=" * 60)
    print("テスト3: 個別サービスの起動・停止")
    print("=" * 60)
    
    try:
        manager = LocalServiceManager()
        
        # 認証サービスを起動
        print("\n認証サービスを起動します...")
        success = manager.start_service("auth")
        
        if success:
            print("✓ 認証サービスが起動しました")
            
            # 状態確認
            time.sleep(2)
            health = manager.check_service_health("auth")
            print(f"\nヘルスチェック結果:")
            print(f"  健全性: {'正常' if health.get('healthy') else '異常'}")
            print(f"  ステータス: {health.get('status')}")
            
            # ログ確認
            logs = manager.get_service_logs("auth", lines=5)
            print(f"\n最新ログ（5行）:")
            for log in logs:
                print(f"  {log}")
            
            # 停止
            print("\n認証サービスを停止します...")
            manager.stop_service("auth")
            print("✓ 認証サービスを停止しました")
            
            return True
        else:
            print("✗ 認証サービスの起動に失敗しました")
            return False
        
    except Exception as e:
        print(f"✗ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_health_check():
    """ヘルスチェック機能のテスト"""
    print("\n" + "=" * 60)
    print("テスト4: ヘルスチェック機能")
    print("=" * 60)
    
    try:
        manager = LocalServiceManager()
        
        # サービスを起動
        print("認証サービスを起動します...")
        manager.start_service("auth")
        
        # ヘルスチェック
        print("\nヘルスチェックを実行します...")
        health = manager.check_service_health("auth")
        
        print(f"\nヘルスチェック結果:")
        print(json.dumps(health, indent=2, ensure_ascii=False))
        
        # クリーンアップ
        manager.stop_service("auth")
        
        return health.get("healthy", False)
        
    except Exception as e:
        print(f"✗ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_log_management():
    """ログ管理機能のテスト"""
    print("\n" + "=" * 60)
    print("テスト5: ログ管理機能")
    print("=" * 60)
    
    try:
        manager = LocalServiceManager()
        
        # サービスを起動
        print("認証サービスを起動します...")
        manager.start_service("auth")
        
        # ログが収集されるまで待機
        time.sleep(3)
        
        # ログ取得
        logs = manager.get_service_logs("auth", lines=10)
        print(f"\n✓ ログを取得しました: {len(logs)}行")
        
        # ログ表示
        print("\n最新ログ:")
        for log in logs[-5:]:
            print(f"  {log}")
        
        # ログ保存
        output_file = "test_auth_service.log"
        success = manager.save_service_logs("auth", output_file)
        
        if success:
            print(f"\n✓ ログをファイルに保存しました: {output_file}")
        
        # クリーンアップ
        manager.stop_service("auth")
        
        return True
        
    except Exception as e:
        print(f"✗ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_status_summary():
    """状態サマリー表示のテスト"""
    print("\n" + "=" * 60)
    print("テスト6: 状態サマリー表示")
    print("=" * 60)
    
    try:
        manager = LocalServiceManager()
        
        # いくつかのサービスを起動
        print("サービスを起動します...")
        manager.start_service("auth")
        time.sleep(1)
        manager.start_service("core-game")
        
        # 状態サマリー表示
        print("\n")
        manager.display_status_summary()
        
        # クリーンアップ
        print("\nサービスを停止します...")
        manager.stop_all_services()
        
        return True
        
    except Exception as e:
        print(f"✗ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """メイン関数"""
    print("サービスマネージャーのテストを開始します\n")
    
    results = []
    
    # テスト実行
    results.append(("設定ファイルの読み込み", test_config_loading()))
    results.append(("サービス状態の取得", test_service_status()))
    results.append(("個別サービスの起動・停止", test_single_service_start_stop()))
    results.append(("ヘルスチェック機能", test_health_check()))
    results.append(("ログ管理機能", test_log_management()))
    results.append(("状態サマリー表示", test_status_summary()))
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print("テスト結果サマリー")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 成功" if result else "✗ 失敗"
        print(f"{status}: {test_name}")
    
    print("=" * 60)
    print(f"合計: {passed}/{total} 成功")
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
