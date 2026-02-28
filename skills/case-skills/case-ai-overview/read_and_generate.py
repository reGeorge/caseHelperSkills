"""
读取飞书表格并生成用例AI概述
Read Lark spreadsheet and generate AI overview for test cases
"""
import sys
import os
import json
import re
import requests

# 添加飞书skills路径
base_path = os.path.dirname(os.path.abspath(__file__))
lark_skills_path = os.path.join(base_path, '../../lark-skills')
sys.path.insert(0, lark_skills_path)


def read_lark_sheet(url: str, app_id: str, app_secret: str) -> list:
    """读取飞书表格"""
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


def main():
    """主函数"""
    # 配置
    app_id = "cli_a83faf50a228900e"
    app_secret = "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"

    # 飞书表格URL
    url = "https://ruijie.feishu.cn/sheets/K8V2sTKLyhE54Ot75EycbnKLnvb?sheet=FYZ5JP"

    print("=" * 80)
    print("读取飞书表格并生成用例AI概述")
    print("=" * 80)
    print(f"表格URL: {url}")
    print("-" * 80)

    try:
        # 读取表格
        print("\n正在读取表格...")
        cases = read_lark_sheet(url, app_id, app_secret)
        print(f"成功读取 {len(cases)} 条用例")

        # 生成概述
        print("\n正在生成AI概述...")
        for case in cases:
            case["用例AI概述"] = generate_overview(case)

        # 显示前5条结果
        print("\n" + "=" * 80)
        print("AI概述预览（前5条）")
        print("=" * 80)

        for i, case in enumerate(cases[:5], 1):
            print(f"\n【用例 {i}】")
            print(f"用例名称: {case.get('用例名称', 'N/A')}")
            print(f"AI概述:   {case.get('用例AI概述', 'N/A')}")
            print("-" * 80)

        # 保存到文件
        output_file = "test_cases_with_ai_overview.json"
        print(f"\n保存结果到文件: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cases, f, ensure_ascii=False, indent=2)

        print("\n" + "=" * 80)
        print("[OK] 处理完成！")
        print(f"[OK] 共处理 {len(cases)} 条用例")
        print("[OK] 已生成AI概述列: 用例AI概述")
        print("=" * 80)

    except Exception as e:
        print(f"\n[错误] 处理失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
