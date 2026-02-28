"""
将AI概述写回飞书表格
Write AI overview back to Lark spreadsheet
"""
import sys
import os
import json
import re
import requests


def read_lark_sheet(url: str, app_id: str, app_secret: str) -> tuple:
    """读取飞书表格，返回 (表格数据, spreadsheet_token, sheet_id)"""
    # 解析URL
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

    # 如果没有sheet_id，获取第一个
    if not sheet_id:
        query_url = f"https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{spreadsheet_token}/sheets/query"
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        response = requests.get(query_url, headers=headers)
        response.raise_for_status()
        result = response.json()
        sheets = result.get("data", {}).get("sheets", [])
        if sheets:
            sheet_id = sheets[0].get("sheet_id")

    # 读取数据
    read_url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/{sheet_id}"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    response = requests.get(read_url, headers=headers)
    response.raise_for_status()
    result = response.json()
    values = result.get("data", {}).get("valueRange", {}).get("values", [])

    return values, spreadsheet_token, sheet_id, access_token


def generate_overview(case: dict) -> str:
    """为单个用例生成概述"""
    case_name = case.get("用例名称", "")
    precondition = case.get("预置条件", "")
    steps = case.get("测试步骤", "")
    expected_result = case.get("期望结果", "")

    parts = []

    # 从用例名称中提取关键信息
    if case_name:
        parts.append(case_name)

    # 补充预置条件中的关键配置
    if precondition:
        config_keywords = ["开启自动学习", "关闭自动学习", "是否校验服务器证书", "不校验服务器证书"]
        for keyword in config_keywords:
            if keyword in precondition:
                simplified = keyword.replace("是否", "")
                if simplified not in " ".join(parts):
                    parts.append(simplified)

    # 从测试步骤中提取关键操作
    if steps:
        special_actions = {
            "加入黑名单": "用户被加入黑名单",
            "移除黑名单": "用户被移除黑名单",
            "首次认证": "首次认证",
            "非首次认证": "已学习用户认证",
        }

        for action, desc in special_actions.items():
            if action in steps:
                if not any(desc in part for part in parts):
                    if len(parts) > 1:
                        parts.insert(-1, desc)
                    else:
                        parts.append(desc)
                break

    # 合并概述
    if parts:
        unique_parts = []
        seen = set()
        for part in parts:
            # 简化文本
            simplified = re.sub(r'\d+、', '', part)
            simplified = re.sub(r'\s+', '', simplified)
            simplified = re.sub(r'^前提[:：]', '', simplified)
            simplified = simplified.replace("，", "、")

            # 去重
            if simplified and simplified not in seen:
                seen.add(simplified)
                unique_parts.append(simplified)

        overview = "、".join(unique_parts)
        if len(overview) > 80:
            overview = overview[:80] + "..."
    else:
        overview = case_name or "未生成概述"

    return overview


def write_to_lark_sheet(spreadsheet_token: str, sheet_id: str, access_token: str,
                        values: list, ai_overviews: list) -> None:
    """将AI概述写回飞书表格"""
    if not values or len(values) < 1:
        print("表格数据为空")
        return

    # 获取表头
    headers = values[0]

    # 查找或添加"用例AI概述"列
    ai_overview_col = "用例AI概述"
    if ai_overview_col not in headers:
        # 添加新列到表头
        headers.append(ai_overview_col)
        print(f"添加新列: {ai_overview_col}")
    else:
        print(f"使用现有列: {ai_overview_col}")

    # 获取列索引
    col_index = headers.index(ai_overview_col)
    print(f"列索引: {col_index}")

    # 使用updateCells接口（更可靠的方法）
    update_url = f"https://open.feishu.cn/open-apis/sheets/v4/spreadsheets/{spreadsheet_token}/update_cells"

    headers_request = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # 准备更新数据
    update_rows = []

    # 表头更新
    update_rows.append({
        "rowIndex": 0,
        "columnIndex": col_index,
        "values": [[ai_overview_col]]
    })

    # 数据行更新
    for i, overview in enumerate(ai_overviews):
        update_rows.append({
            "rowIndex": i + 1,  # 从第二行开始
            "columnIndex": col_index,
            "values": [[overview]]
        })

    data = {
        "update": {
            "rows": update_rows
        }
    }

    print(f"\n正在写入数据...")
    print(f"更新数量: {len(update_rows)}")
    try:
        response = requests.post(update_url, headers=headers_request, json=data)
        result = response.json()

        if result.get("code") == 0:
            print(f"[OK] 写入成功!")
            print(f"[OK] 共更新 {len(ai_overviews)} 行数据")
            return  # 成功则直接返回
    except Exception as e:
        print(f"主方案失败: {e}")

    # 使用备用方案
    print("\n使用备用方案...")
    try_backup_write(spreadsheet_token, sheet_id, access_token, values, ai_overviews)


def try_backup_write(spreadsheet_token: str, sheet_id: str, access_token: str,
                    values: list, ai_overviews: list) -> None:
    """备用写入方案：使用v2接口逐个单元格更新"""
    print("\n使用备用方案：逐个单元格更新...")

    # 获取表头
    headers = values[0]
    ai_overview_col = "用例AI概述"

    # 确保列存在
    if ai_overview_col not in headers:
        headers.append(ai_overview_col)

    col_index = headers.index(ai_overview_col)

    # 转换列索引为字母
    def num_to_col(n):
        result = ""
        while n >= 0:
            result = chr(65 + (n % 26)) + result
            n = n // 26 - 1
        return result

    col_letter = num_to_col(col_index)

    success_count = 0
    error_count = 0

    # 更新表头
    range_str = f"{sheet_id}!{col_letter}1"
    url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/{range_str}"

    headers_request = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    data = {
        "values": [[ai_overview_col]]
    }

    try:
        response = requests.put(url, headers=headers_request, json=data)
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                success_count += 1
            else:
                print(f"表头更新失败: {result.get('msg')}")
                error_count += 1
    except Exception as e:
        print(f"表头更新异常: {e}")
        error_count += 1

    # 批量更新数据（每次50行）
    batch_size = 50
    for i in range(0, min(len(ai_overviews), len(values) - 1), batch_size):
        end_idx = min(i + batch_size, len(ai_overviews))

        start_row = i + 2  # 从第二行开始（Excel中是第2行）
        end_row = end_idx + 1
        range_str = f"{sheet_id}!{col_letter}{start_row}:{col_letter}{end_row}"

        url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/{range_str}"

        # 构建数据
        data_values = [[overview] for overview in ai_overviews[i:end_idx]]
        data = {
            "values": data_values
        }

        try:
            response = requests.put(url, headers=headers_request, json=data)
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    success_count += (end_idx - i)
                    print(f"  进度: {end_idx}/{len(ai_overviews)}", end='\r')
                else:
                    print(f"\n  批次 {i}-{end_idx} 更新失败: {result.get('msg')}")
                    error_count += (end_idx - i)
            else:
                print(f"\n  HTTP错误: {response.status_code}")
                error_count += (end_idx - i)
        except Exception as e:
            print(f"\n  批次 {i}-{end_idx} 异常: {e}")
            error_count += (end_idx - i)

    print(f"\n[备用方案] 写入完成!")
    print(f"[备用方案] 成功: {success_count} 行, 失败: {error_count} 行")


def main():
    """主函数"""
    # 配置
    app_id = "cli_a83faf50a228900e"
    app_secret = "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"

    # 飞书表格URL
    url = "https://ruijie.feishu.cn/sheets/K8V2sTKLyhE54Ot75EycbnKLnvb?sheet=FYZ5JP"

    print("=" * 80)
    print("将AI概述写回飞书表格")
    print("=" * 80)
    print(f"表格URL: {url}")
    print("-" * 80)

    try:
        # 读取表格
        print("\n正在读取表格...")
        values, spreadsheet_token, sheet_id, access_token = read_lark_sheet(url, app_id, app_secret)

        if not values:
            print("表格为空")
            return

        print(f"成功读取 {len(values)} 行数据")

        # 提取表头和数据
        headers = values[0]
        data_rows = values[1:]

        # 转换为字典列表
        cases = []
        for row in data_rows:
            if not any(row):
                continue

            row_dict = {}
            for i, cell in enumerate(row):
                if i < len(headers):
                    key = headers[i]
                    # 处理复杂类型
                    if isinstance(cell, dict):
                        if cell.get("type") == "mention":
                            cell = cell.get("text", "")
                        else:
                            cell = json.dumps(cell, ensure_ascii=False)
                    row_dict[key] = cell if cell else None

            cases.append(row_dict)

        print(f"有效用例数: {len(cases)}")

        # 生成AI概述
        print("\n正在生成AI概述...")
        ai_overviews = []
        for i, case in enumerate(cases, 1):
            overview = generate_overview(case)
            ai_overviews.append(overview)

            if i <= 5:
                print(f"  [{i}] {overview}")

        print(f"共生成 {len(ai_overviews)} 条概述")

        # 确认写入
        print("\n" + "=" * 80)
        print("准备写入飞书表格")
        print("=" * 80)
        print(f"表格: {spreadsheet_token}")
        print(f"工作表: {sheet_id}")
        print(f"更新行数: {len(cases)}")
        print(f"添加列: 用例AI概述")
        print("-" * 80)
        print("注意: 这将直接修改飞书表格，请确认操作")
        print("=" * 80)

        # 写入表格
        write_to_lark_sheet(spreadsheet_token, sheet_id, access_token, values, ai_overviews)

        print("\n" + "=" * 80)
        print("[OK] 处理完成！")
        print("[OK] AI概述已成功写回飞书表格")
        print("=" * 80)

    except Exception as e:
        print(f"\n[错误] 处理失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
