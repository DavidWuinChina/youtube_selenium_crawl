# -*- coding: utf-8 -*-
"""
加密货币频道批量爬虫 - 爬取多个加密货币相关YouTube频道的最新视频
"""

import sys
import os
import time
from datetime import datetime

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.service.url_batch_service import URLBatchService


class CryptoChannelsScraper:
    """加密货币频道批量爬虫类"""
    
    # 预定义的加密货币频道URL列表
    CRYPTO_CHANNELS = [
        "https://youtube.com/@COINMARKETHUB?si=WjLsW0RahAyaE6Wo",
        "https://youtube.com/@hamzatechofficial55?si=S5T5NXXfG8T5_ZUZ",
        "https://youtube.com/@cryptograde?si=d_GHk4WzwcHuy51k",
        "https://youtube.com/@asma_crypto",
        "https://youtube.com/@CRYPTOMASTER_786",
        "https://youtube.com/@crypto_aditi_official",
        "https://youtube.com/@bitzearning6535?si=fLEjp6CJyQN4000M",
        "https://youtube.com/@bitbloomcrypto",
        "https://youtube.com/@crypto_zombie_yt?si=NVTHWAQt5HU-sQWa",
        "https://youtube.com/@bitgirlcrypto916?si=wKqaBspqap0N577-"
    ]
    
    def __init__(self, headless: bool = False):
        """
        初始化批量爬虫
        
        Args:
            headless: 是否无头模式
        """
        self.headless = headless
        self.url_batch_service = URLBatchService(headless)
        
    def scrape_all_channels(self, max_videos_per_channel: int = 20):
        """
        爬取所有加密货币频道的视频
        
        Args:
            max_videos_per_channel: 每个频道最大视频数量
            
        Returns:
            所有视频信息列表
        """
        with self.url_batch_service as service:
            return service.process_multiple_urls(
                self.CRYPTO_CHANNELS, 
                max_videos_per_channel
            )
    
    def save_results(self, videos):
        """
        保存爬取结果
        
        Args:
            videos: 视频数据列表
            
        Returns:
            保存的文件路径字典
        """
        with self.url_batch_service as service:
            return service.save_batch_results(videos, "crypto_channels")
    
    def run(self, max_videos_per_channel: int = 20):
        """
        运行完整的批量爬虫流程
        
        Args:
            max_videos_per_channel: 每个频道最大视频数量
            
        Returns:
            保存的文件路径字典
        """
        with self.url_batch_service as service:
            return service.run_batch_process(
                self.CRYPTO_CHANNELS,
                max_videos_per_channel,
                "crypto_channels"
            )


def main():
    """主函数"""
    # 记录开始时间
    start_time = time.time()
    start_datetime = datetime.now()
    
    print("加密货币频道批量爬虫")
    print("=" * 50)
    print(f"开始时间: {start_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 显示要爬取的频道列表
    print("将要爬取的频道:")
    for i, channel_url in enumerate(CryptoChannelsScraper.CRYPTO_CHANNELS, 1):
        # 提取频道名称显示
        channel_name = channel_url.split('@')[-1].split('?')[0].split('/')[0]
        print(f"  {i:2d}. @{channel_name}")
    
    print(f"\n总共 {len(CryptoChannelsScraper.CRYPTO_CHANNELS)} 个频道")
    
    # 获取用户配置
    try:
        max_videos = int(input("\n请输入每个频道要爬取的最大视频数量 (默认20): ") or "20")
    except ValueError:
        max_videos = 20
    
    headless_input = input("是否使用无头模式? (y/n, 默认n): ").lower()
    headless = headless_input in ['y', 'yes', '是']
    
    print(f"\n开始爬取:")
    print(f"每个频道最多: {max_videos} 个视频")
    print(f"无头模式: {'是' if headless else '否'}")
    print("=" * 50)
    
    # 运行爬虫
    try:
        scraper = CryptoChannelsScraper(headless=headless)
        saved_files = scraper.run(max_videos)
        
        # 显示保存的文件
        if saved_files:
            print(f"\n文件已保存:")
            for format_type, filepath in saved_files.items():
                print(f"  {format_type.upper()}: {filepath}")
        else:
            print("\n没有找到任何视频")
            
    except KeyboardInterrupt:
        print("\n\n用户中断了爬取过程")
    except Exception as e:
        print(f"\n爬取过程中出错: {str(e)}")
    
    # 计算运行时间
    end_time = time.time()
    end_datetime = datetime.now()
    duration = end_time - start_time
    
    print("\n" + "=" * 50)
    print(f"结束时间: {end_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"总运行时间: {duration:.2f} 秒 ({duration/60:.1f} 分钟)")
    print("=" * 50)


if __name__ == "__main__":
    main()
