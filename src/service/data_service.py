# -*- coding: utf-8 -*-
"""
数据服务层 - 处理数据保存和加载
"""

import os
import json
import logging
import pandas as pd
from typing import List, Dict, Optional
from pathlib import Path

from ..config.settings import OUTPUT_CONFIG, OUTPUT_DIR


class DataService:
    """数据服务类 - 处理数据保存和加载"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        """确保输出目录存在"""
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        self.logger.info(f"输出目录: {OUTPUT_DIR}")
    
    def save_videos(self, videos: List[Dict], search_query: str) -> Dict[str, str]:
        """
        保存视频数据
        
        Args:
            videos: 视频数据列表
            search_query: 搜索关键词
            
        Returns:
            保存的文件路径字典
        """
        if not videos:
            self.logger.warning("没有视频数据需要保存")
            return {}
        
        saved_files = {}
        
        # 清理搜索关键词，用作文件名
        safe_query = self._sanitize_filename(search_query)
        
        # 保存为CSV
        if "csv" in OUTPUT_CONFIG["output_formats"]:
            csv_path = self._save_to_csv(videos, safe_query)
            if csv_path:
                saved_files["csv"] = csv_path
        
        # 保存为JSON
        if "json" in OUTPUT_CONFIG["output_formats"]:
            json_path = self._save_to_json(videos, safe_query)
            if json_path:
                saved_files["json"] = json_path
        
        self.logger.info(f"成功保存 {len(videos)} 个视频到 {len(saved_files)} 个文件")
        return saved_files
    
    def _save_to_csv(self, videos: List[Dict], search_query: str) -> Optional[str]:
        """保存为CSV格式"""
        try:
            df = pd.DataFrame(videos)
            filename = f"{search_query}_videos.csv"
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            df.to_csv(
                filepath, 
                index=False, 
                encoding=OUTPUT_CONFIG["csv_encoding"]
            )
            
            self.logger.info(f"已保存CSV文件: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"保存CSV文件失败: {str(e)}")
            return None
    
    def _save_to_json(self, videos: List[Dict], search_query: str) -> Optional[str]:
        """保存为JSON格式"""
        try:
            filename = f"{search_query}_videos.json"
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            with open(filepath, 'w', encoding=OUTPUT_CONFIG["json_encoding"]) as f:
                json.dump(videos, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"已保存JSON文件: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"保存JSON文件失败: {str(e)}")
            return None
    
    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名，移除不安全的字符"""
        # 移除或替换不安全的字符
        unsafe_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in unsafe_chars:
            filename = filename.replace(char, '_')
        
        # 限制长度
        if len(filename) > 50:
            filename = filename[:50]
        
        return filename.strip()
    
    def load_videos_from_csv(self, filepath: str) -> List[Dict]:
        """从CSV文件加载视频数据"""
        try:
            df = pd.read_csv(filepath, encoding=OUTPUT_CONFIG["csv_encoding"])
            return df.to_dict('records')
        except Exception as e:
            self.logger.error(f"加载CSV文件失败: {str(e)}")
            return []
    
    def load_videos_from_json(self, filepath: str) -> List[Dict]:
        """从JSON文件加载视频数据"""
        try:
            with open(filepath, 'r', encoding=OUTPUT_CONFIG["json_encoding"]) as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"加载JSON文件失败: {str(e)}")
            return []
    
    def get_output_files(self, search_query: str) -> Dict[str, str]:
        """获取输出文件路径"""
        safe_query = self._sanitize_filename(search_query)
        files = {}
        
        csv_file = os.path.join(OUTPUT_DIR, f"{safe_query}_videos.csv")
        if os.path.exists(csv_file):
            files["csv"] = csv_file
        
        json_file = os.path.join(OUTPUT_DIR, f"{safe_query}_videos.json")
        if os.path.exists(json_file):
            files["json"] = json_file
        
        return files
    
    def display_video_summary(self, videos: List[Dict]):
        """显示视频摘要"""
        if not videos:
            self.logger.info("没有视频数据")
            return
        
        self.logger.info(f"成功爬取 {len(videos)} 个视频:")
        
        for i, video in enumerate(videos, 1):
            title = video.get('title', '未知标题')
            channel = video.get('channel', '未知频道')
            view_count = video.get('view_count', '未知')
            date = video.get('date', '未知')
            
            self.logger.info(f"\n{i}. {title}")
            self.logger.info(f"   频道: {channel}")
            self.logger.info(f"   观看次数: {view_count}")
            self.logger.info(f"   上传日期: {date}")
            
            # 显示描述前100个字符
            description = video.get('description', '无描述')
            if description and len(description) > 100:
                description = description[:100] + "..."
            self.logger.info(f"   描述: {description}")
    
    def get_statistics(self, videos: List[Dict]) -> Dict:
        """获取视频统计信息"""
        if not videos:
            return {}
        
        stats = {
            "total_videos": len(videos),
            "channels": {},
            "view_count_stats": {},
            "date_stats": {}
        }
        
        # 统计频道
        for video in videos:
            channel = video.get('channel', '未知频道')
            stats["channels"][channel] = stats["channels"].get(channel, 0) + 1
        
        # 统计观看次数
        view_counts = []
        for video in videos:
            view_count = video.get('view_count', '未知')
            if view_count != '未知':
                try:
                    # 移除逗号并转换为数字
                    view_count_num = int(view_count.replace(',', ''))
                    view_counts.append(view_count_num)
                except:
                    pass
        
        if view_counts:
            stats["view_count_stats"] = {
                "min": min(view_counts),
                "max": max(view_counts),
                "avg": sum(view_counts) / len(view_counts)
            }
        
        return stats 