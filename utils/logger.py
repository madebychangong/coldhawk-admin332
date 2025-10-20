"""
로거 설정 및 관리
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from .constants import get_logs_dir, APP_SLUG


class AppLogger:
    """앱 로거 싱글톤"""
    _instance = None
    _logger = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup_logger()
        return cls._instance
    
    def _setup_logger(self):
        """로거 초기화"""
        self._logger = logging.getLogger(APP_SLUG)
        
        # 이미 핸들러가 있으면 중복 방지
        if self._logger.handlers:
            return
        
        self._logger.setLevel(logging.INFO)
        
        # 파일 핸들러 (로그 로테이션)
        log_file = os.path.join(get_logs_dir(), f'{APP_SLUG}.log')
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        
        # 콘솔 핸들러 추가
        console_handler = logging.StreamHandler()
        
        # 포맷
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)
    
    def get_logger(self):
        """로거 인스턴스 반환"""
        return self._logger
    
    @staticmethod
    def info(msg):
        """INFO 로그"""
        AppLogger().get_logger().info(msg)
    
    @staticmethod
    def warning(msg):
        """WARNING 로그"""
        AppLogger().get_logger().warning(msg)
    
    @staticmethod
    def error(msg):
        """ERROR 로그"""
        AppLogger().get_logger().error(msg)
    
    @staticmethod
    def debug(msg):
        """DEBUG 로그"""
        AppLogger().get_logger().debug(msg)
    
    @staticmethod
    def exception(msg):
        """EXCEPTION 로그 (스택 트레이스 포함)"""
        AppLogger().get_logger().exception(msg)


# 전역 로거 인스턴스
logger = AppLogger()