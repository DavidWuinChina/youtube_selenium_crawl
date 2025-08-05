#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube爬虫自动安装脚本
自动安装所需的依赖包
"""

import subprocess
import sys
import os


def install_package(package):
    """安装单个包"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ 成功安装 {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ 安装 {package} 失败")
        return False


def check_package(package):
    """检查包是否已安装"""
    try:
        __import__(package)
        return True
    except ImportError:
        return False


def main():
    """主安装函数"""
    print("=" * 60)
    print("YouTube视频描述爬虫 - 自动安装")
    print("=" * 60)
    
    # 需要安装的包列表
    packages = [
        "selenium",
        "webdriver-manager", 
        "pandas",
        "beautifulsoup4",
        "requests",
        "lxml"
    ]
    
    print("正在检查已安装的包...")
    
    # 检查已安装的包
    installed_packages = []
    missing_packages = []
    
    for package in packages:
        if check_package(package.replace("-", "_")):
            print(f"✅ {package} 已安装")
            installed_packages.append(package)
        else:
            print(f"❌ {package} 未安装")
            missing_packages.append(package)
    
    print(f"\n已安装: {len(installed_packages)}/{len(packages)} 个包")
    
    if missing_packages:
        print(f"\n需要安装 {len(missing_packages)} 个包:")
        for package in missing_packages:
            print(f"  - {package}")
        
        # 询问是否安装
        response = input("\n是否继续安装? (y/n): ").lower().strip()
        
        if response in ['y', 'yes', '是']:
            print("\n开始安装...")
            
            success_count = 0
            for package in missing_packages:
                if install_package(package):
                    success_count += 1
            
            print(f"\n安装完成！成功安装 {success_count}/{len(missing_packages)} 个包")
            
            if success_count == len(missing_packages):
                print("\n🎉 所有依赖包安装成功！")
                print("现在可以运行爬虫了:")
                print("  python simple_scraper.py")
                print("  python test_scraper.py")
            else:
                print("\n⚠️  部分包安装失败，请手动安装:")
                for package in missing_packages:
                    if not check_package(package.replace("-", "_")):
                        print(f"  pip install {package}")
        else:
            print("安装已取消")
    else:
        print("\n🎉 所有依赖包都已安装！")
        print("现在可以运行爬虫了:")
        print("  python simple_scraper.py")
        print("  python test_scraper.py")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main() 