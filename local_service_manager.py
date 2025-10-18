"""
ローカルサービスマネージャー

マイクロサービスの起動・停止・監視を管理するモジュール
"""

import json
import subprocess
import time
import signal
import sys
import os
import requests
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import threading
from pathlib import Path
import logging
from frontend_integration_helper import FrontendIntegrationHelper

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """サービスの状態"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass
class ServiceConfig:
    """サービス設定"""
    name: str
    display_name: str
    path: str
    port: int
    command: str
    health_endpoint: Optional[str] = None
    required: bool = True
    startup_timeout: int = 10
    description: str = ""


@dataclass
class ServiceInfo:
    """サービス情報"""
    config: ServiceConfig
    status: ServiceStatus = ServiceStatus.STOPPED
    process: Optional[subprocess.Popen] = None
    pid: Optional[int] = None
    start_time: Optional[float] = None
    logs: List[str] = field(default_factory=list)
    error_message: Optional[str] = None


class LocalServiceManager:
    """ローカルサービスマネージャー"""
    
    def __init__(self, config_file: str = "local_services_config.json"):
        """
        初期化
        
        Args:
            config_file: サービス設定ファイルのパス
        """
        self.config_file = config_file
        self.services: Dict[str, ServiceInfo] = {}
        self.frontend_info: Optional[ServiceInfo] = None
        self.log_threads: Dict[str, threading.Thread] = {}
        self.stop_log_threads: Dict[str, threading.Event] = {}
        self.frontend_helper = FrontendIntegrationHelper()
        
        # 設定ファイルの読み込み
        self._load_config()
        
        # シグナルハンドラの設定
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _load_config(self) -> None:
        """サービス設定の読み込み"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # サービス設定の読み込み
            for service_data in config_data.get('services', []):
                config = ServiceConfig(**service_data)
                self.services[config.name] = ServiceInfo(config=config)
            
            # フロントエンド設定の読み込み
            if 'frontend' in config_data:
                frontend_data = config_data['frontend']
                config = ServiceConfig(**frontend_data)
                self.frontend_info = ServiceInfo(config=config)
            
            logger.info(f"設定ファイルを読み込みました: {len(self.services)}個のサービス")
            
        except FileNotFoundError:
            logger.error(f"設定ファイルが見つかりません: {self.config_file}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"設定ファイルの解析に失敗しました: {e}")
            raise
        except Exception as e:
            logger.error(f"設定ファイルの読み込みに失敗しました: {e}")
            raise
    
    def _signal_handler(self, signum, frame):
        """シグナルハンドラ"""
        logger.info(f"\nシグナル {signum} を受信しました。サービスを停止します...")
        self.stop_all_services()
        sys.exit(0)
    
    def start_service(self, service_name: str) -> bool:
        """
        個別サービスの起動
        
        Args:
            service_name: サービス名
            
        Returns:
            起動成功の場合True
        """
        # サービス情報の取得
        if service_name == "frontend":
            service_info = self.frontend_info
        else:
            service_info = self.services.get(service_name)
        
        if not service_info:
            logger.error(f"サービスが見つかりません: {service_name}")
            return False
        
        config = service_info.config
        
        # 既に起動している場合
        if service_info.status == ServiceStatus.RUNNING:
            logger.warning(f"サービスは既に起動しています: {config.display_name}")
            return True
        
        try:
            logger.info(f"サービスを起動しています: {config.display_name} (ポート: {config.port})")
            service_info.status = ServiceStatus.STARTING
            
            # 作業ディレクトリの確認
            service_path = Path(config.path)
            if not service_path.exists():
                raise FileNotFoundError(f"サービスディレクトリが見つかりません: {config.path}")
            
            # コマンドの実行
            process = subprocess.Popen(
                config.command,
                shell=True,
                cwd=config.path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            service_info.process = process
            service_info.pid = process.pid
            service_info.start_time = time.time()
            
            # ログ収集スレッドの開始
            self._start_log_thread(service_name, service_info)
            
            # ヘルスチェック（ヘルスエンドポイントがある場合）
            if config.health_endpoint:
                if self._wait_for_health(service_info):
                    service_info.status = ServiceStatus.RUNNING
                    logger.info(f"✓ サービスが起動しました: {config.display_name}")
                    return True
                else:
                    service_info.status = ServiceStatus.FAILED
                    service_info.error_message = "ヘルスチェックがタイムアウトしました"
                    logger.error(f"✗ サービスの起動に失敗しました: {config.display_name}")
                    return False
            else:
                # ヘルスエンドポイントがない場合は少し待機
                time.sleep(2)
                if process.poll() is None:
                    service_info.status = ServiceStatus.RUNNING
                    logger.info(f"✓ サービスが起動しました: {config.display_name}")
                    return True
                else:
                    service_info.status = ServiceStatus.FAILED
                    service_info.error_message = "プロセスが終了しました"
                    logger.error(f"✗ サービスの起動に失敗しました: {config.display_name}")
                    return False
                    
        except Exception as e:
            service_info.status = ServiceStatus.FAILED
            service_info.error_message = str(e)
            logger.error(f"サービスの起動中にエラーが発生しました: {config.display_name} - {e}")
            return False

    def _start_log_thread(self, service_name: str, service_info: ServiceInfo) -> None:
        """
        ログ収集スレッドの開始
        
        Args:
            service_name: サービス名
            service_info: サービス情報
        """
        stop_event = threading.Event()
        self.stop_log_threads[service_name] = stop_event
        
        def collect_logs():
            """ログを収集"""
            try:
                for line in service_info.process.stdout:
                    if stop_event.is_set():
                        break
                    line = line.strip()
                    if line:
                        service_info.logs.append(line)
                        # ログは最新100行のみ保持
                        if len(service_info.logs) > 100:
                            service_info.logs.pop(0)
            except Exception as e:
                logger.error(f"ログ収集エラー ({service_name}): {e}")
        
        thread = threading.Thread(target=collect_logs, daemon=True)
        thread.start()
        self.log_threads[service_name] = thread
    
    def _wait_for_health(self, service_info: ServiceInfo) -> bool:
        """
        ヘルスチェックを待機
        
        Args:
            service_info: サービス情報
            
        Returns:
            ヘルスチェック成功の場合True
        """
        config = service_info.config
        url = f"http://localhost:{config.port}{config.health_endpoint}"
        timeout = config.startup_timeout
        start_time = time.time()
        
        logger.info(f"ヘルスチェックを実行中: {config.display_name}")
        
        while time.time() - start_time < timeout:
            # プロセスが終了していないか確認
            if service_info.process.poll() is not None:
                logger.error(f"プロセスが終了しました: {config.display_name}")
                return False
            
            try:
                response = requests.get(url, timeout=1)
                if response.status_code == 200:
                    logger.info(f"ヘルスチェック成功: {config.display_name}")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(0.5)
        
        logger.error(f"ヘルスチェックがタイムアウトしました: {config.display_name}")
        return False
    
    def stop_service(self, service_name: str, graceful: bool = True) -> bool:
        """
        個別サービスの停止
        
        Args:
            service_name: サービス名
            graceful: グレースフルシャットダウンを行うか
            
        Returns:
            停止成功の場合True
        """
        # サービス情報の取得
        if service_name == "frontend":
            service_info = self.frontend_info
        else:
            service_info = self.services.get(service_name)
        
        if not service_info:
            logger.error(f"サービスが見つかりません: {service_name}")
            return False
        
        config = service_info.config
        
        # 既に停止している場合
        if service_info.status == ServiceStatus.STOPPED:
            logger.info(f"サービスは既に停止しています: {config.display_name}")
            return True
        
        if not service_info.process:
            logger.warning(f"プロセスが見つかりません: {config.display_name}")
            service_info.status = ServiceStatus.STOPPED
            return True
        
        try:
            logger.info(f"サービスを停止しています: {config.display_name}")
            service_info.status = ServiceStatus.STOPPING
            
            # ログスレッドの停止
            if service_name in self.stop_log_threads:
                self.stop_log_threads[service_name].set()
            
            if graceful:
                # グレースフルシャットダウン
                service_info.process.terminate()
                try:
                    service_info.process.wait(timeout=5)
                    logger.info(f"✓ サービスを停止しました: {config.display_name}")
                except subprocess.TimeoutExpired:
                    logger.warning(f"グレースフルシャットダウンがタイムアウトしました。強制終了します: {config.display_name}")
                    service_info.process.kill()
                    service_info.process.wait()
            else:
                # 強制終了
                service_info.process.kill()
                service_info.process.wait()
                logger.info(f"✓ サービスを強制終了しました: {config.display_name}")
            
            service_info.status = ServiceStatus.STOPPED
            service_info.process = None
            service_info.pid = None
            
            return True
            
        except Exception as e:
            logger.error(f"サービスの停止中にエラーが発生しました: {config.display_name} - {e}")
            return False
    
    def start_all_services(self, include_optional: bool = False) -> Dict[str, bool]:
        """
        全サービスの一括起動
        
        Args:
            include_optional: オプションサービスも起動するか
            
        Returns:
            各サービスの起動結果
        """
        results = {}
        
        logger.info("=" * 60)
        logger.info("全サービスを起動します")
        logger.info("=" * 60)
        
        # 必須サービスの起動
        for service_name, service_info in self.services.items():
            if service_info.config.required or include_optional:
                results[service_name] = self.start_service(service_name)
                time.sleep(1)  # サービス間の起動間隔
        
        # フロントエンドの起動
        if self.frontend_info and self.frontend_info.config.required:
            results["frontend"] = self.start_service("frontend")
        
        # 結果のサマリー
        logger.info("=" * 60)
        logger.info("起動結果:")
        success_count = sum(1 for success in results.values() if success)
        logger.info(f"成功: {success_count}/{len(results)}")
        
        for service_name, success in results.items():
            status = "✓" if success else "✗"
            logger.info(f"  {status} {service_name}")
        
        logger.info("=" * 60)
        
        return results
    
    def stop_all_services(self, graceful: bool = True) -> bool:
        """
        全サービスの一括停止
        
        Args:
            graceful: グレースフルシャットダウンを行うか
            
        Returns:
            全て停止成功の場合True
        """
        logger.info("=" * 60)
        logger.info("全サービスを停止します")
        logger.info("=" * 60)
        
        all_success = True
        
        # フロントエンドの停止
        if self.frontend_info:
            if not self.stop_service("frontend", graceful):
                all_success = False
        
        # バックエンドサービスの停止
        for service_name in self.services.keys():
            if not self.stop_service(service_name, graceful):
                all_success = False
        
        logger.info("=" * 60)
        if all_success:
            logger.info("✓ 全サービスを停止しました")
        else:
            logger.warning("一部のサービスの停止に失敗しました")
        logger.info("=" * 60)
        
        return all_success
    
    def restart_service(self, service_name: str) -> bool:
        """
        サービスの再起動
        
        Args:
            service_name: サービス名
            
        Returns:
            再起動成功の場合True
        """
        logger.info(f"サービスを再起動します: {service_name}")
        
        if not self.stop_service(service_name):
            return False
        
        time.sleep(1)
        
        return self.start_service(service_name)

    def check_service_health(self, service_name: str) -> Dict:
        """
        サービスヘルスチェック
        
        Args:
            service_name: サービス名
            
        Returns:
            ヘルスチェック結果
        """
        # サービス情報の取得
        if service_name == "frontend":
            service_info = self.frontend_info
        else:
            service_info = self.services.get(service_name)
        
        if not service_info:
            return {
                "service": service_name,
                "status": "not_found",
                "healthy": False,
                "message": "サービスが見つかりません"
            }
        
        config = service_info.config
        
        # プロセスの状態確認
        if not service_info.process:
            return {
                "service": service_name,
                "display_name": config.display_name,
                "status": service_info.status.value,
                "healthy": False,
                "message": "プロセスが起動していません"
            }
        
        # プロセスが終了していないか確認
        if service_info.process.poll() is not None:
            service_info.status = ServiceStatus.FAILED
            return {
                "service": service_name,
                "display_name": config.display_name,
                "status": "failed",
                "healthy": False,
                "message": "プロセスが終了しました",
                "exit_code": service_info.process.returncode
            }
        
        # ヘルスエンドポイントの確認
        if config.health_endpoint:
            url = f"http://localhost:{config.port}{config.health_endpoint}"
            try:
                response = requests.get(url, timeout=2)
                healthy = response.status_code == 200
                
                result = {
                    "service": service_name,
                    "display_name": config.display_name,
                    "status": service_info.status.value,
                    "healthy": healthy,
                    "port": config.port,
                    "pid": service_info.pid,
                    "uptime": time.time() - service_info.start_time if service_info.start_time else 0,
                    "http_status": response.status_code
                }
                
                # レスポンスボディがJSONの場合は含める
                try:
                    result["response"] = response.json()
                except:
                    pass
                
                return result
                
            except requests.exceptions.RequestException as e:
                return {
                    "service": service_name,
                    "display_name": config.display_name,
                    "status": service_info.status.value,
                    "healthy": False,
                    "port": config.port,
                    "pid": service_info.pid,
                    "message": f"ヘルスチェック失敗: {str(e)}"
                }
        else:
            # ヘルスエンドポイントがない場合はプロセスの存在のみ確認
            return {
                "service": service_name,
                "display_name": config.display_name,
                "status": service_info.status.value,
                "healthy": True,
                "port": config.port,
                "pid": service_info.pid,
                "uptime": time.time() - service_info.start_time if service_info.start_time else 0,
                "message": "プロセスは実行中（ヘルスエンドポイントなし）"
            }
    
    def check_all_services_health(self) -> Dict[str, Dict]:
        """
        全サービスのヘルスチェック
        
        Returns:
            各サービスのヘルスチェック結果
        """
        results = {}
        
        # バックエンドサービス
        for service_name in self.services.keys():
            results[service_name] = self.check_service_health(service_name)
        
        # フロントエンド
        if self.frontend_info:
            results["frontend"] = self.check_service_health("frontend")
        
        return results
    
    def wait_for_service_ready(self, service_name: str, timeout: int = 30) -> bool:
        """
        サービスの起動完了を待機
        
        Args:
            service_name: サービス名
            timeout: タイムアウト（秒）
            
        Returns:
            起動完了の場合True
        """
        start_time = time.time()
        
        logger.info(f"サービスの起動完了を待機中: {service_name}")
        
        while time.time() - start_time < timeout:
            health = self.check_service_health(service_name)
            
            if health.get("healthy"):
                logger.info(f"✓ サービスの起動が完了しました: {service_name}")
                return True
            
            if health.get("status") == "failed":
                logger.error(f"✗ サービスの起動に失敗しました: {service_name}")
                return False
            
            time.sleep(1)
        
        logger.error(f"✗ サービスの起動がタイムアウトしました: {service_name}")
        return False
    
    def monitor_services(self, interval: int = 5, duration: int = 60) -> None:
        """
        サービス状態の監視
        
        Args:
            interval: チェック間隔（秒）
            duration: 監視時間（秒）、0の場合は無限
        """
        logger.info("=" * 60)
        logger.info("サービス監視を開始します")
        logger.info(f"チェック間隔: {interval}秒")
        if duration > 0:
            logger.info(f"監視時間: {duration}秒")
        else:
            logger.info("監視時間: 無限（Ctrl+Cで停止）")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        try:
            while True:
                # 監視時間のチェック
                if duration > 0 and time.time() - start_time >= duration:
                    break
                
                # ヘルスチェック
                results = self.check_all_services_health()
                
                # 結果の表示
                logger.info("\n" + "=" * 60)
                logger.info(f"ヘルスチェック結果 ({time.strftime('%H:%M:%S')})")
                logger.info("=" * 60)
                
                for service_name, health in results.items():
                    status_icon = "✓" if health.get("healthy") else "✗"
                    display_name = health.get("display_name", service_name)
                    status = health.get("status", "unknown")
                    
                    logger.info(f"{status_icon} {display_name} ({service_name}): {status}")
                    
                    if health.get("uptime"):
                        uptime_str = f"{health['uptime']:.1f}秒"
                        logger.info(f"   稼働時間: {uptime_str}")
                    
                    if not health.get("healthy") and health.get("message"):
                        logger.info(f"   メッセージ: {health['message']}")
                
                logger.info("=" * 60)
                
                # 次のチェックまで待機
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("\n監視を停止します")

    def get_service_logs(self, service_name: str, lines: int = 50, level: Optional[str] = None) -> List[str]:
        """
        サービスログの取得
        
        Args:
            service_name: サービス名
            lines: 取得する行数
            level: ログレベルでフィルタリング（INFO, WARNING, ERROR等）
            
        Returns:
            ログ行のリスト
        """
        # サービス情報の取得
        if service_name == "frontend":
            service_info = self.frontend_info
        else:
            service_info = self.services.get(service_name)
        
        if not service_info:
            logger.error(f"サービスが見つかりません: {service_name}")
            return []
        
        logs = service_info.logs.copy()
        
        # ログレベルでフィルタリング
        if level:
            level_upper = level.upper()
            logs = [log for log in logs if level_upper in log.upper()]
        
        # 指定行数のみ返す
        return logs[-lines:] if lines > 0 else logs
    
    def display_service_logs(self, service_name: str, lines: int = 50, level: Optional[str] = None) -> None:
        """
        サービスログの表示
        
        Args:
            service_name: サービス名
            lines: 表示する行数
            level: ログレベルでフィルタリング
        """
        # サービス情報の取得
        if service_name == "frontend":
            service_info = self.frontend_info
        else:
            service_info = self.services.get(service_name)
        
        if not service_info:
            logger.error(f"サービスが見つかりません: {service_name}")
            return
        
        config = service_info.config
        logs = self.get_service_logs(service_name, lines, level)
        
        logger.info("=" * 60)
        logger.info(f"サービスログ: {config.display_name} ({service_name})")
        if level:
            logger.info(f"フィルタ: {level}")
        logger.info(f"表示行数: {len(logs)}")
        logger.info("=" * 60)
        
        for log in logs:
            print(log)
        
        logger.info("=" * 60)
    
    def save_service_logs(self, service_name: str, output_file: str, level: Optional[str] = None) -> bool:
        """
        サービスログをファイルに保存
        
        Args:
            service_name: サービス名
            output_file: 出力ファイルパス
            level: ログレベルでフィルタリング
            
        Returns:
            保存成功の場合True
        """
        try:
            logs = self.get_service_logs(service_name, lines=0, level=level)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                for log in logs:
                    f.write(log + '\n')
            
            logger.info(f"ログをファイルに保存しました: {output_file} ({len(logs)}行)")
            return True
            
        except Exception as e:
            logger.error(f"ログの保存に失敗しました: {e}")
            return False
    
    def save_all_logs(self, output_dir: str = "logs") -> bool:
        """
        全サービスのログを保存
        
        Args:
            output_dir: 出力ディレクトリ
            
        Returns:
            保存成功の場合True
        """
        try:
            # 出力ディレクトリの作成
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            all_success = True
            
            # バックエンドサービス
            for service_name in self.services.keys():
                output_file = os.path.join(output_dir, f"{service_name}_{timestamp}.log")
                if not self.save_service_logs(service_name, output_file):
                    all_success = False
            
            # フロントエンド
            if self.frontend_info:
                output_file = os.path.join(output_dir, f"frontend_{timestamp}.log")
                if not self.save_service_logs("frontend", output_file):
                    all_success = False
            
            if all_success:
                logger.info(f"✓ 全サービスのログを保存しました: {output_dir}")
            else:
                logger.warning("一部のログの保存に失敗しました")
            
            return all_success
            
        except Exception as e:
            logger.error(f"ログの保存に失敗しました: {e}")
            return False
    
    def tail_service_logs(self, service_name: str, follow: bool = True) -> None:
        """
        サービスログのリアルタイム表示
        
        Args:
            service_name: サービス名
            follow: ログを追跡するか
        """
        # サービス情報の取得
        if service_name == "frontend":
            service_info = self.frontend_info
        else:
            service_info = self.services.get(service_name)
        
        if not service_info:
            logger.error(f"サービスが見つかりません: {service_name}")
            return
        
        config = service_info.config
        
        logger.info("=" * 60)
        logger.info(f"サービスログ（リアルタイム）: {config.display_name}")
        logger.info("Ctrl+Cで停止")
        logger.info("=" * 60)
        
        # 既存のログを表示
        for log in service_info.logs[-20:]:
            print(log)
        
        if not follow:
            return
        
        # 新しいログを追跡
        last_index = len(service_info.logs)
        
        try:
            while True:
                current_logs = service_info.logs
                if len(current_logs) > last_index:
                    for log in current_logs[last_index:]:
                        print(log)
                    last_index = len(current_logs)
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            logger.info("\nログ表示を停止します")
    
    def get_service_status(self, service_name: str) -> Dict:
        """
        サービスの詳細状態を取得
        
        Args:
            service_name: サービス名
            
        Returns:
            サービス状態の詳細情報
        """
        # サービス情報の取得
        if service_name == "frontend":
            service_info = self.frontend_info
        else:
            service_info = self.services.get(service_name)
        
        if not service_info:
            return {"error": "サービスが見つかりません"}
        
        config = service_info.config
        
        status = {
            "name": service_name,
            "display_name": config.display_name,
            "description": config.description,
            "status": service_info.status.value,
            "port": config.port,
            "required": config.required,
            "pid": service_info.pid,
            "log_count": len(service_info.logs)
        }
        
        if service_info.start_time:
            status["uptime"] = time.time() - service_info.start_time
            status["start_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(service_info.start_time))
        
        if service_info.error_message:
            status["error_message"] = service_info.error_message
        
        return status
    
    def get_all_services_status(self) -> Dict[str, Dict]:
        """
        全サービスの状態を取得
        
        Returns:
            各サービスの状態情報
        """
        results = {}
        
        # バックエンドサービス
        for service_name in self.services.keys():
            results[service_name] = self.get_service_status(service_name)
        
        # フロントエンド
        if self.frontend_info:
            results["frontend"] = self.get_service_status("frontend")
        
        return results
    
    def display_status_summary(self) -> None:
        """サービス状態のサマリーを表示"""
        statuses = self.get_all_services_status()
        
        logger.info("=" * 60)
        logger.info("サービス状態サマリー")
        logger.info("=" * 60)
        
        for service_name, status in statuses.items():
            if "error" in status:
                logger.error(f"✗ {service_name}: {status['error']}")
                continue
            
            status_value = status.get("status", "unknown")
            status_icon = "✓" if status_value == "running" else "✗"
            
            display_name = status.get("display_name", service_name)
            port = status.get("port", "N/A")
            
            logger.info(f"{status_icon} {display_name} ({service_name})")
            logger.info(f"   ポート: {port}")
            logger.info(f"   状態: {status_value}")
            
            if status.get("uptime"):
                uptime_str = f"{status['uptime']:.1f}秒"
                logger.info(f"   稼働時間: {uptime_str}")
            
            if status.get("error_message"):
                logger.info(f"   エラー: {status['error_message']}")
            
            logger.info("")
        
        logger.info("=" * 60)
    
    def prepare_frontend_integration(self) -> bool:
        """
        フロントエンド統合の準備
        
        Returns:
            準備成功の場合True
        """
        try:
            logger.info("=" * 60)
            logger.info("フロントエンド統合の準備を開始します")
            logger.info("=" * 60)
            
            # テスト用トークンファイルの生成
            logger.info("テスト用JWTトークンを生成中...")
            if not self.frontend_helper.generate_test_tokens_file():
                logger.warning("トークンファイルの生成に失敗しましたが、続行します")
            
            # フロントエンド用環境変数ファイルの生成
            logger.info("フロントエンド用環境変数ファイルを生成中...")
            if not self.frontend_helper.generate_env_file_for_frontend():
                logger.warning("環境変数ファイルの生成に失敗しましたが、続行します")
            
            # CORS設定の確認
            logger.info("CORS設定を確認中...")
            self.frontend_helper.update_vite_config_for_cors()
            
            logger.info("=" * 60)
            logger.info("✓ フロントエンド統合の準備が完了しました")
            logger.info("=" * 60)
            
            # 統合情報の表示
            self.frontend_helper.display_integration_info()
            
            return True
            
        except Exception as e:
            logger.error(f"フロントエンド統合の準備中にエラーが発生しました: {e}")
            return False
    
    def start_with_frontend(self, include_optional: bool = False) -> Dict[str, bool]:
        """
        フロントエンドを含む全サービスの起動
        
        Args:
            include_optional: オプションサービスも起動するか
            
        Returns:
            各サービスの起動結果
        """
        # フロントエンド統合の準備
        if not self.prepare_frontend_integration():
            logger.warning("フロントエンド統合の準備に失敗しましたが、サービスを起動します")
        
        # 全サービスの起動
        return self.start_all_services(include_optional=include_optional)
    
    def display_frontend_integration_info(self) -> None:
        """フロントエンド統合情報を表示"""
        self.frontend_helper.display_integration_info()


def main():
    """メイン関数（テスト用）"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ローカルサービスマネージャー")
    parser.add_argument("command", 
                       choices=["start", "stop", "restart", "status", "health", "logs", "monitor", "frontend-info", "prepare-frontend"],
                       help="実行するコマンド")
    parser.add_argument("--service", "-s", help="対象サービス名")
    parser.add_argument("--all", "-a", action="store_true", help="全サービスを対象")
    parser.add_argument("--optional", action="store_true", help="オプションサービスも含める")
    parser.add_argument("--with-frontend", action="store_true", help="フロントエンド統合準備を含める")
    parser.add_argument("--lines", "-n", type=int, default=50, help="ログ表示行数")
    parser.add_argument("--level", "-l", help="ログレベルフィルタ")
    parser.add_argument("--follow", "-f", action="store_true", help="ログを追跡")
    
    args = parser.parse_args()
    
    manager = LocalServiceManager()
    
    if args.command == "start":
        if args.all:
            if args.with_frontend:
                manager.start_with_frontend(include_optional=args.optional)
            else:
                manager.start_all_services(include_optional=args.optional)
        elif args.service:
            manager.start_service(args.service)
        else:
            print("エラー: --all または --service を指定してください")
    
    elif args.command == "stop":
        if args.all:
            manager.stop_all_services()
        elif args.service:
            manager.stop_service(args.service)
        else:
            print("エラー: --all または --service を指定してください")
    
    elif args.command == "restart":
        if args.service:
            manager.restart_service(args.service)
        else:
            print("エラー: --service を指定してください")
    
    elif args.command == "status":
        manager.display_status_summary()
    
    elif args.command == "health":
        if args.all:
            results = manager.check_all_services_health()
            for service_name, health in results.items():
                print(f"{service_name}: {health}")
        elif args.service:
            health = manager.check_service_health(args.service)
            print(health)
        else:
            print("エラー: --all または --service を指定してください")
    
    elif args.command == "logs":
        if args.service:
            if args.follow:
                manager.tail_service_logs(args.service)
            else:
                manager.display_service_logs(args.service, lines=args.lines, level=args.level)
        else:
            print("エラー: --service を指定してください")
    
    elif args.command == "monitor":
        manager.monitor_services()
    
    elif args.command == "frontend-info":
        manager.display_frontend_integration_info()
    
    elif args.command == "prepare-frontend":
        if manager.prepare_frontend_integration():
            print("\n✓ フロントエンド統合の準備が完了しました")
        else:
            print("\n✗ フロントエンド統合の準備に失敗しました")


if __name__ == "__main__":
    main()
