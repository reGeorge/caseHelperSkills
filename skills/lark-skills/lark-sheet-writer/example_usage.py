"""
飞书表格记录写入示例
Lark Sheet Writer Example

演示如何使用lark_sheet_writer写入和编辑飞书表格记录
Demonstrates how to use lark_sheet_writer to write and edit Lark spreadsheet records
"""

from lark_sheet_writer import LarkSheetWriter
import json

def example_write_record():
    """
    示例1: 写入单条记录
    Example 1: Write single record
    """
    print("=" * 60)
    print("示例1: 写入单条记录")
    print("=" * 60)
    
    # 配置应用凭证
    app_id = "cli_a83faf50a228900e"
    app_secret = "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"
    
    # 创建写入器
    writer = LarkSheetWriter(app_id, app_secret)
    
    # 表格信息
    spreadsheet_token = "OXndwZNS9i6hhjk16VwcRai5ngd"
    sheet_id = "9LD59B"  # 新增AD源
    
    # 测试用例记录
    record = {
        "用例名称": "测试用例1",
        "用例描述": "测试功能",
        "预置条件": "无",
        "测试步骤": "1. 步骤1\n2. 步骤2",
        "期望结果": "测试通过",
        "是否支持自动化": "是"
    }
    
    try:
        # 写入记录
        result = writer.write_record(spreadsheet_token, sheet_id, record)
        print("\n写入结果：")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"错误: {e}")


def example_write_records():
    """
    示例2: 批量写入多条记录
    Example 2: Batch write multiple records
    """
    print("\n" + "=" * 60)
    print("示例2: 批量写入多条记录")
    print("=" * 60)
    
    # 配置应用凭证
    app_id = "cli_a83faf50a228900e"
    app_secret = "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"
    
    # 创建写入器
    writer = LarkSheetWriter(app_id, app_secret)
    
    # 表格信息
    spreadsheet_token = "OXndwZNS9i6hhjk16VwcRai5ngd"
    sheet_id = "9LD59B"  # 新增AD源
    
    # 多条测试用例记录
    records = [
        {
            "用例名称": "测试用例2",
            "用例描述": "测试功能2",
            "预置条件": "无",
            "测试步骤": "1. 步骤1\n2. 步骤2",
            "期望结果": "测试通过",
            "是否支持自动化": "是"
        },
        {
            "用例名称": "测试用例3",
            "用例描述": "测试功能3",
            "预置条件": "无",
            "测试步骤": "1. 步骤1\n2. 步骤2",
            "期望结果": "测试通过",
            "是否支持自动化": "否"
        }
    ]
    
    try:
        # 批量写入记录
        result = writer.write_records(spreadsheet_token, sheet_id, records)
        print("\n批量写入结果：")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"错误: {e}")


def example_update_record():
    """
    示例3: 更新现有记录
    Example 3: Update existing record
    """
    print("\n" + "=" * 60)
    print("示例3: 更新现有记录")
    print("=" * 60)
    
    # 配置应用凭证
    app_id = "cli_a83faf50a228900e"
    app_secret = "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"
    
    # 创建写入器
    writer = LarkSheetWriter(app_id, app_secret)
    
    # 表格信息
    spreadsheet_token = "OXndwZNS9i6hhjk16VwcRai5ngd"
    sheet_id = "9LD59B"  # 新增AD源
    
    # 更新条件和数据
    condition = {
        "用例名称": "测试用例1"
    }
    
    update_data = {
        "用例描述": "更新的测试描述",
        "是否支持自动化": "否"
    }
    
    try:
        # 更新记录
        result = writer.update_record(spreadsheet_token, sheet_id, condition, update_data)
        print("\n更新结果：")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"错误: {e}")


def example_import_from_json():
    """
    示例4: 从JSON文件导入数据
    Example 4: Import data from JSON file
    """
    print("\n" + "=" * 60)
    print("示例4: 从JSON文件导入数据")
    print("=" * 60)
    
    # 配置应用凭证
    app_id = "cli_a83faf50a228900e"
    app_secret = "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"
    
    # 创建写入器
    writer = LarkSheetWriter(app_id, app_secret)
    
    # 表格信息
    spreadsheet_token = "OXndwZNS9i6hhjk16VwcRai5ngd"
    sheet_id = "9LD59B"  # 新增AD源
    
    # 测试数据
    test_data = [
        {
            "用例名称": "导入测试用例1",
            "用例描述": "导入测试功能1",
            "预置条件": "无",
            "测试步骤": "1. 步骤1\n2. 步骤2",
            "期望结果": "测试通过",
            "是否支持自动化": "是"
        },
        {
            "用例名称": "导入测试用例2",
            "用例描述": "导入测试功能2",
            "预置条件": "无",
            "测试步骤": "1. 步骤1\n2. 步骤2",
            "期望结果": "测试通过",
            "是否支持自动化": "否"
        }
    ]
    
    # 保存测试数据到JSON文件
    with open('test_import_data.json', 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
    
    try:
        # 从JSON文件导入
        result = writer.import_from_json(
            spreadsheet_token, sheet_id, 'test_import_data.json', clear_existing=False
        )
        print("\n导入结果：")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"错误: {e}")


def example_validate_data():
    """
    示例5: 验证数据格式
    Example 5: Validate data format
    """
    print("\n" + "=" * 60)
    print("示例5: 验证数据格式")
    print("=" * 60)
    
    # 配置应用凭证
    app_id = "cli_a83faf50a228900e"
    app_secret = "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"
    
    # 创建写入器
    writer = LarkSheetWriter(app_id, app_secret)
    
    # 测试数据
    test_data = [
        {
            "用例名称": "测试用例1",
            "用例描述": "测试功能1",
            "预置条件": "无",
            "测试步骤": "1. 步骤1\n2. 步骤2",
            "期望结果": "测试通过",
            "是否支持自动化": "是"
        },
        {
            "用例名称": "测试用例2",
            "用例描述": "测试功能2",
            "预置条件": "无",
            "测试步骤": "",  # 缺少测试步骤
            "期望结果": "测试通过",
            "是否支持自动化": "否"
        }
    ]
    
    # 验证数据
    required_fields = ["用例名称", "测试步骤", "期望结果"]
    validation_result = writer.validate_data(test_data, required_fields)
    
    print("\n验证结果：")
    print(json.dumps(validation_result, ensure_ascii=False, indent=2))


def example_batch_operations():
    """
    示例6: 批量操作演示
    Example 6: Batch operations demonstration
    """
    print("\n" + "=" * 60)
    print("示例6: 批量操作演示")
    print("=" * 60)
    
    # 配置应用凭证
    app_id = "cli_a83faf50a228900e"
    app_secret = "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"
    
    # 创建写入器
    writer = LarkSheetWriter(app_id, app_secret)
    
    # 表格信息
    spreadsheet_token = "OXndwZNS9i6hhjk16VwcRai5ngd"
    sheet_id = "9LD59B"  # 新增AD源
    
    try:
        # 1. 批量写入
        print("\n1. 批量写入测试用例...")
        batch_records = []
        for i in range(4, 7):
            batch_records.append({
                "用例名称": f"批量测试用例{i}",
                "用例描述": f"批量测试功能{i}",
                "预置条件": "无",
                "测试步骤": "1. 步骤1\n2. 步骤2",
                "期望结果": "测试通过",
                "是否支持自动化": "是" if i % 2 == 0 else "否"
            })
        
        write_result = writer.write_records(spreadsheet_token, sheet_id, batch_records)
        print(f"批量写入结果: {write_result['message']}")
        
        # 2. 批量更新
        print("\n2. 批量更新测试用例...")
        update_condition = {"是否支持自动化": "是"}
        update_data = {"期望结果": "自动化测试通过"}
        
        update_result = writer.update_record(spreadsheet_token, sheet_id, update_condition, update_data)
        print(f"批量更新结果: {update_result['message']}")
        
    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    print("飞书表格记录写入示例")
    print("=" * 60)
    
    # 运行示例
    example_write_record()
    # example_write_records()
    # example_update_record()
    # example_import_from_json()
    # example_validate_data()
    # example_batch_operations()
