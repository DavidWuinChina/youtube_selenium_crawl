# -*- coding: utf-8 -*-
"""
日志服务 - 处理日志配置和管理
"""

import os
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

from ..config.settings import LOGGING_CONFIG, BASE_DIR


class LoggingService:
    """日志服务类 - 处理日志配置和管理"""
    
    def __init__(self):
        self._setup_logging()
    
    def _setup_logging(self):
        """设置日志配置"""
        # 创建日志目录
        log_dir = os.path.join(BASE_DIR, "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # 配置根日志记录器
        logging.basicConfig(
            level=getattr(logging, LOGGING_CONFIG["level"]),
            format=LOGGING_CONFIG["format"],
            handlers=[
                # 控制台处理器
                logging.StreamHandler(),
                # 文件处理器
                RotatingFileHandler(
                    LOGGING_CONFIG["file"],
                    maxBytes=10*1024*1024,  # 10MB
                    backupCount=5,
                    encoding='utf-8'
                )
            ]
        )
        
        # 设置第三方库的日志级别
        logging.getLogger("selenium").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("webdriver_manager").setLevel(logging.WARNING)
    
    def get_logger(self, name: str) -> logging.Logger:
        """获取指定名称的日志记录器"""
        return logging.getLogger(name)
    
    def log_startup(self):
        """记录启动日志"""
        logger = self.get_logger(__name__)
        logger.info("=" * 60)
        logger.info("YouTube爬虫服务启动")
        logger.info("=" * 60)
    
    def log_shutdown(self):
        """记录关闭日志"""
        logger = self.get_logger(__name__)
        logger.info("=" * 60)
        logger.info("YouTube爬虫服务关闭")
        logger.info("=" * 60)
    
    def log_search_start(self, search_query: str, max_videos: int):
        """记录搜索开始日志"""
        logger = self.get_logger(__name__)
        logger.info(f"开始搜索: {search_query}")
        logger.info(f"最大视频数量: {max_videos}")
        logger.info("-" * 40)
    
    def log_search_complete(self, videos_count: int):
        """记录搜索完成日志"""
        logger = self.get_logger(__name__)
        logger.info("-" * 40)
        logger.info(f"搜索完成，共获取 {videos_count} 个视频")
    
    def log_error(self, error: Exception, context: str = ""):
        """记录错误日志"""
        logger = self.get_logger(__name__)
        if context:
            logger.error(f"{context}: {str(error)}")
        else:
            logger.error(f"发生错误: {str(error)}")
    
    def log_warning(self, message: str):
        """记录警告日志"""
        logger = self.get_logger(__name__)
        logger.warning(message)
    
    def log_info(self, message: str):
        """记录信息日志"""
        logger = self.get_logger(__name__)
        logger.info(message)
    
    def log_debug(self, message: str):
        """记录调试日志"""
        logger = self.get_logger(__name__)
        logger.debug(message) 