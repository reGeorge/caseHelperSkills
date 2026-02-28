"""
批量更新飞书表格中的脚本序号

功能：将SDET用例ID回写到飞书表格的"脚本序号"列
"""
import json
import requests


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


def get_sdet_case_info(case_id):
    """获取SDET用例信息"""
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


def read_sheet_values(spreadsheet_token):
    """读取飞书表格所有数据"""
    token = get_tenant_access_token()
    if not token:
        return None

    url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values"
    params = {"valueRenderOption": "ToString"}

    try:
        response = requests.get(url, params=params, headers={
            "Authorization": f"Bearer {token}"
        })
        result = response.json()

        if result.get("code") != 0:
            print(f"[ERROR] 读取表格失败: {result}")
            return None

        # 转换为列表格式
        values = result.get("data", {}).get("valueRanges", [])
        rows = []

        for item in values:
            rows.extend(item.get("values", []))

        return rows
    except Exception as e:
        print(f"[ERROR] 读取表格异常: {e}")
        return None


def update_cell_value(spreadsheet_token, sheet_id, token, row, col, value):
    """更新飞书表格单元格"""
    # 转换列索引为列名 (0->A, 1->B, ...)
    col_name = chr(65 + col) if col < 26 else chr(65 + col // 26 - 1) + chr(65 + col % 26)

    url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "valueRange": {
            "range": f"{sheet_id}!{col_name}{row}:{col_name}{row}",
            "values": [[str(value)]]
        }
    }

    try:
        response = requests.put(url, json=data, headers=headers)
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

    print(f"[INFO] 表格Token: {spreadsheet_token}")
    print(f"[INFO] 工作表ID: {sheet_id}")

    # 读取表格数据
    print("\n[INFO] 读取飞书表格...")
    rows = read_sheet_values(spreadsheet_token)
    if not rows:
        print("[ERROR] 读取表格失败")
        return

    print(f"[OK] 表格读取成功，共 {len(rows)} 行")

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

    # 构建用例名称到行索引的映射
    case_mapping = {}
    for row_idx, row in enumerate(rows[1:], start=1):
        if len(row) > case_name_col:
            case_name = row[case_name_col]
            if case_name:
                case_mapping[case_name] = row_idx

    print(f"[INFO] 建立映射关系，共 {len(case_mapping)} 个用例名称")

    # 获取飞书token
    lark_token = get_tenant_access_token()
    if not lark_token:
        print("[ERROR] 获取飞书token失败")
        return

    # 处理每个用例 (66249-66274)
    print(f"\n[INFO] 开始处理用例 66249-66274...")
    case_ids = list(range(66249, 66275))

    success_count = 0
    not_found_count = 0

    for case_id in case_ids:
        # 查询用例信息
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

        # 在飞书表格中查找对应的行
        if case_name in case_mapping:
            row_idx = case_mapping[case_name]
            print(f"  [INFO] 找到飞书表格记录 (行{row_idx + 1})")

            # 更新飞书表格
            if update_cell_value(spreadsheet_token, sheet_id, lark_token, row_idx + 1, script_seq_col, case_id):
                print(f"  [OK] 脚本序号已更新为 {case_id}")
                success_count += 1
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


if __name__ == '__main__':
    main()
