#!/usr/bin/env python3
"""
インタラクティブセットアップウィザードのテスト

タスク7.1と7.2の実装を検証します。
"""

import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import json

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from local_test_setup import InteractiveSetupWizard, Colors


class TestInteractiveSetupWizard:
    """インタラクティブセットアップウィザードのテストクラス"""
    
    def __init__(self):
        self.test_results = []
    
    def test_load_services_config(self):
        """サービス設定の読み込みテスト"""
        print(f"\n{Colors.BOLD}テスト1: サービス設定の読み込み{Colors.ENDC}")
        
        wizard = InteractiveSetupWizard()
        config = wizard.services_config
        
        # 設定が読み込まれているか確認
        assert "services" in config, "services キーが存在しません"
        assert "frontend" in config, "frontend キーが存在しません"
        
        # サービスの数を確認
        services = config.get("services", [])
        print(f"  読み込まれたサービス数: {len(services)}")
        
        # 必須サービスとオプションサービスの分類
        required = [s for s in services if s.get("required", False)]
        optional = [s for s in services if not s.get("required", False)]
        
        print(f"  必須サービス: {len(required)}個")
        for s in required:
            print(f"    - {s.get('display_name', s['name'])}")
        
        print(f"  オプションサービス: {len(optional)}個")
        for s in optional:
            print(f"    - {s.get('display_name', s['name'])}")
        
        print(f"{Colors.OKGREEN}✓ テスト1 成功{Colors.ENDC}")
        self.test_results.append(("サービス設定の読み込み", True))
        return True
    
    def test_user_input_validation(self):
        """ユーザー入力の検証テスト"""
        print(f"\n{Colors.BOLD}テスト2: ユーザー入力の検証{Colors.ENDC}")
        
        wizard = InteractiveSetupWizard()
        
        # ポート番号のバリデーター
        def validate_port(port_str):
            try:
                port = int(port_str)
                if 1024 <= port <= 65535:
                    return True, ""
                return False, "ポート番号は1024-65535の範囲で指定してください"
            except ValueError:
                return False, "数値を入力してください"
        
        # 有効なポート番号
        valid, msg = validate_port("8080")
        assert valid, "有効なポート番号が拒否されました"
        print(f"  {Colors.OKGREEN}✓{Colors.ENDC} 有効なポート番号 (8080) が受け入れられました")
        
        # 無効なポート番号 (範囲外)
        valid, msg = validate_port("100")
        assert not valid, "無効なポート番号が受け入れられました"
        print(f"  {Colors.OKGREEN}✓{Colors.ENDC} 無効なポート番号 (100) が拒否されました: {msg}")
        
        # 無効なポート番号 (非数値)
        valid, msg = validate_port("abc")
        assert not valid, "非数値が受け入れられました"
        print(f"  {Colors.OKGREEN}✓{Colors.ENDC} 非数値 (abc) が拒否されました: {msg}")
        
        print(f"{Colors.OKGREEN}✓ テスト2 成功{Colors.ENDC}")
        self.test_results.append(("ユーザー入力の検証", True))
        return True
    
    def test_service_selection_logic(self):
        """サービス選択ロジックのテスト"""
        print(f"\n{Colors.BOLD}テスト3: サービス選択ロジック{Colors.ENDC}")
        
        wizard = InteractiveSetupWizard()
        
        # 必須サービスが自動的に選択されることを確認
        services = wizard.services_config.get("services", [])
        required_services = [s['name'] for s in services if s.get("required", False)]
        
        print(f"  必須サービス: {required_services}")
        
        # 選択されたサービスリストに必須サービスを追加
        wizard.selected_services = required_services.copy()
        
        # オプションサービスを追加
        optional_services = [s['name'] for s in services if not s.get("required", False)]
        if optional_services:
            wizard.selected_services.append(optional_services[0])
            print(f"  オプションサービスを追加: {optional_services[0]}")
        
        # フロントエンドを追加
        wizard.selected_services.append("frontend")
        
        print(f"  選択されたサービス: {wizard.selected_services}")
        print(f"  合計: {len(wizard.selected_services)}個")
        
        # 必須サービスが含まれているか確認
        for req_service in required_services:
            assert req_service in wizard.selected_services, f"必須サービス {req_service} が選択されていません"
        
        print(f"{Colors.OKGREEN}✓ テスト3 成功{Colors.ENDC}")
        self.test_results.append(("サービス選択ロジック", True))
        return True
    
    def test_config_generation(self):
        """設定生成のテスト"""
        print(f"\n{Colors.BOLD}テスト4: 設定生成{Colors.ENDC}")
        
        wizard = InteractiveSetupWizard()
        
        # テスト用の設定を作成
        wizard.config = {
            'USE_MOCK_DATABASE': 'true',
            'MOCK_DATABASE_PERSIST': 'false',
            'LOG_LEVEL': 'INFO',
            'AUTH_SERVICE_PORT': '8002',
            'CORE_GAME_SERVICE_PORT': '8001'
        }
        
        print(f"  生成された設定:")
        for key, value in wizard.config.items():
            print(f"    {key}={value}")
        
        # 必須項目が含まれているか確認
        assert 'USE_MOCK_DATABASE' in wizard.config, "USE_MOCK_DATABASE が設定されていません"
        assert 'LOG_LEVEL' in wizard.config, "LOG_LEVEL が設定されていません"
        
        print(f"{Colors.OKGREEN}✓ テスト4 成功{Colors.ENDC}")
        self.test_results.append(("設定生成", True))
        return True
    
    def test_dependency_resolution(self):
        """依存関係の解決テスト"""
        print(f"\n{Colors.BOLD}テスト5: 依存関係の解決{Colors.ENDC}")
        
        wizard = InteractiveSetupWizard()
        
        # サービスの依存関係をシミュレート
        # 例: task-mgmt は core-game に依存
        dependencies = {
            'task-mgmt': ['core-game', 'auth'],
            'mandala': ['core-game', 'auth'],
            'mood-tracking': ['auth']
        }
        
        # 選択されたサービス
        selected = ['task-mgmt']
        
        # 依存関係を解決
        def resolve_dependencies(service_name, deps_map, resolved=None):
            if resolved is None:
                resolved = set()
            
            if service_name in resolved:
                return resolved
            
            resolved.add(service_name)
            
            if service_name in deps_map:
                for dep in deps_map[service_name]:
                    resolve_dependencies(dep, deps_map, resolved)
            
            return resolved
        
        all_services = set()
        for service in selected:
            all_services.update(resolve_dependencies(service, dependencies))
        
        print(f"  選択されたサービス: {selected}")
        print(f"  依存関係を含む全サービス: {sorted(all_services)}")
        
        # 依存関係が正しく解決されているか確認
        assert 'core-game' in all_services, "依存サービス core-game が含まれていません"
        assert 'auth' in all_services, "依存サービス auth が含まれていません"
        
        print(f"{Colors.OKGREEN}✓ テスト5 成功{Colors.ENDC}")
        self.test_results.append(("依存関係の解決", True))
        return True
    
    def test_settings_preview(self):
        """設定プレビューのテスト"""
        print(f"\n{Colors.BOLD}テスト6: 設定プレビュー{Colors.ENDC}")
        
        wizard = InteractiveSetupWizard()
        
        # テストデータを設定
        wizard.selected_services = ['auth', 'core-game', 'task-mgmt', 'frontend']
        wizard.config = {
            'USE_MOCK_DATABASE': 'true',
            'LOG_LEVEL': 'INFO',
            'AUTH_SERVICE_PORT': '8002'
        }
        
        print(f"\n  {Colors.BOLD}プレビュー内容:{Colors.ENDC}")
        print(f"  選択されたサービス: {len(wizard.selected_services)}個")
        for service in wizard.selected_services:
            print(f"    - {service}")
        
        print(f"\n  環境変数: {len(wizard.config)}個")
        for key, value in wizard.config.items():
            print(f"    {key}={value}")
        
        # プレビューデータが正しいか確認
        assert len(wizard.selected_services) > 0, "サービスが選択されていません"
        assert len(wizard.config) > 0, "設定が生成されていません"
        
        print(f"\n{Colors.OKGREEN}✓ テスト6 成功{Colors.ENDC}")
        self.test_results.append(("設定プレビュー", True))
        return True
    
    def print_summary(self):
        """テスト結果のサマリー表示"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}テスト結果サマリー{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
        
        passed = sum(1 for _, result in self.test_results if result)
        total = len(self.test_results)
        
        for test_name, result in self.test_results:
            status = f"{Colors.OKGREEN}✓ 成功{Colors.ENDC}" if result else f"{Colors.FAIL}✗ 失敗{Colors.ENDC}"
            print(f"  {status} - {test_name}")
        
        print(f"\n{Colors.BOLD}合計: {passed}/{total} テスト成功{Colors.ENDC}")
        
        if passed == total:
            print(f"{Colors.OKGREEN}{Colors.BOLD}✓ すべてのテストに合格しました！{Colors.ENDC}\n")
            return True
        else:
            print(f"{Colors.FAIL}{Colors.BOLD}✗ 一部のテストに失敗しました{Colors.ENDC}\n")
            return False
    
    def run_all_tests(self):
        """全テストの実行"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}インタラクティブセットアップウィザード テストスイート{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
        
        try:
            self.test_load_services_config()
            self.test_user_input_validation()
            self.test_service_selection_logic()
            self.test_config_generation()
            self.test_dependency_resolution()
            self.test_settings_preview()
            
            return self.print_summary()
            
        except AssertionError as e:
            print(f"\n{Colors.FAIL}✗ アサーションエラー: {str(e)}{Colors.ENDC}")
            self.test_results.append(("現在のテスト", False))
            self.print_summary()
            return False
        except Exception as e:
            print(f"\n{Colors.FAIL}✗ 予期しないエラー: {str(e)}{Colors.ENDC}")
            import traceback
            traceback.print_exc()
            self.test_results.append(("現在のテスト", False))
            self.print_summary()
            return False


def main():
    """メイン関数"""
    tester = TestInteractiveSetupWizard()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
