#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试description获取的脚本
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException


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


def debug_description_getting(driver, video_url):
    """调试description获取过程"""
    try:
        driver.get(video_url)
        time.sleep(3)
        
        print(f"\n正在调试视频: {video_url}")
        print("=" * 60)
        
        # 尝试点击"显示更多"按钮
        try:
            show_more_selectors = [
                "tp-yt-paper-button#expand",
                "button#expand",
                "ytd-button-renderer#expand",
                "ytd-button-renderer[aria-label*='显示更多']",
                "ytd-button-renderer[aria-label*='Show more']"
            ]
            
            for selector in show_more_selectors:
                try:
                    show_more_button = driver.find_element(By.CSS_SELECTOR, selector)
                    if show_more_button.is_displayed():
                        print(f"找到'显示更多'按钮: {selector}")
                        driver.execute_script("arguments[0].click();", show_more_button)
                        time.sleep(2)
                        break
                except NoSuchElementException:
                    continue
        except Exception as e:
            print(f"点击'显示更多'按钮时出错: {str(e)}")
        
        # 尝试多种CSS选择器获取描述
        description_selectors = [
            "ytd-expandable-video-description-body-renderer yt-formatted-string",
            "ytd-video-secondary-info-renderer yt-formatted-string",
            "#description yt-formatted-string",
            "ytd-video-description-renderer yt-formatted-string",
            "#description-text yt-formatted-string",
            "ytd-expandable-video-description-body-renderer #description-text",
            "ytd-video-secondary-info-renderer #description-text",
            "ytd-video-description-renderer #description-text"
        ]
        
        print("\n调试所有描述元素:")
        for selector in description_selectors:
            try:
                description_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"\n选择器: {selector}")
                print(f"找到 {len(description_elements)} 个元素")
                
                for i, element in enumerate(description_elements):
                    text = element.text.strip()
                    print(f"  元素 {i+1}:")
                    print(f"    长度: {len(text)} 字符")
                    print(f"    前100字符: {text[:100]}...")
                    print(f"    第一行: {text.split('\\n')[0] if '\\n' in text else text}")
                    
                    # 检查是否包含观看次数信息
                    if any(keyword in text for keyword in ['views', '观看', '次观看']):
                        print(f"    ⚠️  包含观看次数信息")
                    
                    # 检查是否包含日期信息
                    if any(keyword in text for keyword in ['ago', '小时前', '天前', '周前', '月前']):
                        print(f"    ⚠️  包含日期信息")
                    
                    print()
                    
            except Exception as e:
                print(f"  选择器 {selector} 出错: {str(e)}")
        
        # 检查页面源码中的描述信息
        print("\n检查页面源码中的描述信息:")
        try:
            page_source = driver.page_source
            import re
            
            # 查找包含观看次数和日期的信息
            view_date_patterns = [
                r'([\d,]+)\s*views?\s*([^\\n]+)',
                r'([\d,]+)\s*观看\s*([^\\n]+)',
                r'([^\\n]*views?[^\\n]*)',
                r'([^\\n]*观看[^\\n]*)'
            ]
            
            for pattern in view_date_patterns:
                matches = re.findall(pattern, page_source, re.IGNORECASE)
                if matches:
                    print(f"  找到匹配: {matches[:3]}")  # 只显示前3个匹配
        
        except Exception as e:
            print(f"  检查页面源码时出错: {str(e)}")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"调试过程中出错: {str(e)}")


def main():
    """主函数"""
    print("YouTube Description 调试工具")
    print("=" * 60)
    
    # 测试视频URL
    test_urls = [
        "https://www.youtube.com/watch?v=r7F9mql1L44",
        "https://www.youtube.com/watch?v=BIyDtWNcxgQ",
        "https://www.youtube.com/watch?v=MQvrwmptkfo"
    ]
    
    driver = setup_driver()
    
    try:
        for i, url in enumerate(test_urls, 1):
            print(f"\n测试视频 {i}/{len(test_urls)}")
            debug_description_getting(driver, url)
            time.sleep(2)
            
    except Exception as e:
        print(f"程序运行出错: {str(e)}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main() 