# 🚀 最終デプロイメント手順書

## ❌ 発生している問題
- GitHub CLI認証エラー
- リポジトリアクセスエラー
- 自動化スクリプトの認証問題

## ✅ 確実な手動デプロイ手順

### ステップ1: GitHubリポジトリ作成確認

1. **ブラウザでGitHubにアクセス**
   - https://github.com/satoshiyoshimoto0426
   - ログインしていることを確認

2. **リポジトリ存在確認**
   - `therapeutic-gamification-app` リポジトリが存在するか確認
   - 存在しない場合は新規作成

3. **新規リポジトリ作成**（存在しない場合）
   - https://github.com/new
   - Repository name: `therapeutic-gamification-app`
   - Description: `Therapeutic Gamification App for ADHD Support`
   - Public を選択
   - README, .gitignore, license は追加しない
   - Create repository をクリック

### ステップ2: Personal Access Token作成

1. **GitHub Settings**
   - https://github.com/settings/tokens
   - Generate new token (classic) をクリック

2. **トークン設定**
   - Note: `therapeutic-app-deploy`
   - Expiration: 90 days
   - Scopes:
     - ✅ repo (Full control of private repositories)
     - ✅ workflow (Update GitHub Action workflows)
   - Generate token をクリック

3. **トークンをコピー**
   - 生成されたトークンをメモ帳にコピー
   - **重要**: 一度しか表示されません

### ステップ3: 手動Git操作

PowerShellで以下のコマンドを順番に実行：

```powershell
# 1. Gitリモート設定
git remote remove origin
git remote add origin https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app.git

# 2. ファイル追加・コミット
git add .
git commit -m "feat: complete deployment setup"

# 3. ブランチ設定
git branch -M main

# 4. プッシュ（認証が求められます）
git push -u origin main
```

**認証プロンプトで入力：**
- Username: `satoshiyoshimoto0426`
- Password: `[Personal Access Token]`

### ステップ4: GitHub Secrets設定

1. **GitHub Secretsページ**
   - https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app/settings/secrets/actions

2. **Secret 1: GCP_PROJECT_ID**
   - Name: `GCP_PROJECT_ID`
   - Value: `therapeutic-gamification-app-prod`

3. **Secret 2: GCP_SA_KEY**
   - Google Cloud Console: https://console.cloud.google.com/iam-admin/serviceaccounts
   - CREATE SERVICE ACCOUNT
   - Name: `github-actions`
   - 以下のロールを追加:
     - Cloud Run Admin
     - Cloud Build Editor
     - Storage Admin
     - Service Account User
     - Cloud Datastore Owner
     - Secret Manager Admin
     - Logging Viewer
   - KEYS → ADD KEY → Create new key → JSON
   - ダウンロードしたJSONファイルの内容全体をコピー
   - GitHub SecretsのGCP_SA_KEYに設定

### ステップ5: デプロイ監視

1. **GitHub Actions確認**
   - https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app/actions
   - CI/CDパイプラインが自動実行される
   - 約15-20分でデプロイ完了

2. **Cloud Run確認**
   - https://console.cloud.google.com/run
   - プロジェクト: `therapeutic-gamification-app-prod`
   - サービス: `therapeutic-gamification-app`

## 🎯 成功の確認方法

### GitHub Actions
- ✅ 全ジョブが緑色（成功）
- ✅ テスト → ビルド → デプロイ の順で完了

### Cloud Run
- ✅ サービスが作成されている
- ✅ サービスURLにアクセス可能
- ✅ `/health` エンドポイントが応答

## 🎮 アプリケーション機能

デプロイ完了後、以下の機能が利用可能：

### 治療的ゲーミフィケーション
- **タスク管理**: ポモドーロタイマー・習慣トラッキング
- **RPG要素**: XP・レベル・装備・ガチャシステム
- **AI生成ストーリー**: パーソナライズド治療体験
- **マンダラ**: 瞑想・マインドフルネス支援

### ADHD支援機能
- **認知負荷軽減**: シンプルUI・自動保存・フォーカスモード
- **時間知覚支援**: 視覚的タイマー・リマインダー
- **集中支援**: 気晴らし制限・段階的タスク分解

### 保護者・治療者支援
- **進捗レポート**: 詳細な活動分析・成長記録
- **安全性監視**: 治療的安全性AI監視システム
- **ケアポイント**: 保護者向けポイント・報酬システム

## 🔗 重要なリンク

- **GitHub Repository**: https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app
- **GitHub Actions**: https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app/actions
- **Google Cloud Console**: https://console.cloud.google.com/
- **Cloud Run**: https://console.cloud.google.com/run

---

## 🎉 デプロイ完了！

上記の手順を実行すれば、確実にTherapeutic Gamification Appがデプロイされます。

**素晴らしいアプリケーションをお楽しみください！** 🎮✨