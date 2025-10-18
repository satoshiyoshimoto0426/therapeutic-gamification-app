"""
ローカルテスト環境のロギングシステム

このモジュールは、構造化ログ、ログレベル管理、
ログファイルローテーションを提供します。
"""

import logging
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Union
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from enum import Enum


class LogLevel(Enum):
    """ログレベルの列挙"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class LogFormat(Enum):
    """ログフォーマットの種類"""
    SIMPLE = "simple"      # シンプルなテキスト形式
    DETAILED = "detailed"  # 詳細なテキスト形式
    JSON = "json"          # JSON形式（構造化ログ）


class ColoredFormatter(logging.Formatter):
    """カラー付きログフォーマッター（コンソール出力用）"""
    
    # ANSIカラーコード
    COLORS = {
        'DEBUG': '\033[36m',      # シアン
        'INFO': '\033[32m',       # 緑
        'WARNING': '\033[33m',    # 黄
        'ERROR': '\033[31m',      # 赤
        'CRITICAL': '\033[35m',   # マゼンタ
        'RESET': '\033[0m'        # リセット
    }
    
    # レベルアイコン
    ICONS = {
        'DEBUG': '🔍',
        'INFO': 'ℹ️',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🔴'
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """ログレコードをフォーマット"""
        # カラーとアイコンを追加
        levelname = record.levelname
        color = self.COLORS.get(levelname, self.COLORS['RESET'])
        icon = self.ICONS.get(levelname, '')
        reset = self.COLORS['RESET']
        
        # レコードを一時的に変更
        original_levelname = record.levelname
        record.levelname = f"{color}{icon} {levelname}{reset}"
        
        # フォーマット
        result = super().format(record)
        
        # 元に戻す
        record.levelname = original_levelname
        
        return result


class JsonFormatter(logging.Formatter):
    """JSON形式のログフォーマッター（構造化ログ）"""
    
    def format(self, record: logging.LogRecord) -> str:
        """ログレコードをJSON形式でフォーマット"""
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # 追加のフィールド
        if hasattr(record, 'service_name'):
            log_data['service_name'] = record.service_name
        
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        
        # 例外情報
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # カスタムフィールド
        if hasattr(record, 'extra_data'):
            log_data['extra'] = record.extra_data
        
        return json.dumps(log_data, ensure_ascii=False)


class LocalTestLogger:
    """ローカルテスト環境用のロガー"""
    
    def __init__(
        self,
        name: str = "local_test",
        log_level: LogLevel = LogLevel.INFO,
        log_dir: Optional[Path] = None,
        console_format: LogFormat = LogFormat.SIMPLE,
        file_format: LogFormat = LogFormat.JSON,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        enable_rotation: bool = True
    ):
        """
        Args:
            name: ロガー名
            log_level: ログレベル
            log_dir: ログディレクトリ
            console_format: コンソール出力のフォーマット
            file_format: ファイル出力のフォーマット
            max_file_size: ログファイルの最大サイズ（バイト）
            backup_count: バックアップファイルの数
            enable_rotation: ログローテーションを有効にするか
        """
        self.name = name
        self.log_level = log_level
        self.log_dir = log_dir or Path("logs")
        self.console_format = console_format
        self.file_format = file_format
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        self.enable_rotation = enable_rotation
        
        # ログディレクトリを作成
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # ロガーを設定
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level.value)
        self.logger.handlers.clear()  # 既存のハンドラをクリア
        
        # ハンドラを追加
        self._setup_console_handler()
        self._setup_file_handler()
    
    def _setup_console_handler(self) -> None:
        """コンソールハンドラを設定"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level.value)
        
        # フォーマッターを設定
        if self.console_format == LogFormat.JSON:
            formatter = JsonFormatter()
        elif self.console_format == LogFormat.DETAILED:
            formatter = ColoredFormatter(
                '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        else:  # SIMPLE
            formatter = ColoredFormatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S'
            )
        
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def _setup_file_handler(self) -> None:
        """ファイルハンドラを設定"""
        log_file = self.log_dir / f"{self.name}.log"
        
        # ローテーションハンドラを選択
        if self.enable_rotation:
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
        else:
            file_handler = logging.FileHandler(
                log_file,
                encoding='utf-8'
            )
        
        file_handler.setLevel(self.log_level.value)
        
        # フォーマッターを設定
        if self.file_format == LogFormat.JSON:
            formatter = JsonFormatter()
        elif self.file_format == LogFormat.DETAILED:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        else:  # SIMPLE
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def debug(self, message: str, **kwargs) -> None:
        """デバッグログを出力"""
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """情報ログを出力"""
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """警告ログを出力"""
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """エラーログを出力"""
        self._log(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """重大エラーログを出力"""
        self._log(logging.CRITICAL, message, **kwargs)
    
    def _log(self, level: int, message: str, **kwargs) -> None:
        """ログを出力（内部メソッド）"""
        extra = {}
        
        # カスタムフィールドを追加
        if 'service_name' in kwargs:
            extra['service_name'] = kwargs.pop('service_name')
        
        if 'request_id' in kwargs:
            extra['request_id'] = kwargs.pop('request_id')
        
        if 'user_id' in kwargs:
            extra['user_id'] = kwargs.pop('user_id')
        
        if kwargs:
            extra['extra_data'] = kwargs
        
        self.logger.log(level, message, extra=extra)
    
    def log_exception(self, message: str, exc_info: bool = True, **kwargs) -> None:
        """例外情報を含むログを出力"""
        extra = {}
        if kwargs:
            extra['extra_data'] = kwargs
        
        self.logger.error(message, exc_info=exc_info, extra=extra)
    
    def set_level(self, level: LogLevel) -> None:
        """ログレベルを変更"""
        self.log_level = level
        self.logger.setLevel(level.value)
        for handler in self.logger.handlers:
            handler.setLevel(level.value)
    
    def get_logger(self) -> logging.Logger:
        """標準のロガーオブジェクトを取得"""
        return self.logger


class ServiceLogger:
    """サービス専用のロガー"""
    
    def __init__(
        self,
        service_name: str,
        base_logger: Optional[LocalTestLogger] = None,
        log_dir: Optional[Path] = None
    ):
        """
        Args:
            service_name: サービス名
            base_logger: ベースとなるロガー
            log_dir: ログディレクトリ
        """
        self.service_name = service_name
        
        if base_logger:
            self.logger = base_logger
        else:
            log_dir = log_dir or Path("logs") / "services"
            self.logger = LocalTestLogger(
                name=f"service.{service_name}",
                log_dir=log_dir
            )
    
    def debug(self, message: str, **kwargs) -> None:
        """デバッグログを出力"""
        self.logger.debug(message, service_name=self.service_name, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """情報ログを出力"""
        self.logger.info(message, service_name=self.service_name, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """警告ログを出力"""
        self.logger.warning(message, service_name=self.service_name, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """エラーログを出力"""
        self.logger.error(message, service_name=self.service_name, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """重大エラーログを出力"""
        self.logger.critical(message, service_name=self.service_name, **kwargs)
    
    def log_exception(self, message: str, exc_info: bool = True, **kwargs) -> None:
        """例外情報を含むログを出力"""
        self.logger.log_exception(
            message,
            exc_info=exc_info,
            service_name=self.service_name,
            **kwargs
        )


# グローバルロガーインスタンス
_global_logger: Optional[LocalTestLogger] = None


def get_logger(
    name: Optional[str] = None,
    log_level: Optional[LogLevel] = None
) -> LocalTestLogger:
    """
    グローバルロガーを取得
    
    Args:
        name: ロガー名（Noneの場合はグローバルロガーを使用）
        log_level: ログレベル
        
    Returns:
        LocalTestLogger: ロガーインスタンス
    """
    global _global_logger
    
    if name:
        # 新しいロガーを作成
        return LocalTestLogger(
            name=name,
            log_level=log_level or LogLevel.INFO
        )
    
    # グローバルロガーを返す
    if _global_logger is None:
        _global_logger = LocalTestLogger(
            log_level=log_level or LogLevel.INFO
        )
    elif log_level:
        _global_logger.set_level(log_level)
    
    return _global_logger


def setup_logging(
    log_level: LogLevel = LogLevel.INFO,
    log_dir: Optional[Path] = None,
    console_format: LogFormat = LogFormat.SIMPLE,
    file_format: LogFormat = LogFormat.JSON
) -> LocalTestLogger:
    """
    ロギングシステムを初期化
    
    Args:
        log_level: ログレベル
        log_dir: ログディレクトリ
        console_format: コンソール出力のフォーマット
        file_format: ファイル出力のフォーマット
        
    Returns:
        LocalTestLogger: 設定されたロガー
    """
    global _global_logger
    
    _global_logger = LocalTestLogger(
        log_level=log_level,
        log_dir=log_dir,
        console_format=console_format,
        file_format=file_format
    )
    
    return _global_logger


def get_service_logger(service_name: str) -> ServiceLogger:
    """
    サービス専用のロガーを取得
    
    Args:
        service_name: サービス名
        
    Returns:
        ServiceLogger: サービスロガー
    """
    return ServiceLogger(service_name=service_name, base_logger=get_logger())
