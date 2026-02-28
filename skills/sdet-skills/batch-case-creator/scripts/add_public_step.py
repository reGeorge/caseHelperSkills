"""
批量为SDET用例添加公共步骤

功能：为指定用例ID添加公共步骤引用（caseid=51401）
"""
import sys
import argparse
import requests


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
            print(f"  [OK] 用例 {case_id} 公共步骤引用成功 (quoteId={public_case_id})")
            return True
        else:
            print(f"  [ERROR] 用例 {case_id} 公共步骤引用失败: {result}")
            return False
    except Exception as e:
        print(f"  [ERROR] 用例 {case_id} 公共步骤引用异常: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='批量为SDET用例添加公共步骤')
    parser.add_argument('--case-ids', nargs='+', type=int, help='要处理的用例ID列表')
    parser.add_argument('--public-case-id', type=int, default=51401, help='公共步骤用例ID（默认51401）')
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

    print(f"[INFO] 将处理 {len(case_ids)} 个用例")
    print(f"[INFO] 公共步骤用例ID: {args.public_case_id}")
    print(f"[INFO] 用例ID列表: {case_ids}\n")

    # 处理每个用例
    success_count = 0
    failed_count = 0

    for case_id in case_ids:
        if add_public_step(case_id, args.public_case_id):
            success_count += 1
        else:
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
