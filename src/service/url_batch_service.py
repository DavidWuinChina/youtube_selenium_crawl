# -*- coding: utf-8 -*-
"""
URL批量处理服务类 - 用于批量处理YouTube频道URL
"""

import time
import re
import logging
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urlparse

from .youtube_service import YouTubeService
from .browser_service import BrowserService
from .data_service import DataService
from .logging_service import LoggingService
from ..utils.element_extractors import extract_video_links, extract_channel_about_info, extract_channel_subscribers_from_page
from ..utils.text_parsers import is_video_older_than_24_hours
from ..config.settings import SCRAPER_CONFIG


class URLBatchService:
    """URL批量处理服务类"""
    
    def __init__(self, headless: bool = None):
        """
        初始化URL批量处理服务
        
        Args:
            headless: 是否无头模式
        """
        self.headless = headless
        self.browser_service = BrowserService()
        self.data_service = DataService()
        self.logging_service = LoggingService()
        self.logger = self.logging_service.get_logger(__name__)
        self.driver = None
        self.youtube_service = None
        
    def __enter__(self):
        """上下文管理器入口"""
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.stop()
    
    def start(self):
        """启动服务"""
        self.logging_service.log_startup()
        self.browser_service.create_driver(self.headless)
        self.driver = self.browser_service.get_driver()
        self.youtube_service = YouTubeService(self.driver)
        self.logger.info("URL批量处理服务启动成功")
    
    def stop(self):
        """停止服务"""
        if self.browser_service:
            self.browser_service.close_driver()
        self.logging_service.log_shutdown()
        self.logger.info("URL批量处理服务已停止")
    
    def extract_channel_name_from_url(self, url: str) -> str:
        """从URL中提取频道名称"""
        try:
            # 匹配 @username 格式
            match = re.search(r'@([^/?&#]+)', url)
            if match:
                return match.group(1)
            
            # 如果没有找到，返回URL的最后一部分
            parsed = urlparse(url)
            path_parts = parsed.path.strip('/').split('/')
            if path_parts:
                return path_parts[-1]
            
            return "unknown_channel"
        except Exception as e:
            self.logger.error(f"提取频道名称失败: {str(e)}")
            return "unknown_channel"
     
    def _smart_convert_to_videos_url(self, url: str) -> str:
        """
        智能转换URL到videos页面，保留原始参数
        
        Args:
            url: 原始频道URL
            
        Returns:
            转换后的videos页面URL
        """
        try:
            # 如果URL已经包含videos路径，直接返回
            if '/videos' in url:
                return url
            
            # 如果包含错误拼写，修正它
            if '/vidoes' in url:
                return url.replace('/vidoes', '/videos')
            
            # 对于频道主页URL，添加/videos
            # 处理有参数的情况：https://youtube.com/@channel?si=xxx
            if '?' in url:
                base_url, params = url.split('?', 1)
                # 确保base_url以@username结尾，然后添加/videos
                if '@' in base_url and not base_url.endswith('/videos'):
                    # 移除可能的尾部斜杠
                    base_url = base_url.rstrip('/')
                    return f"{base_url}/videos?{params}"
                else:
                    return url
            else:
                # 没有参数的情况
                base_url = url.rstrip('/')
                if '@' in base_url and not base_url.endswith('/videos'):
                    return f"{base_url}/videos"
                else:
                    return url
                    
        except Exception as e:
            self.logger.warning(f"URL转换失败，使用原始URL: {str(e)}")
            return url
    
    def _build_about_url(self, url: str) -> str:
        """根据频道URL构建关于(about)页面URL，尽量保留原始参数结构"""
        try:
            if '?' in url:
                base_url, params = url.split('?', 1)
                base_url = base_url.rstrip('/')
                # 确保是频道主页样式
                if '@' in base_url:
                    return f"{base_url}/about?{params}"
                return f"{base_url}/about?{params}"
            base_url = url.rstrip('/')
            return f"{base_url}/about"
        except Exception:
            return url

    def process_channel_url(self, channel_url: str, max_videos: int = 20) -> List[Dict]:
        """
        处理单个频道URL
        
        Args:
            channel_url: 频道URL
            max_videos: 最大视频数量
            
        Returns:
            视频信息列表
        """
        if not self.driver:
            raise RuntimeError("服务未启动，请先调用start()方法")
        
        channel_name = self.extract_channel_name_from_url(channel_url)
        self.logger.info(f"开始处理频道: {channel_name} - {channel_url}")
        
        try:
            # 先访问频道关于页，提取频道信息
            about_url = self._build_about_url(channel_url)
            self.logger.info(f"访问频道关于页: {about_url}")
            self.driver.get(about_url)
            time.sleep(SCRAPER_CONFIG["page_load_delay"])
            channel_about_info = extract_channel_about_info(self.driver)

            # 智能处理URL：保留参数但确保能找到视频
            videos_url = self._smart_convert_to_videos_url(channel_url)
            self.logger.info(f"访问频道页面: {videos_url}")
            if videos_url != channel_url:
                self.logger.info(f"原始URL: {channel_url}")
            self.driver.get(videos_url)
            time.sleep(SCRAPER_CONFIG["page_load_delay"])
            
            # 滚动加载更多视频
            self._scroll_to_load_videos()
            
            # 提取视频链接
            video_links = extract_video_links(self.driver, max_videos)
            self.logger.info(f"从频道 {channel_name} 获取到 {len(video_links)} 个视频链接")
            
            # 处理每个视频 - 24小时内的视频不计入max_videos限制
            videos = []
            valid_video_count = 0  # 只计算24小时前的视频
            
            for i, link in enumerate(video_links):
                # 如果已经获取到足够的24小时前的视频，停止处理
                if valid_video_count >= max_videos:
                    break
                
                video_info = self._process_single_video(link, i + 1, channel_name)
                if video_info:
                    # 添加源信息
                    video_info['source_channel'] = channel_name
                    video_info['source_url'] = channel_url
                    video_info['scrape_timestamp'] = datetime.now().isoformat()

                    # 合并频道关于信息
                    try:
                        from ..utils.text_parsers import normalize_subscriber_text
                        subscribers_value = channel_about_info.get('subscribers') or "未知"
                        if subscribers_value == "未知":
                            # 尝试在当前频道页(含Videos页)再次抓取订阅数
                            subscribers_value = extract_channel_subscribers_from_page(self.driver)
                        subscribers_value = normalize_subscriber_text(subscribers_value) or "未知"

                        video_info.update({
                            'bio': channel_about_info.get('bio', '未知'),
                            'subscribers': subscribers_value,
                            'location': channel_about_info.get('location', '未知'),
                        })
                        # 用户反馈不需要视频总数
                        if 'video_num' in video_info:
                            del video_info['video_num']
                    except Exception:
                        pass
                    
                    # 判断视频是否超过24小时
                    upload_date = video_info.get('date', '未知')
                    is_old_video = is_video_older_than_24_hours(upload_date)
                    video_info['is_older_than_24h'] = is_old_video
                    
                    if is_old_video:
                        # 24小时前的视频计入有效计数
                        valid_video_count += 1
                        self.logger.info(f"✓ 有效视频 #{valid_video_count}: {video_info.get('title', 'Unknown')[:50]}... (发布时间: {upload_date})")
                    else:
                        # 24小时内的视频不计入有效计数，但仍然保存
                        self.logger.info(f"⊗ 跳过24小时内视频: {video_info.get('title', 'Unknown')[:50]}... (发布时间: {upload_date})")
                    
                    videos.append(video_info)
            
            # 统计24小时内和24小时前的视频数量
            old_videos = [v for v in videos if v.get('is_older_than_24h', True)]
            new_videos = [v for v in videos if not v.get('is_older_than_24h', True)]
            
            self.logger.info(f"频道 {channel_name} 处理完成:")
            self.logger.info(f"  总视频数: {len(videos)} 个")
            self.logger.info(f"  24小时前视频: {len(old_videos)} 个 (计入指定数量)")
            self.logger.info(f"  24小时内视频: {len(new_videos)} 个 (不计入指定数量)")
            
            return videos
            
        except Exception as e:
            self.logger.error(f"处理频道 {channel_name} 时出错: {str(e)}")
            return []
    
    def _scroll_to_load_videos(self):
        """滚动页面以加载更多视频"""
        self.logger.info("正在加载频道视频...")
        
        scroll_count = SCRAPER_CONFIG["scroll_count"]
        scroll_delay = SCRAPER_CONFIG["scroll_delay"]
        
        for i in range(scroll_count):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_delay)
    
    def _process_single_video(self, video_url: str, index: int, channel_name: str) -> Optional[Dict]:
        """处理单个视频"""
        try:
            self.logger.info(f"处理频道 {channel_name} 第 {index} 个视频: {video_url}")
            
            # 使用YouTube服务处理视频
            video_info = self.youtube_service._process_single_video(video_url, index)
            
            if video_info:
                self.logger.info(f"成功获取视频信息: {video_info.get('title', 'Unknown')[:50]}...")
            
            return video_info
            
        except Exception as e:
            self.logger.error(f"处理视频时出错: {str(e)}")
            return None
    
    def process_multiple_urls(self, 
                             channel_urls: List[str], 
                             max_videos_per_channel: int = 20,
                             delay_between_channels: int = 2) -> List[Dict]:
        """
        批量处理多个频道URL
        
        Args:
            channel_urls: 频道URL列表
            max_videos_per_channel: 每个频道最大视频数量
            delay_between_channels: 频道间延迟时间（秒）
            
        Returns:
            所有视频信息列表
        """
        all_videos = []
        successful_channels = 0
        failed_channels = []
        
        self.logger.info(f"开始批量处理 {len(channel_urls)} 个频道URL")
        start_time = datetime.now()
        
        for i, channel_url in enumerate(channel_urls, 1):
            channel_name = self.extract_channel_name_from_url(channel_url)
            self.logger.info(f"正在处理第 {i}/{len(channel_urls)} 个频道: {channel_name}")
            
            try:
                # 处理单个频道
                videos = self.process_channel_url(channel_url, max_videos_per_channel)
                
                if videos:
                    # 为每个视频添加批处理元数据
                    for video in videos:
                        video['batch_process'] = True
                        video['batch_timestamp'] = datetime.now().isoformat()
                        video['batch_channel_index'] = i
                        video['batch_total_channels'] = len(channel_urls)
                    
                    all_videos.extend(videos)
                    successful_channels += 1
                    
                    # 分别统计24小时内外的视频
                    old_videos = [v for v in videos if v.get('is_older_than_24h', True)]
                    new_videos = [v for v in videos if not v.get('is_older_than_24h', True)]
                    self.logger.info(f"频道 {channel_name}: 获取 {len(videos)} 个视频 (24小时前: {len(old_videos)}个, 24小时内: {len(new_videos)}个)")
                else:
                    self.logger.warning(f"频道 {channel_name}: 未获取到任何视频")
                    failed_channels.append(channel_name)
                
                # 添加延迟
                if i < len(channel_urls) and delay_between_channels > 0:
                    self.logger.info(f"等待 {delay_between_channels} 秒后继续下一个频道...")
                    time.sleep(delay_between_channels)
                    
            except Exception as e:
                self.logger.error(f"处理频道 {channel_name} 时出错: {str(e)}")
                failed_channels.append(channel_name)
                continue
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        # 计算最终统计信息
        total_old_videos = sum(1 for v in all_videos if v.get('is_older_than_24h', True))
        total_new_videos = sum(1 for v in all_videos if not v.get('is_older_than_24h', True))
        
        # 输出统计信息
        self._log_batch_statistics(
            duration, successful_channels, len(channel_urls), 
            len(all_videos), total_old_videos, total_new_videos, failed_channels
        )
        
        return all_videos
    
    def _log_batch_statistics(self, duration, successful, total, video_count, old_videos, new_videos, failed):
        """记录批处理统计信息"""
        self.logger.info("=" * 60)
        self.logger.info("URL批量处理完成！")
        self.logger.info(f"总耗时: {duration}")
        self.logger.info(f"成功处理频道: {successful}/{total}")
        self.logger.info(f"总共获取视频: {video_count} 个")
        self.logger.info(f"  - 24小时前视频: {old_videos} 个 (计入指定数量)")
        self.logger.info(f"  - 24小时内视频: {new_videos} 个 (不计入指定数量)")
        
        if failed:
            self.logger.warning(f"失败的频道: {', '.join(failed)}")
    
    def save_batch_results(self, videos: List[Dict], filename_prefix: str = "url_batch") -> Dict:
        """
        保存批处理结果
        
        Args:
            videos: 视频数据列表
            filename_prefix: 文件名前缀
            
        Returns:
            保存的文件路径字典
        """
        if not videos:
            self.logger.warning("没有视频数据需要保存")
            return {}
        
        try:
            # 使用时间戳作为文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename_prefix}_{timestamp}"
            
            # 保存数据
            saved_files = self.data_service.save_videos(videos, filename)
            
            # 显示统计信息
            self._display_batch_summary(videos)
            
            return saved_files
            
        except Exception as e:
            self.logger.error(f"保存批处理结果时出错: {str(e)}")
            raise
    
    def _display_batch_summary(self, videos: List[Dict]):
        """显示批处理摘要"""
        old_videos = [v for v in videos if v.get('is_older_than_24h', True)]
        new_videos = [v for v in videos if not v.get('is_older_than_24h', True)]
        
        self.logger.info(f"保存了 {len(videos)} 个视频信息")
        self.logger.info(f"  - 24小时前视频: {len(old_videos)} 个")
        self.logger.info(f"  - 24小时内视频: {len(new_videos)} 个")
        
        # 按频道统计
        channel_stats = {}
        channel_old_stats = {}
        channel_new_stats = {}
        
        for video in videos:
            channel = video.get('source_channel', 'Unknown')
            if channel not in channel_stats:
                channel_stats[channel] = 0
                channel_old_stats[channel] = 0
                channel_new_stats[channel] = 0
            
            channel_stats[channel] += 1
            if video.get('is_older_than_24h', True):
                channel_old_stats[channel] += 1
            else:
                channel_new_stats[channel] += 1
        
        self.logger.info("按频道统计:")
        for channel in sorted(channel_stats.keys()):
            total = channel_stats[channel]
            old = channel_old_stats[channel]
            new = channel_new_stats[channel]
            self.logger.info(f"  {channel}: {total} 个视频 (24h前: {old}, 24h内: {new})")
    
    def run_batch_process(self, 
                         channel_urls: List[str], 
                         max_videos_per_channel: int = 20,
                         filename_prefix: str = "crypto_channels") -> Dict:
        """
        运行完整的URL批处理流程
        
        Args:
            channel_urls: 频道URL列表
            max_videos_per_channel: 每个频道最大视频数量
            filename_prefix: 文件名前缀
            
        Returns:
            保存的文件路径字典
        """
        try:
            # 批量处理频道URL
            videos = self.process_multiple_urls(channel_urls, max_videos_per_channel)
            
            # 保存结果
            if videos:
                saved_files = self.save_batch_results(videos, filename_prefix)
                return saved_files
            else:
                self.logger.warning("没有获取到任何视频")
                return {}
            
        except Exception as e:
            self.logger.error(f"运行URL批处理时出错: {str(e)}")
            raise
