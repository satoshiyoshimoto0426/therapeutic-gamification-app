# AWS自動デプロイスクリプト (PowerShell)
# 治療的ゲーミフィケーションアプリケーション

# エラーで停止
$ErrorActionPreference = "Stop"

# カラー出力用の関数
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Header {
    param([string]$Text)
    Write-Host "`n$('='*70)" -ForegroundColor Cyan
    Write-Host "  $Text" -ForegroundColor Cyan
    Write-Host "$('='*70)`n" -ForegroundColor Cyan
}

# メイン処理
try {
    Write-Header "AWS デプロイ自動化スクリプト"
    
    # ステップ1: 前提条件チェック
    Write-ColorOutput "[1/7] 前提条件をチェック中..." "Yellow"
    
    # Pythonチェック
    try {
        $pythonVersion = python --version 2>&1
        Write-ColorOutput "  ✓ Python: $pythonVersion" "Green"
    } catch {
        Write-ColorOutput "  ✗ Python が見つかりません" "Red"
        Write-ColorOutput "    https://www.python.org/downloads/ からインストールしてください" "Yellow"
        exit 1
    }
    
    # AWS CLIチェック
    try {
        $awsVersion = aws --version 2>&1
        Write-ColorOutput "  ✓ AWS CLI: $awsVersion" "Green"
    } catch {
        Write-ColorOutput "  ✗ AWS CLI が見つかりません" "Red"
        Write-ColorOutput "    https://aws.amazon.com/cli/ からインストールしてください" "Yellow"
        exit 1
    }
    
    # Dockerチェック
    try {
        $dockerVersion = docker --version 2>&1
        Write-ColorOutput "  ✓ Docker: $dockerVersion" "Green"
    } catch {
        Write-ColorOutput "  ✗ Docker が見つかりません" "Red"
        Write-ColorOutput "    https://www.docker.com/get-started からインストールしてください" "Yellow"
        exit 1
    }
    
    # ステップ2: AWS認証確認
    Write-ColorOutput "`n[2/7] AWS認証情報を確認中..." "Yellow"
    try {
        $identity = aws sts get-caller-identity | ConvertFrom-Json
        $ACCOUNT_ID = $identity.Account
        Write-ColorOutput "  ✓ アカウントID: $ACCOUNT_ID" "Green"
        Write-ColorOutput "  ✓ ユーザーARN: $($identity.Arn)" "Green"
    } catch {
        Write-ColorOutput "  ✗ AWS認証に失敗しました" "Red"
        Write-ColorOutput "    'aws configure' を実行して認証情報を設定してください" "Yellow"
        exit 1
    }
    
    # ステップ3: 環境変数ファイルチェック
    Write-ColorOutput "`n[3/7] 環境変数ファイルを確認中..." "Yellow"
    if (Test-Path ".env.production") {
        Write-ColorOutput "  ✓ .env.production が存在します" "Green"
    } else {
        Write-ColorOutput "  ⚠ .env.production が見つかりません" "Yellow"
        Write-ColorOutput "    .env.production.template をコピーして作成しますか? (Y/N)" "Yellow"
        $response = Read-Host
        if ($response -eq "Y" -or $response -eq "y") {
            Copy-Item .env.production.template .env.production
            Write-ColorOutput "  ✓ .env.production を作成しました" "Green"
            Write-ColorOutput "    エディタで編集してから再度実行してください" "Yellow"
            notepad .env.production
            exit 0
        } else {
            Write-ColorOutput "  ✗ .env.production が必要です" "Red"
            exit 1
        }
    }
    
    # ステップ4: ECRリポジトリの確認/作成
    Write-ColorOutput "`n[4/7] ECRリポジトリを確認中..." "Yellow"
    try {
        aws ecr describe-repositories --repository-names therapeutic-app --region ap-northeast-1 2>&1 | Out-Null
        Write-ColorOutput "  ✓ ECRリポジトリは既に存在します" "Green"
    } catch {
        Write-ColorOutput "  ⚠ ECRリポジトリが存在しません。作成します..." "Yellow"
        aws ecr create-repository --repository-name therapeutic-app --region ap-northeast-1 | Out-Null
        Write-ColorOutput "  ✓ ECRリポジトリを作成しました" "Green"
    }
    
    # ステップ5: ECRログインとイメージビルド
    Write-ColorOutput "`n[5/7] Dockerイメージをビルド中..." "Yellow"
    
    # ECRにログイン
    Write-ColorOutput "  ECRにログイン中..." "Gray"
    $ECR_PASSWORD = aws ecr get-login-password --region ap-northeast-1
    $ECR_PASSWORD | docker login --username AWS --password-stdin "$ACCOUNT_ID.dkr.ecr.ap-northeast-1.amazonaws.com" 2>&1 | Out-Null
    Write-ColorOutput "  ✓ ECRログイン成功" "Green"
    
    # Dockerイメージをビルド
    Write-ColorOutput "  Dockerイメージをビルド中（数分かかります）..." "Gray"
    docker build -t therapeutic-app . 2>&1 | Out-Null
    Write-ColorOutput "  ✓ ビルド完了" "Green"
    
    # ステップ6: イメージをECRにプッシュ
    Write-ColorOutput "`n[6/7] イメージをECRにプッシュ中..." "Yellow"
    $ECR_URI = "$ACCOUNT_ID.dkr.ecr.ap-northeast-1.amazonaws.com/therapeutic-app:latest"
    
    docker tag therapeutic-app:latest $ECR_URI
    Write-ColorOutput "  タグ付け完了" "Gray"
    
    docker push $ECR_URI 2>&1 | Out-Null
    Write-ColorOutput "  ✓ プッシュ完了" "Green"
    Write-ColorOutput "  ECR URI: $ECR_URI" "Cyan"
    
    # ステップ7: デプロイスクリプトを実行
    Write-ColorOutput "`n[7/7] AWSインフラをデプロイ中..." "Yellow"
    Write-ColorOutput "  デプロイスクリプトを起動します..." "Gray"
    Write-ColorOutput "  プロンプトで以下のECR URIを入力してください:" "Yellow"
    Write-ColorOutput "  $ECR_URI" "Cyan"
    Write-ColorOutput "`n  Enterキーを押して続行..." "Yellow"
    Read-Host
    
    # Pythonスクリプトを実行
    python deploy_to_aws.py
    
    # 完了メッセージ
    Write-Header "デプロイ完了！"
    
    Write-ColorOutput "次のステップ:" "Cyan"
    Write-ColorOutput "  1. デプロイ状態を監視:" "White"
    Write-ColorOutput "     python monitor_aws_deployment.py --continuous 30" "Gray"
    Write-ColorOutput "`n  2. ALB DNS名を取得:" "White"
    Write-ColorOutput "     `$ALB_DNS = aws elbv2 describe-load-balancers --names therapeutic-app-alb --query 'LoadBalancers[0].DNSName' --output text" "Gray"
    Write-ColorOutput "`n  3. アプリケーションにアクセス:" "White"
    Write-ColorOutput "     http://`$ALB_DNS" "Gray"
    Write-ColorOutput "`n  4. 詳細なガイド:" "White"
    Write-ColorOutput "     AWS_DEPLOYMENT_COMPLETE.md を参照" "Gray"
    
} catch {
    Write-ColorOutput "`n✗ エラーが発生しました:" "Red"
    Write-ColorOutput $_.Exception.Message "Red"
    Write-ColorOutput "`nスタックトレース:" "Yellow"
    Write-ColorOutput $_.ScriptStackTrace "Gray"
    exit 1
}
