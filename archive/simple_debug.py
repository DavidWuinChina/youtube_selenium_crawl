#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的description调试脚本
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
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


def test_single_video():
    """测试单个视频的description获取"""
    driver = setup_driver()
    
    try:
        # 测试一个视频
        video_url = "https://www.youtube.com/watch?v=r7F9mql1L44"
        print(f"正在测试视频: {video_url}")
        
        driver.get(video_url)
        time.sleep(5)
        
        print("\n检查所有可能的描述元素:")
        
        # 检查所有可能的描述选择器
        selectors = [
            "ytd-expandable-video-description-body-renderer yt-formatted-string",
            "ytd-video-secondary-info-renderer yt-formatted-string",
            "#description yt-formatted-string",
            "ytd-video-description-renderer yt-formatted-string"
        ]
        
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"\n选择器: {selector}")
                print(f"找到 {len(elements)} 个元素")
                
                for i, element in enumerate(elements):
                    text = element.text.strip()
                    if text:
                        print(f"  元素 {i+1}:")
                        print(f"    长度: {len(text)} 字符")
                        print(f"    内容: {text[:200]}...")
                        
                        # 检查第一行
                        lines = text.split('\n')
                        if lines:
                            first_line = lines[0].strip()
                            print(f"    第一行: '{first_line}'")
                            
                            # 检查是否包含观看次数或日期
                            if any(keyword in first_line.lower() for keyword in ['views', '观看', '次观看', 'ago', '小时前', '天前']):
                                print(f"    ⚠️  第一行包含观看次数或日期信息")
                        
                        print()
                        
            except Exception as e:
                print(f"  选择器 {selector} 出错: {str(e)}")
        
        # 检查页面源码中的信息
        print("\n检查页面源码中的观看次数和日期信息:")
        page_source = driver.page_source
        
        import re
        
        # 查找观看次数和日期
        patterns = [
            r'([\d,]+)\s*views?\s*([^\\n]+)',
            r'([\d,]+)\s*观看\s*([^\\n]+)',
            r'(\d+\s*(?:hours?|days?|weeks?|months?)\s+ago)',
            r'(\d+\s*(?:小时前|天前|周前|月前))'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, page_source, re.IGNORECASE)
            if matches:
                print(f"  找到匹配: {matches[:3]}")
        
        print("\n测试完成!")
        
    except Exception as e:
        print(f"测试过程中出错: {str(e)}")
    finally:
        driver.quit()


if __name__ == "__main__":
    test_single_video() 