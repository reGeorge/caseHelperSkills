#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
手工用例结构化分析工具
从手工用例中提取关键信息，为自动化设计提供数据支撑
"""
import json
import re
from collections import defaultdict
from typing import Dict, List, Any

class TestCaseAnalyzer:
    """测试用例分析器"""
    
    def __init__(self):
        self.config_keywords = {
            '无感接入类型': ['仅有线', '仅无线', '全部'],
            'MAC快速接入': ['勾选', '未勾选'],
            'MAC快速认证数': ['满足', '未满足']
        }
        
        self.operation_keywords = {
            '有线认证': ['有线portal认证', '有线认证', '有线MAB'],
            '无线认证': ['无线portal认证', '无线1x认证', '无线认证'],
            'MAB认证': ['MAB认证', '有线MAB', '无线MAB'],
            '抢占MAC': ['抢占MAC', '抢占']
        }
        
        self.test_type_keywords = {
            '正向': ['（正向）', '正向'],
            '异常': ['失败', '拒绝', '异常']
        }
    
    def analyze_case(self, case_data: Dict) -> Dict[str, Any]:
        """
        分析单个测试用例
        
        Args:
            case_data: 手工用例数据
        
        Returns:
            分析结果
        """
        case_name = case_data.get('用例名称', '')
        case_desc = case_data.get('用例描述', '')
        
        result = {
            'case_id': case_data.get('用例编号'),
            'case_name': case_name,
            'case_summary': self._extract_summary(case_desc),
            
            'config_state': self._extract_config_state(case_name),
            'operation': self._extract_operation(case_name),
            'test_type': self._extract_test_type(case_name),
            'priority': case_data.get('用例等级', 'p2'),
            
            'key_points': self._extract_key_points(case_name),
            'business_scenario': self._extract_scenario(case_name)
        }
        
        return result
    
    def _extract_summary(self, description: str) -> str:
        """提取用例简述"""
        # 通常用例描述的第一句就是简述
        if not description:
            return ""
        
        # 提取第一个句号之前的内容
        sentences = description.split('，')
        if sentences:
            return sentences[0][:100]  # 限制长度
        
        return description[:100]
    
    def _extract_config_state(self, case_name: str) -> Dict[str, str]:
        """提取配置状态"""
        config_state = {}
        
        for config_name, keywords in self.config_keywords.items():
            for keyword in keywords:
                if keyword in case_name:
                    config_state[config_name] = keyword
                    break
        
        return config_state
    
    def _extract_operation(self, case_name: str) -> List[str]:
        """提取用户操作"""
        operations = []
        
        for op_name, keywords in self.operation_keywords.items():
            for keyword in keywords:
                if keyword in case_name:
                    operations.append(op_name)
                    break
        
        return operations
    
    def _extract_test_type(self, case_name: str) -> str:
        """提取测试类型"""
        for test_type, keywords in self.test_type_keywords.items():
            for keyword in keywords:
                if keyword in case_name:
                    return test_type
        
        return '常规'
    
    def _extract_key_points(self, case_name: str) -> List[str]:
        """提取关键点"""
        key_points = []
        
        # 提取关键业务点
        if '注册' in case_name:
            key_points.append('注册MAC')
        if '认证' in case_name:
            key_points.append('执行认证')
        if '抢占' in case_name:
            key_points.append('MAC抢占')
        if '历史数据' in case_name:
            key_points.append('历史数据处理')
        
        return key_points
    
    def _extract_scenario(self, case_name: str) -> str:
        """提取业务场景"""
        scenarios = []
        
        if '有线' in case_name:
            scenarios.append('有线')
        if '无线' in case_name:
            scenarios.append('无线')
        
        return '+'.join(scenarios) if scenarios else '通用'
    
    def analyze_batch(self, cases: List[Dict]) -> Dict[str, Any]:
        """
        批量分析用例
        
        Returns:
            分类统计结果
        """
        analyzed_cases = []
        
        for case in cases:
            analyzed = self.analyze_case(case)
            analyzed_cases.append(analyzed)
        
        # 按配置状态分类
        by_config = defaultdict(list)
        for case in analyzed_cases:
            config_key = self._make_config_key(case['config_state'])
            by_config[config_key].append(case)
        
        # 按操作分类
        by_operation = defaultdict(list)
        for case in analyzed_cases:
            for op in case['operation']:
                by_operation[op].append(case)
        
        # 按测试类型分类
        by_test_type = defaultdict(list)
        for case in analyzed_cases:
            by_test_type[case['test_type']].append(case)
        
        # 生成目录树建议
        directory_tree = self._generate_directory_tree(by_config, by_operation)
        
        return {
            'total_cases': len(analyzed_cases),
            'analyzed_cases': analyzed_cases,
            'classification': {
                'by_config': dict(by_config),
                'by_operation': dict(by_operation),
                'by_test_type': dict(by_test_type)
            },
            'directory_tree': directory_tree
        }
    
    def _make_config_key(self, config_state: Dict) -> str:
        """生成配置状态键"""
        if not config_state:
            return '默认配置'
        
        parts = []
        for key, value in sorted(config_state.items()):
            parts.append(f"{key}={value}")
        
        return ', '.join(parts)
    
    def _generate_directory_tree(self, by_config: Dict, by_operation: Dict) -> Dict:
        """生成目录树建议"""
        tree = {
            'structure_type': 'recommended',
            'levels': [
                {
                    'level': 1,
                    'name': '按配置状态',
                    'children': list(by_config.keys())
                },
                {
                    'level': 2,
                    'name': '按用户操作',
                    'children': list(by_operation.keys())
                }
            ]
        }
        
        return tree
    
    def export_to_mapping(self, analysis_result: Dict) -> List[Dict]:
        """
        导出为映射表格式
        
        Returns:
            映射表数据
        """
        mapping = []
        
        for case in analysis_result['analyzed_cases']:
            mapping.append({
                'directory': self._make_config_key(case['config_state']),
                'case_title': case['case_name'],
                'manual_case_id': case['case_id'],
                'auto_case_id': '',  # 待填充
                'case_summary': case['case_summary'],
                'case_detail': {
                    'config_state': case['config_state'],
                    'operation': case['operation'],
                    'test_type': case['test_type'],
                    'key_points': case['key_points']
                }
            })
        
        return mapping


def main():
    """主函数"""
    import json
    
    # 加载手工用例数据
    with open('sandbox/workspace/lark_latest_data.json', 'r', encoding='utf-8') as f:
        cases = json.load(f)
    
    print('='*80)
    print('手工用例结构化分析')
    print('='*80)
    print()
    
    # 初始化分析器
    analyzer = TestCaseAnalyzer()
    
    # 批量分析
    result = analyzer.analyze_batch(cases)
    
    # 输出统计
    print(f'总用例数: {result["total_cases"]}')
    print()
    
    print('='*80)
    print('按配置状态分类')
    print('='*80)
    for config, cases in result['classification']['by_config'].items():
        print(f'\n{config} ({len(cases)}个):')
        for case in cases:
            print(f'  - [{case["case_id"]}] {case["case_name"][:50]}...')
    
    print()
    print('='*80)
    print('按用户操作分类')
    print('='*80)
    for operation, cases in result['classification']['by_operation'].items():
        print(f'\n{operation} ({len(cases)}个):')
        for case in cases:
            print(f'  - [{case["case_id"]}] {case["case_name"][:50]}...')
    
    print()
    print('='*80)
    print('按测试类型分类')
    print('='*80)
    for test_type, cases in result['classification']['by_test_type'].items():
        print(f'\n{test_type} ({len(cases)}个)')
    
    # 导出映射表
    mapping = analyzer.export_to_mapping(result)
    
    # 保存结果
    output = {
        'analysis_summary': {
            'total_cases': result['total_cases'],
            'classification_stats': {
                'config_groups': len(result['classification']['by_config']),
                'operation_groups': len(result['classification']['by_operation']),
                'test_type_groups': len(result['classification']['by_test_type'])
            }
        },
        'classification': result['classification'],
        'directory_tree': result['directory_tree'],
        'mapping_table': mapping
    }
    
    with open('sandbox/workspace/test_case_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print()
    print('='*80)
    print('分析完成')
    print('='*80)
    print(f'结果已保存到: sandbox/workspace/test_case_analysis.json')


if __name__ == '__main__':
    main()
