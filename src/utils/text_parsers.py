import re


def parse_view_count_and_date(text):
    """从文本中解析观看次数和日期"""
    try:
        view_count = "未知"
        upload_date = "未知"
        
        # 提取观看次数 - 支持中文和英文格式
        view_patterns = [
            r'([\d,]+)\s*(?:views?|观看|次观看)',
            r'([\d,]+)\s*(?:views?)',
            r'([\d,]+)\s*(?:观看)',
            r'([\d,]+)\s*(?:次观看)'
        ]
        
        for pattern in view_patterns:
            view_match = re.search(pattern, text, re.IGNORECASE)
            if view_match:
                view_count = view_match.group(1)
                break
        
        # 提取日期 - 支持多种格式
        date_patterns = [
            r'(\d{4}年\d{1,2}月\d{1,2}日)',  # 中文日期格式
            r'(\d{1,2}月\d{1,2}日)',  # 中文日期格式（无年份）
            r'(\w+\s+\d{1,2},\s+\d{4})',  # 英文日期格式
            r'(\d+\s+(?:hours?|days?|weeks?|months?)\s+ago)',  # 英文相对时间
            r'(\d+\s*(?:小时前|天前|周前|月前))',  # 中文相对时间
            r'(\d{1,2}/\d{1,2}/\d{4})',  # 数字日期格式
        ]
        
        for pattern in date_patterns:
            date_match = re.search(pattern, text, re.IGNORECASE)
            if date_match:
                date_str = date_match.group(1)
                # 处理相对时间
                if "ago" in date_str.lower() or "前" in date_str:
                    upload_date = convert_relative_date(date_str)
                else:
                    upload_date = date_str
                break
        
        return view_count, upload_date
        
    except Exception as e:
        print(f"解析观看次数和日期时出错: {str(e)}")
        return "未知", "未知"


def convert_relative_date(relative_date):
    """转换相对时间为绝对时间"""
    try:
        # 英文相对时间
        if "ago" in relative_date.lower():
            number_match = re.search(r'(\d+)', relative_date)
            if number_match:
                number = int(number_match.group(1))
                if "hour" in relative_date.lower():
                    return f"{number}小时前"
                elif "day" in relative_date.lower():
                    return f"{number}天前"
                elif "week" in relative_date.lower():
                    return f"{number}周前"
                elif "month" in relative_date.lower():
                    return f"{number}月前"
        
        # 中文相对时间
        elif "前" in relative_date:
            number_match = re.search(r'(\d+)', relative_date)
            if number_match:
                number = int(number_match.group(1))
                if "小时前" in relative_date:
                    return f"{number}小时前"
                elif "天前" in relative_date:
                    return f"{number}天前"
                elif "周前" in relative_date:
                    return f"{number}周前"
                elif "月前" in relative_date:
                    return f"{number}月前"
        
        return relative_date
        
    except Exception:
        return relative_date


def parse_title_from_page_source(page_source):
    """从页面源码中解析标题"""
    try:
        title_patterns = [
            r'"title":"([^"]+)"',
            r'"videoTitle":"([^"]+)"',
            r'<title>([^<]+)</title>'
        ]
        
        for pattern in title_patterns:
            matches = re.findall(pattern, page_source)
            if matches:
                title = matches[0].replace('\\n', '\n').replace('\\"', '"')
                if title and len(title) > 0:
                    return title
    except Exception:
        pass
    
    return None


def parse_description_from_page_source(page_source):
    """从页面源码中解析描述"""
    try:
        desc_patterns = [
            r'"description":"([^"]+)"',
            r'"shortDescription":"([^"]+)"'
        ]
        
        for pattern in desc_patterns:
            matches = re.findall(pattern, page_source)
            if matches:
                description = matches[0].replace('\\n', '\n').replace('\\"', '"')
                # 移除第一行的观看次数和日期信息
                lines = description.split('\n')
                if lines and ("views" in lines[0].lower() or "观看" in lines[0] or "次观看" in lines[0]):
                    lines = lines[1:]
                description = '\n'.join(lines).strip()
                
                if description and len(description) > 10:
                    if len(description) > 2000:
                        description = description[:2000] + "..."
                    return description
    except Exception:
        pass
    
    return None


def filter_youtube_default_description(description):
    """过滤掉YouTube默认描述"""
    if not description:
        return False
    
    default_keywords = [
        "在 YouTube 上畅享你喜爱的视频和音乐",
        "Enjoy the videos and music you love",
        "YouTube 上观看你喜爱的视频和音乐"
    ]
    
    return not any(keyword in description for keyword in default_keywords)


def clean_description(description):
    """清理描述内容"""
    if not description:
        return "无描述"
    
    # 过滤掉YouTube默认描述
    if not filter_youtube_default_description(description):
        return "无描述"
    
    # 限制长度
    if len(description) > 2000:
        description = description[:2000] + "..."
    
    return description if description else "无描述"


def is_video_older_than_24_hours(upload_date):
    """
    判断视频是否超过24小时
    
    Args:
        upload_date: 上传日期字符串
        
    Returns:
        bool: True表示超过24小时，False表示24小时内
    """
    if not upload_date or upload_date == "未知":
        return True  # 无法判断时间的视频默认认为是老视频
    
    try:
        # 处理相对时间格式
        if "小时前" in upload_date or "hour" in upload_date.lower():
            # 提取小时数
            number_match = re.search(r'(\d+)', upload_date)
            if number_match:
                hours = int(number_match.group(1))
                return hours >= 24  # 24小时及以上才算老视频
            return True
        
        # 处理天、周、月、年的情况（都超过24小时）
        if any(keyword in upload_date for keyword in ["天前", "周前", "月前", "年前", "day", "week", "month", "year"]):
            return True
        
        # 处理绝对日期格式（都认为是老视频）
        if any(keyword in upload_date for keyword in ["年", "月", "日", "/", "-"]):
            return True
        
        # 默认情况下认为是老视频
        return True
        
    except Exception as e:
        print(f"判断视频时间时出错: {str(e)}")
        return True  # 出错时默认认为是老视频 