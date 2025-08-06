# YouTube爬虫包
__version__ = "2.0.0"
__author__ = "YouTube Crawler"

from .service.scraper_service import YouTubeScraperService
from .main import main

# 导入服务层
from .service import (
    BrowserService,
    YouTubeService,
    DataService,
    LoggingService,
    YouTubeScraperService,
    YouTubeUserService
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
    text_parsers,
    element_extractors,
    css_selectors,
    file_utils
)

__all__ = [
    # 主要类
    'YouTubeScraperService',
    'YouTubeUserService',
    'main',
    
    # 服务层
    'BrowserService',
    'YouTubeService',
    'DataService',
    'LoggingService',
    'YouTubeScraperService',
    'YouTubeUserService',
    
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
    'text_parsers',
    'element_extractors',
    'css_selectors',
    'file_utils'
] 