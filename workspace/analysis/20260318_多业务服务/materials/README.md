# 多业务服务 - 物料清单

**创建时间**: 2026-03-18  
**任务**: 多业务服务自动化用例落地

---

## 📂 目录结构

```
20260318_多业务服务/
├── materials/                    # 物料文件夹
│   ├── README.md               # 本文件
│   ├── lark_test_cases.json    # 飞书原始数据(18条)
│   ├── case_design_analysis.md   # Phase 0分析报告
│   ├── case_coverage_report.html # 可视化交互页面
│   ├── create_phase1_public_steps.py    # Phase 1脚本(待创建)
│   ├── create_phase2_directories.py     # Phase 2目录脚本(待创建)
│   ├── create_phase3_cases.py          # Phase 2用例脚本(待创建)
│   └── writeback_case_ids.py          # Phase 3回写脚本(待创建)
└── logs/                        # 执行日志(待创建)
```

---

## 📄 物料文件说明

### 已生成物料

| 文件名 | 类型 | 状态 | 说明 |
|--------|------|------|------|
| lark_test_cases.json | 原始数据 | ✅ 已生成 | 飞书表格读取的18条手工用例数据 |
| 01_step_creation_guide.md | 引导文档 | ✅ 已生成 | 公共步骤创建引导(含API契约) |
| case_design_analysis.md | 分析报告 | ✅ 已生成 | Phase 0详细分析,包含维度拆解、目录设计等 |
| case_coverage_report.html | 可视化页面 | ✅ 已生成 | 交互式HTML报告,4个Tab页面 |

### 待创建物料

| 文件名 | 类型 | 状态 | 说明 |
|--------|------|------|------|
| create_phase1_public_steps.py | Python脚本 | ⏸ 待创建 | Phase 1批量创建6个公共步骤 |
| create_phase2_directories.py | Python脚本 | ⏸ 待创建 | Phase 1批量创建15个目录 |
| create_phase3_cases.py | Python脚本 | ⏸ 待创建 | Phase 2批量创建18条自动化用例 |
| writeback_case_ids.py | Python脚本 | ⏸ 待创建 | Phase 3飞书ID回写脚本 |

---

## 🔄 数据生命周期

### 阶段1: 数据读取与验证
- **数据源**: 飞书表格 Mw7escaVhh92SSts8incmbbUnkc (sheet=hlPkUI)
- **数据量**: 18条手工用例
- **ID范围**: 多业务服务-007 ~ 多业务服务-032
- **验证**: ✅ 用例ID前缀验证通过
- **输出**: lark_test_cases.json

### 阶段2: 数据分析与设计
- **分析方法**: 规则引擎自动分析
- **分析维度**: 6个独立维度(D1-D6)
- **目录设计**: 3层目录结构(根→类别→场景)
- **公共步骤**: 6个推荐步骤
- **输出**: case_design_analysis.md, case_coverage_report.html

### 阶段3: 数据转换与创建 (待执行)
- **输入**: lark_test_cases.json
- **转换**: 手工用例 → 自动化用例
- **创建**: SDET平台公共步骤+目录+用例
- **输出**: 18条自动化用例 + 6个公共步骤 + 15个目录

### 阶段4: 数据回写 (待执行)
- **输入**: SDET平台返回的case_id列表
- **操作**: 飞书API写入
- **回写**: 将case_id写入飞书表格对应列
- **输出**: 飞书表格更新完成

---

## 📊 数据统计

### 用例分类
| 操作类型 | 数量 | 占比 |
|---------|------|------|
| 新增 | 6 | 33.3% |
| 删除 | 3 | 16.7% |
| 编辑 | 1 | 5.6% |
| 状态管理 | 5 | 27.8% |
| 查询 | 3 | 16.7% |

### 服务类型
| 服务类型 | 涉及用例数 |
|---------|-----------|
| 打印机服务 | 6 |
| IP服务 | 3 |
| 邮箱服务 | 3 |
| 未指定/通用 | 6 |

---

## ⚠️ 注意事项

### 关键依赖
1. **飞书API凭证**: 已配置 (app_id + app_secret)
2. **SDET平台API**: 待确认权限和访问方式
3. **公共步骤ID**: 需要在Phase 1创建后获取
4. **目录ID**: 需要在Phase 1创建后获取

### 风险点
1. **无现有公共步骤**: 所有自动化步骤需从零开始
2. **数据准备复杂**: 涉及用户、服务、权限等多重关系
3. **API支持未知**: 需确认SDET平台是否支持相关业务API
4. **手工UI依赖**: 原始用例基于UI操作,转换到API需要重新设计

### 建议方案
根据分析,推荐采用**方案B: API自动化**
- 优点: 执行快、稳定性好、维护成本低
- 缺点: 前期投入大(需建设公共步骤)
- 实施顺序: Phase 1(公共步骤) → Phase 2(目录+用例) → Phase 3(ID回写)

---

## 🚀 下一步行动

### 立即执行
1. **用户审批**: 审核Phase 0分析报告
2. **选择方案**: UI自动化 vs API自动化
3. **确认环境**: SDET平台API访问权限

### Phase 1 准备
1. 创建 `create_phase1_public_steps.py`
2. 创建 `create_phase2_directories.py`
3. 准备测试数据(用户、服务、模板等)

### Phase 2 执行
1. 创建 `create_phase3_cases.py`
2. 批量创建18条自动化用例
3. 记录case_id映射关系

### Phase 3 收尾
1. 创建 `writeback_case_ids.py`
2. 执行飞书ID回写
3. 生成最终报告并归档

---

**最后更新**: 2026-03-18
