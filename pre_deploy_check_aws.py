#!/usr/bin/env python3
"""
AWS デプロイ前チェックスクリプト
デプロイ前に必要な設定と認証情報を確認
"""

import boto3
import sys
import os
from typing import Dict, List, Tuple

class PreDeployChecker:
    def __init__(self):
        self.checks_passed = []
        self.checks_failed = []
        self.warnings = []
        
    def print_header(self, text: str):
        """ヘッダーを表示"""
        print(f"\n{'='*60}")
        print(f"  {text}")
        print(f"{'='*60}\n")
    
    def check_aws_credentials(self) -> bool:
        """AWS認証情報を確認"""
        print("🔑 AWS認証情報を確認中...")
        
        try:
            sts = boto3.client('sts')
            identity = sts.get_caller_identity()
            
            print(f"   ✅ AWS認証成功")
            print(f"   アカウントID: {identity['Account']}")
            print(f"   ユーザーARN: {identity['Arn']}")
            
            self.checks_passed.append("AWS認証情報")
            return True
            
        except Exception as e:
            print(f"   ❌ AWS認証失敗: {e}")
            print(f"   → aws configure を実行してください")
            self.checks_failed.append("AWS認証情報")
            return False
    
    def check_aws_permissions(self) -> bool:
        """必要なAWS権限を確認"""
        print("\n🔐 AWS権限を確認中...")
        
        required_services = [
            ('ecs', 'ECS'),
            ('ec2', 'EC2'),
            ('elbv2', 'ELB'),
            ('ecr', 'ECR'),
            ('iam', 'IAM'),
            ('logs', 'CloudWatch Logs')
        ]
        
        all_ok = True
        for service, name in required_services:
            try:
                client = boto3.client(service)
                # 簡単な読み取り操作でテスト
                if service == 'ecs':
                    client.list_clusters(maxResults=1)
                elif service == 'ec2':
                    client.describe_vpcs(MaxResults=1)
                elif service == 'elbv2':
                    client.describe_load_balancers(PageSize=1)
                elif service == 'ecr':
                    client.describe_repositories(maxResults=1)
                elif service == 'iam':
                    client.list_roles(MaxItems=1)
                elif service == 'logs':
                    client.describe_log_groups(limit=1)
                
                print(f"   ✅ {name} アクセス可能")
                
            except Exception as e:
                print(f"   ❌ {name} アクセス不可: {e}")
                all_ok = False
        
        if all_ok:
            self.checks_passed.append("AWS権限")
        else:
            self.checks_failed.append("AWS権限")
            print(f"\n   ⚠️  IAMポリシーを確認してください")
        
        return all_ok
    
    def check_docker(self) -> bool:
        """Dockerがインストールされているか確認"""
        print("\n🐳 Dockerを確認中...")
        
        try:
            import subprocess
            result = subprocess.run(
                ['docker', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"   ✅ Docker検出: {version}")
                self.checks_passed.append("Docker")
                return True
            else:
                raise Exception("Dockerが見つかりません")
                
        except Exception as e:
            print(f"   ❌ Docker未インストール: {e}")
            print(f"   → https://www.docker.com/get-started からインストールしてください")
            self.checks_failed.append("Docker")
            return False
    
    def check_env_file(self) -> bool:
        """環境変数ファイルを確認"""
        print("\n📄 環境変数ファイルを確認中...")
        
        if os.path.exists('.env.production'):
            print(f"   ✅ .env.production が存在します")
            
            # 必須の環境変数をチェック
            required_vars = [
                'FIRESTORE_PROJECT_ID',
                'LINE_CHANNEL_ACCESS_TOKEN',
                'LINE_CHANNEL_SECRET',
                'JWT_SECRET'
            ]
            
            with open('.env.production', 'r') as f:
                content = f.read()
                
            missing_vars = []
            for var in required_vars:
                if var not in content or f'{var}=your-' in content:
                    missing_vars.append(var)
            
            if missing_vars:
                print(f"   ⚠️  以下の環境変数が未設定です:")
                for var in missing_vars:
                    print(f"      - {var}")
                self.warnings.append("環境変数の一部が未設定")
            else:
                print(f"   ✅ 必須環境変数が設定されています")
            
            self.checks_passed.append("環境変数ファイル")
            return True
            
        else:
            print(f"   ❌ .env.production が見つかりません")
            print(f"   → .env.production.template をコピーして作成してください")
            self.checks_failed.append("環境変数ファイル")
            return False
    
    def check_dockerfile(self) -> bool:
        """Dockerfileを確認"""
        print("\n🏗️  Dockerfileを確認中...")
        
        if os.path.exists('Dockerfile'):
            print(f"   ✅ Dockerfile が存在します")
            self.checks_passed.append("Dockerfile")
            return True
        else:
            print(f"   ❌ Dockerfile が見つかりません")
            self.checks_failed.append("Dockerfile")
            return False
    
    def check_ecr_repository(self) -> bool:
        """ECRリポジトリの存在を確認"""
        print("\n📦 ECRリポジトリを確認中...")
        
        try:
            ecr = boto3.client('ecr')
            response = ecr.describe_repositories(
                repositoryNames=['therapeutic-app']
            )
            
            repo_uri = response['repositories'][0]['repositoryUri']
            print(f"   ✅ ECRリポジトリが存在します")
            print(f"   URI: {repo_uri}")
            self.checks_passed.append("ECRリポジトリ")
            return True
            
        except ecr.exceptions.RepositoryNotFoundException:
            print(f"   ⚠️  ECRリポジトリが存在しません")
            print(f"   → デプロイスクリプトが自動作成します")
            self.warnings.append("ECRリポジトリ未作成（自動作成されます）")
            return True
            
        except Exception as e:
            print(f"   ❌ ECR確認エラー: {e}")
            return False
    
    def check_secrets_rotation(self) -> bool:
        """認証情報のローテーション確認（手動確認）"""
        print("\n🔄 認証情報のローテーション確認...")
        print(f"   ⚠️  重要: 以下の認証情報を再発行しましたか？")
        print(f"      1. AWSアクセスキー")
        print(f"      2. LINEチャンネルトークン")
        
        response = input("\n   認証情報を再発行しましたか？ (yes/no): ").strip().lower()
        
        if response in ['yes', 'y']:
            print(f"   ✅ 認証情報のローテーション確認済み")
            self.checks_passed.append("認証情報ローテーション")
            return True
        else:
            print(f"   ❌ 認証情報を再発行してください！")
            print(f"   → AWS_DEPLOYMENT_GUIDE.md を参照")
            self.checks_failed.append("認証情報ローテーション")
            return False
    
    def print_summary(self):
        """チェック結果のサマリーを表示"""
        self.print_header("チェック結果サマリー")
        
        print(f"✅ 成功: {len(self.checks_passed)}項目")
        for check in self.checks_passed:
            print(f"   - {check}")
        
        if self.warnings:
            print(f"\n⚠️  警告: {len(self.warnings)}項目")
            for warning in self.warnings:
                print(f"   - {warning}")
        
        if self.checks_failed:
            print(f"\n❌ 失敗: {len(self.checks_failed)}項目")
            for check in self.checks_failed:
                print(f"   - {check}")
        
        print(f"\n{'='*60}")
        
        if self.checks_failed:
            print(f"❌ デプロイ前チェック失敗")
            print(f"   上記の問題を解決してから再度実行してください")
            return False
        elif self.warnings:
            print(f"⚠️  警告がありますが、デプロイ可能です")
            response = input(f"   デプロイを続行しますか？ (yes/no): ").strip().lower()
            return response in ['yes', 'y']
        else:
            print(f"✅ すべてのチェックに合格しました！")
            print(f"   デプロイを開始できます")
            return True
    
    def run_all_checks(self) -> bool:
        """すべてのチェックを実行"""
        self.print_header("AWS デプロイ前チェック")
        
        # 各チェックを実行
        self.check_aws_credentials()
        self.check_aws_permissions()
        self.check_docker()
        self.check_env_file()
        self.check_dockerfile()
        self.check_ecr_repository()
        self.check_secrets_rotation()
        
        # サマリーを表示
        return self.print_summary()


def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║         AWS デプロイ前チェックツール                      ║
    ║   治療的ゲーミフィケーションアプリケーション              ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    checker = PreDeployChecker()
    
    if checker.run_all_checks():
        print(f"\n🚀 次のステップ:")
        print(f"   1. python deploy_to_aws.py を実行")
        print(f"   2. ECRイメージURIを入力")
        print(f"   3. デプロイ完了を待つ\n")
        sys.exit(0)
    else:
        print(f"\n❌ デプロイ前チェックに失敗しました")
        print(f"   問題を解決してから再度実行してください\n")
        sys.exit(1)


if __name__ == '__main__':
    main()
