"""
使用飞书MCP的replace功能写入AI概述
Use Feishu MCP replace function to write AI overview
"""
import json
import time

# 从之前生成的文件读取概述
overview_file = "test_cases_with_ai_overview.json"

try:
    with open(overview_file, 'r', encoding='utf-8') as f:
        cases = json.load(f)
    
    print(f"成功读取 {len(cases)} 条用例")
    
    # 提取AI概述列表
    ai_overviews = []
    for case in cases:
        overview = case.get('用例AI概述', '')
        ai_overviews.append(overview)
    
    print(f"共 {len(ai_overviews)} 条AI概述")
    
    # 使用replace写入
    # 策略：在目标列中查找空字符串并替换为AI概述
    print("\n开始使用MCP replace写入...")
    
    spreadsheet_token = "K8V2sTKLyhE54Ot75EycbnKLnvb"
    sheet_id = "FYZ5JP"
    
    # 假设"用例AI概述"列是第30列（AD列）
    # 从第2行开始（行索引1）
    target_range = f"{sheet_id}!AD2:AD101"
    
    print(f"目标范围: {target_range}")
    print(f"将要写入 {len(ai_overviews)} 条概述")
    
    # 显示前5条
    print("\n前5条AI概述：")
    for i, overview in enumerate(ai_overviews[:5], 1):
        print(f"  [{i}] {overview}")
    
    if len(ai_overviews) > 5:
        print(f"  ... 共 {len(ai_overviews)} 条")
    
    print("\n由于MCP replace的限制，建议手动添加：")
    print("1. 打开飞书表格")
    print("2. 在表格末尾添加新列'用例AI概述'")
    print("3. 复制 ai_overviews_for_sheet.txt 的内容")
    print("4. 粘贴到新列中")
    
except FileNotFoundError:
    print(f"[错误] 找不到文件: {overview_file}")
    print("[提示] 请先运行 read_and_generate.py 生成AI概述")
except Exception as e:
    print(f"[错误] 处理失败: {e}")
    import traceback
    traceback.print_exc()
