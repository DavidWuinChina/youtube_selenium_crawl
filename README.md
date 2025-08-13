# YouTube视频爬虫系统

一个基于Selenium的YouTube视频信息爬虫系统，采用服务层架构设计，支持通用搜索和用户频道爬取。

## 🏗️ 项目架构

```
youtube_crawl/
├── user_channel_scraper.py    # 用户频道爬虫入口
├── fixed_scraper.py           # 通用搜索爬虫入口
├── crypto_channels_scraper.py # 加密货币频道批量爬虫
├── src/                       # 源代码目录
│   ├── __init__.py           # 包初始化文件
│   ├── main.py               # 通用搜索主程序入口
│   ├── user_main.py          # 用户频道主程序入口
│   ├── config/               # 配置层
│   │   ├── __init__.py
│   │   └── settings.py       # 所有配置参数
│   ├── service/              # 服务层
│   │   ├── __init__.py
│   │   ├── browser_service.py     # 浏览器服务
│   │   ├── youtube_service.py     # YouTube业务逻辑
│   │   ├── scraper_service.py     # 通用爬虫服务
│   │   ├── user_service.py        # 用户频道服务
│   │   ├── batch_service.py       # 批量处理服务
│   │   ├── data_service.py        # 数据服务
│   │   └── logging_service.py     # 日志服务
│   └── utils/                # 工具层
│       ├── __init__.py
│       ├── element_extractors.py  # 网页元素提取器
│       ├── text_parsers.py        # 文本解析器
│       ├── css_selectors.py       # CSS选择器
│       └── file_utils.py          # 文件操作工具
├── data/                     # 输出数据目录
├── archive/                  # 归档文件目录
├── logs/                     # 日志目录 (自动创建)
├── README.md
├── requirements.txt
└── install.py
```

## 🎯 主要特性

### 1. **现代化服务层架构**
- **配置层 (config)**: 集中管理所有配置参数
- **服务层 (service)**: 处理业务逻辑，职责分离
- **工具层 (utils)**: 可复用的工具函数
- **入口层**: 简洁的程序入口

### 2. **多重爬取模式**
- **通用搜索模式**: 搜索任意关键词的YouTube视频
- **用户频道模式**: 爬取特定用户频道的所有视频
- **批量频道模式**: 批量爬取多个频道的最新视频

### 3. **服务层设计**
- **BrowserService**: 浏览器管理
- **YouTubeService**: YouTube业务逻辑
- **ScraperService**: 通用爬虫服务
- **UserService**: 用户频道服务
- **BatchService**: 批量处理服务
- **DataService**: 数据保存和加载
- **LoggingService**: 日志管理

### 4. **智能工具层**
- **ElementExtractors**: 网页元素提取
- **TextParsers**: 文本解析处理
- **CSSSelectors**: CSS选择器定义
- **FileUtils**: 文件操作工具

### 5. **配置驱动**
- 所有参数都在 `settings.py` 中配置
- 支持不同环境的配置
- 易于维护和修改

### 6. **错误处理和日志**
- 完整的日志系统
- 错误重试机制
- 详细的错误信息

## 📋 功能特性

### 通用搜索功能
- ✅ 搜索任意YouTube视频
- ✅ 提取视频标题、频道、观看次数、上传日期
- ✅ 获取视频描述（排除第一行的观看信息）
- ✅ 支持CSV和JSON格式输出

### 用户频道功能
- ✅ 爬取特定用户频道的所有视频
- ✅ 按最新时间顺序获取视频
- ✅ 自动滚动加载更多视频
- ✅ 批量处理视频信息

### 批量频道功能
- ✅ 批量爬取多个YouTube频道
- ✅ 预设加密货币相关频道列表
- ✅ 每个频道获取最新20条视频
- ✅ 自动添加频道标识和时间戳
- ✅ 统计报告和错误处理

### 系统功能
- ✅ 完整的日志记录
- ✅ 错误重试机制
- ✅ 配置化管理
- ✅ 模块化设计
- ✅ 上下文管理器支持

## 🚀 快速开始

### 安装依赖

```bash
# 安装依赖包
pip install -r requirements.txt

# 或者运行安装脚本
python install.py
```

### 基本使用

#### 1. 通用搜索模式

```bash
# 运行通用搜索爬虫
python fixed_scraper.py
```

#### 2. 用户频道模式

```bash
# 运行用户频道爬虫
python user_channel_scraper.py
```

#### 3. 批量频道模式

```bash
# 运行加密货币频道批量爬虫
python crypto_channels_scraper.py
```

### 程序化使用

#### 通用搜索

```python
# 方式1: 使用上下文管理器
from src.service import YouTubeScraperService

with YouTubeScraperService(headless=False) as scraper:
    saved_files = scraper.run("Python教程", 10)

# 方式2: 手动管理
scraper = YouTubeScraperService(headless=False)
scraper.start()
videos = scraper.search_videos("Python教程", 10)
saved_files = scraper.save_results(videos, "Python教程")
scraper.stop()
```

#### 用户频道爬取

```python
# 方式1: 使用上下文管理器
from src.service import YouTubeUserService

with YouTubeUserService(headless=False) as scraper:
    saved_files = scraper.run("investanswersclips", 10)

# 方式2: 手动管理
scraper = YouTubeUserService(headless=False)
scraper.start()
videos = scraper.search_user_videos("investanswersclips", 10)
saved_files = scraper.save_results(videos, "investanswersclips")
scraper.stop()
```

#### 批量频道爬取

```python
# 方式1: 使用预设的加密货币频道列表
from src.service import URLBatchService

# 预定义的加密货币频道URL
crypto_channels = [
    "https://youtube.com/@moon_star512?si=s9sMMU9GNzFK56Qo",
    "https://youtube.com/@COINMARKETHUB?si=WjLsW0RahAyaE6Wo",
    "https://youtube.com/@cryptograde?si=d_GHk4WzwcHuy51k",
    "https://youtube.com/@asma_crypto",
    "https://youtube.com/@bitbloomcrypto",
    "https://www.youtube.com/@drcrypto2"
]

# 使用URL批处理服务
from src.service import URLBatchService

with URLBatchService(headless=False) as batch_service:
    saved_files = batch_service.run_batch_process(
        channel_urls=crypto_channels,
        max_videos_per_channel=20,
        filename_prefix="crypto_channels"
    )

# 方式2: 自定义频道URL列表
custom_channel_urls = [
    "https://youtube.com/@your_channel1", 
    "https://youtube.com/@your_channel2"
]
with URLBatchService(headless=False) as batch_service:
    videos = batch_service.process_multiple_urls(custom_channel_urls, 15)
```

## 📁 输出文件

程序会在 `data/` 目录下生成以下文件：

### 通用搜索
- `{搜索关键词}_videos.csv` - CSV格式的视频数据
- `{搜索关键词}_videos.json` - JSON格式的视频数据

### 用户频道
- `user_{用户名}_videos.csv` - CSV格式的用户视频数据
- `user_{用户名}_videos.json` - JSON格式的用户视频数据

### 批量频道
- `crypto_channels_{时间戳}_videos.csv` - CSV格式的批量数据
- `crypto_channels_{时间戳}_videos.json` - JSON格式的批量数据

### 数据格式

```json
{
  "title": "视频标题",
  "channel": "频道名称", 
  "view_count": "观看次数",
  "date": "上传日期",
  "description": "视频描述",
  "url": "视频链接",
  "source_channel": "源频道名称",
  "scrape_timestamp": "爬取时间戳"
}
```

## ⚙️ 配置说明

所有配置都在 `src/config/settings.py` 中：

### 浏览器配置
```python
BROWSER_CONFIG = {
    "headless": False,  # 是否无头模式
    "window_size": "1920,1080",
    "implicit_wait": 10,
    "page_load_timeout": 15,
    # ... 更多配置
}
```

### 爬虫配置
```python
SCRAPER_CONFIG = {
    "max_videos": 10,  # 默认最大视频数量
    "scroll_count": 3,  # 滚动次数
    "scroll_delay": 2,  # 滚动间隔（秒）
    # ... 更多配置
}
```

### 输出配置
```python
OUTPUT_CONFIG = {
    "csv_encoding": "utf-8-sig",
    "json_encoding": "utf-8",
    "max_description_length": 2000,
    "output_formats": ["csv", "json"],
}
```

## 🔧 项目结构详解

### 配置层 (config/)
- **settings.py**: 集中管理所有配置参数
- 支持浏览器、爬虫、输出、日志、正则表达式等配置

### 服务层 (service/)
- **browser_service.py**: 浏览器驱动管理
- **youtube_service.py**: YouTube业务逻辑处理
- **scraper_service.py**: 通用爬虫服务
- **user_service.py**: 用户频道服务
- **data_service.py**: 数据保存和加载
- **logging_service.py**: 日志配置和管理

### 工具层 (utils/)
- **element_extractors.py**: 网页元素提取工具
- **text_parsers.py**: 文本解析工具
- **css_selectors.py**: CSS选择器定义
- **file_utils.py**: 文件操作工具

### 主程序
- **main.py**: 通用搜索程序入口
- **user_main.py**: 用户频道程序入口

## 📊 日志系统

程序会自动在 `logs/` 目录下生成日志文件：

- 控制台输出
- 文件日志（自动轮转）
- 错误重试记录
- 性能统计

## 🛠️ 开发指南

### 添加新的配置项

在 `src/config/settings.py` 中添加：

```python
NEW_CONFIG = {
    "key": "value",
    # ... 更多配置
}
```

### 添加新的服务

在 `src/service/` 目录下创建新的服务类：

```python
class NewService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def do_something(self):
        # 实现功能
        pass
```

### 添加新的工具函数

在 `src/utils/` 目录下添加：

```python
def new_utility_function():
    # 实现工具函数
    pass
```

## 🔍 故障排除

### 常见问题

1. **ChromeDriver问题**
   - 程序使用 `webdriver-manager` 自动管理
   - 确保网络连接正常

2. **页面加载超时**
   - 调整 `page_load_timeout` 配置
   - 检查网络连接

3. **元素定位失败**
   - 检查 `css_selectors.py` 中的选择器
   - 可能需要更新选择器

4. **用户频道爬取失败**
   - 确保用户名正确
   - 检查频道是否存在
   - 验证网络连接

### 调试模式

设置日志级别为DEBUG：

```python
# 在 settings.py 中修改
LOGGING_CONFIG = {
    "level": "DEBUG",  # 改为DEBUG
    # ...
}
```

## 📈 性能优化

### 配置优化

```python
# 禁用图片加载以提高速度
BROWSER_CONFIG["chrome_options"].append("--disable-images")

# 调整滚动参数
SCRAPER_CONFIG["scroll_count"] = 2  # 减少滚动次数
SCRAPER_CONFIG["scroll_delay"] = 1  # 减少延迟
```

### 无头模式

```python
# 使用无头模式提高性能
scraper = YouTubeScraperService(headless=True)
user_scraper = YouTubeUserService(headless=True)
```

## 📞 联系方式

如有问题或建议，请提交 Issue 或 Pull Request。

---

**注意**: 请遵守YouTube的服务条款和robots.txt文件。本工具仅用于学习和研究目的。 
=======
**注意**: 请遵守YouTube的服务条款和robots.txt文件。本工具仅用于学习和研究目的。 
>>>>>>> 0fb5a81f9426a6658e4b731305a72dbbd5b7c829
