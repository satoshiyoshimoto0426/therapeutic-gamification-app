# PowerShellでのAWSデプロイガイド

## ✅ PowerShellで実行可能です

Pythonスクリプトは PowerShell から問題なく実行できます。

## 🚀 PowerShellでのデプロイ手順

### ステップ1: 前提条件の確認

```powershell
# Pythonのバージョン確認
python --version

# AWS CLIの確認
aws --version

# Dockerの確認
docker --version

# boto3のインストール（必要な場合）
pip install boto3
```

### ステップ2: AWS認証情報の設定

```powershell
# AWS CLIを設定
aws configure

# 入力項目：
# AWS Access Key ID: [新しいアクセスキー]
# AWS Secret Access Key: [新しいシークレットキー]
# Default region name: ap-northeast-1
# Default output format: json
```

### ステップ3: 環境変数ファイルの作成

```powershell
# テンプレートをコピー
Copy-Item .env.production.template .env.production

# エディタで編集
notepad .env.production
```

### ステップ4: デプロイ前チェック

```powershell
# デプロイ前チェックを実行
python pre_deploy_check_aws.py
```

### ステップ5: ECRリポジトリの作成とイメージプッシュ

```powershell
# ECRリポジトリを作成
aws ecr create-repository --repository-name therapeutic-app --region ap-northeast-1

# アカウントIDを取得
$ACCOUNT_ID = aws sts get-caller-identity --query Account --output text

# ECRにログイン
$ECR_PASSWORD = aws ecr get-login-password --region ap-northeast-1
$ECR_PASSWORD | docker login --username AWS --password-stdin "$ACCOUNT_ID.dkr.ecr.ap-northeast-1.amazonaws.com"

# Dockerイメージをビルド
docker build -t therapeutic-app .

# タグ付け
docker tag therapeutic-app:latest "$ACCOUNT_ID.dkr.ecr.ap-northeast-1.amazonaws.com/therapeutic-app:latest"

# プッシュ
docker push "$ACCOUNT_ID.dkr.ecr.ap-northeast-1.amazonaws.com/therapeutic-app:latest"

# ECR URIを表示（後で使用）
Write-Host "ECR URI: $ACCOUNT_ID.dkr.ecr.ap-northeast-1.amazonaws.com/therapeutic-app:latest" -ForegroundColor Green
```

### ステップ6: 自動デプロイ実行

```powershell
# デプロイスクリプトを実行
python deploy_to_aws.py

# プロンプトでECR URIを入力:
# 例: 123456789012.dkr.ecr.ap-northeast-1.amazonaws.com/therapeutic-app:latest
```

### ステップ7: デプロイ監視

```powershell
# 1回だけ状態確認
python monitor_aws_deployment.py

# 継続的に監視（30秒ごと）
python monitor_aws_deployment.py --continuous 30
```

## 🔧 PowerShell特有のコマンド

### 変数の使用

```powershell
# アカウントIDを変数に保存
$ACCOUNT_ID = aws sts get-caller-identity --query Account --output text

# 変数を使用
Write-Host "アカウントID: $ACCOUNT_ID"

# ECR URIを変数に保存
$ECR_URI = "$ACCOUNT_ID.dkr.ecr.ap-northeast-1.amazonaws.com/therapeutic-app:latest"
```

### ALB DNS名の取得

```powershell
# ALBのDNS名を取得
$ALB_DNS = aws elbv2 describe-load-balancers `
    --names therapeutic-app-alb `
    --query 'LoadBalancers[0].DNSName' `
    --output text

Write-Host "アプリケーションURL: http://$ALB_DNS" -ForegroundColor Green
```

### ヘルスチェック

```powershell
# ヘルスチェック
$ALB_DNS = aws elbv2 describe-load-balancers `
    --names therapeutic-app-alb `
    --query 'LoadBalancers[0].DNSName' `
    --output text

Invoke-WebRequest -Uri "http://$ALB_DNS/health" -Method Get
```

### ログの確認

```powershell
# CloudWatch Logsを確認
aws logs tail /ecs/therapeutic-app --follow
```

## 📝 PowerShell用の便利なスクリプト

### 完全自動デプロイスクリプト

```powershell
# deploy-aws.ps1 として保存

# エラーで停止
$ErrorActionPreference = "Stop"

Write-Host "=== AWS デプロイ開始 ===" -ForegroundColor Cyan

# 1. アカウントIDを取得
Write-Host "`n[1/6] アカウントIDを取得中..." -ForegroundColor Yellow
$ACCOUNT_ID = aws sts get-caller-identity --query Account --output text
Write-Host "アカウントID: $ACCOUNT_ID" -ForegroundColor Green

# 2. ECRリポジトリを作成（既存の場合はスキップ）
Write-Host "`n[2/6] ECRリポジトリを確認中..." -ForegroundColor Yellow
try {
    aws ecr describe-repositories --repository-names therapeutic-app --region ap-northeast-1 | Out-Null
    Write-Host "ECRリポジトリは既に存在します" -ForegroundColor Green
} catch {
    Write-Host "ECRリポジトリを作成中..." -ForegroundColor Yellow
    aws ecr create-repository --repository-name therapeutic-app --region ap-northeast-1
    Write-Host "ECRリポジトリを作成しました" -ForegroundColor Green
}

# 3. ECRにログイン
Write-Host "`n[3/6] ECRにログイン中..." -ForegroundColor Yellow
$ECR_PASSWORD = aws ecr get-login-password --region ap-northeast-1
$ECR_PASSWORD | docker login --username AWS --password-stdin "$ACCOUNT_ID.dkr.ecr.ap-northeast-1.amazonaws.com"
Write-Host "ECRログイン成功" -ForegroundColor Green

# 4. Dockerイメージをビルド
Write-Host "`n[4/6] Dockerイメージをビルド中..." -ForegroundColor Yellow
docker build -t therapeutic-app .
Write-Host "ビルド完了" -ForegroundColor Green

# 5. タグ付けとプッシュ
Write-Host "`n[5/6] イメージをECRにプッシュ中..." -ForegroundColor Yellow
$ECR_URI = "$ACCOUNT_ID.dkr.ecr.ap-northeast-1.amazonaws.com/therapeutic-app:latest"
docker tag therapeutic-app:latest $ECR_URI
docker push $ECR_URI
Write-Host "プッシュ完了" -ForegroundColor Green

# 6. デプロイスクリプトを実行
Write-Host "`n[6/6] デプロイを実行中..." -ForegroundColor Yellow
Write-Host "ECR URI: $ECR_URI" -ForegroundColor Cyan
Write-Host "`nデプロイスクリプトを起動します..." -ForegroundColor Yellow
Write-Host "プロンプトで以下のURIを入力してください:" -ForegroundColor Yellow
Write-Host $ECR_URI -ForegroundColor Cyan

python deploy_to_aws.py

Write-Host "`n=== デプロイ完了 ===" -ForegroundColor Cyan
```

### 使用方法

```powershell
# スクリプトに実行権限を付与（初回のみ）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# スクリプトを実行
.\deploy-aws.ps1
```

## ⚠️ PowerShellでの注意点

### 1. 実行ポリシー

PowerShellスクリプトを実行する前に、実行ポリシーを確認：

```powershell
# 現在のポリシーを確認
Get-ExecutionPolicy

# 必要に応じて変更
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. 長いコマンドの改行

PowerShellでは `` ` `` (バッククォート) で改行：

```powershell
# 正しい改行
aws elbv2 describe-load-balancers `
    --names therapeutic-app-alb `
    --query 'LoadBalancers[0].DNSName' `
    --output text
```

### 3. 環境変数の設定

```powershell
# 一時的な環境変数
$env:AWS_REGION = "ap-northeast-1"

# 永続的な環境変数（ユーザーレベル）
[System.Environment]::SetEnvironmentVariable("AWS_REGION", "ap-northeast-1", "User")
```

### 4. パイプの使用

```powershell
# PowerShellのパイプ
Get-Content .env.production | Select-String "LINE"

# AWS CLIの出力をフィルタ
aws ecs list-clusters | ConvertFrom-Json | Select-Object -ExpandProperty clusterArns
```

## 🔍 トラブルシューティング

### Pythonスクリプトが見つからない

```powershell
# Pythonのパスを確認
Get-Command python

# フルパスで実行
& "C:\Python39\python.exe" deploy_to_aws.py
```

### Docker コマンドが失敗する

```powershell
# Docker Desktopが起動しているか確認
Get-Process "Docker Desktop"

# Dockerサービスを再起動
Restart-Service docker
```

### AWS CLI認証エラー

```powershell
# 認証情報を確認
aws sts get-caller-identity

# 認証情報を再設定
aws configure
```

## 📚 参考コマンド集

```powershell
# サービスの状態確認
aws ecs describe-services `
    --cluster therapeutic-app-cluster `
    --services therapeutic-app-service

# タスクのリスト
aws ecs list-tasks `
    --cluster therapeutic-app-cluster `
    --service-name therapeutic-app-service

# ログの確認
aws logs tail /ecs/therapeutic-app --follow

# ALB情報の取得
aws elbv2 describe-load-balancers --names therapeutic-app-alb

# サービスの更新（新しいデプロイ）
aws ecs update-service `
    --cluster therapeutic-app-cluster `
    --service therapeutic-app-service `
    --force-new-deployment
```

---

**PowerShellで快適にデプロイできます！** 🚀

何か問題があれば、エラーメッセージを教えてください。
