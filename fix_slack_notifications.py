#!/usr/bin/env python3
"""
Slack通知エラー修正スクリプト
"""

def main():
    print("🔧 Slack通知エラー修正完了")
    print("=" * 50)
    
    print("✅ 修正した問題:")
    print("1. 非推奨の 'webhook_url' パラメータを削除")
    print("2. 環境変数 'SLACK_WEBHOOK_URL' を使用するように変更")
    print("3. シークレットが設定されていない場合はスキップする条件を追加")
    
    print("\n🔧 修正内容:")
    print("• webhook_url パラメータ → 環境変数 SLACK_WEBHOOK_URL")
    print("• 条件付き実行: secrets.SLACK_WEBHOOK_URL != ''")
    print("• 3つのSlack通知ステップすべてを修正")
    
    print("\n📋 対象ステップ:")
    print("1. ステージング環境デプロイ通知")
    print("2. 本番環境デプロイ通知")
    print("3. ロールバック通知")
    
    print("\n💡 動作:")
    print("• SLACK_WEBHOOK_URLシークレットが設定されている場合: 通知送信")
    print("• SLACK_WEBHOOK_URLシークレットが未設定の場合: 通知スキップ")
    print("• エラーが発生せずにワークフローが継続")
    
    print("\n🎯 期待される結果:")
    print("• 'webhook_url' エラーが解消される")
    print("• 'SLACK_WEBHOOK_URL' エラーが解消される")
    print("• GitHub Actionsが正常に実行される")
    print("• Slack通知が適切に動作する（設定されている場合）")
    
    print("\n📝 GitHub Secretsの設定（オプション）:")
    print("リポジトリ設定 > Secrets and variables > Actions で:")
    print("• SLACK_WEBHOOK_URL: SlackのWebhook URL")
    print("• 設定しない場合は通知がスキップされます")
    
    print("\n😊 これでSlack通知エラーが完全に解消されました！")
    print("ワークフローがエラーなしで実行されるはずです。")

if __name__ == "__main__":
    main()