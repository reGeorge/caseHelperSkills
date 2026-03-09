#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SDET平台配置文件
"""

import os

class Config:
    """平台配置"""
    
    # 本地路径配置
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    KNOWLEDGE_BASE_DIR = os.path.join(BASE_DIR, "knowledge")
    COMMON_CASES_DIR = os.path.join(KNOWLEDGE_BASE_DIR, "common_cases")
    MANIFEST_PATH = os.path.join(KNOWLEDGE_BASE_DIR, "common_cases_manifest.json")
    
    # SDET平台基础URL
    TEST_PLATFORM_URL = "https://sdet.ruishan.cc/api/sdet-atp"
    
    # 认证Token（从schema.md中提取）
    TEST_PLATFORM_TOKEN = "NDY7d2VpYmluOzE3NzQyMzUwMDczOTY7MTcyZTFiNDQyYWVlZjkwM2FkNTU2ZDdhZTMwODhiYzJkNmEzYjAyNmUyMmZiMTJjNjExNmIwNWQwZGIxOWM3MA=="
    
    # 创建者信息
    CREATOR_NAME = "魏斌"
    CREATOR_ID = 46
    
    # 默认父目录ID
    DEFAULT_PARENT_ID = 65566  # 注册无感控制目录


# 创建全局配置对象
config = Config()
