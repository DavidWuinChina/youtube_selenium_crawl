# -*- coding: utf-8 -*-
"""
YouTube爬虫配置文件
"""

import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.parent.parent

# 输出目录
OUTPUT_DIR = os.path.join(BASE_DIR, "data")

# 浏览器配置
BROWSER_CONFIG = {
    "headless": True,  # 启用无头模式提高性能
    "window_size": "1920,1080",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "implicit_wait": 10,  # 减少隐式等待时间
    "page_load_timeout": 30,  # 减少页面加载超时时间
    "chrome_options": [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--disable-extensions",
        "--disable-plugins",
        "--disable-web-security",
        "--disable-features=VizDisplayCompositor",
        "--disable-blink-features=AutomationControlled",  # 避免被检测为自动化工具
        "--exclude-switches=enable-automation",  # 排除自动化开关
        "--use-fake-ui-for-media-stream",  # 使用假UI
        "--use-fake-device-for-media-stream",  # 使用假设备
        "--disable-background-timer-throttling",  # 禁用后台定时器限制
        "--disable-backgrounding-occluded-windows",  # 禁用后台窗口
        "--disable-renderer-backgrounding",  # 禁用渲染器后台
        "--disable-features=TranslateUI",  # 禁用翻译UI
        "--disable-ipc-flooding-protection",  # 禁用IPC洪水保护
        # 性能优化选项
        "--disable-images",  # 禁用图片加载以提高速度
        "--disable-notifications",  # 禁用通知
        "--disable-popup-blocking",  # 禁用弹窗拦截
        "--disable-default-apps",  # 禁用默认应用
        "--disable-sync",  # 禁用同步
        "--disable-background-networking",  # 禁用后台网络
        "--aggressive-cache-discard",  # 积极缓存丢弃
        "--memory-pressure-off",  # 关闭内存压力
        "--max_old_space_size=4096",  # 增加内存限制
        "--disable-logging",  # 禁用日志
        "--disable-gpu-rasterization",  # 禁用GPU光栅化
    ]
}

# 爬虫配置
SCRAPER_CONFIG = {
    "max_videos": 10,  # 默认最大视频数量
    "scroll_count": 3,  # 增加滚动次数以获取更多视频
    "scroll_delay": 2,  # 减少滚动间隔（秒）
    "page_load_delay": 3,  # 大幅减少页面加载延迟（秒）
    "retry_count": 2,  # 保持重试次数
    "retry_delay": 2,  # 减少重试延迟（秒）
}

# YouTube URL配置
YOUTUBE_CONFIG = {
    "search_url": "https://www.youtube.com/results?search_query={}",
    "video_url_pattern": "watch?v=",
}

# 输出配置
OUTPUT_CONFIG = {
    "csv_encoding": "utf-8-sig",
    "json_encoding": "utf-8",
    "max_description_length": 2000,
    "output_formats": ["csv", "json"],
}

# 日志配置
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": os.path.join(BASE_DIR, "logs", "youtube_crawler.log"),
}

# 正则表达式配置
REGEX_CONFIG = {
    "view_count_patterns": [
        r'([\d,]+)\s*(?:views?|观看|次观看)',
        r'([\d,]+)\s*(?:views?)',
        r'([\d,]+)\s*(?:观看)',
        r'([\d,]+)\s*(?:次观看)'
    ],
    "date_patterns": [
        r'(\d{4}年\d{1,2}月\d{1,2}日)',  # 中文日期格式
        r'(\d{1,2}月\d{1,2}日)',  # 中文日期格式（无年份）
        r'(\w+\s+\d{1,2},\s+\d{4})',  # 英文日期格式
        r'(\d+\s+(?:hours?|days?|weeks?|months?)\s+ago)',  # 英文相对时间
        r'(\d+\s*(?:小时前|天前|周前|月前))',  # 中文相对时间
        r'(\d{1,2}/\d{1,2}/\d{4})',  # 数字日期格式
    ],
    "title_patterns": [
        r'"title":"([^"]+)"',
        r'"videoTitle":"([^"]+)"',
        r'<title>([^<]+)</title>'
    ],
    "description_patterns": [
        r'"description":"([^"]+)"',
        r'"shortDescription":"([^"]+)"'
    ]
}

# 过滤配置
FILTER_CONFIG = {
    "youtube_default_keywords": [
        "在 YouTube 上畅享你喜爱的视频和音乐",
        "Enjoy the videos and music you love",
        "YouTube 上观看你喜爱的视频和音乐"
    ],
    "min_description_length": 10,
    "min_title_length": 1,
}

# 错误处理配置
ERROR_CONFIG = {
    "max_retries": 2,  # 保持重试次数
    "retry_delay": 1,  # 减少重试延迟
    "continue_on_error": True,
    "log_errors": True,
} 