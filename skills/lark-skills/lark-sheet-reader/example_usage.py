"""
飞书表格内容读取示例
Lark Sheet Reader Example

演示如何使用lark_sheet_reader读取飞书表格内容
Demonstrates how to use lark_sheet_reader to read Lark spreadsheet content
"""

from lark_sheet_reader import LarkSheetReader
import json

def example_read_from_url():
    """
    示例1: 从URL读取表格内容
    Example 1: Read sheet content from URL
    """
    print("=" * 60)
    print("示例1: 从URL读取表格内容")
    print("=" * 60)
    
    # 配置应用凭证
    app_id = "cli_a83faf50a228900e"
    app_secret = "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"
    
    # 创建读取器
    reader = LarkSheetReader(app_id, app_secret)
    
    # 飞书表格URL
    url = "https://ruijie.feishu.cn/sheets/HxOTs5bwZhz5K4tLHIdcFxY3nSb?sheet=0RTcwI"
    
    try:
        # 读取表格内容
        data = reader.read_from_url(url)
        
        # 输出JSON
        print("\n读取到的测试用例：")
        print(reader.to_json(data))
        
        # 保存到文件
        reader.save_to_file(data, "test_cases.json")
        
    except Exception as e:
        print(f"错误: {e}")


def example_read_specific_sheet():
    """
    示例2: 读取指定工作表
    Example 2: Read specific sheet
    """
    print("\n" + "=" * 60)
    print("示例2: 读取指定工作表")
    print("=" * 60)
    
    # 配置应用凭证
    app_id = "cli_a83faf50a228900e"
    app_secret = "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"
    
    # 创建读取器
    reader = LarkSheetReader(app_id, app_secret)
    
    # 表格token和工作表ID
    spreadsheet_token = "OXndwZNS9i6hhjk16VwcRai5ngd"
    sheet_id = "9LD59B"  # 新增AD源
    
    try:
        # 读取指定工作表
        data = reader.read_sheet(spreadsheet_token, sheet_id)
        
        # 输出JSON
        print(f"\n工作表 '{sheet_id}' 的内容：")
        print(reader.to_json(data))
        
    except Exception as e:
        print(f"错误: {e}")


def example_read_first_sheet():
    """
    示例3: 读取第一个工作表
    Example 3: Read first sheet
    """
    print("\n" + "=" * 60)
    print("示例3: 读取第一个工作表")
    print("=" * 60)
    
    # 配置应用凭证
    app_id = "cli_a83faf50a228900e"
    app_secret = "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"
    
    # 创建读取器
    reader = LarkSheetReader(app_id, app_secret)
    
    # 表格token
    spreadsheet_token = "OXndwZNS9i6hhjk16VwcRai5ngd"
    
    try:
        # 读取第一个工作表（不指定sheet_id）
        data = reader.read_sheet(spreadsheet_token)
        
        # 输出JSON
        print("\n第一个工作表的内容：")
        print(reader.to_json(data))
        
    except Exception as e:
        print(f"错误: {e}")


def example_filter_data():
    """
    示例4: 过滤数据
    Example 4: Filter data
    """
    print("\n" + "=" * 60)
    print("示例4: 过滤数据")
    print("=" * 60)
    
    # 配置应用凭证
    app_id = "cli_a83faf50a228900e"
    app_secret = "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"
    
    # 创建读取器
    reader = LarkSheetReader(app_id, app_secret)
    
    # 表格token和工作表ID
    spreadsheet_token = "OXndwZNS9i6hhjk16VwcRai5ngd"
    sheet_id = "9LD59B"
    
    try:
        # 读取工作表
        data = reader.read_sheet(spreadsheet_token, sheet_id)
        
        # 过滤支持自动化的用例
        auto_cases = [
            case for case in data 
            if case.get("是否支持自动化") == "是"
        ]
        
        print(f"\n支持自动化的测试用例（共{len(auto_cases)}个）：")
        print(reader.to_json(auto_cases))
        
    except Exception as e:
        print(f"错误: {e}")


def example_batch_read():
    """
    示例5: 批量读取多个工作表
    Example 5: Batch read multiple sheets
    """
    print("\n" + "=" * 60)
    print("示例5: 批量读取多个工作表")
    print("=" * 60)
    
    # 配置应用凭证
    app_id = "cli_a83faf50a228900e"
    app_secret = "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"
    
    # 创建读取器
    reader = LarkSheetReader(app_id, app_secret)
    
    # 表格token
    spreadsheet_token = "OXndwZNS9i6hhjk16VwcRai5ngd"
    
    # 要读取的工作表ID列表
    sheet_ids = ["9LD59B", "KFphLl", "9395c9"]
    
    try:
        all_data = {}
        
        for sheet_id in sheet_ids:
            print(f"\n正在读取工作表: {sheet_id}")
            data = reader.read_sheet(spreadsheet_token, sheet_id)
            all_data[sheet_id] = data
            
        # 保存所有数据
        with open("all_test_cases.json", 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n所有工作表数据已保存到: all_test_cases.json")
        
    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    print("飞书表格内容读取示例")
    print("=" * 60)
    
    # 运行示例
    example_read_from_url()
    # example_read_specific_sheet()
    # example_read_first_sheet()
    # example_filter_data()
    # example_batch_read()
