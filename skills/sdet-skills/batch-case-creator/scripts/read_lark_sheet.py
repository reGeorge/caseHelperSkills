#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
读取飞书表格数据
Read Lark spreadsheet data
"""
import sys
import os
import json
import re
import requests
import argparse

def read_lark_sheet(url: str, app_id: str, app_secret: str) -> list:
    """
    读取飞书表格
    
    Args:
        url: 飞书表格URL
        app_id: 飞书应用ID
        app_secret: 飞书应用密钥
    
    Returns:
        list: 表格数据列表，每个元素是一个字典
    """
    # 解析URL提取spreadsheet_token和sheet_id
    match = re.search(r'/sheets/([a-zA-Z0-9]+)', url)
    if not match:
        raise ValueError("无法从URL中提取spreadsheet_token")
    spreadsheet_token = match.group(1)
    
    match = re.search(r'sheet=([a-zA-Z0-9]+)', url)
    sheet_id = match.group(1) if match else None
    
    # 获取access_token
    token_url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal/"
    headers = {"Content-Type": "application/json"}
    data = {"app_id": app_id, "app_secret": app_secret}
    
    response = requests.post(token_url, headers=headers, json=data)
    response.raise_for_status()
    result = response.json()
    access_token = result.get("app_access_token")
    
    if not access_token:
        raise ValueError("获取access_token失败")
    
    # 如果没有sheet_id，获取第一个sheet
    if not sheet_id:
        query_url = f"https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{spreadsheet_token}/sheets/query"
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        response = requests.get(query_url, headers=headers)
        response.raise_for_status()
        result = response.json()
        sheets = result.get("data", {}).get("sheets", [])
        if sheets:
            sheet_id = sheets[0].get("sheet_id")
        else:
            raise ValueError("未找到任何sheet")
    
    # 读取数据
    read_url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/{sheet_id}"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    response = requests.get(read_url, headers=headers)
    response.raise_for_status()
    result = response.json()
    values = result.get("data", {}).get("valueRange", {}).get("values", [])
    
    # 转换为字典列表
    if not values or len(values) < 2:
        return []
    
    headers = values[0]
    result_data = []
    
    for row in values[1:]:
        if not any(row):
            continue
        
        row_dict = {}
        for i, cell in enumerate(row):
            if i < len(headers):
                key = headers[i]
                # 处理复杂类型（如飞书mention）
                if isinstance(cell, dict):
                    if cell.get("type") == "mention":
                        cell = cell.get("text", "")
                    else:
                        cell = json.dumps(cell, ensure_ascii=False)
                row_dict[key] = cell if cell else None
        
        result_data.append(row_dict)
    
    return result_data


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='读取飞书表格数据')
    parser.add_argument('--url', required=True, help='飞书表格URL')
    parser.add_argument('--app-id', help='飞书应用ID')
    parser.add_argument('--app-secret', help='飞书应用密钥')
    parser.add_argument('--output', help='输出JSON文件路径（可选）')
    parser.add_argument('--limit', type=int, help='限制读取行数（用于测试）')
    
    args = parser.parse_args()
    
    # 配置（可以从环境变量或配置文件读取）
    app_id = args.app_id or os.environ.get('LARK_APP_ID', 'cli_a83faf50a228900e')
    app_secret = args.app_secret or os.environ.get('LARK_APP_SECRET', 'VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH')
    
    try:
        print("=" * 80)
        print("读取飞书表格")
        print("=" * 80)
        print(f"表格URL: {args.url}")
        print("-" * 80)
        
        # 读取表格
        print("\n正在读取表格...")
        data = read_lark_sheet(args.url, app_id, app_secret)
        
        # 限制行数（用于测试）
        if args.limit and len(data) > args.limit:
            data = data[:args.limit]
            print(f"已限制为前 {args.limit} 行数据")
        
        print(f"成功读取 {len(data)} 行数据")
        
        # 输出到文件或控制台
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"\n数据已保存到: {args.output}")
        else:
            print("\n表格数据：")
            print("=" * 80)
            print(json.dumps(data[:5], ensure_ascii=False, indent=2))  # 只显示前5条
            if len(data) > 5:
                print(f"... (共 {len(data)} 条)")
            print("=" * 80)
        
        print("\n[OK] 读取完成")
        return 0
        
    except Exception as e:
        print(f"\n[错误] 读取失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
