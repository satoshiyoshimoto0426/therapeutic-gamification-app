#!/usr/bin/env python3
"""
本番環境設定検証スクリプト
Google Cloud Platform設定、Firestore、Cloud Run、Secret Manager設定の検証を行う
"""

import json
import yaml
import subprocess
import sys
import os
from typing import Dict, List, Tuple, Any
from datetime import datetime
import logging

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('production_validation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ProductionConfigValidator:
    """本番環境設定検証クラス"""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.validation_results = {
            "timestamp": datetime.now().isoformat(),
            "project_id": project_id,
            "validations": {},
            "errors": [],
            "warnings": [],
            "overall_status": "UNKNOWN"
        }
    
    def run_gcloud_command(self, command: List[str]) -> Tuple[bool, str, str]:
        """gcloudコマンドを実行"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
    
    def validate_project_setup(self) -> bool:
        """プロジェクト基本設定の検証"""
        logger.info("プロジェクト基本設定を検証中...")
        
        # プロジェクト存在確認
        success, stdout, stderr = self.run_gcloud_command([
            "gcloud", "projects", "describe", self.project_id, "--format=json"
        ])
        
        if not success:
            self.validation_results["errors"].append(f"プロジェクト {self.project_id} が見つかりません: {stderr}")
            return False
        
        project_info = json.loads(stdout)
        self.validation_results["validations"]["project"] = {
            "status": "VALID",
            "project_id": project_info.get("projectId"),
            "project_number": project_info.get("projectNumber"),
            "lifecycle_state": project_info.get("lifecycleState")
        }
        
        # 必要なAPIの有効化確認
        required_apis = [
            "run.googleapis.com",
            "firestore.googleapis.com",
            "storage.googleapis.com",
            "secretmanager.googleapis.com",
            "cloudkms.googleapis.com",
            "monitoring.googleapis.com",
            "logging.googleapis.com",
            "cloudbuild.googleapis.com"
        ]
        
        enabled_apis = []
        for api in required_apis:
            success, stdout, stderr = self.run_gcloud_command([
                "gcloud", "services", "list", "--enabled", 
                f"--filter=name:{api}", "--format=value(name)"
            ])
            
            if success and api in stdout:
                enabled_apis.append(api)
            else:
                self.validation_results["errors"].append(f"API {api} が有効化されていません")
        
        self.validation_results["validations"]["apis"] = {
            "status": "VALID" if len(enabled_apis) == len(required_apis) else "INVALID",
            "enabled_apis": enabled_apis,
            "required_apis": required_apis
        }
        
        return len(enabled_apis) == len(required_apis)
    
    def validate_cloud_run_config(self) -> bool:
        """Cloud Run設定の検証"""
        logger.info("Cloud Run設定を検証中...")
        
        # Cloud Runサービス存在確認
        success, stdout, stderr = self.run_gcloud_command([
            "gcloud", "run", "services", "list", 
            "--filter=metadata.name:therapeutic-gamification-app",
            "--format=json"
        ])
        
        if not success:
            self.validation_results["errors"].append(f"Cloud Runサービス確認エラー: {stderr}")
            return False
        
        services = json.loads(stdout) if stdout.strip() else []
        
        if not services:
            self.validation_results["warnings"].append("Cloud Runサービス 'therapeutic-gamification-app' が見つかりません")
            self.validation_results["validations"]["cloud_run"] = {
                "status": "NOT_DEPLOYED",
                "message": "サービスが未デプロイ"
            }
            return True  # デプロイ前なので警告のみ
        
        service = services[0]
        self.validation_results["validations"]["cloud_run"] = {
            "status": "VALID",
            "service_name": service.get("metadata", {}).get("name"),
            "region": service.get("metadata", {}).get("labels", {}).get("cloud.googleapis.com/location"),
            "url": service.get("status", {}).get("url"),
            "ready": service.get("status", {}).get("conditions", [{}])[0].get("status") == "True"
        }
        
        return True
    
    def validate_firestore_config(self) -> bool:
        """Firestore設定の検証"""
        logger.info("Firestore設定を検証中...")
        
        # Firestoreデータベース存在確認
        success, stdout, stderr = self.run_gcloud_command([
            "gcloud", "firestore", "databases", "list", "--format=json"
        ])
        
        if not success:
            self.validation_results["errors"].append(f"Firestoreデータベース確認エラー: {stderr}")
            return False
        
        databases = json.loads(stdout) if stdout.strip() else []
        
        # デフォルトデータベースの確認
        default_db = next((db for db in databases if db.get("name").endswith("/(default)")), None)
        
        if not default_db:
            self.validation_results["errors"].append("Firestoreデフォルトデータベースが見つかりません")
            return False
        
        self.validation_results["validations"]["firestore"] = {
            "status": "VALID",
            "database_id": default_db.get("name"),
            "location_id": default_db.get("locationId"),
            "type": default_db.get("type")
        }
        
        # セキュリティルールの確認
        success, stdout, stderr = self.run_gcloud_command([
            "gcloud", "firestore", "rules", "list", "--format=json"
        ])
        
        if success and stdout.strip():
            rules = json.loads(stdout)
            self.validation_results["validations"]["firestore"]["security_rules"] = {
                "status": "CONFIGURED",
                "rules_count": len(rules)
            }
        else:
            self.validation_results["warnings"].append("Firestoreセキュリティルールが設定されていません")
        
        return True
    
    def validate_secret_manager_config(self) -> bool:
        """Secret Manager設定の検証"""
        logger.info("Secret Manager設定を検証中...")
        
        required_secrets = [
            "openai-api-key",
            "line-channel-secret", 
            "jwt-secret",
            "stripe-secret-key"
        ]
        
        existing_secrets = []
        
        for secret_name in required_secrets:
            success, stdout, stderr = self.run_gcloud_command([
                "gcloud", "secrets", "describe", secret_name, "--format=json"
            ])
            
            if success:
                secret_info = json.loads(stdout)
                existing_secrets.append({
                    "name": secret_name,
                    "status": "EXISTS",
                    "replication": secret_info.get("replication", {}).get("replication"),
                    "labels": secret_info.get("labels", {})
                })
            else:
                self.validation_results["warnings"].append(f"Secret '{secret_name}' が見つかりません")
                existing_secrets.append({
                    "name": secret_name,
                    "status": "MISSING"
                })
        
        self.validation_results["validations"]["secret_manager"] = {
            "status": "VALID" if len([s for s in existing_secrets if s["status"] == "EXISTS"]) == len(required_secrets) else "PARTIAL",
            "secrets": existing_secrets
        }
        
        return True
    
    def validate_kms_config(self) -> bool:
        """Cloud KMS設定の検証"""
        logger.info("Cloud KMS設定を検証中...")
        
        # キーリング存在確認
        success, stdout, stderr = self.run_gcloud_command([
            "gcloud", "kms", "keyrings", "list", 
            "--location=asia-northeast1",
            "--filter=name:therapeutic-app-keyring",
            "--format=json"
        ])
        
        if not success:
            self.validation_results["errors"].append(f"KMSキーリング確認エラー: {stderr}")
            return False
        
        keyrings = json.loads(stdout) if stdout.strip() else []
        
        if not keyrings:
            self.validation_results["warnings"].append("KMSキーリング 'therapeutic-app-keyring' が見つかりません")
            self.validation_results["validations"]["kms"] = {
                "status": "NOT_CONFIGURED",
                "message": "キーリングが未作成"
            }
            return True  # 設定前なので警告のみ
        
        # 暗号化キー確認
        required_keys = ["openai-key", "line-key", "jwt-key", "stripe-key"]
        existing_keys = []
        
        for key_name in required_keys:
            success, stdout, stderr = self.run_gcloud_command([
                "gcloud", "kms", "keys", "list",
                "--location=asia-northeast1",
                "--keyring=therapeutic-app-keyring",
                f"--filter=name:{key_name}",
                "--format=json"
            ])
            
            if success and stdout.strip():
                keys = json.loads(stdout)
                if keys:
                    existing_keys.append(key_name)
        
        self.validation_results["validations"]["kms"] = {
            "status": "VALID" if len(existing_keys) == len(required_keys) else "PARTIAL",
            "keyring": keyrings[0].get("name"),
            "existing_keys": existing_keys,
            "required_keys": required_keys
        }
        
        return True
    
    def validate_vpc_security_config(self) -> bool:
        """VPC Security設定の検証"""
        logger.info("VPC Security設定を検証中...")
        
        # VPCネットワーク確認
        success, stdout, stderr = self.run_gcloud_command([
            "gcloud", "compute", "networks", "list", "--format=json"
        ])
        
        if not success:
            self.validation_results["errors"].append(f"VPCネットワーク確認エラー: {stderr}")
            return False
        
        networks = json.loads(stdout) if stdout.strip() else []
        default_network = next((net for net in networks if net.get("name") == "default"), None)
        
        self.validation_results["validations"]["vpc"] = {
            "status": "VALID" if default_network else "MISSING",
            "networks": [net.get("name") for net in networks]
        }
        
        # VPCコネクタ確認
        success, stdout, stderr = self.run_gcloud_command([
            "gcloud", "compute", "networks", "vpc-access", "connectors", "list",
            "--region=asia-northeast1", "--format=json"
        ])
        
        if success and stdout.strip():
            connectors = json.loads(stdout)
            self.validation_results["validations"]["vpc"]["connectors"] = len(connectors)
        else:
            self.validation_results["warnings"].append("VPCコネクタが設定されていません")
        
        return True
    
    def validate_monitoring_config(self) -> bool:
        """監視設定の検証"""
        logger.info("監視設定を検証中...")
        
        # アラートポリシー確認
        success, stdout, stderr = self.run_gcloud_command([
            "gcloud", "alpha", "monitoring", "policies", "list", "--format=json"
        ])
        
        if success and stdout.strip():
            policies = json.loads(stdout)
            therapeutic_policies = [p for p in policies if "therapeutic" in p.get("displayName", "").lower()]
            
            self.validation_results["validations"]["monitoring"] = {
                "status": "CONFIGURED" if therapeutic_policies else "NOT_CONFIGURED",
                "alert_policies": len(therapeutic_policies),
                "total_policies": len(policies)
            }
        else:
            self.validation_results["warnings"].append("監視アラートポリシーが設定されていません")
            self.validation_results["validations"]["monitoring"] = {
                "status": "NOT_CONFIGURED",
                "message": "アラートポリシー未設定"
            }
        
        return True
    
    def validate_logging_config(self) -> bool:
        """ログ設定の検証"""
        logger.info("ログ設定を検証中...")
        
        # ログシンク確認
        success, stdout, stderr = self.run_gcloud_command([
            "gcloud", "logging", "sinks", "list", "--format=json"
        ])
        
        if success and stdout.strip():
            sinks = json.loads(stdout)
            therapeutic_sinks = [s for s in sinks if "therapeutic" in s.get("name", "").lower()]
            
            self.validation_results["validations"]["logging"] = {
                "status": "CONFIGURED" if therapeutic_sinks else "NOT_CONFIGURED",
                "log_sinks": len(therapeutic_sinks),
                "total_sinks": len(sinks)
            }
        else:
            self.validation_results["warnings"].append("ログシンクが設定されていません")
            self.validation_results["validations"]["logging"] = {
                "status": "NOT_CONFIGURED",
                "message": "ログシンク未設定"
            }
        
        return True
    
    def validate_iam_permissions(self) -> bool:
        """IAM権限の検証"""
        logger.info("IAM権限を検証中...")
        
        # サービスアカウント確認
        success, stdout, stderr = self.run_gcloud_command([
            "gcloud", "iam", "service-accounts", "list",
            "--filter=email:therapeutic-app-service-account*",
            "--format=json"
        ])
        
        if success and stdout.strip():
            service_accounts = json.loads(stdout)
            if service_accounts:
                sa = service_accounts[0]
                self.validation_results["validations"]["iam"] = {
                    "status": "VALID",
                    "service_account": sa.get("email"),
                    "display_name": sa.get("displayName")
                }
            else:
                self.validation_results["warnings"].append("治療アプリ用サービスアカウントが見つかりません")
                self.validation_results["validations"]["iam"] = {
                    "status": "MISSING",
                    "message": "サービスアカウント未作成"
                }
        else:
            self.validation_results["errors"].append(f"サービスアカウント確認エラー: {stderr}")
            return False
        
        return True
    
    def validate_security_settings(self) -> bool:
        """セキュリティ設定の検証"""
        logger.info("セキュリティ設定を検証中...")
        
        # Cloud Armor設定確認
        success, stdout, stderr = self.run_gcloud_command([
            "gcloud", "compute", "security-policies", "list",
            "--filter=name:therapeutic-app-security-policy",
            "--format=json"
        ])
        
        if success and stdout.strip():
            policies = json.loads(stdout)
            if policies:
                policy = policies[0]
                self.validation_results["validations"]["security"] = {
                    "status": "CONFIGURED",
                    "cloud_armor_policy": policy.get("name"),
                    "rules_count": len(policy.get("rules", []))
                }
            else:
                self.validation_results["warnings"].append("Cloud Armorセキュリティポリシーが見つかりません")
                self.validation_results["validations"]["security"] = {
                    "status": "NOT_CONFIGURED",
                    "message": "Cloud Armor未設定"
                }
        else:
            self.validation_results["warnings"].append("Cloud Armor設定確認でエラーが発生しました")
        
        return True
    
    def run_full_validation(self) -> Dict[str, Any]:
        """全体検証の実行"""
        logger.info("本番環境設定の全体検証を開始...")
        
        validation_steps = [
            ("project_setup", self.validate_project_setup),
            ("cloud_run", self.validate_cloud_run_config),
            ("firestore", self.validate_firestore_config),
            ("secret_manager", self.validate_secret_manager_config),
            ("kms", self.validate_kms_config),
            ("vpc_security", self.validate_vpc_security_config),
            ("monitoring", self.validate_monitoring_config),
            ("logging", self.validate_logging_config),
            ("iam", self.validate_iam_permissions),
            ("security", self.validate_security_settings)
        ]
        
        success_count = 0
        total_count = len(validation_steps)
        
        for step_name, validation_func in validation_steps:
            try:
                logger.info(f"検証ステップ: {step_name}")
                if validation_func():
                    success_count += 1
                    logger.info(f"✓ {step_name} 検証完了")
                else:
                    logger.error(f"✗ {step_name} 検証失敗")
            except Exception as e:
                logger.error(f"✗ {step_name} 検証中にエラー: {str(e)}")
                self.validation_results["errors"].append(f"{step_name} 検証エラー: {str(e)}")
        
        # 全体ステータス決定
        if success_count == total_count and not self.validation_results["errors"]:
            self.validation_results["overall_status"] = "READY"
        elif success_count >= total_count * 0.8:  # 80%以上成功
            self.validation_results["overall_status"] = "MOSTLY_READY"
        else:
            self.validation_results["overall_status"] = "NOT_READY"
        
        self.validation_results["summary"] = {
            "total_validations": total_count,
            "successful_validations": success_count,
            "success_rate": success_count / total_count,
            "error_count": len(self.validation_results["errors"]),
            "warning_count": len(self.validation_results["warnings"])
        }
        
        logger.info(f"検証完了: {success_count}/{total_count} ステップ成功")
        logger.info(f"全体ステータス: {self.validation_results['overall_status']}")
        
        return self.validation_results
    
    def generate_report(self) -> str:
        """検証レポートの生成"""
        report = f"""
# 本番環境設定検証レポート

## 概要
- **プロジェクトID**: {self.project_id}
- **検証日時**: {self.validation_results['timestamp']}
- **全体ステータス**: {self.validation_results['overall_status']}

## サマリー
- **総検証項目**: {self.validation_results['summary']['total_validations']}
- **成功項目**: {self.validation_results['summary']['successful_validations']}
- **成功率**: {self.validation_results['summary']['success_rate']:.1%}
- **エラー数**: {self.validation_results['summary']['error_count']}
- **警告数**: {self.validation_results['summary']['warning_count']}

## 検証結果詳細

"""
        
        for validation_name, validation_result in self.validation_results["validations"].items():
            status = validation_result.get("status", "UNKNOWN")
            status_icon = "✓" if status in ["VALID", "CONFIGURED"] else "⚠" if status in ["PARTIAL", "NOT_CONFIGURED", "NOT_DEPLOYED"] else "✗"
            
            report += f"### {validation_name.upper()}\n"
            report += f"**ステータス**: {status_icon} {status}\n\n"
            
            for key, value in validation_result.items():
                if key != "status":
                    report += f"- **{key}**: {value}\n"
            report += "\n"
        
        if self.validation_results["errors"]:
            report += "## エラー\n\n"
            for error in self.validation_results["errors"]:
                report += f"- ❌ {error}\n"
            report += "\n"
        
        if self.validation_results["warnings"]:
            report += "## 警告\n\n"
            for warning in self.validation_results["warnings"]:
                report += f"- ⚠️ {warning}\n"
            report += "\n"
        
        report += """
## 推奨アクション

### 即座に対応が必要な項目
"""
        
        if self.validation_results["errors"]:
            report += "- エラー項目の修正\n"
        
        if self.validation_results["overall_status"] == "NOT_READY":
            report += "- 基本設定の完了\n"
        
        report += """
### デプロイ前に確認すべき項目
- Secret Managerのシークレット値設定
- Cloud Armorセキュリティポリシーの適用
- 監視アラートの通知先設定
- Firestoreセキュリティルールの適用

### 本番運用開始後の監視項目
- API応答時間（1.2秒P95目標）
- 治療安全性F1スコア（98%目標）
- 同時接続ユーザー数（20,000人目標）
- エラー率（1%未満目標）
"""
        
        return report

def main():
    """メイン実行関数"""
    if len(sys.argv) != 2:
        print("使用方法: python production_config_validator.py <PROJECT_ID>")
        sys.exit(1)
    
    project_id = sys.argv[1]
    
    # gcloudコマンドの存在確認
    success, _, _ = subprocess.run(["which", "gcloud"], capture_output=True).returncode == 0
    if not success:
        logger.error("gcloudコマンドが見つかりません。Google Cloud SDKをインストールしてください。")
        sys.exit(1)
    
    # プロジェクト設定
    subprocess.run(["gcloud", "config", "set", "project", project_id], capture_output=True)
    
    # 検証実行
    validator = ProductionConfigValidator(project_id)
    results = validator.run_full_validation()
    
    # 結果保存
    with open(f"production_validation_results_{project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # レポート生成
    report = validator.generate_report()
    with open(f"production_validation_report_{project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    # 結果表示
    print("\n" + "="*80)
    print("本番環境設定検証結果")
    print("="*80)
    print(f"プロジェクトID: {project_id}")
    print(f"全体ステータス: {results['overall_status']}")
    print(f"成功率: {results['summary']['success_rate']:.1%}")
    print(f"エラー数: {results['summary']['error_count']}")
    print(f"警告数: {results['summary']['warning_count']}")
    
    if results["overall_status"] == "READY":
        print("\n✅ 本番環境設定は完了しています！")
        sys.exit(0)
    elif results["overall_status"] == "MOSTLY_READY":
        print("\n⚠️ 本番環境設定はほぼ完了していますが、いくつかの警告があります。")
        sys.exit(0)
    else:
        print("\n❌ 本番環境設定に問題があります。エラーを修正してください。")
        sys.exit(1)

if __name__ == "__main__":
    main()