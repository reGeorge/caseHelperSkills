#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量创建自动化测试用例
Batch create automated test cases from Lark spreadsheet
"""
import sys
import os
import json
import argparse

# 添加父目录到路径以导入相关模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../platform-client'))
sys.path.insert(0, os.path.dirname(__file__))

from platform_client import PlatformClient
from read_lark_sheet import read_lark_sheet


def filter_cases(cases: list) -> list:
    """
    筛选符合条件的用例
    
    条件：
    1. 是否支持自动化 == "是"
    2. 脚本序号为空或null
    
    Args:
        cases: 用例列表
    
    Returns:
        list: 筛选后的用例列表
    """
    filtered = []
    for case in cases:
        support_automation = case.get("是否支持自动化")
        script_id = case.get("脚本序号")
        
        # 检查是否支持自动化
        if support_automation != "是":
            continue
        
        # 检查脚本序号是否为空
        if script_id is not None and script_id != "":
            continue
        
        filtered.append(case)
    
    return filtered


def copy_steps_from_case(client: PlatformClient, source_case_id: int, target_case_id: int):
    """
    从源用例复制所有步骤到目标用例
    
    Args:
        client: PlatformClient实例
        source_case_id: 源用例ID
        target_case_id: 目标用例ID
    
    Note:
        由于API路径问题，此功能暂未实现。
        建议在SDET平台上手动添加公共步骤。
    """
    print(f"  [跳过] 公共步骤复制功能暂未实现")
    print(f"  [提示] 请在SDET平台上手动为用例 {target_case_id} 添加公共步骤")
    return True


def create_case_with_steps(client: PlatformClient, case_data: dict, directory_id: int, public_case_id: int):
    """
    创建用例并添加公共步骤
    
    Args:
        client: PlatformClient实例
        case_data: 用例数据
        directory_id: 目标目录ID
        public_case_id: 公共步骤用例ID
    
    Returns:
        dict: {"success": bool, "case_id": int, "message": str}
    """
    # 创建用例
    result = client.create_case(
        name=case_data.get("用例名称", "未命名用例"),
        directory_id=directory_id,
        description=case_data.get("用例描述", ""),
        note=f"来源: {case_data.get('用例编号', '未知')}"
    )
    
    if not result['success']:
        return {
            "success": False,
            "case_id": None,
            "message": f"创建用例失败: {result['message']}"
        }
    
    case_id = result['data']
    print(f"  [OK] 用例创建成功 (ID: {case_id})")
    
    # 复制公共步骤
    if public_case_id:
        copy_steps_from_case(client, public_case_id, case_id)
    
    return {
        "success": True,
        "case_id": case_id,
        "message": "创建成功"
    }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='批量创建自动化测试用例')
    parser.add_argument('--sheet-url', required=True, help='飞书表格URL')
    parser.add_argument('--directory-id', type=int, default=66241, help='目标目录ID（默认66241）')
    parser.add_argument('--public-case-id', type=int, default=51401, help='公共步骤用例ID（默认51401）')
    parser.add_argument('--dry-run', action='store_true', help='预览模式，不实际创建')
    parser.add_argument('--limit', type=int, help='限制创建数量（用于测试）')
    parser.add_argument('--config', default='config.json', help='配置文件路径')
    
    args = parser.parse_args()
    
    # 加载配置
    config_path = os.path.join(os.path.dirname(__file__), args.config)
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        # 使用默认配置
        config = {
            "lark": {
                "app_id": os.environ.get('LARK_APP_ID', 'cli_a83faf50a228900e'),
                "app_secret": os.environ.get('LARK_APP_SECRET', 'VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH')
            },
            "sdet": {
                "base_url": "https://sdet.ruishan.cc/api/sdet-atp",
                "token": os.environ.get('SDET_TOKEN', ''),
                "creator_name": "自动化脚本",
                "creator_id": "9999"
            }
        }
    
    try:
        print("=" * 80)
        print("批量创建自动化测试用例")
        print("=" * 80)
        print(f"表格URL: {args.sheet_url}")
        print(f"目标目录ID: {args.directory_id}")
        print(f"公共步骤ID: {args.public_case_id}")
        print(f"预览模式: {'是' if args.dry_run else '否'}")
        print("-" * 80)
        
        # Step 1: 读取飞书表格
        print("\n[Step 1] 读取飞书表格...")
        cases = read_lark_sheet(
            args.sheet_url,
            config['lark']['app_id'],
            config['lark']['app_secret']
        )
        print(f"读取到 {len(cases)} 条记录")
        
        # Step 2: 筛选符合条件的记录
        print("\n[Step 2] 筛选符合条件的记录...")
        print("筛选条件: 是否支持自动化=是 且 脚本序号为空")
        filtered_cases = filter_cases(cases)
        print(f"筛选后剩余 {len(filtered_cases)} 条记录")
        
        if not filtered_cases:
            print("\n[警告] 没有找到符合条件的记录")
            return 0
        
        # 限制数量（用于测试）
        if args.limit and len(filtered_cases) > args.limit:
            filtered_cases = filtered_cases[:args.limit]
            print(f"已限制为前 {args.limit} 条记录")
        
        # Step 3: 预览或创建
        if args.dry_run:
            print("\n[Step 3] 预览模式 - 以下用例将被创建：")
            print("=" * 80)
            for i, case in enumerate(filtered_cases, 1):
                print(f"\n{i}. {case.get('用例名称', '未命名')}")
                print(f"   用例编号: {case.get('用例编号', '未知')}")
                print(f"   是否支持自动化: {case.get('是否支持自动化', '未知')}")
                print(f"   脚本序号: {case.get('脚本序号', '空')}")
            print("\n" + "=" * 80)
            print(f"[OK] 预览完成，共 {len(filtered_cases)} 条记录将被创建")
            return 0
        
        # Step 4: 初始化客户端
        print("\n[Step 3] 初始化SDET客户端...")
        client = PlatformClient(
            base_url=config['sdet']['base_url'],
            token=config['sdet']['token'],
            creator_name=config['sdet']['creator_name'],
            creator_id=config['sdet']['creator_id']
        )
        
        # Step 5: 批量创建
        print("\n[Step 4] 批量创建用例...")
        print("=" * 80)
        
        success_count = 0
        failed_count = 0
        
        for i, case in enumerate(filtered_cases, 1):
            print(f"\n[{i}/{len(filtered_cases)}] 创建用例: {case.get('用例名称', '未命名')}")
            
            result = create_case_with_steps(
                client=client,
                case_data=case,
                directory_id=args.directory_id,
                public_case_id=args.public_case_id
            )
            
            if result['success']:
                success_count += 1
            else:
                failed_count += 1
                print(f"  [ERROR] {result['message']}")
        
        # 输出统计
        print("\n" + "=" * 80)
        print("[完成] 批量创建结束")
        print(f"成功: {success_count} 条")
        print(f"失败: {failed_count} 条")
        print("=" * 80)
        
        return 0 if failed_count == 0 else 1
        
    except Exception as e:
        print(f"\n[错误] 执行失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
