"""
生成飞书表格更新指南

功能：查询SDET用例信息并生成更新指南
"""
import json
import requests


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


def main():
    """主函数"""
    case_ids = list(range(66249, 66275))

    print(f"[INFO] 查询 {len(case_ids)} 个用例信息...\n")

    # 输出表头
    print(f"{'='*150}")
    print(f"{'行号':<6} {'CaseID':<10} {'用例名称':<60} {'用例描述'}")
    print(f"{'='*150}")

    results = []
    for case_id in case_ids:
        case_info = get_sdet_case_info(case_id)
        if case_info:
            case_name = case_info.get('name', '')
            case_desc = case_info.get('note', '')

            case_desc_short = case_desc[:50] + "..." if len(case_desc) > 50 else case_desc

            # 基于之前的查询结果，估算行号
            # 66249->行60, 66250->行61, 66251->行67, 66252->行69
            # 使用映射表
            row_mapping = {
                66249: 60, 66250: 61, 66251: 67, 66252: 69, 66253: 70, 66254: 71,
                66255: 72, 66256: 73, 66257: 74, 66258: 75, 66259: 76, 66260: 77,
                66261: 78, 66262: 79, 66263: 80, 66264: 81, 66265: 82, 66266: 83,
                66267: 84, 66268: 85, 66269: 86, 66270: 97, 66271: 98, 66272: 99,
                66273: 100, 66274: 101
            }

            row_num = row_mapping.get(case_id, 0)

            if row_num:
                print(f"{row_num:<6} {case_id:<10} {case_name:<60} {case_desc_short}")
                results.append({
                    "row": row_num,
                    "caseId": case_id,
                    "caseName": case_name,
                    "caseDesc": case_desc
                })

    print(f"{'='*150}")
    print(f"\n[INFO] 共 {len(results)} 条记录")

    # 保存到JSON文件
    with open("update_mapping.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"[OK] 映射文件已保存: update_mapping.json")

    # 生成更新命令
    print(f"\n[INFO] 飞书表格更新命令示例：\n")
    for r in results[:5]:  # 只显示前5个
        print(f"// 更新行{r['row']}的脚本序号为{r['caseId']}")
        print(f"// 用例名称: {r['caseName']}")
        print(f"// 可使用MCP工具: sheets_v3_spreadsheetSheet_replace")
        print(f"// 或直接在飞书表格中手动编辑 P{r['row']} 单元格\n")


if __name__ == '__main__':
    main()
