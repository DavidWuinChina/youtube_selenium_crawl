#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube视频描述爬虫 - 主入口文件
使用模块化架构，输出文件保存到data文件夹
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import main

if __name__ == "__main__":
    main() 