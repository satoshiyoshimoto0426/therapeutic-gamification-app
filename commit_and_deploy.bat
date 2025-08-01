@echo off
echo 🚀 Therapeutic Gamification App - 自動デプロイメント開始
echo ============================================================

echo.
echo 📋 変更ファイルをステージング中...
git add .

echo.
echo 💾 コミット実行中...
git commit -m "feat: setup automatic deployment with CI/CD pipeline - %date% %time%"

echo.
echo 🚀 GitHubにプッシュ中...
git push origin main

echo.
echo ✅ デプロイメントトリガー完了！
echo.
echo 📊 次のステップ:
echo 1. GitHubリポジトリのActionsタブを開く
echo 2. CI/CDパイプラインの進行状況を確認
echo 3. 必要に応じてGitHub Secretsを設定
echo 4. デプロイ完了まで15-20分待機
echo.
echo 🔗 重要なリンク:
echo - GitHub Actions: https://github.com/[your-repo]/actions
echo - Cloud Run Console: https://console.cloud.google.com/run
echo - Deployment Guide: DEPLOYMENT_GUIDE.md
echo.
pause