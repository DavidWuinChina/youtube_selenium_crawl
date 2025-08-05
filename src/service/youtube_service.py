# -*- coding: utf-8 -*-
"""
YouTube服务层 - 处理业务逻辑
"""

import time
import logging
from typing import List, Dict, Optional, Tuple
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

from ..config.settings import (
    SCRAPER_CONFIG, 
    YOUTUBE_CONFIG, 
    OUTPUT_CONFIG,
    ERROR_CONFIG
)
from ..utils.extractors import (
    extract_title,
    extract_channel_name,
    extract_view_count_and_date,
    extract_video_description,
    extract_video_links
)
from ..utils.selectors import PAGE_LOAD_SELECTORS


class YouTubeService:
    """YouTube服务类 - 处理爬虫业务逻辑"""
    
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.logger = logging.getLogger(__name__)
    
    def search_videos(self, search_query: str, max_videos: int = None) -> List[Dict]:
        """
        搜索YouTube视频
        
        Args:
            search_query: 搜索关键词
            max_videos: 最大视频数量
            
        Returns:
            视频信息列表
        """
        if max_videos is None:
            max_videos = SCRAPER_CONFIG["max_videos"]
        
        self.logger.info(f"开始搜索: {search_query}, 最大数量: {max_videos}")
        
        try:
            # 构建搜索URL
            search_url = YOUTUBE_CONFIG["search_url"].format(
                search_query.replace(' ', '+')
            )
            
            # 访问搜索页面
            self._navigate_to_search_page(search_url)
            
            # 滚动加载更多视频
            self._scroll_to_load_videos()
            
            # 提取视频链接
            video_links = extract_video_links(self.driver, max_videos)
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
            self.logger.error(f"搜索过程中出错: {str(e)}")
            return []
    
    def _navigate_to_search_page(self, search_url: str):
        """导航到搜索页面"""
        self.logger.info(f"正在访问: {search_url}")
        self.driver.get(search_url)
        time.sleep(SCRAPER_CONFIG["page_load_delay"])
    
    def _scroll_to_load_videos(self):
        """滚动页面以加载更多视频"""
        self.logger.info("正在加载视频...")
        scroll_count = SCRAPER_CONFIG["scroll_count"]
        scroll_delay = SCRAPER_CONFIG["scroll_delay"]
        
        for i in range(scroll_count):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_delay)
    
    def _process_single_video(self, video_url: str, index: int) -> Optional[Dict]:
        """
        处理单个视频
        
        Args:
            video_url: 视频URL
            index: 视频索引
            
        Returns:
            视频信息字典
        """
        self.logger.info(f"正在处理第 {index} 个视频: {video_url}")
        
        for retry in range(ERROR_CONFIG["max_retries"]):
            try:
                return self._extract_video_details(video_url)
            except Exception as e:
                self.logger.warning(f"处理视频失败 (重试 {retry + 1}/{ERROR_CONFIG['max_retries']}): {str(e)}")
                if retry < ERROR_CONFIG["max_retries"] - 1:
                    time.sleep(ERROR_CONFIG["retry_delay"])
                    continue
                else:
                    self.logger.error(f"处理视频最终失败: {video_url}")
                    if ERROR_CONFIG["continue_on_error"]:
                        return None
                    else:
                        raise
        
        return None
    
    def _extract_video_details(self, video_url: str) -> Dict:
        """
        提取视频详细信息
        
        Args:
            video_url: 视频URL
            
        Returns:
            视频信息字典
        """
        # 访问视频页面
        self.driver.get(video_url)
        time.sleep(SCRAPER_CONFIG["page_load_delay"])
        
        # 等待页面加载 - 使用更宽松的策略
        self._wait_for_page_load()
        
        # 提取视频信息
        title = extract_title(self.driver)
        channel = extract_channel_name(self.driver)
        view_count, upload_date = extract_view_count_and_date(self.driver)
        description = extract_video_description(self.driver)
        
        # 构建视频信息
        video_info = {
            "title": title,
            "channel": channel,
            "view_count": view_count,
            "date": upload_date,
            "description": description,
            "url": video_url
        }
        
        self.logger.info(f"成功获取视频信息: {title[:50]}...")
        return video_info
    
    def _wait_for_page_load(self):
        """等待页面加载完成 - 使用更宽松的策略"""
        try:
            # 首先等待页面基本加载
            time.sleep(3)
            
            # 尝试等待标题元素，但不强制要求
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(("css selector", "h1"))
                )
            except TimeoutException:
                self.logger.warning("页面标题加载超时，继续处理...")
            
            # 再等待一段时间确保页面稳定
            time.sleep(2)
            
        except Exception as e:
            self.logger.warning(f"页面加载等待时出错: {str(e)}")
    
    def validate_search_query(self, search_query: str) -> Tuple[bool, str]:
        """
        验证搜索关键词
        
        Args:
            search_query: 搜索关键词
            
        Returns:
            (是否有效, 错误信息)
        """
        if not search_query or not search_query.strip():
            return False, "搜索关键词不能为空"
        
        if len(search_query.strip()) < 1:
            return False, "搜索关键词太短"
        
        if len(search_query.strip()) > 100:
            return False, "搜索关键词太长"
        
        return True, ""
    
    def validate_max_videos(self, max_videos: int) -> Tuple[bool, str]:
        """
        验证最大视频数量
        
        Args:
            max_videos: 最大视频数量
            
        Returns:
            (是否有效, 错误信息)
        """
        if max_videos <= 0:
            return False, "视频数量必须大于0"
        
        if max_videos > 100:
            return False, "视频数量不能超过100"
        
        return True, "" 