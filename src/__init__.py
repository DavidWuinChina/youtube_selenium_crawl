# YouTube爬虫包
__version__ = "2.0.0"
__author__ = "YouTube Crawler"

from .scraper import YouTubeScraper
from .main import main

# 导入服务层
from .service import (
    BrowserService,
    YouTubeService,
    DataService,
    LoggingService
)

# 导入配置层
from .config import (
    BROWSER_CONFIG,
    SCRAPER_CONFIG,
    YOUTUBE_CONFIG,
    OUTPUT_CONFIG,
    LOGGING_CONFIG,
    REGEX_CONFIG,
    FILTER_CONFIG,
    ERROR_CONFIG
)

# 导入工具层
from .utils import (
    parsers,
    extractors,
    selectors
)

__all__ = [
    # 主要类
    'YouTubeScraper',
    'main',
    
    # 服务层
    'BrowserService',
    'YouTubeService',
    'DataService',
    'LoggingService',
    
    # 配置层
    'BROWSER_CONFIG',
    'SCRAPER_CONFIG',
    'YOUTUBE_CONFIG',
    'OUTPUT_CONFIG',
    'LOGGING_CONFIG',
    'REGEX_CONFIG',
    'FILTER_CONFIG',
    'ERROR_CONFIG',
    
    # 工具层
    'parsers',
    'extractors',
    'selectors'
] 