# -*- coding: utf-8 -*-
"""
YouTube用户帖子爬虫主入口 - 专门用于搜索特定用户的帖子
"""

from .service.user_service import YouTubeUserService


def main():
    """用户搜索主函数"""
    print("YouTube用户帖子爬虫")
    print("=" * 50)
    
    # 获取用户输入
    username = input("请输入YouTube用户名 (例如: @username): ").strip()
    if not username:
        print("用户名不能为空！")
        return
    
    # 移除@符号（如果用户输入了的话）
    if username.startswith('@'):
        username = username[1:]
    
    try:
        max_videos = int(input("请输入要爬取的最大视频数量 (默认10): ") or "10")
    except ValueError:
        max_videos = 10
    
    print(f"\n开始搜索用户: {username}")
    print(f"最大爬取数量: {max_videos}")
    print("=" * 50)
    
    # 使用上下文管理器运行爬虫
    try:
        with YouTubeUserService(headless=False) as scraper:
            # 运行完整的爬虫流程
            saved_files = scraper.run(username, max_videos)
            
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