import sys
import os
import json

# 添加路径
sys.path.insert(0, os.path.dirname(__file__))

# 模拟飞书API，直接使用之前读取的数据
from case_ai_overview import CaseAIOverviewGenerator


# 之前读取的测试用例数据（前5条）
test_cases = [
    {
        "用例包名称": None,
        "测试点编号": None,
        "测试点": None,
        "用例标签": None,
        "用例编号": "证书认证-RZ-001",
        "用例名称": "开启证书认证，未学习到本地的证书用户认证成功",
        "用例描述": None,
        "预置条件": "1、新增证书身份源，且UNC上已导入CA根证书和服务器证书\n２、客户端苹果手机导入CA根证书和客户端证书\n3、开启证书用户自动学习\n4、UNC对接AC，且AC配置无线１X认证",
        "测试步骤": "前提：集群\n1、开启证书认证\n2、苹果手机首次证书认证（苹果手机修改为EAP-TLS）",
        "期望结果": "2、苹果手机证书认证成功",
        "测试人员": "季玉凤",
        "备注说明": "PASS",
        "是否支持自动化": "是",
    },
    {
        "用例编号": "证书认证-RZ-002",
        "用例名称": "开启证书认证，已学习到本地的证书用户认证成功",
        "预置条件": "1、新增证书身份源，且UNC上已导入CA根证书和服务器证书\n２、客户端苹果手机导入CA根证书和客户端证书\n3、开启证书用户自动学习\n4、UNC对接AC，且AC配置无线１X认证",
        "测试步骤": "前提：集群\n1、开启证书认证\n2、苹果手机非首次证书认证（苹果手机修改为EAP-TLS）",
        "期望结果": "2、苹果手机证书认证成功",
        "是否支持自动化": "是",
    },
    {
        "用例编号": "证书认证-RZ-003",
        "用例名称": "关闭证书认证，未学习到本地的证书用户认证失败",
        "预置条件": "1、新增证书身份源，且UNC上已导入CA根证书和服务器证书\n２、客户端苹果手机导入CA根证书和客户端证书\n3、开启证书用户自动学习\n4、UNC对接AC，且AC配置无线１X认证",
        "测试步骤": "集群\n1、关闭证书认证\n2、苹果手机首次证书认证",
        "期望结果": "2、苹果手机证书认证失败",
        "是否支持自动化": "否",
    },
    {
        "用例编号": "证书认证-RZ-004",
        "用例名称": "开启证书认证，开启'是否校验服务器证书'，校验成功",
        "预置条件": "1、开启证书认证\n2、UNC对接AC，且AC配置无线１X认证",
        "测试步骤": "前提：集群\n1、开启'是否校验服务器证书'\n2、win10电脑导入客户端证书\n3、win10电脑证书认证",
        "期望结果": "3、win10电脑证书认证成功",
        "是否支持自动化": "是",
    },
    {
        "用例编号": "证书认证-RZ-005",
        "用例名称": "开启证书认证，开启'是否校验服务器证书'，校验失败",
        "预置条件": "1、开启证书认证\n2、UNC对接AC，且AC配置无线１X认证",
        "测试步骤": "前提：集群\n1、开启'是否校验服务器证书'\n2、win10电脑导入客户端证书\n3、win10电脑证书认证",
        "期望结果": "3、win10电脑证书认证失败，提示：校验服务器证书失败",
        "是否支持自动化": "是",
    }
]

# 示例用例（你提供的）
example_case = {
    "用例名称": "开启自动学习-已学习到本地的证书用户被加入黑名单则认证失败",
    "用例描述": "",
    "预置条件": "1、开启证书认证\n2、UNC存在组root\\A\\AA\nroot\\A\nroot\\B\nroot\\BB",
    "测试步骤": "前提：单机环境\n1、安卓手机导入证书，其中证书主题test、证书主题中用户名test1、证书主题中的备用名称test2\n2、开启证书用户自动学习，下拉选择'证书主题'作为用户姓名，新学习用户自动分配用户组：root\\A\\AA\n３、证书认证\n４、将学习到本地的用户test1加入黑名单\n５、再次证书认证",
    "期望结果": "５、证书认证失败，提示用户已被加入黑名单"
}

def test_generator():
    """测试生成器"""
    print("=" * 80)
    print("测试用例AI概述生成器")
    print("=" * 80)
    
    # 测试示例用例
    print("\n【测试示例用例】")
    print(f"用例名称: {example_case['用例名称']}")
    print(f"预置条件: {example_case['预置条件'][:100]}...")
    print(f"测试步骤: {example_case['测试步骤'][:100]}...")
    print(f"期望结果: {example_case['期望结果'][:100]}...")
    print("-" * 80)
    
    # 创建生成器（使用任意app_id和app_secret，因为只是规则生成）
    generator = CaseAIOverviewGenerator(
        app_id="test",
        app_secret="test"
    )
    
    # 生成概述
    overview = generator.generate_overview(example_case)
    print(f"生成的AI概述:")
    print(f"  {overview}")
    print("-" * 80)
    
    # 测试批量生成
    print("\n【测试批量生成】")
    print("=" * 80)
    
    for i, case in enumerate(test_cases, 1):
        overview = generator.generate_overview(case)
        case['用例AI概述'] = overview
        
        print(f"\n用例 {i}:")
        print(f"  名称: {case['用例名称']}")
        print(f"  AI概述: {overview}")
        print("-" * 80)
    
    # 保存结果
    print("\n保存结果到文件...")
    result_cases = test_cases.copy()
    result_cases.insert(0, example_case)  # 添加示例用例
    
    output_file = "test_cases_with_overview.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result_cases, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] 结果已保存到: {output_file}")
    print(f"[OK] 共处理 {len(result_cases)} 条用例")
    print("=" * 80)


if __name__ == "__main__":
    test_generator()
