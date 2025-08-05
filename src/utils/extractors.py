from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from .selectors import *
from .parsers import parse_view_count_and_date, parse_title_from_page_source, parse_description_from_page_source, clean_description


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


def extract_view_count_and_date(driver):
    """提取观看次数和上传日期"""
    try:
        # 首先尝试从描述的第一行获取观看次数和日期
        description_info = extract_description_first_line(driver)
        if description_info:
            view_count, upload_date = parse_view_count_and_date(description_info)
            if view_count != "未知" and upload_date != "未知":
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
                    time.sleep(2)
                    break
            except NoSuchElementException:
                continue
        
        # 获取描述的第一行
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
                            if first_line and ("views" in first_line.lower() or "观看" in first_line or "次观看" in first_line):
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
                    time.sleep(2)
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
            if lines and ("views" in lines[0].lower() or "观看" in lines[0] or "次观看" in lines[0]):
                # 移除第一行，保留剩余部分作为description
                remaining_lines = lines[1:]
                if remaining_lines:
                    description = '\n'.join(remaining_lines).strip()
                    if description and len(description) > 5:  # 确保有实际内容
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
                    for link_selector in VIDEO_LINK_SELECTORS:
                        link_element = element.find_element(By.CSS_SELECTOR, link_selector)
                        href = link_element.get_attribute("href")
                        if href and "watch?v=" in href:
                            video_links.append(href)
                            break
                except NoSuchElementException:
                    continue
        except Exception:
            continue
    
    return video_links 