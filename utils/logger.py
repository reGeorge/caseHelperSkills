#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
日志工具模块
"""

import logging
import sys


def setup_logger(name='platform_skills'):
    """
    设置并返回一个logger实例
    
    Args:
        name: logger名称
    
    Returns:
        logging.Logger: 配置好的logger实例
    """
    logger = logging.getLogger(name)
    
    # 如果logger已经有handlers，直接返回（避免重复添加）
    if logger.handlers:
        return logger
    
    # 设置日志级别
    logger.setLevel(logging.DEBUG)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(console_handler)
    
    return logger
