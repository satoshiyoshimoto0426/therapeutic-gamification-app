#!/usr/bin/env python3
"""
治療的ゲーミフィケーションアプリ - ローカルデプロイスクリプト

最も簡単にゲームを起動できるデプロイ方法
"""

import os
import sys
import subprocess
import time
import threading
from datetime import datetime

class LocalGameDeployer:
    """ローカルゲームデプロイヤー"""
    
    def __init__(self):
        self.services = [
            ("コアゲーム", "services/core-game", 8001),
            ("認証", "services/auth", 8002),
            ("タスク管理", "services/task-mgmt", 8003),
            ("Mandala", "services/mandala", 8004),
            ("AIストーリー", "services/ai-story", 8005),
            ("気分追跡", "services/mood-tracking", 8006),
            ("ADHD支援", "services/adhd-support", 8007),
            ("治療安全性", "services/therapeutic-safety", 8008),
            ("LINE Bot", "services/line-bot", 8009),
        ]
        self.processes = []
        self.frontend_process = None
        self.service_status = {}  # サービス状態管理
        self.skip_frontend = False  # フロントエンドスキップフラグ
        
    def check_dependencies(self):
        """依存関係チェック"""
        print("🔍 依存関係をチェック中...")
        
        # Python依存関係
        required_packages = ["fastapi", "uvicorn", "pydantic", "httpx"]
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"❌ {package} - 未インストール")
        
        if missing_packages:
            print(f"\n📦 不足パッケージをインストール中...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install"] + missing_packages, check=True)
                print("✅ パッケージインストール完了")
            except subprocess.CalledProcessError as e:
                print(f"❌ パッケージインストール失敗: {e}")
        
        # Node.js依存関係（フロントエンド）
        if os.path.exists("frontend/package.json"):
            print("📦 フロントエンド依存関係をチェック中...")
            try:
                if not os.path.exists("frontend/node_modules"):
                    print("📦 npm install実行中...")
                    subprocess.run(["npm", "install"], cwd="frontend", check=True)
                    print("✅ npm install完了")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("⚠️ Node.js/npmが見つかりません。フロントエンドはスキップします。")
        
        print("✅ 依存関係チェック完了\n")
    
    def start_backend_service(self, name, path, port):
        """バックエンドサービス起動"""
        try:
            print(f"🚀 {name}サービス起動中... (ポート: {port})")
            
            # main.pyが存在するかチェック
            main_file = os.path.join(path, "main.py")
            if not os.path.exists(main_file):
                print(f"⚠️  {main_file} が見つかりません。スキップします。")
                return None
            
            # ポートが利用可能かチェック
            import socket
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex(('localhost', port))
                    if result == 0:
                        print(f"⚠️  ポート {port} は既に使用中です。既存サービスを確認します。")
                        # 既存サービスのヘルスチェック
                        if self.check_service_health(port):
                            print(f"✅ 既存の{name}サービスが正常動作中です。")
                            self.service_status[name] = {"status": "existing", "port": port, "process": "existing"}
                            return "existing"
                        else:
                            print(f"❌ ポート {port} は使用中ですが、サービスが応答しません。")
                            return None
            except Exception as e:
                # ポートチェックでエラーが発生した場合は続行
                pass
            
            # UTF-8環境変数を設定（Windows対応）
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            env['PYTHONPATH'] = os.path.abspath('.')  # プロジェクトルートをPYTHONPATHに追加
            
            # uvicornでサービス起動
            cmd = [
                sys.executable, "-m", "uvicorn", 
                "main:app", 
                "--host", "0.0.0.0", 
                "--port", str(port),
                "--reload",
                "--log-level", "warning"  # ログレベルを下げて出力を抑制
            ]
            
            # Windows環境でのエンコーディング問題を解決
            process = subprocess.Popen(
                cmd,
                cwd=path,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace'  # エンコーディングエラーを無視
            )
            
            # 起動確認（段階的チェック）
            max_attempts = 5
            for attempt in range(max_attempts):
                time.sleep(2)  # 2秒待機
                
                if process.poll() is not None:
                    # プロセスが終了している場合
                    stdout, stderr = process.communicate()
                    print(f"❌ {name}サービス起動失敗 (試行 {attempt + 1}/{max_attempts})")
                    if stderr and len(stderr.strip()) > 0:
                        # エラーメッセージの重要部分のみ表示
                        error_lines = stderr.strip().split('\n')
                        important_errors = [line for line in error_lines if any(keyword in line.lower() for keyword in ['error', 'exception', 'failed', 'cannot', 'unable'])]
                        if important_errors:
                            print(f"   主要エラー: {important_errors[-1][:150]}...")
                    break
                
                # ヘルスチェック
                if self.check_service_health(port):
                    print(f"✅ {name}サービス起動成功 - http://localhost:{port}")
                    self.service_status[name] = {"status": "running", "port": port, "process": process}
                    return process
                
                if attempt < max_attempts - 1:  # 最後の試行でない場合のみ表示
                    print(f"   {name}サービス起動中... (試行 {attempt + 1}/{max_attempts})")
            
            # 最終チェック
            if process.poll() is None:
                print(f"⚠️  {name}サービスは起動しましたが、ヘルスチェックに失敗しました")
                print(f"   手動確認: http://localhost:{port}")
                self.service_status[name] = {"status": "unhealthy", "port": port, "process": process}
                return process
            else:
                self.service_status[name] = {"status": "failed", "port": port, "process": None}
                return None
                
        except Exception as e:
            print(f"❌ {name}サービス起動エラー: {str(e)}")
            return None
    
    def check_service_health(self, port):
        """サービスヘルスチェック"""
        try:
            # httpxが利用できない場合はurllibを使用
            try:
                import httpx
                with httpx.Client() as client:
                    # まず/healthエンドポイントを試す
                    try:
                        response = client.get(f"http://localhost:{port}/health", timeout=3.0)
                        if response.status_code == 200:
                            return True
                    except:
                        pass
                    
                    # /healthが失敗した場合、ルートエンドポイントを試す
                    try:
                        response = client.get(f"http://localhost:{port}/", timeout=3.0)
                        return response.status_code in [200, 404]  # 404でもサービスは動作中
                    except:
                        pass
                    
                    # 最後にdocsエンドポイントを試す
                    try:
                        response = client.get(f"http://localhost:{port}/docs", timeout=3.0)
                        return response.status_code == 200
                    except:
                        pass
                        
                return False
            except ImportError:
                # httpxが利用できない場合、urllibを使用
                import urllib.request
                import urllib.error
                
                endpoints = ["/health", "/", "/docs"]
                
                for endpoint in endpoints:
                    try:
                        url = f"http://localhost:{port}{endpoint}"
                        req = urllib.request.Request(url)
                        with urllib.request.urlopen(req, timeout=3) as response:
                            if response.status in [200, 404]:
                                return True
                    except (urllib.error.URLError, urllib.error.HTTPError):
                        continue
                    except Exception:
                        continue
                
                return False
                    
        except Exception as e:
            # デバッグ用にエラーを表示しない（静かに失敗）
            return False
    
    def start_frontend(self):
        """フロントエンド起動"""
        try:
            if not os.path.exists("frontend/package.json"):
                print("⚠️  フロントエンドが見つかりません。バックエンドのみ起動します。")
                return None
            
            print("🎨 フロントエンド起動中... (ポート: 3000)")
            
            # Vite開発サーバー起動
            process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd="frontend",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 起動確認（5秒待機）
            time.sleep(5)
            if process.poll() is None:
                print("✅ フロントエンド起動成功 - http://localhost:3000")
                return process
            else:
                print("❌ フロントエンド起動失敗")
                return None
                
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"⚠️ Node.js/npmが見つかりません。フロントエンドはスキップします。")
            return None
        except Exception as e:
            print(f"❌ フロントエンド起動エラー: {str(e)}")
            return None
    
    def perform_comprehensive_health_check(self):
        """包括的ヘルスチェック"""
        print("\n🔍 包括的ヘルスチェックを実行中...")
        
        results = {}
        
        # 定義されたサービスのヘルスチェック
        for name, path, port in self.services:
            print(f"   {name}サービスをチェック中... (ポート: {port})")
            
            # ポート使用状況チェック
            import socket
            port_in_use = False
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex(('localhost', port))
                    port_in_use = (result == 0)
            except:
                port_in_use = False
            
            if not port_in_use:
                results[name] = "port_not_in_use"
                print(f"      ❌ ポート {port} が使用されていません")
                continue
            
            # ヘルスチェック実行
            health_status = self.check_service_health(port)
            if health_status:
                results[name] = "healthy"
                print(f"      ✅ 正常動作中")
            else:
                results[name] = "unhealthy"
                print(f"      ⚠️  ポートは使用中だがヘルスチェック失敗")
        
        # フロントエンドチェック
        print("   フロントエンドをチェック中... (ポート: 3000)")
        frontend_health = self.check_service_health(3000)
        if frontend_health:
            results["フロントエンド"] = "healthy"
            print("      ✅ 正常動作中")
        else:
            results["フロントエンド"] = "unavailable"
            print("      ❌ 利用不可")
        
        # 結果サマリー表示
        print("\n📊 ヘルスチェック結果サマリー:")
        healthy_count = 0
        total_count = len(results)
        
        for name, status in results.items():
            status_emoji = {
                "healthy": "✅",
                "unhealthy": "⚠️ ",
                "port_not_in_use": "❌",
                "unavailable": "❌",
                "no_port": "❓"
            }
            status_text = {
                "healthy": "正常動作中",
                "unhealthy": "異常",
                "port_not_in_use": "未起動",
                "unavailable": "利用不可",
                "no_port": "ポート不明"
            }
            
            emoji = status_emoji.get(status, '❓')
            text = status_text.get(status, status)
            print(f"   {name}: {emoji} {text}")
            
            if status == "healthy":
                healthy_count += 1
        
        print(f"\n🎯 結果: {healthy_count}/{total_count} サービスが正常動作中")
        
        if healthy_count == total_count:
            print("🎉 すべてのサービスが正常に動作しています！")
        elif healthy_count > 0:
            print("⚠️  一部のサービスに問題があります。")
        else:
            print("❌ サービスが起動していません。deploy_local.pyを実行してください。")
        
        return results
    
    def create_game_launcher(self):
        """ゲームランチャー作成"""
        launcher_html = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎮 治療的ゲーミフィケーションアプリ - ゲームランチャー</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            color: white;
        }
        .container {
            max-width: 800px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        h1 {
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }
        .service-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .service-card {
            background: rgba(255, 255, 255, 0.2);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            transition: transform 0.3s ease;
            border: 2px solid transparent;
        }
        .service-card:hover {
            transform: translateY(-5px);
            border-color: rgba(255, 255, 255, 0.3);
        }
        .service-card.available {
            border-color: #4CAF50;
            background: rgba(76, 175, 80, 0.2);
        }
        .service-card.unavailable {
            border-color: #f44336;
            background: rgba(244, 67, 54, 0.2);
            opacity: 0.7;
        }
        .service-title {
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .service-url {
            font-size: 0.9em;
            opacity: 0.8;
            margin-bottom: 15px;
        }
        .btn {
            background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
            border: none;
            color: white;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1em;
            font-weight: bold;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }
        .btn:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        }
        .btn:disabled {
            background: #666;
            cursor: not-allowed;
            transform: none;
        }
        .main-game-btn {
            font-size: 1.5em;
            padding: 20px 40px;
            margin: 20px 0;
        }
        .status {
            text-align: center;
            margin: 20px 0;
            padding: 15px;
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.1);
        }
        .instructions {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            margin-top: 30px;
        }
        .instructions h3 {
            margin-top: 0;
        }
        .instructions ul {
            text-align: left;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 治療的ゲーミフィケーションアプリ</h1>
        
        <div class="status">
            <h3>🚀 ゲーム起動状況</h3>
            <p id="status-text">サービス状況を確認中...</p>
        </div>
        
        <div class="service-grid">
            <div class="service-card" id="frontend-card">
                <div class="service-title">🎨 メインゲーム</div>
                <div class="service-url">http://localhost:3000</div>
                <a href="http://localhost:3000" class="btn" id="frontend-btn">ゲーム開始</a>
            </div>
            
            <div class="service-card" id="core-game-card">
                <div class="service-title">⚡ コアゲーム</div>
                <div class="service-url">http://localhost:8001</div>
                <a href="http://localhost:8001/docs" class="btn" id="core-game-btn">API確認</a>
            </div>
            
            <div class="service-card" id="auth-card">
                <div class="service-title">🔐 認証</div>
                <div class="service-url">http://localhost:8002</div>
                <a href="http://localhost:8002/docs" class="btn" id="auth-btn">API確認</a>
            </div>
            
            <div class="service-card" id="task-card">
                <div class="service-title">📋 タスク管理</div>
                <div class="service-url">http://localhost:8003</div>
                <a href="http://localhost:8003/docs" class="btn" id="task-btn">API確認</a>
            </div>
            
            <div class="service-card" id="mandala-card">
                <div class="service-title">🌸 Mandala</div>
                <div class="service-url">http://localhost:8004</div>
                <a href="http://localhost:8004/docs" class="btn" id="mandala-btn">API確認</a>
            </div>
            
            <div class="service-card" id="story-card">
                <div class="service-title">📚 AIストーリー</div>
                <div class="service-url">http://localhost:8005</div>
                <a href="http://localhost:8005/docs" class="btn" id="story-btn">API確認</a>
            </div>
            
            <div class="service-card" id="mood-card">
                <div class="service-title">😊 気分追跡</div>
                <div class="service-url">http://localhost:8006</div>
                <a href="http://localhost:8006/docs" class="btn" id="mood-btn">API確認</a>
            </div>
            
            <div class="service-card" id="adhd-card">
                <div class="service-title">🧠 ADHD支援</div>
                <div class="service-url">http://localhost:8007</div>
                <a href="http://localhost:8007/docs" class="btn" id="adhd-btn">API確認</a>
            </div>
            
            <div class="service-card" id="safety-card">
                <div class="service-title">🛡️ 治療安全性</div>
                <div class="service-url">http://localhost:8008</div>
                <a href="http://localhost:8008/docs" class="btn" id="safety-btn">API確認</a>
            </div>
            
            <div class="service-card" id="linebot-card">
                <div class="service-title">💬 LINE Bot</div>
                <div class="service-url">http://localhost:8009</div>
                <a href="http://localhost:8009/docs" class="btn" id="linebot-btn">API確認</a>
            </div>
        </div>
        
        <div class="instructions">
            <h3>🎯 ゲームの始め方</h3>
            <ul>
                <li><strong>メインゲーム</strong>をクリックしてゲームを開始</li>
                <li>初回は簡単なアカウント設定を行います</li>
                <li>朝のタスク配信から1日が始まります</li>
                <li>タスクを完了してXPを獲得しましょう</li>
                <li>夜にはAIが生成したストーリーを楽しめます</li>
            </ul>
            
            <h3>🔧 開発者向け</h3>
            <ul>
                <li>各サービスの<strong>API確認</strong>ボタンでSwagger UIにアクセス</li>
                <li>APIの動作確認やテストが可能</li>
                <li>ログはターミナルで確認できます</li>
            </ul>
        </div>
    </div>
    
    <script>
        // サービス状況チェック
        async function checkServices() {
            const services = [
                { id: 'frontend', url: 'http://localhost:3000', name: 'メインゲーム' },
                { id: 'core-game', url: 'http://localhost:8001/health', name: 'コアゲーム' },
                { id: 'auth', url: 'http://localhost:8002/health', name: '認証' },
                { id: 'task', url: 'http://localhost:8003/health', name: 'タスク管理' },
                { id: 'mandala', url: 'http://localhost:8004/health', name: 'Mandala' },
                { id: 'story', url: 'http://localhost:8005/health', name: 'AIストーリー' },
                { id: 'mood', url: 'http://localhost:8006/health', name: '気分追跡' },
                { id: 'adhd', url: 'http://localhost:8007/health', name: 'ADHD支援' },
                { id: 'safety', url: 'http://localhost:8008/health', name: '治療安全性' },
                { id: 'linebot', url: 'http://localhost:8009/health', name: 'LINE Bot' }
            ];
            
            let availableCount = 0;
            
            for (const service of services) {
                const card = document.getElementById(service.id + '-card');
                const btn = document.getElementById(service.id + '-btn');
                
                if (!card || !btn) {
                    console.warn(`要素が見つかりません: ${service.id}`);
                    continue;
                }
                
                try {
                    // 複数のエンドポイントを試行
                    let isAvailable = false;
                    
                    // 1. /healthエンドポイント
                    try {
                        const healthResponse = await fetch(service.url, { 
                            method: 'GET',
                            mode: 'no-cors',
                            timeout: 2000
                        });
                        isAvailable = true;
                    } catch (e) {
                        // 2. ルートエンドポイント
                        try {
                            const rootUrl = service.url.replace('/health', '');
                            const rootResponse = await fetch(rootUrl, { 
                                method: 'GET',
                                mode: 'no-cors',
                                timeout: 2000
                            });
                            isAvailable = true;
                        } catch (e2) {
                            // 3. /docsエンドポイント
                            try {
                                const docsUrl = service.url.replace('/health', '/docs');
                                const docsResponse = await fetch(docsUrl, { 
                                    method: 'GET',
                                    mode: 'no-cors',
                                    timeout: 2000
                                });
                                isAvailable = true;
                            } catch (e3) {
                                isAvailable = false;
                            }
                        }
                    }
                    
                    if (isAvailable) {
                        card.classList.add('available');
                        card.classList.remove('unavailable');
                        btn.disabled = false;
                        availableCount++;
                    } else {
                        card.classList.add('unavailable');
                        card.classList.remove('available');
                        btn.disabled = true;
                    }
                    
                } catch (error) {
                    console.warn(`${service.name}のチェックでエラー:`, error);
                    card.classList.add('unavailable');
                    card.classList.remove('available');
                    btn.disabled = true;
                }
            }
            
            // ステータス更新
            const statusText = document.getElementById('status-text');
            if (availableCount === services.length) {
                statusText.innerHTML = '🎉 全サービス正常動作中！ゲームを開始できます。';
            } else if (availableCount > 0) {
                statusText.innerHTML = `⚠️ ${availableCount}/${services.length} サービスが動作中。一部機能が制限される可能性があります。`;
            } else {
                statusText.innerHTML = '❌ サービスが起動していません。deploy_local.pyを実行してください。';
            }
        }
        
        // 5秒ごとにサービス状況をチェック
        checkServices();
        setInterval(checkServices, 5000);
    </script>
</body>
</html>"""
        
        with open("game_launcher.html", "w", encoding="utf-8") as f:
            f.write(launcher_html)
        
        print("🎮 ゲームランチャー作成完了: game_launcher.html")
        print("   ブラウザで game_launcher.html を開いてゲームを開始できます")
    
    def start_all_services(self):
        """全サービス起動"""
        print("🚀 治療的ゲーミフィケーションアプリ - ローカルデプロイ開始")
        print(f"開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        # 依存関係チェック
        self.check_dependencies()
        
        # バックエンドサービス起動
        print("🔧 バックエンドサービス起動中...")
        for name, path, port in self.services:
            process = self.start_backend_service(name, path, port)
            if process:
                self.processes.append((name, process))
        
        print()
        
        # フロントエンド起動
        if not self.skip_frontend:
            print("🎨 フロントエンド起動中...")
            self.frontend_process = self.start_frontend()
        else:
            print("🚫 フロントエンドはスキップされました")
        
        print()
        
        # ゲームランチャー作成
        self.create_game_launcher()
        
        # 包括的ヘルスチェック実行
        self.perform_comprehensive_health_check()
        
        print("="*60)
        print("🎉 ローカルデプロイメント完了！")
        print()
        print("🎮 ゲーム開始方法:")
        print("1. ブラウザで game_launcher.html を開く")
        if not self.skip_frontend:
            print("2. または直接 http://localhost:3000 にアクセス")
        print()
        print("🔧 開発者向けAPI文書:")
        for name, path, port in self.services:
            if name in self.service_status and self.service_status[name]["status"] in ["running", "existing"]:
                print(f"- {name}: http://localhost:{port}/docs")
        print()
        print("📊 サービス監視:")
        print("- 60秒ごとに自動ヘルスチェックを実行")
        print("- サービス状況はリアルタイムで表示されます")
        print()
        print("⚠️  終了するには Ctrl+C を押してください")
        print("="*60)
    
    def stop_all_services(self):
        """全サービス停止"""
        print("\n🛑 サービス停止中...")
        
        stopped_count = 0
        failed_count = 0
        
        # バックエンドサービス停止
        for name, process in self.processes:
            if isinstance(process, str) and process == "existing":
                print(f"🔄 {name}サービス: 既存プロセスのため停止をスキップ")
                continue
                
            try:
                if process.poll() is None:  # プロセスが生きている場合のみ停止
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                        print(f"✅ {name}サービス停止")
                        stopped_count += 1
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
                        print(f"🔪 {name}サービス強制停止")
                        stopped_count += 1
                else:
                    print(f"⚠️  {name}サービス: 既に停止済み")
            except Exception as e:
                print(f"❌ {name}サービス停止失敗: {str(e)}")
                failed_count += 1
        
        # フロントエンド停止
        if self.frontend_process:
            try:
                if self.frontend_process.poll() is None:
                    self.frontend_process.terminate()
                    try:
                        self.frontend_process.wait(timeout=5)
                        print("✅ フロントエンド停止")
                        stopped_count += 1
                    except subprocess.TimeoutExpired:
                        self.frontend_process.kill()
                        self.frontend_process.wait()
                        print("🔪 フロントエンド強制停止")
                        stopped_count += 1
                else:
                    print("⚠️  フロントエンド: 既に停止済み")
            except Exception as e:
                print(f"❌ フロントエンド停止失敗: {str(e)}")
                failed_count += 1
        
        print(f"🎯 サービス停止完了: {stopped_count}個停止, {failed_count}個失敗")
        
        # サービス状態をクリア
        self.service_status.clear()
        self.processes.clear()
    
    def monitor_services(self):
        """サービス監視"""
        print("🔍 サービス監視を開始します...")
        
        monitor_interval = 60  # 60秒ごとにチェック
        
        while True:
            try:
                time.sleep(monitor_interval)
                
                print(f"\n📊 サービス状況チェック ({datetime.now().strftime('%H:%M:%S')})")
                
                # プロセス状態チェック
                failed_services = []
                healthy_services = []
                unhealthy_services = []
                
                for name, process in self.processes:
                    if isinstance(process, str) and process == "existing":
                        # 既存プロセスのヘルスチェック
                        service_info = self.service_status.get(name, {})
                        port = service_info.get("port")
                        if port and self.check_service_health(port):
                            healthy_services.append(name)
                            print(f"   {name}: 🔄 既存プロセス正常動作中 (ポート: {port})")
                        else:
                            unhealthy_services.append(name)
                            print(f"   {name}: ⚠️  既存プロセス応答なし")
                        continue
                    
                    if process.poll() is not None:
                        failed_services.append(name)
                        print(f"   {name}: ❌ プロセス停止")
                        # サービス状態を更新
                        if name in self.service_status:
                            self.service_status[name]["status"] = "failed"
                    else:
                        # ヘルスチェック実行
                        service_info = self.service_status.get(name, {})
                        port = service_info.get("port")
                        if port and self.check_service_health(port):
                            healthy_services.append(name)
                            print(f"   {name}: ✅ 正常動作中 (ポート: {port})")
                            self.service_status[name]["status"] = "running"
                        else:
                            unhealthy_services.append(name)
                            print(f"   {name}: ⚠️  プロセス動作中だがヘルスチェック失敗")
                            self.service_status[name]["status"] = "unhealthy"
                
                # フロントエンドプロセスチェック
                frontend_status = "未起動"
                if self.frontend_process:
                    if self.frontend_process.poll() is not None:
                        frontend_status = "停止"
                        print("   フロントエンド: ❌ プロセス停止")
                    else:
                        if self.check_service_health(3000):
                            frontend_status = "正常"
                            print("   フロントエンド: ✅ 正常動作中 (ポート: 3000)")
                        else:
                            frontend_status = "異常"
                            print("   フロントエンド: ⚠️  プロセス動作中だがヘルスチェック失敗")
                
                # サマリー表示
                total_backend_services = len(self.processes)
                healthy_count = len(healthy_services)
                
                print(f"\n📈 サマリー:")
                print(f"   バックエンドサービス: {healthy_count}/{total_backend_services} 正常動作中")
                print(f"   フロントエンド: {frontend_status}")
                
                if failed_services:
                    print(f"   ❌ 停止: {', '.join(failed_services)}")
                if unhealthy_services:
                    print(f"   ⚠️  異常: {', '.join(unhealthy_services)}")
                
                # 全体的な健康状態
                if healthy_count == total_backend_services and frontend_status == "正常":
                    print("   🎉 全サービス正常動作中！")
                elif healthy_count > 0 or frontend_status in ["正常", "異常"]:
                    print("   ⚠️  一部サービスに問題があります")
                else:
                    print("   ❌ 重大な問題: ほとんどのサービスが停止しています")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"⚠️  監視エラー: {str(e)}")
                time.sleep(5)  # エラー時は短い間隔で再試行
    
    def run(self):
        """メイン実行"""
        try:
            self.start_all_services()
            
            # サービス監視を別スレッドで開始
            monitor_thread = threading.Thread(target=self.monitor_services, daemon=True)
            monitor_thread.start()
            
            # メインループ
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.stop_all_services()
        except Exception as e:
            print(f"❌ 予期しないエラー: {str(e)}")
            self.stop_all_services()

def main():
    """メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='治療的ゲーミフィケーションアプリ - ローカルデプロイ')
    parser.add_argument('--health-check-only', action='store_true', 
                       help='ヘルスチェックのみ実行')
    parser.add_argument('--no-frontend', action='store_true', 
                       help='フロントエンドを起動しない')
    parser.add_argument('--services', nargs='+', 
                       help='起動するサービスを指定 (例: core-game auth task-mgmt)')
    parser.add_argument('--launcher-only', action='store_true',
                       help='ゲームランチャーのみ作成')
    parser.add_argument('--quick-start', action='store_true',
                       help='最小限のサービスで高速起動')
    parser.add_argument('--port-check', action='store_true',
                       help='ポート使用状況のみチェック')
    
    args = parser.parse_args()
    
    deployer = LocalGameDeployer()
    
    if args.port_check:
        try:
            print("ポート使用状況チェック中...")
            import socket
            for name, path, port in deployer.services:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(1)
                        result = s.connect_ex(('localhost', port))
                        if result == 0:
                            print(f"   ポート {port} ({name}): 使用中")
                        else:
                            print(f"   ポート {port} ({name}): 未使用")
                except Exception as e:
                    print(f"   ポート {port} ({name}): チェック失敗")
        except Exception as e:
            print(f"エラー: {str(e)}")
        return
    
    if args.health_check_only:
        try:
            print("ヘルスチェックモードで実行中...")
            deployer.perform_comprehensive_health_check()
        except Exception as e:
            print(f"エラー: {str(e)}")
        return
    
    if args.launcher_only:
        try:
            print("ゲームランチャーのみ作成中...")
            deployer.create_game_launcher()
            print("完了！ブラウザで game_launcher.html を開いてください。")
        except Exception as e:
            print(f"エラー: {str(e)}")
        return
    
    if args.quick_start:
        try:
            print("高速起動モード: 最小限のサービスのみ起動")
            # コアサービスのみに限定
            core_services = []
            for name, path, port in deployer.services:
                if any(keyword in path.lower() for keyword in ['core-game', 'auth', 'task-mgmt']):
                    core_services.append((name, path, port))
            deployer.services = core_services
            deployer.skip_frontend = True
        except Exception as e:
            print(f"エラー: {str(e)}")
            return
    
    if args.services:
        # 指定されたサービスのみ起動
        all_services = deployer.services.copy()
        deployer.services = []
        for service_name in args.services:
            for name, path, port in all_services:
                if service_name in path:
                    deployer.services.append((name, path, port))
                    break
        print(f"🎯 指定されたサービスのみ起動: {[s[0] for s in deployer.services]}")
    
    if args.no_frontend:
        print("🚫 フロントエンドはスキップします")
        deployer.skip_frontend = True
    else:
        deployer.skip_frontend = False
    
    deployer.run()

if __name__ == "__main__":
    main()