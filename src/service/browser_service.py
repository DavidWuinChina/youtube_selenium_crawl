# -*- coding: utf-8 -*-
"""
浏览器服务层 - 处理浏览器相关操作
"""

import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from ..config.settings import BROWSER_CONFIG


class BrowserService:
    """浏览器服务类 - 处理浏览器相关操作"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.driver = None
    
    def create_driver(self, headless: bool = None) -> webdriver.Chrome:
        """
        创建Chrome浏览器驱动
        
        Args:
            headless: 是否无头模式，None则使用配置文件中的设置
            
        Returns:
            Chrome WebDriver实例
        """
        if headless is None:
            headless = BROWSER_CONFIG["headless"]
        
        self.logger.info(f"创建Chrome浏览器驱动 (headless: {headless})")
        
        # 创建Chrome选项
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument("--headless")
        
        # 添加配置的Chrome选项
        for option in BROWSER_CONFIG["chrome_options"]:
            chrome_options.add_argument(option)
        
        # 设置窗口大小
        chrome_options.add_argument(f"--window-size={BROWSER_CONFIG['window_size']}")
        
        # 设置用户代理
        chrome_options.add_argument(f"--user-agent={BROWSER_CONFIG['user_agent']}")
        
        # 使用webdriver-manager自动管理ChromeDriver
        service = Service(ChromeDriverManager().install())
        
        # 创建WebDriver
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 设置隐式等待时间
        self.driver.implicitly_wait(BROWSER_CONFIG["implicit_wait"])
        
        # 设置页面加载超时
        self.driver.set_page_load_timeout(BROWSER_CONFIG["page_load_timeout"])
        
        self.logger.info("Chrome浏览器驱动创建成功")
        return self.driver
    
    def get_driver(self) -> webdriver.Chrome:
        """获取当前WebDriver实例"""
        if self.driver is None:
            raise RuntimeError("WebDriver未初始化，请先调用create_driver()")
        return self.driver
    
    def close_driver(self):
        """关闭浏览器驱动"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("浏览器驱动已关闭")
            except Exception as e:
                self.logger.warning(f"关闭浏览器驱动时出错: {str(e)}")
            finally:
                self.driver = None
    
    def __enter__(self):
        """上下文管理器入口"""
        self.create_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close_driver()
    
    def is_driver_ready(self) -> bool:
        """检查WebDriver是否准备就绪"""
        return self.driver is not None
    
    def get_page_title(self) -> str:
        """获取当前页面标题"""
        if not self.is_driver_ready():
            return ""
        
        try:
            return self.driver.title
        except Exception as e:
            self.logger.error(f"获取页面标题失败: {str(e)}")
            return ""
    
    def get_current_url(self) -> str:
        """获取当前页面URL"""
        if not self.is_driver_ready():
            return ""
        
        try:
            return self.driver.current_url
        except Exception as e:
            self.logger.error(f"获取当前URL失败: {str(e)}")
            return ""
    
    def refresh_page(self):
        """刷新当前页面"""
        if not self.is_driver_ready():
            return
        
        try:
            self.driver.refresh()
            self.logger.info("页面已刷新")
        except Exception as e:
            self.logger.error(f"刷新页面失败: {str(e)}")
    
    def take_screenshot(self, filename: str = None):
        """截取屏幕截图"""
        if not self.is_driver_ready():
            return
        
        try:
            if filename is None:
                import time
                filename = f"screenshot_{int(time.time())}.png"
            
            self.driver.save_screenshot(filename)
            self.logger.info(f"截图已保存: {filename}")
        except Exception as e:
            self.logger.error(f"截图失败: {str(e)}")
    
    def execute_script(self, script: str):
        """执行JavaScript脚本"""
        if not self.is_driver_ready():
            return
        
        try:
            return self.driver.execute_script(script)
        except Exception as e:
            self.logger.error(f"执行JavaScript脚本失败: {str(e)}")
            return None 