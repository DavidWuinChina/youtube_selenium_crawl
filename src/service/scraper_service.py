# -*- coding: utf-8 -*-
"""
YouTube爬虫服务类 - 使用服务层架构
"""

from .browser_service import BrowserService
from .youtube_service import YouTubeService
from .data_service import DataService
from .logging_service import LoggingService


class YouTubeScraperService:
    """YouTube爬虫服务类 - 使用服务层架构"""
    
    def __init__(self, headless: bool = None):
        """
        初始化爬虫服务
        
        Args:
            headless: 是否无头模式
        """
        self.headless = headless
        self.browser_service = BrowserService()
        self.youtube_service = None
        self.data_service = DataService()
        self.logging_service = LoggingService()
        self.logger = self.logging_service.get_logger(__name__)
    
    def __enter__(self):
        """上下文管理器入口"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.stop()
    
    def start(self):
        """启动爬虫服务"""
        self.logging_service.log_startup()
        
        # 创建浏览器驱动
        self.browser_service.create_driver(self.headless)
        
        # 创建YouTube服务
        self.youtube_service = YouTubeService(self.browser_service.get_driver())
        
        self.logger.info("爬虫服务启动成功")
    
    def stop(self):
        """停止爬虫服务"""
        if self.browser_service:
            self.browser_service.close_driver()
        
        self.logging_service.log_shutdown()
        self.logger.info("爬虫服务已停止")
    
    def search_videos(self, search_query: str, max_videos: int = None):
        """
        搜索YouTube视频
        
        Args:
            search_query: 搜索关键词
            max_videos: 最大视频数量
            
        Returns:
            视频信息列表
        """
        if not self.youtube_service:
            raise RuntimeError("爬虫服务未启动，请先调用start()方法")
        
        # 验证输入
        is_valid, message = self.youtube_service.validate_search_query(search_query)
        if not is_valid:
            raise ValueError(f"搜索关键词无效: {message}")
        
        if max_videos is not None:
            is_valid, message = self.youtube_service.validate_max_videos(max_videos)
            if not is_valid:
                raise ValueError(f"视频数量无效: {message}")
        
        # 记录搜索开始
        self.logging_service.log_search_start(search_query, max_videos or 10)
        
        try:
            # 执行搜索
            videos = self.youtube_service.search_videos(search_query, max_videos)
            
            # 记录搜索完成
            self.logging_service.log_search_complete(len(videos))
            
            return videos
            
        except Exception as e:
            self.logging_service.log_error(e, "搜索视频时出错")
            raise
    
    def save_results(self, videos, search_query: str):
        """
        保存搜索结果
        
        Args:
            videos: 视频数据列表
            search_query: 搜索关键词
            
        Returns:
            保存的文件路径字典
        """
        try:
            # 保存数据
            saved_files = self.data_service.save_videos(videos, search_query)
            
            # 显示摘要
            self.data_service.display_video_summary(videos)
            
            # 显示统计信息
            stats = self.data_service.get_statistics(videos)
            if stats:
                self.logger.info(f"统计信息: {stats}")
            
            return saved_files
            
        except Exception as e:
            self.logging_service.log_error(e, "保存结果时出错")
            raise
    
    def run(self, search_query: str, max_videos: int = None):
        """
        运行完整的爬虫流程
        
        Args:
            search_query: 搜索关键词
            max_videos: 最大视频数量
            
        Returns:
            保存的文件路径字典
        """
        try:
            # 搜索视频
            videos = self.search_videos(search_query, max_videos)
            
            # 保存结果
            saved_files = self.save_results(videos, search_query)
            
            return saved_files
            
        except Exception as e:
            self.logging_service.log_error(e, "运行爬虫时出错")
            raise 