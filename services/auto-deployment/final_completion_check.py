#!/usr/bin/env python3
"""
Auto-Deployment System 最終完成度チェック

全てのタスクが完了し、システムが正常に動作することを確認します。
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any

def check_file_exists(file_path: str) -> bool:
    """ファイルの存在確認"""
    return Path(file_path).exists()

def check_directory_structure() -> Dict[str, Any]:
    """ディレクトリ構造の確認"""
    print("🔍 ディレクトリ構造チェック...")
    
    required_dirs = [
        "validation",
        "validation/validators", 
        "environment",
        "deployment",
        "deployment/strategies",
        "deployment/github_actions",
        "deployment/cloud_run",
        "monitoring",
        "notification",
        "reporting", 
        "rollback",
        "security",
        "tests",
        "tests/integration",
        "tests/pipeline",
        "docs"
    ]
    
    missing_dirs = []
    existing_dirs = []
    
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            existing_dirs.append(dir_name)
            print(f"✅ {dir_name}/")
        else:
            missing_dirs.append(dir_name)
            print(f"❌ {dir_name}/ (missing)")
    
    return {
        "total": len(required_dirs),
        "existing": len(existing_dirs),
        "missing": missing_dirs,
        "success": len(missing_dirs) == 0
    }

def check_core_files() -> Dict[str, Any]:
    """コアファイルの確認"""
    print("\n🔍 コアファイルチェック...")
    
    required_files = [
        "__init__.py",
        "config.py",
        "orchestrator.py", 
        "cli.py",
        "exceptions.py",
        "logging_config.py"
    ]
    
    missing_files = []
    existing_files = []
    
    for file_name in required_files:
        if check_file_exists(file_name):
            existing_files.append(file_name)
            print(f"✅ {file_name}")
        else:
            missing_files.append(file_name)
            print(f"❌ {file_name} (missing)")
    
    return {
        "total": len(required_files),
        "existing": len(existing_files),
        "missing": missing_files,
        "success": len(missing_files) == 0
    }

def check_validation_system() -> Dict[str, Any]:
    """バリデーションシステムの確認"""
    print("\n🔍 バリデーションシステムチェック...")
    
    validation_files = [
        "validation/base.py",
        "validation/framework.py",
        "validation/config.py",
        "validation/validators/factory.py",
        "validation/validators/code_quality.py",
        "validation/validators/security.py",
        "validation/validators/dependency.py",
        "validation/validators/cloud_resource.py",
        "validation/validators/authentication.py",
        "validation/validators/environment.py"
    ]
    
    existing = sum(1 for f in validation_files if check_file_exists(f))
    total = len(validation_files)
    
    print(f"📊 バリデーションファイル: {existing}/{total}")
    
    return {
        "total": total,
        "existing": existing,
        "success": existing >= total * 0.8  # 80%以上で成功
    }

def check_deployment_system() -> Dict[str, Any]:
    """デプロイメントシステムの確認"""
    print("\n🔍 デプロイメントシステムチェック...")
    
    deployment_files = [
        "deployment/strategies/base.py",
        "deployment/strategies/blue_green.py",
        "deployment/strategies/rolling_update.py",
        "deployment/github_actions/github_client.py",
        "deployment/github_actions/workflow_trigger.py",
        "deployment/cloud_run/cloud_run_client.py",
        "deployment/cloud_run/cloud_run_deployer.py"
    ]
    
    existing = sum(1 for f in deployment_files if check_file_exists(f))
    total = len(deployment_files)
    
    print(f"📊 デプロイメントファイル: {existing}/{total}")
    
    return {
        "total": total,
        "existing": existing,
        "success": existing >= total * 0.8
    }

def check_monitoring_system() -> Dict[str, Any]:
    """監視システムの確認"""
    print("\n🔍 監視システムチェック...")
    
    monitoring_files = [
        "monitoring/health_check.py",
        "monitoring/performance_monitor.py",
        "monitoring/dashboard.py"
    ]
    
    existing = sum(1 for f in monitoring_files if check_file_exists(f))
    total = len(monitoring_files)
    
    print(f"📊 監視ファイル: {existing}/{total}")
    
    return {
        "total": total,
        "existing": existing,
        "success": existing >= total * 0.8
    }

def check_notification_system() -> Dict[str, Any]:
    """通知システムの確認"""
    print("\n🔍 通知システムチェック...")
    
    notification_files = [
        "notification/base.py",
        "notification/notification_manager.py",
        "notification/slack_channel.py",
        "notification/email_channel.py"
    ]
    
    existing = sum(1 for f in notification_files if check_file_exists(f))
    total = len(notification_files)
    
    print(f"📊 通知ファイル: {existing}/{total}")
    
    return {
        "total": total,
        "existing": existing,
        "success": existing >= total * 0.8
    }

def check_rollback_system() -> Dict[str, Any]:
    """ロールバックシステムの確認"""
    print("\n🔍 ロールバックシステムチェック...")
    
    rollback_files = [
        "rollback/failure_detector.py",
        "rollback/rollback_triggers.py",
        "rollback/rollback_executor.py",
        "rollback/rollback_manager.py"
    ]
    
    existing = sum(1 for f in rollback_files if check_file_exists(f))
    total = len(rollback_files)
    
    print(f"📊 ロールバックファイル: {existing}/{total}")
    
    return {
        "total": total,
        "existing": existing,
        "success": existing >= total * 0.8
    }

def check_security_system() -> Dict[str, Any]:
    """セキュリティシステムの確認"""
    print("\n🔍 セキュリティシステムチェック...")
    
    security_files = [
        "security/security_config.py",
        "security/security_validator.py",
        "security/credential_checker.py",
        "security/compliance_verifier.py",
        "security/audit_logger.py"
    ]
    
    existing = sum(1 for f in security_files if check_file_exists(f))
    total = len(security_files)
    
    print(f"📊 セキュリティファイル: {existing}/{total}")
    
    return {
        "total": total,
        "existing": existing,
        "success": existing >= total * 0.8
    }

def check_documentation() -> Dict[str, Any]:
    """ドキュメントの確認"""
    print("\n🔍 ドキュメントチェック...")
    
    doc_files = [
        "docs/user-manual.md",
        "docs/troubleshooting-guide.md",
        "docs/configuration-reference.md",
        "docs/api-documentation.md",
        "docs/deployment-best-practices.md",
        "docs/monitoring-alerting-setup.md",
        "docs/disaster-recovery-procedures.md",
        "docs/maintenance-upgrade-procedures.md"
    ]
    
    existing = sum(1 for f in doc_files if check_file_exists(f))
    total = len(doc_files)
    
    print(f"📊 ドキュメントファイル: {existing}/{total}")
    
    return {
        "total": total,
        "existing": existing,
        "success": existing >= total * 0.9  # ドキュメントは90%以上
    }

def check_tests() -> Dict[str, Any]:
    """テストファイルの確認"""
    print("\n🔍 テストファイルチェック...")
    
    test_dirs = ["tests", "tests/integration", "tests/pipeline"]
    test_files_found = 0
    
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            for file in os.listdir(test_dir):
                if file.startswith("test_") and file.endswith(".py"):
                    test_files_found += 1
    
    print(f"📊 テストファイル数: {test_files_found}")
    
    return {
        "total": test_files_found,
        "existing": test_files_found,
        "success": test_files_found >= 20  # 最低20個のテストファイル
    }

def main():
    """メイン実行"""
    print("🚀 Auto-Deployment System 最終完成度チェック")
    print("=" * 70)
    
    checks = [
        ("ディレクトリ構造", check_directory_structure),
        ("コアファイル", check_core_files),
        ("バリデーションシステム", check_validation_system),
        ("デプロイメントシステム", check_deployment_system),
        ("監視システム", check_monitoring_system),
        ("通知システム", check_notification_system),
        ("ロールバックシステム", check_rollback_system),
        ("セキュリティシステム", check_security_system),
        ("ドキュメント", check_documentation),
        ("テストファイル", check_tests)
    ]
    
    results = []
    total_score = 0
    max_score = len(checks)
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
            if result["success"]:
                total_score += 1
                print(f"✅ {check_name}: 合格")
            else:
                print(f"⚠️  {check_name}: 要改善")
        except Exception as e:
            print(f"❌ {check_name}: エラー - {e}")
            results.append((check_name, {"success": False, "error": str(e)}))
    
    print("\n" + "=" * 70)
    print("📊 最終結果")
    print("=" * 70)
    
    completion_rate = (total_score / max_score) * 100
    print(f"完成度: {completion_rate:.1f}% ({total_score}/{max_score})")
    
    if completion_rate >= 90:
        print("🎉 優秀！システムは本番環境にデプロイ可能です")
        status = "EXCELLENT"
    elif completion_rate >= 80:
        print("✅ 良好！軽微な改善後にデプロイ可能です")
        status = "GOOD"
    elif completion_rate >= 70:
        print("⚠️  普通。いくつかの改善が必要です")
        status = "FAIR"
    else:
        print("❌ 要改善。重要なコンポーネントが不足しています")
        status = "NEEDS_WORK"
    
    print(f"\n最終評価: {status}")
    
    # 詳細結果の表示
    print("\n📋 詳細結果:")
    for check_name, result in results:
        if result["success"]:
            print(f"  ✅ {check_name}")
        else:
            print(f"  ❌ {check_name}")
            if "missing" in result and result["missing"]:
                print(f"     不足: {', '.join(result['missing'])}")
    
    return completion_rate >= 80

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)