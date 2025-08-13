from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from .css_selectors import *
from .text_parsers import parse_view_count_and_date, parse_title_from_page_source, parse_description_from_page_source, clean_description


def extract_title(driver):
    """提取视频标题"""
    for selector in TITLE_SELECTORS:
        try:
            title_element = driver.find_element(By.CSS_SELECTOR, selector)
            title = title_element.text.strip()
            if title and len(title) > 0:
                return title
        except NoSuchElementException:
            continue
    
    # 如果上述方法都失败，尝试从页面源码获取
    try:
        page_source = driver.page_source
        title = parse_title_from_page_source(page_source)
        if title:
            return title
    except Exception:
        pass
    
    return "未知标题"


def extract_channel_name(driver):
    """提取频道名称"""
    for selector in CHANNEL_SELECTORS:
        try:
            channel_element = driver.find_element(By.CSS_SELECTOR, selector)
            channel = channel_element.text.strip()
            if channel and len(channel) > 0:
                return channel
        except NoSuchElementException:
            continue
    
    return "未知频道"


def extract_full_description_text(driver):
    """提取完整的描述文本，用于获取第一行信息"""
    try:
        # 尝试点击"显示更多"按钮
        for selector in SHOW_MORE_SELECTORS:
            try:
                show_more_button = driver.find_element(By.CSS_SELECTOR, selector)
                if show_more_button.is_displayed():
                    driver.execute_script("arguments[0].click();", show_more_button)
                    import time
                    time.sleep(0.8)  # 减少等待时间到0.8秒
                    break
            except NoSuchElementException:
                continue
        
        # 获取完整描述文本
        for selector in DESCRIPTION_SELECTORS:
            try:
                description_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in description_elements:
                    text = element.text.strip()
                    if text and len(text) > 10:
                        print(f"获取到完整描述文本，长度: {len(text)}")
                        return text
            except Exception:
                continue
        
        return None
        
    except Exception as e:
        print(f"获取完整描述文本时出错: {str(e)}")
        return None


def extract_view_count_and_date(driver):
    """提取观看次数和上传日期 - 直接从description第一行获取"""
    try:
        # 首先尝试从完整描述中获取第一行信息
        full_description = extract_full_description_text(driver)
        if full_description:
            lines = full_description.split('\n')
            if lines and len(lines[0].strip()) > 0:
                first_line = lines[0].strip()
                print(f"从description第一行提取信息: {first_line}")
                
                # 优先使用YouTube专用解析函数
                from .text_parsers import parse_youtube_first_line
                view_count, upload_date = parse_youtube_first_line(first_line)
                if view_count != "未知" or upload_date != "未知":
                    print(f"YouTube专用解析成功: views={view_count}, date={upload_date}")
                    return view_count, upload_date
                
                # 如果YouTube专用解析失败，回退到通用方法
                print("YouTube专用解析失败，尝试通用方法...")
                view_count, upload_date = parse_view_count_and_date(first_line)
                if view_count != "未知" or upload_date != "未知":
                    return view_count, upload_date
        
        # 如果从描述获取失败，尝试其他方法
        for selector in VIEW_COUNT_SELECTORS:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    text = element.text.strip()
                    if text and ("views" in text.lower() or "观看" in text or "次观看" in text):
                        view_count, upload_date = parse_view_count_and_date(text)
                        if view_count != "未知" or upload_date != "未知":
                            return view_count, upload_date
            except Exception:
                continue
        
        return "未知", "未知"
        
    except Exception as e:
        print(f"获取观看次数和日期时出错: {str(e)}")
        return "未知", "未知"


def extract_description_first_line(driver):
    """提取描述的第一行信息（包含观看次数和日期）"""
    try:
        # 尝试点击"显示更多"按钮
        for selector in SHOW_MORE_SELECTORS:
            try:
                show_more_button = driver.find_element(By.CSS_SELECTOR, selector)
                if show_more_button.is_displayed():
                    driver.execute_script("arguments[0].click();", show_more_button)
                    import time
                    time.sleep(0.8)  # 减少等待时间到0.8秒
                    break
            except NoSuchElementException:
                continue
        
        # 获取描述的第一行 - 改进逻辑
        for selector in DESCRIPTION_SELECTORS:
            try:
                description_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in description_elements:
                    text = element.text.strip()
                    if text and len(text) > 0:
                        # 获取第一行
                        lines = text.split('\n')
                        if lines:
                            first_line = lines[0].strip()
                            # 改进判断条件：检查是否包含观看次数或日期信息
                            if first_line and (
                                any(keyword in first_line.lower() for keyword in ["views", "观看", "次观看", "ago", "前", "年", "月", "日"]) or
                                any(char.isdigit() for char in first_line)  # 包含数字
                            ):
                                print(f"找到描述第一行: {first_line}")
                                return first_line
            except Exception:
                continue
        
        # 如果上述方法失败，尝试更宽泛的搜索
        print("尝试备用方法获取描述第一行...")
        for selector in ["#description", "#description-text", ".ytd-video-description-renderer"]:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    text = element.text.strip()
                    if text and len(text) > 0:
                        lines = text.split('\n')
                        if lines:
                            first_line = lines[0].strip()
                            if first_line and len(first_line) > 5:
                                print(f"备用方法找到第一行: {first_line}")
                                return first_line
            except Exception:
                continue
        
        return None
        
    except Exception as e:
        print(f"获取描述第一行时出错: {str(e)}")
        return None


def extract_video_description(driver):
    """提取视频描述"""
    try:
        # 尝试点击"显示更多"按钮
        for selector in SHOW_MORE_SELECTORS:
            try:
                show_more_button = driver.find_element(By.CSS_SELECTOR, selector)
                if show_more_button.is_displayed():
                    driver.execute_script("arguments[0].click();", show_more_button)
                    import time
                    time.sleep(0.8)  # 减少等待时间到0.8秒
                    break
            except NoSuchElementException:
                continue
        
        # 获取完整描述
        full_description = ""
        for selector in DESCRIPTION_SELECTORS:
            try:
                description_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in description_elements:
                    text = element.text.strip()
                    if text and len(text) > 10:
                        full_description = text
                        break
                if full_description:
                    break
            except Exception:
                continue
        
        # 如果获取到完整描述，移除第一行（观看次数和日期）
        if full_description:
            lines = full_description.split('\n')
            # 改进判断条件：检查第一行是否包含观看次数或日期信息
            if lines and (
                any(keyword in lines[0].lower() for keyword in ["views", "观看", "次观看", "ago", "前", "年", "月", "日"]) or
                any(char.isdigit() for char in lines[0])  # 包含数字
            ):
                # 移除第一行，保留剩余部分作为description
                remaining_lines = lines[1:]
                if remaining_lines:
                    description = '\n'.join(remaining_lines).strip()
                    if description and len(description) > 5:  # 确保有实际内容
                        print(f"提取到描述内容: {description[:100]}...")
                        return clean_description(description)
        
        # 如果上述方法失败，尝试从页面源码获取
        try:
            page_source = driver.page_source
            description = parse_description_from_page_source(page_source)
            if description:
                return clean_description(description)
        except Exception:
            pass
        
        return "无描述"
        
    except Exception as e:
        print(f"获取描述时出错: {str(e)}")
        return "获取失败"


def extract_video_links(driver, max_videos):
    """提取视频链接"""
    video_links = []
    
    for selector in VIDEO_ELEMENTS_SELECTORS:
        try:
            video_elements = driver.find_elements(By.CSS_SELECTOR, selector)
            
            for element in video_elements[:max_videos]:
                try:
                    # 尝试多种链接选择器
                    for link_selector in VIDEO_LINK_SELECTORS:
                        try:
                            link_elements = element.find_elements(By.CSS_SELECTOR, link_selector)
                            for link_element in link_elements:
                                href = link_element.get_attribute("href")
                                if href and "watch?v=" in href:
                                    # 避免重复链接
                                    if href not in video_links:
                                        video_links.append(href)
                                        break
                            if len(video_links) >= max_videos:
                                break
                        except Exception:
                            continue
                    
                    if len(video_links) >= max_videos:
                        break
                        
                except Exception:
                    continue
                    
            if len(video_links) >= max_videos:
                break
                
        except Exception:
            continue
    
    return video_links 