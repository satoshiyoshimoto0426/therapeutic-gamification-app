#!/usr/bin/env python3
"""
Google Cloud プロジェクトID修正スクリプト
"""

import subprocess
import sys
import json

def run_command(cmd, capture_output=True):
    """コマンドを実行して結果を返す"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1

def main():
    print("🔍 Google Cloud プロジェクト設定を確認中...")
    
    # 利用可能なプロジェクト一覧を取得
    print("\n📋 利用可能なプロジェクト一覧:")
    stdout, stderr, code = run_command("gcloud projects list --format='table(projectId,name,projectNumber)'")
    if code == 0:
        print(stdout)
    else:
        print(f"エラー: {stderr}")
        return
    
    # 現在のプロジェクトを確認
    print("\n🎯 現在設定されているプロジェクト:")
    stdout, stderr, code = run_command("gcloud config get-value project")
    if code == 0:
        current_project = stdout
        print(f"現在のプロジェクト: {current_project}")
        
        if current_project == "YOUR_EXISTING_PROJECT_ID" or not current_project:
            print("⚠️ プロジェクトIDが正しく設定されていません")
            
            # プロジェクト一覧から最初の有効なプロジェクトを取得
            stdout, stderr, code = run_command("gcloud projects list --format='value(projectId)' --limit=1")
            if code == 0 and stdout:
                suggested_project = stdout.strip()
                print(f"💡 推奨プロジェクトID: {suggested_project}")
                
                # プロジェクトを設定
                print(f"\n🔧 プロジェクトを {suggested_project} に設定中...")
                stdout, stderr, code = run_command(f"gcloud config set project {suggested_project}")
                if code == 0:
                    print("✅ プロジェクトが正常に設定されました")
                    
                    # 設定確認
                    stdout, stderr, code = run_command("gcloud config get-value project")
                    if code == 0:
                        print(f"✅ 確認: 現在のプロジェクト = {stdout}")
                else:
                    print(f"❌ プロジェクト設定エラー: {stderr}")
            else:
                print("❌ 利用可能なプロジェクトが見つかりません")
        else:
            print("✅ プロジェクトは正しく設定されています")
    else:
        print(f"エラー: {stderr}")
    
    # 必要なAPIを有効化
    print("\n🚀 必要なAPIを有効化中...")
    apis = [
        "run.googleapis.com",
        "cloudbuild.googleapis.com",
        "containerregistry.googleapis.com"
    ]
    
    for api in apis:
        print(f"  📡 {api} を有効化中...")
        stdout, stderr, code = run_command(f"gcloud services enable {api}")
        if code == 0:
            print(f"  ✅ {api} が有効化されました")
        else:
            print(f"  ⚠️ {api} の有効化でエラー: {stderr}")

if __name__ == "__main__":
    main()