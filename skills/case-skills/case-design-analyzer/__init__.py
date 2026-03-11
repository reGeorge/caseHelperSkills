"""
case-design-analyzer 包初始化

用例设计分析器 - 从手工用例生成自动化用例设计指导报告
"""

from .case_design_analyzer import (
    CaseDesignAnalyzer,
    ManualCase,
    Dimension,
    DataSource,
    StepInfo,
    VerificationPoint,
)

__version__ = "1.0.0"
__author__ = "SDET Team"

__all__ = [
    "CaseDesignAnalyzer",
    "ManualCase",
    "Dimension",
    "DataSource",
    "StepInfo",
    "VerificationPoint",
]
