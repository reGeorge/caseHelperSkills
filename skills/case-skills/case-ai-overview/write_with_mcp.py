"""
使用飞书MCP生成用例AI概述并写回表格
Use Feishu MCP to generate test case AI overview and write back to spreadsheet
"""
import json
import re

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
        if overview:
            ai_overviews.append(overview)
    
    print(f"共 {len(ai_overviews)} 条AI概述")
    
    # 显示前5条
    print("\n前5条AI概述：")
    for i, overview in enumerate(ai_overviews[:5], 1):
        print(f"  [{i}] {overview}")
    
    if len(ai_overviews) > 5:
        print(f"  ... 共 {len(ai_overviews)} 条")
    
    # 保存为文本格式（便于复制到表格）
    output_file = "ai_overviews_for_sheet.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("用例AI概述\n")
        for overview in ai_overviews:
            f.write(f"{overview}\n")
    
    print(f"\n[OK] AI概述已保存到: {output_file}")
    print("[提示] 请复制文件内容并粘贴到飞书表格的'用例AI概述'列中")
    
except FileNotFoundError:
    print(f"[错误] 找不到文件: {overview_file}")
    print("[提示] 请先运行 read_and_generate.py 生成AI概述")
except Exception as e:
    print(f"[错误] 处理失败: {e}")
    import traceback
    traceback.print_exc()
