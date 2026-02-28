"""
批量添加公共步骤并更新飞书表格

功能：
1. 为SDET平台上的用例添加公共步骤（caseid=51401）
2. 将用例ID回写到飞书表格的"脚本序号"列
"""
import os
import sys
import json
import argparse
import requests
from urllib.parse import urlparse, parse_qs


def read_lark_sheet_data(sheet_url):
    """
    读取飞书表格数据

    Args:
        sheet_url: 飞书表格URL

    Returns:
        list: 表格数据
    """
    # 从URL中提取参数
    parsed = urlparse(sheet_url)
    query = parse_qs(parsed.query)

    # 获取sheet_token和sheet_id
    path_parts = parsed.path.split('/')
    sheet_token = path_parts[-1] if path_parts else None

    if not sheet_token:
        print("[ERROR] 无法从URL中提取sheet_token")
        return None

    sheet_id = query.get('sheet', [''])[0]

    # 飞书应用配置
    app_id = "cli_a83faf50a228900e"
    app_secret = "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"

    # 获取tenant_access_token
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    data = {"app_id": app_id, "app_secret": app_secret}

    try:
        response = requests.post(url, json=data, headers=headers)
        result = response.json()

        if result.get("code") != 0:
            print(f"[ERROR] 获取tenant_access_token失败: {result}")
            return None

        tenant_access_token = result.get("tenant_access_token")

        # 获取表格数据
        url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{sheet_token}/values"
        params = {"valueRenderOption": "ToString"}

        response = requests.get(url, params=params, headers={
            "Authorization": f"Bearer {tenant_access_token}"
        })
        result = response.json()

        if result.get("code") != 0:
            print(f"[ERROR] 获取表格数据失败: {result}")
            return None

        # 转换为列表格式
        values = result.get("data", {}).get("valueRanges", [])
        rows = []

        for item in values:
            rows.extend(item.get("values", []))

        return rows

    except Exception as e:
        print(f"[ERROR] 读取飞书表格异常: {e}")
        return None


def find_sheet_info(sheet_url):
    """
    从URL中提取sheet_token和sheet_id

    Args:
        sheet_url: 飞书表格URL

    Returns:
        tuple: (sheet_token, sheet_id)
    """
    parsed = urlparse(sheet_url)
    query = parse_qs(parsed.query)

    path_parts = parsed.path.split('/')
    sheet_token = path_parts[-1] if path_parts else None

    sheet_id = query.get('sheet', [''])[0]

    return sheet_token, sheet_id


def get_tenant_access_token():
    """获取飞书tenant_access_token"""
    app_id = "cli_a83faf50a228900e"
    app_secret = "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"

    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    data = {"app_id": app_id, "app_secret": app_secret}

    try:
        response = requests.post(url, json=data, headers=headers)
        result = response.json()

        if result.get("code") != 0:
            print(f"[ERROR] 获取tenant_access_token失败: {result}")
            return None

        return result.get("tenant_access_token")
    except Exception as e:
        print(f"[ERROR] 获取tenant_access_token异常: {e}")
        return None


def add_public_step(case_id, public_case_id=51401):
    """
    为用例添加公共步骤引用

    Args:
        case_id: 目标用例ID
        public_case_id: 公共步骤用例ID

    Returns:
        bool: 是否成功
    """
    token = "NDY7d2VpYmluOzE3NzI1MDc0ODAxNzQ7M2UwMTEzMGZjYWZmZjRkMDE1MTU5ZGNmYmE4OWY5OWJiNGUxNDMyZTY3NzAxNTIxMDJlNjVlOGZkNjIwMGUyMQ=="
    url = "https://sdet.ruishan.cc/api/sdet-atp/flow"
    headers = {
        "Content-Type": "application/json",
        "token": token
    }
    data = {
        "caseId": case_id,
        "type": "1",
        "status": 0,
        "exception": 0,
        "delayTime": 0,
        "quoteId": str(public_case_id)
    }

    try:
        response = requests.post(url, json=data, headers=headers, verify=False)
        result = response.json()

        if response.status_code == 200 and result.get('success', True):
            print(f"  [OK] 用例 {case_id} 公共步骤引用成功")
            return True
        else:
            print(f"  [ERROR] 用例 {case_id} 公共步骤引用失败: {result}")
            return False
    except Exception as e:
        print(f"  [ERROR] 用例 {case_id} 公共步骤引用异常: {e}")
        return False


def update_lark_sheet(sheet_token, sheet_id, token, row_index, col_index, value):
    """
    更新飞书表格单元格

    Args:
        sheet_token: 表格token
        sheet_id: 工作表ID
        token: tenant_access_token
        row_index: 行索引（从0开始）
        col_index: 列索引（从0开始）
        value: 要写入的值

    Returns:
        bool: 是否成功
    """
    url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{sheet_token}/values"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "valueRange": {
            "range": f"{sheet_id}!{chr(65 + col_index)}{row_index + 1}",
            "values": [[str(value)]]
        }
    }

    try:
        response = requests.put(url, json=data, headers=headers)
        result = response.json()

        if result.get("code") == 0:
            print(f"  [OK] 飞书表格更新成功 (行{row_index + 1}, 列{col_index + 1})")
            return True
        else:
            print(f"  [ERROR] 飞书表格更新失败: {result}")
            return False
    except Exception as e:
        print(f"  [ERROR] 飞书表格更新异常: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='批量添加公共步骤并更新飞书表格')
    parser.add_argument('--sheet-url', required=True, help='飞书表格URL')
    parser.add_argument('--case-ids', nargs='+', type=int, help='要处理的用例ID列表')
    parser.add_argument('--public-case-id', type=int, default=51401, help='公共步骤用例ID（默认51401）')
    parser.add_argument('--dry-run', action='store_true', help='预览模式，不实际操作')
    parser.add_argument('--case-id-range', nargs=2, type=int, metavar=('START', 'END'),
                       help='用例ID范围（包含两端）')

    args = parser.parse_args()

    # 确定要处理的用例ID列表
    if args.case_ids:
        case_ids = args.case_ids
    elif args.case_id_range:
        start, end = args.case_id_range
        case_ids = list(range(start, end + 1))
    else:
        # 默认处理刚刚创建的用例 66249-66274
        case_ids = list(range(66249, 66275))

    print(f"[INFO] 将处理 {len(case_ids)} 个用例: {case_ids}")
    print(f"[INFO] 公共步骤用例ID: {args.public_case_id}")
    print(f"[INFO] 飞书表格URL: {args.sheet_url}")
    if args.dry_run:
        print("[INFO] 预览模式，不会实际操作")

    # 读取飞书表格数据
    print("\n[INFO] 读取飞书表格...")
    sheet_token, sheet_id = find_sheet_info(args.sheet_url)
    if not sheet_token:
        print("[ERROR] 无法解析飞书表格URL")
        return

    rows = read_lark_sheet_data(args.sheet_url)
    if not rows:
        print("[ERROR] 读取飞书表格失败")
        return

    print(f"[OK] 飞书表格读取成功，共 {len(rows)} 行")

    # 查找字段列索引
    if len(rows) < 1:
        print("[ERROR] 表格没有数据")
        return

    header = rows[0]
    print(f"\n[INFO] 表头: {header}")

    # 查找关键字段
    try:
        case_name_col = header.index("用例名称")
        case_no_col = header.index("用例编号")
        script_seq_col = header.index("脚本序号")
        auto_support_col = header.index("是否支持自动化")
        print(f"[INFO] 字段列索引: 用例名称={case_name_col}, 用例编号={case_no_col}, 脚本序号={script_seq_col}, 是否支持自动化={auto_support_col}")
    except ValueError as e:
        print(f"[ERROR] 未找到必要字段: {e}")
        return

    # 构建用例名称到行索引和用例编号的映射
    case_mapping = {}
    for row_idx, row in enumerate(rows[1:], start=1):
        if len(row) > max(case_name_col, case_no_col):
            case_name = row[case_name_col]
            case_no = row[case_no_col] if len(row) > case_no_col else ""
            case_mapping[case_name] = (row_idx, case_no)

    print(f"[INFO] 建立映射关系，共 {len(case_mapping)} 个用例名称")

    # 获取飞书token
    lark_token = get_tenant_access_token()
    if not lark_token:
        print("[ERROR] 获取飞书token失败")
        return

    # 处理每个用例
    print("\n[INFO] 开始处理用例...")
    success_count = 0
    failed_count = 0

    for case_id in case_ids:
        print(f"\n处理用例 {case_id}...")

        # 添加公共步骤
        if not args.dry_run:
            if not add_public_step(case_id, args.public_case_id):
                failed_count += 1
                continue
        else:
            print(f"  [预览] 将添加公共步骤 (quoteId={args.public_case_id})")

        # 查找用例名称（通过查询SDET API）
        try:
            url = f"https://sdet.ruishan.cc/api/sdet-atp/case/{case_id}"
            headers = {"token": "NDY7d2VpYmluOzE3NzI1MDc0ODAxNzQ7M2UwMTEzMGZjYWZmZjRkMDE1MTU5ZGNmYmE4OWY5OWJiNGUxNDMyZTY3NzAxNTIxMDJlNjVlOGZkNjIwMGUyMQ=="}
            response = requests.get(url, headers=headers, verify=False)
            result = response.json()

            if response.status_code != 200 or not result.get('success', True):
                print(f"  [ERROR] 查询用例信息失败: {result}")
                if not args.dry_run:
                    failed_count += 1
                continue

            case_data = result.get('data', {})
            case_name = case_data.get('name', '')
            case_no = case_data.get('caseNo', '')

            if not case_name:
                print(f"  [WARNING] 用例名称为空，无法更新飞书表格")
                if not args.dry_run:
                    success_count += 1
                continue

            # 在飞书表格中查找对应的行
            if case_name in case_mapping:
                row_idx, sheet_case_no = case_mapping[case_name]
                print(f"  [INFO] 找到飞书表格记录 (行{row_idx + 1}): {case_name}")

                # 更新飞书表格
                if not args.dry_run:
                    if update_lark_sheet(sheet_token, sheet_id, lark_token, row_idx, script_seq_col, case_id):
                        success_count += 1
                    else:
                        failed_count += 1
                else:
                    print(f"  [预览] 将更新飞书表格 (行{row_idx + 1}, 列{script_seq_col + 1}) = {case_id}")
                    success_count += 1
            else:
                print(f"  [WARNING] 在飞书表格中未找到用例名称: {case_name}")
                if not args.dry_run:
                    success_count += 1
        except Exception as e:
            print(f"  [ERROR] 处理异常: {e}")
            if not args.dry_run:
                failed_count += 1

    # 输出总结
    print(f"\n{'='*60}")
    print(f"处理完成！")
    print(f"  成功: {success_count}")
    print(f"  失败: {failed_count}")
    print(f"  总计: {len(case_ids)}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
