#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新字段格式的脚本
"""

import time
from fixed_scraper import search_youtube_videos, save_results


def test_new_format():
    """测试新的字段格式"""
    print("=" * 60)
    print("测试新字段格式 - 观看次数和日期解析")
    print("=" * 60)
    
    # 测试参数
    test_query = "NBA"
    test_max_videos = 2
    
    print(f"测试搜索词: {test_query}")
    print(f"测试视频数量: {test_max_videos}")
    print("=" * 60)
    
    try:
        # 开始测试爬取
        print("开始测试爬取...")
        start_time = time.time()
        
        videos = search_youtube_videos(test_query, test_max_videos)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n测试完成！")
        print(f"耗时: {duration:.2f} 秒")
        print(f"成功爬取: {len(videos)} 个视频")
        
        if videos:
            # 保存测试结果
            save_results(videos, f"new_format_test_{test_query}")
            
            # 显示详细结果
            print("\n详细结果:")
            for i, video in enumerate(videos, 1):
                print(f"\n{i}. {video['title']}")
                print(f"   频道: {video['channel']}")
                print(f"   观看次数: {video['view_count']}")
                print(f"   上传日期: {video['date']}")
                print(f"   链接: {video['url']}")
                print(f"   描述长度: {len(video['description'])} 字符")
                print(f"   描述预览: {video['description'][:200]}...")
                
                # 检查字段是否完整
                required_fields = ['title', 'channel', 'view_count', 'date', 'description', 'url']
                missing_fields = []
                for field in required_fields:
                    if field not in video or not video[field]:
                        missing_fields.append(field)
                
                if missing_fields:
                    print(f"   ❌ 缺失字段: {missing_fields}")
                else:
                    print(f"   ✅ 所有字段完整")
        else:
            print("没有找到任何视频，请检查网络连接或搜索词")
            
    except Exception as e:
        print(f"测试过程中出错: {str(e)}")
        print("请检查:")
        print("1. 网络连接是否正常")
        print("2. Chrome浏览器是否已安装")
        print("3. 依赖包是否已正确安装")


if __name__ == "__main__":
    test_new_format() 