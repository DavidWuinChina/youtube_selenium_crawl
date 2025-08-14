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

# 频道“关于”页 - 简介选择器
CHANNEL_ABOUT_BIO_SELECTORS = [
    "yt-formatted-string#description",
    "yt-formatted-string[slot='description']",
    "#description-container yt-formatted-string",
    "div#description-container",
    "div#description"
]

# 频道订阅者数量选择器
CHANNEL_SUBSCRIBER_COUNT_SELECTORS = [
    "yt-formatted-string#subscriber-count",
    "yt-formatted-string#owner-sub-count",
    "tp-yt-paper-tooltip yt-formatted-string#subscriber-count",
    "#subscriber-count",
    "yt-formatted-string[aria-label*='subscriber']",
]

# 频道视频总数选择器（不同布局可能显示在标签或头部信息中）
CHANNEL_VIDEOS_COUNT_SELECTORS = [
    "yt-formatted-string#videos-count",
    "div#tabsContent yt-tab-shape-wiz[tab-title*='Videos']",
    "div#tabsContent tp-yt-paper-tab[aria-label*='Videos']",
]

# 频道页（包含首页/关于）“更多/展开”按钮选择器
CHANNEL_ABOUT_SHOW_MORE_SELECTORS = [
    "ytd-text-inline-expander#description #expand",
    "#description #expand",
    "tp-yt-paper-button#expand",
    "ytd-button-renderer#expand",
    "button#expand",
]

# 频道“更多信息/More info”按钮与弹窗容器
CHANNEL_MORE_INFO_BUTTON_SELECTORS = [
    "ytd-button-renderer a",
    "ytd-button-renderer button",
    "yt-button-shape button",
    "yt-button-shape a",
    "a",
    "button",
]

DIALOG_CONTAINER_SELECTORS = [
    "tp-yt-paper-dialog[opened]",
    "tp-yt-paper-dialog",
    "ytd-popup-container",
    "#contentWrapper",
]
