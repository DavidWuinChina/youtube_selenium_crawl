# YouTube视频描述爬虫

一个基于Selenium的YouTube视频信息爬虫，采用经典的企业级分层架构设计。

## 🏗️ 项目架构

```
youtube_crawl/
├── fixed_scraper.py          # 主入口文件
├── src/                      # 源代码目录
│   ├── __init__.py          # 包初始化文件
│   ├── main.py              # 主程序入口
│   ├── scraper.py           # 简化的爬虫类 (149行)
│   ├── config/              # 配置层
│   │   ├── __init__.py
│   │   └── settings.py      # 所有配置参数
│   ├── service/             # 服务层
│   │   ├── __init__.py
│   │   ├── browser_service.py    # 浏览器服务
│   │   ├── youtube_service.py    # YouTube业务逻辑
│   │   ├── data_service.py       # 数据服务
│   │   └── logging_service.py    # 日志服务
│   └── utils/               # 工具层
│       ├── __init__.py
│       ├── parsers.py       # 解析工具
│       ├── extractors.py    # 元素提取工具
│       └── selectors.py     # CSS选择器
├── data/                    # 输出数据目录
├── archive/                 # 归档文件目录
├── logs/                    # 日志目录 (自动创建)
├── README.md
├── requirements.txt
└── install.py
```

## 🎯 主要特性

### 1. **经典分层架构**
- **配置层 (config)**: 集中管理所有配置参数
- **服务层 (service)**: 处理业务逻辑，职责分离
- **工具层 (utils)**: 可复用的工具函数
- **主入口 (main)**: 简洁的程序入口

### 2. **服务层设计**
- **BrowserService**: 浏览器管理
- **YouTubeService**: YouTube业务逻辑
- **DataService**: 数据保存和加载
- **LoggingService**: 日志管理

### 3. **配置驱动**
- 所有参数都在 `settings.py` 中配置
- 支持不同环境的配置
- 易于维护和修改

### 4. **错误处理和日志**
- 完整的日志系统
- 错误重试机制
- 详细的错误信息

### 5. **代码复用**
- 工具函数模块化
- 服务层可独立使用
- 配置层可扩展

## 📋 功能特性

- ✅ 搜索YouTube视频
- ✅ 提取视频标题、频道、观看次数、上传日期
- ✅ 获取视频描述（排除第一行的观看信息）
- ✅ 支持CSV和JSON格式输出
- ✅ 完整的日志记录
- ✅ 错误重试机制
- ✅ 配置化管理
- ✅ 模块化设计

## 🚀 快速开始

### 安装依赖

```bash
# 安装依赖包
pip install -r requirements.txt

# 或者运行安装脚本
python install.py
```

### 基本使用

```bash
# 运行爬虫
python fixed_scraper.py
```

### 程序化使用

```python
# 方式1: 使用上下文管理器
from src.scraper import YouTubeScraper

with YouTubeScraper(headless=False) as scraper:
    saved_files = scraper.run("Python教程", 10)

# 方式2: 手动管理
scraper = YouTubeScraper(headless=False)
scraper.start()
videos = scraper.search_videos("Python教程", 10)
saved_files = scraper.save_results(videos, "Python教程")
scraper.stop()
```

## 📁 输出文件

程序会在 `data/` 目录下生成以下文件：

- `{搜索关键词}_videos.csv` - CSV格式的视频数据
- `{搜索关键词}_videos.json` - JSON格式的视频数据

### 数据格式

```json
{
  "title": "视频标题",
  "channel": "频道名称", 
  "view_count": "观看次数",
  "date": "上传日期",
  "description": "视频描述",
  "url": "视频链接"
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
- **data_service.py**: 数据保存和加载
- **logging_service.py**: 日志配置和管理

### 工具层 (utils/)
- **parsers.py**: 数据解析工具
- **extractors.py**: 页面元素提取工具
- **selectors.py**: CSS选择器定义

### 主程序
- **scraper.py**: 简化的爬虫类，协调各服务
- **main.py**: 程序入口，处理用户交互

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
   - 检查 `selectors.py` 中的选择器
   - 可能需要更新选择器

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
scraper = YouTubeScraper(headless=True)
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证。

## 🔄 版本历史

- **v2.0.0**: 重构为服务层架构
- **v1.0.0**: 初始版本

## 📞 联系方式

如有问题或建议，请提交 Issue 或 Pull Request。

---

**注意**: 请遵守YouTube的服务条款和robots.txt文件。本工具仅用于学习和研究目的。 