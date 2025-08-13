# YouTube页面元素选择器

# 标题选择器
TITLE_SELECTORS = [
    "h1.ytd-video-primary-info-renderer",
    "h1.ytd-watch-metadata",
    "h1.ytd-video-primary-info-renderer yt-formatted-string",
    "ytd-video-primary-info-renderer h1",
    "h1.title",
    "ytd-watch-metadata h1"
]

# 频道名称选择器
CHANNEL_SELECTORS = [
    "ytd-channel-name yt-formatted-string.ytd-channel-name",
    "ytd-channel-name a",
    "ytd-channel-name yt-formatted-string",
    "ytd-video-owner-renderer yt-formatted-string"
]

# 观看次数和日期选择器
VIEW_COUNT_SELECTORS = [
    "ytd-video-view-count-renderer yt-formatted-string",
    "#count",
    "span.view-count",
    "ytd-video-view-count-renderer",
    "ytd-video-primary-info-renderer yt-formatted-string"
]

# 描述选择器
DESCRIPTION_SELECTORS = [
    "ytd-expandable-video-description-body-renderer yt-formatted-string",
    "ytd-video-secondary-info-renderer yt-formatted-string",
    "#description yt-formatted-string",
    "ytd-video-description-renderer yt-formatted-string",
    # 新版 YouTube Watch 页面描述容器
    "#description-inline-expander",
    "#description-inline-expander yt-formatted-string",
    "ytd-text-inline-expander#description-inline-expander yt-formatted-string"
]

# 显示更多按钮选择器
SHOW_MORE_SELECTORS = [
    "tp-yt-paper-button#expand",
    "button#expand",
    "ytd-button-renderer#expand",
    # 新版描述区域的展开按钮
    "#description-inline-expander #expand",
    "ytd-text-inline-expander#description-inline-expander #expand"
]

# 视频元素选择器
VIDEO_ELEMENTS_SELECTORS = [
    "ytd-video-renderer",
    "ytd-rich-item-renderer",
    "ytd-grid-video-renderer",
    "ytd-video-card-renderer",
    "ytd-rich-grid-media"
]

# 视频链接选择器
VIDEO_LINK_SELECTORS = [
    "a#video-title",
    "a#thumbnail",
    "a[href*='watch?v=']",
    "ytd-thumbnail a",
    "a.yt-simple-endpoint"
]

# 页面加载等待选择器
PAGE_LOAD_SELECTORS = [
    "h1.ytd-video-primary-info-renderer",
    "h1.ytd-watch-metadata"
] 