# -*- coding: utf-8 -*-
"""
YouTube用户频道服务类 - 专门用于搜索特定用户的帖子
"""

import time
import logging
from typing import List, Dict, Optional, Tuple
from selenium.webdriver.common.by import By

from .browser_service import BrowserService
from .youtube_service import YouTubeService
from .data_service import DataService
from .logging_service import LoggingService


class YouTubeUserService:
    """YouTube用户频道服务类 - 专门用于搜索特定用户的帖子"""
    
    def __init__(self, headless: bool = None):
        """
        初始化用户服务
        
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
        """启动用户服务"""
        self.logging_service.log_startup()
        
        # 创建浏览器驱动
        self.browser_service.create_driver(self.headless)
        
        # 创建YouTube服务
        self.youtube_service = YouTubeService(self.browser_service.get_driver())
        
        self.logger.info("用户服务启动成功")
    
    def stop(self):
        """停止用户服务"""
        if self.browser_service:
            self.browser_service.close_driver()
        
        self.logging_service.log_shutdown()
        self.logger.info("用户服务已停止")
    
    def search_user_videos(self, username: str, max_videos: int = None):
        """
        搜索特定用户的YouTube视频
        
        Args:
            username: 用户名
            max_videos: 最大视频数量
            
        Returns:
            视频信息列表
        """
        if not self.youtube_service:
            raise RuntimeError("用户服务未启动，请先调用start()方法")
        
        # 验证输入
        is_valid, message = self._validate_username(username)
        if not is_valid:
            raise ValueError(f"用户名无效: {message}")
        
        if max_videos is not None:
            is_valid, message = self.youtube_service.validate_max_videos(max_videos)
            if not is_valid:
                raise ValueError(f"视频数量无效: {message}")
        
        # 记录搜索开始
        self.logging_service.log_search_start(f"用户: {username}", max_videos or 10)
        
        try:
            # 执行用户搜索
            videos = self._search_user_videos(username, max_videos)
            
            # 记录搜索完成
            self.logging_service.log_search_complete(len(videos))
            
            return videos
            
        except Exception as e:
            self.logging_service.log_error(e, "搜索用户视频时出错")
            raise
    
    def _validate_username(self, username: str):
        """
        验证用户名
        
        Args:
            username: 用户名
            
        Returns:
            (是否有效, 错误信息)
        """
        if not username or not username.strip():
            return False, "用户名不能为空"
        
        if len(username.strip()) < 2:
            return False, "用户名至少需要2个字符"
        
        if len(username.strip()) > 50:
            return False, "用户名不能超过50个字符"
        
        return True, ""
    
    def _search_user_videos(self, username: str, max_videos: int = None):
        """
        搜索用户视频的具体实现
        
        Args:
            username: 用户名
            max_videos: 最大视频数量
            
        Returns:
            视频信息列表
        """
        if max_videos is None:
            from ..config.settings import SCRAPER_CONFIG
            max_videos = SCRAPER_CONFIG["max_videos"]
        
        self.logger.info(f"开始搜索用户: {username}, 最大数量: {max_videos}")
        
        try:
            # 构建用户频道URL
            channel_url = f"https://www.youtube.com/@{username}/videos"
            
            # 访问用户频道页面
            self._navigate_to_user_channel(channel_url)
            
            # 滚动加载更多视频
            self._scroll_to_load_videos()
            
            # 提取视频链接
            from ..utils.element_extractors import extract_video_links
            video_links = extract_video_links(self.youtube_service.driver, max_videos)
            self.logger.info(f"获取到 {len(video_links)} 个视频链接")
            
            # 处理每个视频
            videos = []
            for i, link in enumerate(video_links):
                if i >= max_videos:
                    break
                
                video_info = self._process_single_video(link, i + 1)
                if video_info:
                    videos.append(video_info)
            
            self.logger.info(f"成功处理 {len(videos)} 个视频")
            return videos
            
        except Exception as e:
            self.logger.error(f"搜索用户视频过程中出错: {str(e)}")
            return []
    
    def _navigate_to_user_channel(self, channel_url: str):
        """导航到用户频道页面（默认按最新时间排序）"""
        self.logger.info(f"正在访问用户频道: {channel_url}")
        self.youtube_service.driver.get(channel_url)
        
        from ..config.settings import SCRAPER_CONFIG
        time.sleep(SCRAPER_CONFIG["page_load_delay"])
        
        # YouTube频道的/videos页面默认就是按最新时间排序的
        self.logger.info("页面已按最新时间排序（默认）")
    
    def _scroll_to_load_videos(self):
        """滚动页面以加载更多视频"""
        self.logger.info("正在加载用户视频...")
        
        from ..config.settings import SCRAPER_CONFIG
        scroll_count = SCRAPER_CONFIG["scroll_count"]
        scroll_delay = SCRAPER_CONFIG["scroll_delay"]
        
        for i in range(scroll_count):
            self.youtube_service.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_delay)
    
    def _process_single_video(self, video_url: str, index: int):
        """处理单个视频"""
        try:
            self.logger.info(f"处理第 {index} 个视频: {video_url}")
            video_info = self.youtube_service._extract_video_details(video_url)
            return video_info
        except Exception as e:
            self.logger.error(f"处理视频时出错: {str(e)}")
            return None
    
    def save_results(self, videos, username: str):
        """
        保存搜索结果
        
        Args:
            videos: 视频数据列表
            username: 用户名
            
        Returns:
            保存的文件路径字典
        """
        try:
            # 保存数据
            saved_files = self.data_service.save_videos(videos, f"user_{username}")
            
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
    
    def run(self, username: str, max_videos: int = None):
        """
        运行完整的用户爬虫流程
        
        Args:
            username: 用户名
            max_videos: 最大视频数量
            
        Returns:
            保存的文件路径字典
        """
        try:
            # 搜索用户视频
            videos = self.search_user_videos(username, max_videos)
            
            # 保存结果
            saved_files = self.save_results(videos, username)
            
            return saved_files
            
        except Exception as e:
            self.logging_service.log_error(e, "运行用户爬虫时出错")
            raise 