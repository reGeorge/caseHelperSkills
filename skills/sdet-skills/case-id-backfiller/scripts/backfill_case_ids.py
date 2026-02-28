"""
用例ID回填脚本

功能：将SDET平台上的用例ID回写到飞书表格的"脚本序号"列
"""
import os
import sys
import json
import argparse
import requests

# 添加lark-sheet-writer的路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'skills', 'lark-skills', 'lark-sheet-writer'))
from lark_sheet_writer import LarkSheetWriter


def get_sdet_case_info(case_id):
    """
    获取SDET用例信息

    Args:
        case_id: 用例ID

    Returns:
        dict: 用例信息
    """
    token = "NDY7d2VpYmluOzE3NzI1MDc0ODAxNzQ7M2UwMTEzMGZjYWZmZjRkMDE1MTU5ZGNmYmE4OWY5OWJiNGUxNDMyZTY3NzAxNTIxMDJlNjVlOGZkNjIwMGUyMQ=="
    url = f"https://sdet.ruishan.cc/api/sdet-atp/case/{case_id}"

    try:
        response = requests.get(url, headers={"token": token}, verify=False)
        result = response.json()

        if response.status_code != 200 or not result.get('success', True):
            print(f"  [ERROR] 查询用例 {case_id} 失败: {result}")
            return None

        return result.get('data')
    except Exception as e:
        print(f"  [ERROR] 查询用例 {case_id} 异常: {e}")
        return None


def load_mapping_file(mapping_file):
    """
    从映射文件加载用例信息

    Args:
        mapping_file: 映射文件路径

    Returns:
        list: 用例信息列表
    """
    try:
        with open(mapping_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"[INFO] 从 {mapping_file} 加载了 {len(data)} 条记录")
        return data
    except Exception as e:
        print(f"[ERROR] 加载映射文件失败: {e}")
        return None


def find_matching_row(data, headers, case_name, case_name_col):
    """
    在飞书表格中查找匹配的行

    Args:
        data: 表格数据
        headers: 表头
        case_name: 用例名称
        case_name_col: 用例名称列索引

    Returns:
        int: 匹配的行号（0-based），如果未找到返回None
    """
    for row_idx, row in enumerate(data):
        if len(row) > case_name_col and row[case_name_col] == case_name:
            return row_idx
    return None


def backfill_case_ids(case_ids, spreadsheet_token, sheet_id, dry_run=False):
    """
    回填用例ID到飞书表格

    Args:
        case_ids: 用例ID列表
        spreadsheet_token: 飞书表格token
        sheet_id: 工作表ID
        dry_run: 预览模式
    """
    # 初始化飞书表格写入器
    writer = LarkSheetWriter(
        app_id="cli_a83faf50a228900e",
        app_secret="VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"
    )

    # 获取表头和数据
    headers = writer.get_sheet_headers(spreadsheet_token, sheet_id)
    if not headers:
        print("[ERROR] 无法获取表头")
        return

    data = writer.get_sheet_data(spreadsheet_token, sheet_id)
    if not data:
        print("[ERROR] 无法获取表格数据")
        return

    print(f"[INFO] 表格有 {len(data)} 行数据")
    print(f"[INFO] 表头: {headers}")

    # 查找列索引
    try:
        case_name_col = headers.index("用例名称")
        script_id_col = headers.index("脚本序号")
        print(f"[INFO] 用例名称列索引: {case_name_col}, 脚本序号列索引: {script_id_col}")
    except ValueError as e:
        print(f"[ERROR] 未找到必要字段: {e}")
        return

    # 处理每个用例
    success_count = 0
    not_found_count = 0

    for case_id in case_ids:
        # 获取用例信息
        print(f"\n处理用例 {case_id}...")
        case_info = get_sdet_case_info(case_id)

        if not case_info:
            continue

        case_name = case_info.get('name', '')
        case_no = case_info.get('caseNo', '')

        if not case_name:
            print(f"  [WARNING] 用例名称为空")
            continue

        print(f"  用例名称: {case_name}")
        print(f"  用例编号: {case_no}")

        # 查找匹配的行
        row_idx = find_matching_row(data, headers, case_name, case_name_col)

        if row_idx is not None:
            print(f"  [INFO] 找到匹配的行 (行{row_idx + 1})")

            if dry_run:
                print(f"  [预览] 将更新 {sheet_id}!{chr(65 + script_id_col)}{row_idx + 1} 为 {case_id}")
                success_count += 1
            else:
                # 更新飞书表格
                update_data = {"脚本序号": str(case_id)}
                result = writer.update_record(
                    spreadsheet_token=spreadsheet_token,
                    sheet_id=sheet_id,
                    condition={"用例名称": case_name},
                    update_data=update_data
                )

                if result.get('success'):
                    print(f"  [OK] 脚本序号已更新为 {case_id}")
                    success_count += 1
                else:
                    print(f"  [ERROR] 更新失败: {result}")
        else:
            print(f"  [WARNING] 在飞书表格中未找到用例名称: {case_name}")
            not_found_count += 1

    # 输出总结
    print(f"\n{'='*60}")
    print(f"处理完成！")
    print(f"  成功: {success_count}")
    print(f"  未找到: {not_found_count}")
    print(f"  总计: {len(case_ids)}")
    print(f"{'='*60}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='回填用例ID到飞书表格')
    parser.add_argument('--case-ids', nargs='+', type=int, help='要回填的用例ID列表')
    parser.add_argument('--case-id-range', nargs=2, type=int, metavar=('START', 'END'),
                       help='用例ID范围（包含两端）')
    parser.add_argument('--mapping-file', help='从映射文件读取用例信息')
    parser.add_argument('--spreadsheet-token', default='K8V2sTKLyhE54Ot75EycbnKLnvb',
                       help='飞书表格token（默认K8V2sTKLyhE54Ot75EycbnKLnvb）')
    parser.add_argument('--sheet-id', default='FYZ5JP',
                       help='工作表ID（默认FYZ5JP）')
    parser.add_argument('--dry-run', action='store_true', help='预览模式，不实际更新')

    args = parser.parse_args()

    # 确定要处理的用例ID列表
    if args.mapping_file:
        # 从映射文件读取
        mapping_data = load_mapping_file(args.mapping_file)
        if not mapping_data:
            print("[ERROR] 加载映射文件失败")
            return
        case_ids = [item['用例ID'] for item in mapping_data]
    elif args.case_ids:
        case_ids = args.case_ids
    elif args.case_id_range:
        start, end = args.case_id_range
        case_ids = list(range(start, end + 1))
    else:
        # 默认处理 66249-66274
        case_ids = list(range(66249, 66275))

    print(f"[INFO] 将处理 {len(case_ids)} 个用例")
    print(f"[INFO] 飞书表格: {args.spreadsheet_token}")
    print(f"[INFO] 工作表: {args.sheet_id}")
    if args.dry_run:
        print("[INFO] 预览模式，不会实际更新飞书表格")

    # 回填用例ID
    backfill_case_ids(case_ids, args.spreadsheet_token, args.sheet_id, args.dry_run)


if __name__ == '__main__':
    main()
