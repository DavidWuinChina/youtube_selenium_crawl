# -*- coding: utf-8 -*-
"""
YouTube爬虫主入口 - 使用服务层架构
"""

from .scraper import YouTubeScraper


def main():
    """主函数"""
    print("YouTube视频描述爬虫")
    print("=" * 50)
    
    # 获取用户输入
    search_query = input("请输入搜索关键词: ").strip()
    if not search_query:
        print("搜索关键词不能为空！")
        return
    
    try:
        max_videos = int(input("请输入要爬取的最大视频数量 (默认10): ") or "10")
    except ValueError:
        max_videos = 10
    
    print(f"\n开始搜索: {search_query}")
    print(f"最大爬取数量: {max_videos}")
    print("=" * 50)
    
    # 使用上下文管理器运行爬虫
    try:
        with YouTubeScraper(headless=False) as scraper:
            # 运行完整的爬虫流程
            saved_files = scraper.run(search_query, max_videos)
            
            # 显示保存的文件
            if saved_files:
                print(f"\n文件已保存:")
                for format_type, filepath in saved_files.items():
                    print(f"  {format_type.upper()}: {filepath}")
            else:
                print("\n没有找到任何视频")
                
    except Exception as e:
        print(f"爬取过程中出错: {str(e)}")


if __name__ == "__main__":
    main() 