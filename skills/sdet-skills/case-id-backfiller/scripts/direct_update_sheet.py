"""
直接更新飞书表格单元格（使用PUT方法）

功能：直接更新飞书表格中的指定单元格
"""
import json
import requests


def get_access_token():
    """获取飞书access_token"""
    app_id = "cli_a83faf50a228900e"
    app_secret = "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"

    url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal/"
    headers = {"Content-Type": "application/json"}
    data = {"app_id": app_id, "app_secret": app_secret}

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    if result.get("code") == 0:
        return result.get("app_access_token")
    return None


def get_sdet_case_info(case_id):
    """获取SDET用例信息"""
    token = "NDY7d2VpYmluOzE3NzI1MDc0ODAxNzQ7M2UwMTEzMGZjYWZmZjRkMDE1MTU5ZGNmYmE4OWY5OWJiNGUxNDMyZTY3NzAxNTIxMDJlNjVlOGZkNjIwMGUyMQ=="
    url = f"https://sdet.ruishan.cc/api/sdet-atp/case/{case_id}"

    try:
        response = requests.get(url, headers={"token": token}, verify=False)
        result = response.json()

        if response.status_code != 200 or not result.get('success', True):
            return None

        return result.get('data')
    except Exception as e:
        print(f"  [ERROR] 查询用例 {case_id} 异常: {e}")
        return None


def get_sheet_data(spreadsheet_token, sheet_id, token):
    """获取飞书表格数据"""
    url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values"
    params = {
        "valueRenderOption": "ToString"
    }

    try:
        response = requests.get(url, params=params, headers={"Authorization": f"Bearer {token}"})
        result = response.json()

        if result.get("code") == 0:
            return result.get("data", {}).get("valueRanges", [])
        else:
            print(f"[ERROR] 读取表格失败: {result}")
            return None
    except Exception as e:
        print(f"[ERROR] 读取表格异常: {e}")
        return None


def find_row_by_case_name(data, case_name, case_name_col):
    """根据用例名称查找行号"""
    for item in data:
        values = item.get("values", [])
        for row_idx, row in enumerate(values):
            if len(row) > case_name_col and row[case_name_col] == case_name:
                return row_idx
    return None


def update_cell(spreadsheet_token, sheet_id, token, row, col, value):
    """更新指定单元格"""
    # 转换列索引为列名 (0->A, 1->B, ...)
    col_name = chr(65 + col) if col < 26 else chr(65 + col // 26 - 1) + chr(65 + col % 26)

    url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/{sheet_id}!{col_name}{row}:{col_name}{row}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "valueRange": {
            "values": [[str(value)]]
        }
    }

    try:
        response = requests.put(url, headers=headers, json=data)
        result = response.json()

        if result.get("code") == 0:
            return True
        else:
            print(f"  [ERROR] 更新单元格失败: {result}")
            return False
    except Exception as e:
        print(f"  [ERROR] 更新单元格异常: {e}")
        return False


def main():
    """主函数"""
    spreadsheet_token = "K8V2sTKLyhE54Ot75EycbnKLnvb"
    sheet_id = "FYZ5JP"

    # 获取飞书token
    print("[INFO] 获取飞书token...")
    lark_token = get_access_token()
    if not lark_token:
        print("[ERROR] 获取飞书token失败")
        return

    # 获取表格数据
    print("[INFO] 读取飞书表格...")
    data = get_sheet_data(spreadsheet_token, sheet_id, lark_token)
    if not data:
        print("[ERROR] 读取表格失败")
        return

    # 查找表头
    headers = []
    for item in data:
        values = item.get("values", [])
        if values and len(values) > 0:
            headers = values[0]
            break

    print(f"[INFO] 表头: {headers}")

    # 查找列索引
    try:
        case_name_col = headers.index("用例名称")
        script_id_col = headers.index("脚本序号")
        case_desc_col = headers.index("用例描述")
        print(f"[INFO] 用例名称列索引: {case_name_col}, 脚本序号列索引: {script_id_col}, 用例描述列索引: {case_desc_col}")
    except ValueError as e:
        print(f"[ERROR] 未找到必要字段: {e}")
        return

    # 处理26个用例
    case_ids = list(range(66249, 66275))
    success_count = 0
    not_found_count = 0

    print(f"\n[INFO] 开始处理 {len(case_ids)} 个用例...")

    # 输出表头
    print(f"\n{'='*120}")
    print(f"{'行号':<6} {'CaseID':<10} {'用例名称':<50} {'用例描述':<50}")
    print(f"{'='*120}")

    for case_id in case_ids:
        # 获取用例信息
        case_info = get_sdet_case_info(case_id)
        if not case_info:
            continue

        case_name = case_info.get('name', '')
        case_desc = case_info.get('note', '')

        if not case_name:
            print(f"  [WARNING] 用例 {case_id} 名称为空")
            continue

        # 查找匹配的行
        row_idx = find_row_by_case_name(data, case_name, case_name_col)

        if row_idx is not None:
            # 行号从1开始（表头在第1行）
            actual_row = row_idx + 1  # 表头在第1行
            if actual_row == 1:
                actual_row = 2  # 跳过表头

            case_desc_short = case_desc[:47] + "..." if len(case_desc) > 50 else case_desc
            print(f"{actual_row:<6} {case_id:<10} {case_name:<50} {case_desc_short:<50}")

            # 更新飞书表格
            if update_cell(spreadsheet_token, sheet_id, lark_token, actual_row + 1, script_id_col, case_id):
                print(f"  [OK] 脚本序号已更新为 {case_id}")
                success_count += 1
        else:
            print(f"  [WARNING] 在飞书表格中未找到用例名称: {case_name}")
            not_found_count += 1

    print(f"{'='*120}")
    print(f"\n处理完成！")
    print(f"  成功: {success_count}")
    print(f"  未找到: {not_found_count}")
    print(f"  总计: {len(case_ids)}")


if __name__ == '__main__':
    main()
