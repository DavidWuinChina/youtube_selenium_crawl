import time
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re


class YouTubeScraper:
    def __init__(self, headless=False):
        """
        初始化YouTube爬虫
        
        Args:
            headless (bool): 是否使用无头模式运行浏览器
        """
        self.driver = None
        self.headless = headless
        self.setup_driver()
    
    def setup_driver(self):
        """设置Chrome浏览器驱动"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        # 添加其他选项以提高稳定性
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # 使用webdriver-manager自动管理ChromeDriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)
    
    def search_videos(self, search_query, max_videos=50):
        """
        搜索YouTube视频
        
        Args:
            search_query (str): 搜索关键词
            max_videos (int): 最大爬取视频数量
            
        Returns:
            list: 视频信息列表
        """
        videos = []
        
        try:
            # 访问YouTube搜索页面
            search_url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
            self.driver.get(search_url)
            
            # 等待页面加载
            time.sleep(3)
            
            # 滚动页面以加载更多视频
            self._scroll_to_load_videos(max_videos)
            
            # 获取视频链接
            video_links = self._get_video_links(max_videos)
            
            print(f"找到 {len(video_links)} 个视频链接")
            
            # 逐个访问视频页面获取详细信息
            for i, link in enumerate(video_links):
                if i >= max_videos:
                    break
                    
                try:
                    video_info = self._get_video_details(link)
                    if video_info:
                        videos.append(video_info)
                        print(f"已爬取 {i+1}/{len(video_links)} 个视频")
                        
                except Exception as e:
                    print(f"爬取视频 {link} 时出错: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"搜索过程中出错: {str(e)}")
            
        return videos
    
    def _scroll_to_load_videos(self, max_videos):
        """滚动页面以加载更多视频"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        videos_loaded = 0
        
        while videos_loaded < max_videos:
            # 滚动到底部
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # 计算当前加载的视频数量
            video_elements = self.driver.find_elements(By.CSS_SELECTOR, "ytd-video-renderer, ytd-rich-item-renderer")
            videos_loaded = len(video_elements)
            
            # 检查是否到达页面底部
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            
            print(f"已加载 {videos_loaded} 个视频")
    
    def _get_video_links(self, max_videos):
        """获取视频链接列表"""
        video_links = []
        
        try:
            # 查找视频元素
            video_elements = self.driver.find_elements(By.CSS_SELECTOR, "ytd-video-renderer, ytd-rich-item-renderer")
            
            for element in video_elements[:max_videos]:
                try:
                    # 查找视频链接
                    link_element = element.find_element(By.CSS_SELECTOR, "a#video-title")
                    href = link_element.get_attribute("href")
                    
                    if href and "watch?v=" in href:
                        video_links.append(href)
                        
                except NoSuchElementException:
                    continue
                    
        except Exception as e:
            print(f"获取视频链接时出错: {str(e)}")
            
        return video_links
    
    def _get_video_details(self, video_url):
        """获取单个视频的详细信息"""
        try:
            self.driver.get(video_url)
            time.sleep(2)
            
            # 等待页面加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1.ytd-video-primary-info-renderer"))
            )
            
            # 获取视频标题
            title_element = self.driver.find_element(By.CSS_SELECTOR, "h1.ytd-video-primary-info-renderer")
            title = title_element.text.strip()
            
            # 获取频道名称
            try:
                channel_element = self.driver.find_element(By.CSS_SELECTOR, "ytd-channel-name yt-formatted-string.ytd-channel-name")
                channel = channel_element.text.strip()
            except NoSuchElementException:
                channel = "未知频道"
            
            # 获取观看次数和上传日期
            view_count, upload_date = self._get_view_count_and_date()
            
            # 获取视频描述
            description = self._get_video_description()
            
            # 获取视频时长
            try:
                duration_element = self.driver.find_element(By.CSS_SELECTOR, "span.ytp-time-duration")
                duration = duration_element.text.strip()
            except NoSuchElementException:
                duration = "未知"
            
            return {
                "title": title,
                "channel": channel,
                "view_count": view_count,
                "date": upload_date,
                "duration": duration,
                "description": description,
                "url": video_url
            }
            
        except Exception as e:
            print(f"获取视频详情时出错: {str(e)}")
            return None
    
    def _get_view_count_and_date(self):
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
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
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
                                            upload_date = self._convert_relative_date(date_str)
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
    
    def _convert_relative_date(self, relative_date):
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
    
    def _get_video_description(self):
        """获取视频描述"""
        try:
            # 尝试点击"显示更多"按钮
            try:
                show_more_button = self.driver.find_element(By.CSS_SELECTOR, "tp-yt-paper-button#expand")
                show_more_button.click()
                time.sleep(1)
            except NoSuchElementException:
                pass
            
            # 获取描述文本
            description_element = self.driver.find_element(By.CSS_SELECTOR, "ytd-expandable-video-description-body-renderer yt-formatted-string")
            description = description_element.text.strip()
            
            return description
            
        except NoSuchElementException:
            return "无描述"
        except Exception as e:
            print(f"获取描述时出错: {str(e)}")
            return "获取失败"
    
    def save_to_csv(self, videos, filename="youtube_videos.csv"):
        """保存视频信息到CSV文件"""
        if videos:
            df = pd.DataFrame(videos)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"已保存 {len(videos)} 个视频信息到 {filename}")
        else:
            print("没有视频信息可保存")
    
    def save_to_json(self, videos, filename="youtube_videos.json"):
        """保存视频信息到JSON文件"""
        if videos:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(videos, f, ensure_ascii=False, indent=2)
            print(f"已保存 {len(videos)} 个视频信息到 {filename}")
        else:
            print("没有视频信息可保存")
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()


def main():
    """主函数"""
    # 创建爬虫实例
    scraper = YouTubeScraper(headless=False)  # 设置为True可以无头模式运行
    
    try:
        # 设置搜索关键词和最大视频数量
        search_query = input("请输入要搜索的关键词: ")
        max_videos = int(input("请输入要爬取的最大视频数量 (默认20): ") or "20")
        
        print(f"开始搜索: {search_query}")
        print(f"最大爬取数量: {max_videos}")
        
        # 开始爬取
        videos = scraper.search_videos(search_query, max_videos)
        
        if videos:
            print(f"\n成功爬取 {len(videos)} 个视频")
            
            # 保存结果
            scraper.save_to_csv(videos, f"{search_query}_videos.csv")
            scraper.save_to_json(videos, f"{search_query}_videos.json")
            
            # 显示前几个视频的信息
            print("\n前5个视频信息:")
            for i, video in enumerate(videos[:5]):
                print(f"\n{i+1}. {video['title']}")
                print(f"   频道: {video['channel']}")
                print(f"   观看次数: {video['view_count']}")
                print(f"   描述: {video['description'][:100]}...")
        else:
            print("没有找到任何视频")
            
    except KeyboardInterrupt:
        print("\n用户中断了程序")
    except Exception as e:
        print(f"程序运行出错: {str(e)}")
    finally:
        scraper.close()


if __name__ == "__main__":
    main() 