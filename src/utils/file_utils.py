import pandas as pd
import json
import os


def save_results(videos, search_query, output_dir="data"):
    """保存结果到文件"""
    if not videos:
        print("没有找到任何视频")
        return
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存为CSV
    df = pd.DataFrame(videos)
    csv_filename = os.path.join(output_dir, f"{search_query}_videos.csv")
    df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
    print(f"已保存 {len(videos)} 个视频信息到 {csv_filename}")
    
    # 保存为JSON
    json_filename = os.path.join(output_dir, f"{search_query}_videos.json")
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)
    print(f"已保存 {len(videos)} 个视频信息到 {json_filename}")
    
    # 显示结果
    print(f"\n成功爬取 {len(videos)} 个视频:")
    for i, video in enumerate(videos):
        print(f"\n{i+1}. {video['title']}")
        print(f"   频道: {video['channel']}")
        print(f"   观看次数: {video['view_count']}")
        print(f"   上传日期: {video['date']}")
        print(f"   描述: {video['description'][:100]}...")


def display_video_info(video):
    """显示单个视频信息"""
    print(f"标题: {video['title']}")
    print(f"频道: {video['channel']}")
    print(f"观看次数: {video['view_count']}")
    print(f"上传日期: {video['date']}")
    print(f"描述: {video['description'][:200]}...")
    print(f"链接: {video['url']}")
    print("-" * 50)


def validate_input(search_query, max_videos):
    """验证用户输入"""
    if not search_query or not search_query.strip():
        return False, "搜索关键词不能为空！"
    
    if max_videos <= 0:
        return False, "视频数量必须大于0！"
    
    if max_videos > 100:
        return False, "视频数量不能超过100！"
    
    return True, "输入有效" 