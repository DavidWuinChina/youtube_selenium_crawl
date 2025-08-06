# -*- coding: utf-8 -*-
"""
YouTube用户频道爬虫 - 直接访问用户频道页面
专门用于搜索特定用户的帖子
"""

import sys
import os
import time
import logging
from typing import List, Dict, Optional
from selenium.webdriver.common.by import By

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.service.browser_service import BrowserService
from src.service.data_service import DataService
from src.service.logging_service import LoggingService
from src.service.user_service import YouTubeUserService
from src.config.settings import SCRAPER_CONFIG


class YouTubeChannelScraper:
    """YouTube用户频道爬虫类 - 使用服务层架构"""
    
    def __init__(self, headless: bool = False):
        """
        初始化频道爬虫
        
        Args:
            headless: 是否无头模式
        """
        self.headless = headless
        self.user_service = YouTubeUserService(headless)
    
    def __enter__(self):
        """上下文管理器入口"""
        self.user_service.__enter__()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.user_service.__exit__(exc_type, exc_val, exc_tb)
    
    def search_user_videos(self, username: str, max_videos: int = 10):
        """
        搜索特定用户的YouTube视频
        
        Args:
            username: 用户名
            max_videos: 最大视频数量
            
        Returns:
            视频信息列表
        """
        return self.user_service.search_user_videos(username, max_videos)
    
    def save_results(self, videos, username: str):
        """
        保存搜索结果
        
        Args:
            videos: 视频数据列表
            username: 用户名
            
        Returns:
            保存的文件路径字典
        """
        return self.user_service.save_results(videos, username)
    
    def run(self, username: str, max_videos: int = 10):
        """
        运行完整的用户爬虫流程
        
        Args:
            username: 用户名
            max_videos: 最大视频数量
            
        Returns:
            保存的文件路径字典
        """
        return self.user_service.run(username, max_videos)


def main():
    """用户搜索主函数"""
    print("YouTube用户频道爬虫")
    print("=" * 50)
    
    # 获取用户输入
    username = input("请输入YouTube用户名 (例如: username，注意不要留空格): ").strip()
    if not username:
        print("用户名不能为空！")
        return
    
    # 移除@符号（如果用户输入了的话）
    if username.startswith('@'):
        username = username[1:]
    
    try:
        max_videos = int(input("请输入要爬取的最大视频数量 (默认10): ") or "10")
    except ValueError:
        max_videos = 10
    
    print(f"\n开始搜索用户: {username}")
    print(f"最大爬取数量: {max_videos}")
    print("=" * 50)
    
    # 使用上下文管理器运行爬虫
    try:
        with YouTubeChannelScraper(headless=False) as scraper:
            # 运行完整的爬虫流程
            saved_files = scraper.run(username, max_videos)
            
            # 显示保存的文件
            if saved_files:
                print(f"\n文件已保存:")
                for format_type, filepath in saved_files.items():
                    print(f"  {format_type.upper()}: {filepath}")
            else:
                print("\n没有找到任何视频")
                
    except Exception as e:
        print(f"爬取过程中出错: {str(e)}")


if __name__ == "__main__":
    main() 