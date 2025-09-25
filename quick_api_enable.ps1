# Google Cloud APIs 一括有効化スクリプト (PowerShell版)
# 治療的ゲーミフィケーションアプリ用

$PROJECT_ID = "abiding-beanbag-467909-d8"

Write-Host "🚀 Google Cloud APIs を有効化中..." -ForegroundColor Green
Write-Host "プロジェクト: $PROJECT_ID" -ForegroundColor Yellow

# プロジェクト設定
Write-Host "🔧 プロジェクト設定中..." -ForegroundColor Blue
gcloud config set project $PROJECT_ID

# 必要なAPIのリスト
$APIS = @(
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "containerregistry.googleapis.com", 
    "artifactregistry.googleapis.com",
    "firestore.googleapis.com",
    "storage-api.googleapis.com",
    "storage-component.googleapis.com",
    "iam.googleapis.com",
    "iamcredentials.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "secretmanager.googleapis.com",
    "compute.googleapis.com",
    "servicenetworking.googleapis.com",
    "vpcaccess.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
    "cloudtrace.googleapis.com",
    "clouderrorreporting.googleapis.com",
    "cloudfunctions.googleapis.com",
    "cloudscheduler.googleapis.com",
    "pubsub.googleapis.com",
    "cloudkms.googleapis.com",
    "binaryauthorization.googleapis.com",
    "dns.googleapis.com",
    "certificatemanager.googleapis.com"
)

# APIを一つずつ有効化
Write-Host "📦 APIを有効化中..." -ForegroundColor Blue
$enabledCount = 0
$totalCount = $APIS.Count

foreach ($api in $APIS) {
    $enabledCount++
    Write-Host "[$enabledCount/$totalCount] $api を有効化中..." -ForegroundColor Cyan
    
    try {
        $result = gcloud services enable $api --project=$PROJECT_ID 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ $api" -ForegroundColor Green
        } else {
            Write-Host "⚠️ $api (既に有効化済みまたはエラー)" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "❌ $api (エラー: $_)" -ForegroundColor Red
    }
    
    # 少し待機
    Start-Sleep -Seconds 1
}

Write-Host "✅ API有効化完了！" -ForegroundColor Green

# 重要なAPIの確認
Write-Host "🔍 重要なAPIの確認中..." -ForegroundColor Blue

$CRITICAL_APIS = @(
    "run.googleapis.com",
    "cloudbuild.googleapis.com", 
    "firestore.googleapis.com",
    "iam.googleapis.com"
)

foreach ($api in $CRITICAL_APIS) {
    try {
        $result = gcloud services list --enabled --filter="name:$api" --format="value(name)" 2>$null
        if ($result -match $api) {
            Write-Host "✅ $api" -ForegroundColor Green
        } else {
            Write-Host "❌ $api" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "❌ $api (確認エラー)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🎉 設定完了！" -ForegroundColor Green
Write-Host "📝 次のステップ:" -ForegroundColor Yellow
Write-Host "1. GitHub Actionsでデプロイを再実行してください" -ForegroundColor White
Write-Host "2. エラーが続く場合は、Google Cloud Consoleで手動確認してください" -ForegroundColor White
Write-Host "3. プロジェクトURL: https://console.cloud.google.com/apis/dashboard?project=$PROJECT_ID" -ForegroundColor White