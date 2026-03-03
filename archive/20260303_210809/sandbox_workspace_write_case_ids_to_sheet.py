"""
逐个单元格写入Case ID到飞书表格
Write case ID to Lark spreadsheet cell by cell
"""
import sys
import requests
import json


def get_access_token(app_id: str, app_secret: str) -> str:
    """获取飞书access token"""
    token_url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal/"
    headers = {"Content-Type": "application/json"}
    data = {"app_id": app_id, "app_secret": app_secret}

    response = requests.post(token_url, headers=headers, json=data)
    response.raise_for_status()
    result = response.json()
    return result.get("app_access_token")


def read_sheet_data(spreadsheet_token: str, sheet_id: str, access_token: str) -> tuple[list[str], list[list[str]]]:
    """读取飞书表格数据，返回 (headers, data)"""
    read_url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/{sheet_id}"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(read_url, headers=headers)
    response.raise_for_status()
    result = response.json()
    values = result.get("data", {}).get("valueRange", {}).get("values", [])

    if not values:
        return [], []

    headers = values[0]
    data = values[1:] if len(values) > 1 else []
    return headers, data


def col_index_to_letter(col: int) -> str:
    """将列索引转换为列字母（0->A, 1->B, ..., 25->Z, 26->AA）"""
    result = ""
    while col >= 0:
        result = chr(65 + (col % 26)) + result
        col = col // 26 - 1
    return result


def write_single_cell(spreadsheet_token: str, sheet_id: str, access_token: str,
                      row_index: int, col_index: int, value: str) -> bool:
    """
    逐个单元格写入（使用正确的飞书API格式）

    Args:
        spreadsheet_token: 表格token
        sheet_id: 工作表ID
        access_token: 访问令牌
        row_index: 行索引（从0开始，0是表头行）
        col_index: 列索引（从0开始）
        value: 要写入的值

    Returns:
        bool: 是否成功
    """
    col_letter = col_index_to_letter(col_index)
    row_num = row_index + 1  # Excel行号从1开始
    # range格式：sheet_id!起始单元格:结束单元格（单个单元格也要写成范围）
    range_str = f"{sheet_id}!{col_letter}{row_num}:{col_letter}{row_num}"

    # 使用正确的URL格式
    url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # 使用正确的请求体格式
    data = {
        "valueRange": {
            "range": range_str,
            "values": [[value]]
        }
    }

    try:
        # 使用PUT方法（根据飞书文档）
        response = requests.put(url, headers=headers, json=data)

        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                print(f"  [OK] 写入成功: {col_letter}{row_num} = {value}")
                return True
            else:
                print(f"  [ERROR] 写入失败: {col_letter}{row_num}, 错误: {result.get('msg')}")
                return False
        else:
            print(f"  [ERROR] HTTP错误: {response.status_code}, 响应: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"  [ERROR] 写入异常: {col_letter}{row_num}, 异常: {e}")
        return False


def main():
    """主函数"""
    # 配置
    spreadsheet_token = "PLB6sIEHjhVHRAtzXzZcRrw8nwl"
    sheet_id = "YwlyHq"
    app_id = "cli_a83faf50a228900e"
    app_secret = "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"

    # Case ID映射（Excel行号 -> Case ID）
    # 根据任务描述：
    # 第4条用例（Excel行号6）-> 66330
    # 第6条用例（Excel行号8）-> 66331
    # 第13条用例（Excel行号15）-> 66332
    # 第14条用例（Excel行号16）-> 66333
    # 第21条用例（Excel行号23）-> 66334
    # 第23条用例（Excel行号25）-> 66335
    case_id_mapping: dict[int, int] = {
        6: 66330,
        8: 66331,
        15: 66332,
        16: 66333,
        23: 66334,
        25: 66335,
    }

    print("=" * 80)
    print("逐个单元格写入Case ID到飞书表格")
    print("=" * 80)

    # 获取access token
    print("\n[INFO] 获取飞书access token...")
    access_token = get_access_token(app_id, app_secret)
    print(f"[OK] Token获取成功")

    # 读取表格数据
    print(f"\n[INFO] 读取表格数据...")
    headers, data = read_sheet_data(spreadsheet_token, sheet_id, access_token)
    print(f"[OK] 读取到 {len(data)} 行数据")
    print(f"[INFO] 表头字段数: {len(headers)}")

    # 查找列索引
    try:
        script_id_col = headers.index("脚本序号")
        case_name_col = headers.index("用例名称")
        print(f"[INFO] 脚本序号列索引: {script_id_col} ({col_index_to_letter(script_id_col)}列)")
        print(f"[INFO] 用例名称列索引: {case_name_col}")
    except ValueError as e:
        print(f"[ERROR] 未找到必要字段: {e}")
        print(f"[INFO] 可用表头: {headers[:5]}...")  # 只显示前5个
        return {"success": False, "error": str(e)}

    # 统计结果
    results = []

    # 逐个写入
    print(f"\n[INFO] 开始写入 {len(case_id_mapping)} 个Case ID...")
    print("-" * 80)

    for row_num, case_id in case_id_mapping.items():
        # row_num是Excel行号（从1开始），转换为索引（从0开始）
        row_index = row_num - 1

        # 检查行是否在数据范围内
        if row_index >= len(data):
            print(f"  [WARNING] 行号 {row_num} 超出数据范围")
            results.append({
                "row_num": row_num,
                "case_id": case_id,
                "success": False,
                "message": "行号超出数据范围"
            })
            continue

        # 显示用例名称（如果有）
        row_data = data[row_index]
        case_name = row_data[case_name_col] if case_name_col < len(row_data) else ""

        print(f"\n写入行 {row_num} (Case ID: {case_id})")
        if case_name:
            print(f"  用例名称: {case_name[:50]}...")

        # 写入Case ID
        success = write_single_cell(spreadsheet_token, sheet_id, access_token,
                                    row_index, script_id_col, str(case_id))

        results.append({
            "row_num": row_num,
            "case_id": case_id,
            "success": success,
            "message": "写入成功" if success else "写入失败"
        })

    # 输出统计结果
    success_count = sum(1 for r in results if r["success"])
    error_count = len(results) - success_count

    print("\n" + "=" * 80)
    print("写入完成!")
    print("=" * 80)
    print(f"成功: {success_count} 行")
    print(f"失败: {error_count} 行")
    print(f"总计: {len(case_id_mapping)} 行")
    print("=" * 80)

    # 保存结果到文件
    output_file = r'd:\Code\caseHelper\sandbox\workspace\write_case_ids_result.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "total": len(case_id_mapping),
            "success_count": success_count,
            "error_count": error_count,
            "results": results
        }, f, ensure_ascii=False, indent=2)

    print(f"\n结果已保存到: {output_file}")

    return {
        "success": True,
        "success_count": success_count,
        "error_count": error_count,
        "total": len(case_id_mapping)
    }


if __name__ == "__main__":
    main()
