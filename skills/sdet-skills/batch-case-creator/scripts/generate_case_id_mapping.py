"""
生成用例ID映射文件

功能：查询SDET用例信息，生成用例名称和用例ID的映射文件
可用于手动更新飞书表格的"脚本序号"列
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
    except:
        return None


def main():
    """主函数"""
    print(f"[INFO] 查询用例信息 66249-66274...")

    case_ids = list(range(66249, 66275))
    mappings = []

    for case_id in case_ids:
        case_info = get_sdet_case_info(case_id)

        if case_info:
            case_name = case_info.get('name', '')
            case_no = case_info.get('caseNo', '')
            mappings.append({
                "用例ID": case_id,
                "用例名称": case_name,
                "用例编号": case_no
            })
            print(f"  {case_id}: {case_name} ({case_no})")

    # 保存为JSON文件
    output_file = "case_id_mapping.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(mappings, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] 映射文件已保存: {output_file}")
    print(f"[INFO] 共 {len(mappings)} 条记录")

    # 保存为CSV文件
    csv_file = "case_id_mapping.csv"
    with open(csv_file, 'w', encoding='utf-8-sig') as f:
        f.write("用例ID,用例名称,用例编号\n")
        for m in mappings:
            f.write(f"{m['用例ID']},{m['用例名称']},{m['用例编号']}\n")

    print(f"[OK] CSV文件已保存: {csv_file}")


if __name__ == '__main__':
    main()
