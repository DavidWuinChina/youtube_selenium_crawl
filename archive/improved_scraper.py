import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
import json


def setup_driver():
    """设置Chrome浏览器驱动"""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)
    return driver


def get_view_count_and_date(driver):
    """获取观看次数和上传日期"""
    try:
        import re
        from datetime import datetime, timedelta
        
        # 尝试获取包含观看次数和日期的元素
        info_selectors = [
            "ytd-video-primary-info-renderer yt-formatted-string",
            "ytd-video-view-count-renderer",
            "#count",
            "span.view-count",
            "ytd-video-view-count-renderer yt-formatted-string"
        ]
        
        view_count = "未知"
        upload_date = "未知"
        
        for selector in info_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    text = element.text.strip()
                    if text and ("views" in text.lower() or "观看" in text):
                        # 解析观看次数和日期
                        lines = text.split('\n')
                        for line in lines:
                            line = line.strip()
                            if "views" in line.lower() or "观看" in line:
                                # 提取观看次数
                                view_match = re.search(r'([\d,]+)\s*(?:views?|观看)', line, re.IGNORECASE)
                                if view_match:
                                    view_count = view_match.group(1)
                                
                                # 提取日期
                                date_match = re.search(r'(\w+\s+\d+,\s+\d{4}|\d+\s+(?:hours?|days?|weeks?|months?)\s+ago)', line, re.IGNORECASE)
                                if date_match:
                                    date_str = date_match.group(1)
                                    # 处理相对时间
                                    if "ago" in date_str.lower():
                                        upload_date = convert_relative_date(date_str)
                                    else:
                                        upload_date = date_str
                                break
                        break
                if view_count != "未知":
                    break
            except NoSuchElementException:
                continue
        
        return view_count, upload_date
        
    except Exception as e:
        print(f"获取观看次数和日期时出错: {str(e)}")
        return "未知", "未知"


def convert_relative_date(relative_date):
    """转换相对日期为绝对日期"""
    try:
        import re
        from datetime import datetime, timedelta
        
        now = datetime.now()
        relative_date = relative_date.lower()
        
        # 匹配小时
        hour_match = re.search(r'(\d+)\s*hours?\s+ago', relative_date)
        if hour_match:
            hours = int(hour_match.group(1))
            result_date = now - timedelta(hours=hours)
            return result_date.strftime("%Y-%m-%d")
        
        # 匹配天数
        day_match = re.search(r'(\d+)\s*days?\s+ago', relative_date)
        if day_match:
            days = int(day_match.group(1))
            result_date = now - timedelta(days=days)
            return result_date.strftime("%Y-%m-%d")
        
        # 匹配周数
        week_match = re.search(r'(\d+)\s*weeks?\s+ago', relative_date)
        if week_match:
            weeks = int(week_match.group(1))
            result_date = now - timedelta(weeks=weeks)
            return result_date.strftime("%Y-%m-%d")
        
        # 匹配月数
        month_match = re.search(r'(\d+)\s*months?\s+ago', relative_date)
        if month_match:
            months = int(month_match.group(1))
            result_date = now - timedelta(days=months*30)
            return result_date.strftime("%Y-%m-%d")
        
        return relative_date
    except Exception:
        return relative_date


def get_video_description_improved(driver):
    """改进的视频描述获取方法"""
    try:
        # 方法1: 尝试点击"显示更多"按钮
        try:
            show_more_selectors = [
                "tp-yt-paper-button#expand",
                "button#expand",
                "ytd-button-renderer#expand"
            ]
            
            for selector in show_more_selectors:
                try:
                    show_more_button = driver.find_element(By.CSS_SELECTOR, selector)
                    if show_more_button.is_displayed():
                        driver.execute_script("arguments[0].click();", show_more_button)
                        time.sleep(2)
                        break
                except NoSuchElementException:
                    continue
        except Exception:
            pass
        
        # 方法2: 尝试多种CSS选择器获取描述
        description_selectors = [
            "ytd-expandable-video-description-body-renderer yt-formatted-string",
            "ytd-video-secondary-info-renderer yt-formatted-string",
            "#description yt-formatted-string",
            "ytd-video-description-renderer yt-formatted-string"
        ]
        
        description = ""
        for selector in description_selectors:
            try:
                description_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in description_elements:
                    text = element.text.strip()
                    if text and len(text) > 10:
                        description = text
                        break
                if description:
                    break
            except Exception:
                continue
        
        # 方法3: 从页面源码获取描述
        if not description:
            try:
                page_source = driver.page_source
                import re
                desc_patterns = [
                    r'"description":"([^"]+)"',
                    r'"shortDescription":"([^"]+)"'
                ]
                
                for pattern in desc_patterns:
                    matches = re.findall(pattern, page_source)
                    if matches:
                        description = matches[0].replace('\\n', '\n').replace('\\"', '"')
                        break
            except Exception:
                pass
        
        if description:
            description = description.replace('\\n', '\n').replace('\\"', '"')
            if len(description) > 2000:
                description = description[:2000] + "..."
            return description
        else:
            return "无描述"
        
    except Exception as e:
        print(f"获取描述时出错: {str(e)}")
        return "获取失败"


def search_youtube_videos(search_query, max_videos=10):
    """搜索YouTube视频并获取描述"""
    driver = setup_driver()
    videos = []
    
    try:
        search_url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
        print(f"正在访问: {search_url}")
        driver.get(search_url)
        time.sleep(5)
        
        # 滚动页面加载更多视频
        print("正在加载视频...")
        for i in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        
        # 获取视频链接
        video_elements = driver.find_elements(By.CSS_SELECTOR, "ytd-video-renderer, ytd-rich-item-renderer")
        print(f"找到 {len(video_elements)} 个视频元素")
        
        video_links = []
        for element in video_elements[:max_videos]:
            try:
                link_element = element.find_element(By.CSS_SELECTOR, "a#video-title")
                href = link_element.get_attribute("href")
                if href and "watch?v=" in href:
                    video_links.append(href)
            except NoSuchElementException:
                continue
        
        print(f"获取到 {len(video_links)} 个视频链接")
        
        # 逐个访问视频页面获取详细信息
        for i, link in enumerate(video_links):
            if i >= max_videos:
                break
                
            try:
                print(f"正在处理第 {i+1} 个视频: {link}")
                video_info = get_video_details(driver, link)
                if video_info:
                    videos.append(video_info)
                    print(f"成功获取视频信息: {video_info['title'][:50]}...")
                    
            except Exception as e:
                print(f"处理视频时出错: {str(e)}")
                continue
                
    except Exception as e:
        print(f"搜索过程中出错: {str(e)}")
    finally:
        driver.quit()
        
    return videos


def get_video_details(driver, video_url):
    """获取单个视频的详细信息"""
    try:
        driver.get(video_url)
        time.sleep(3)
        
        # 等待页面加载
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1.ytd-video-primary-info-renderer"))
        )
        
        # 获取视频标题
        title_element = driver.find_element(By.CSS_SELECTOR, "h1.ytd-video-primary-info-renderer")
        title = title_element.text.strip()
        
        # 获取频道名称
        try:
            channel_element = driver.find_element(By.CSS_SELECTOR, "ytd-channel-name yt-formatted-string.ytd-channel-name")
            channel = channel_element.text.strip()
        except NoSuchElementException:
            channel = "未知频道"
        
        # 获取视频描述
        description = get_video_description_improved(driver)
        
        # 获取观看次数和上传日期
        view_count, upload_date = get_view_count_and_date(driver)
        
        return {
            "title": title,
            "channel": channel,
            "view_count": view_count,
            "date": upload_date,
            "description": description,
            "url": video_url
        }
        
    except Exception as e:
        print(f"获取视频详情时出错: {str(e)}")
        return None


def save_results(videos, search_query):
    """保存结果到文件"""
    if videos:
        # 保存为CSV
        df = pd.DataFrame(videos)
        csv_filename = f"{search_query}_videos.csv"
        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        print(f"已保存 {len(videos)} 个视频信息到 {csv_filename}")
        
        # 保存为JSON
        json_filename = f"{search_query}_videos.json"
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
            print(f"   描述长度: {len(video['description'])} 字符")
            print(f"   描述预览: {video['description'][:100]}...")
    else:
        print("没有找到任何视频")


def main():
    """主函数"""
    print("YouTube视频描述爬虫 - 改进版")
    print("=" * 50)
    
    search_query = input("请输入要搜索的关键词: ")
    max_videos = int(input("请输入要爬取的最大视频数量 (默认5): ") or "5")
    
    print(f"\n开始搜索: {search_query}")
    print(f"最大爬取数量: {max_videos}")
    print("=" * 50)
    
    videos = search_youtube_videos(search_query, max_videos)
    save_results(videos, search_query)


if __name__ == "__main__":
    main() 