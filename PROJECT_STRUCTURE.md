# 项目结构说明

最后更新: 2026-03-03 21:08:09

```

caseHelper/
├── agent_service/          # Agent服务
│   ├── main.py
│   ├── security.py
│   ├── requirements.txt
│   └── ...
├── skills/                 # 核心能力
│   ├── lark-skills/       # 飞书能力
│   ├── sdet-skills/       # SDET平台能力
│   └── case-skills/       # 用例处理能力
├── sandbox/               # 工作区（不提交git）
│   └── workspace/
│       ├── lark_latest_data.json      # 飞书最新数据
│       ├── case_id_mapping.json       # 用例ID映射
│       ├── final_case_report.json     # 最终报告
│       └── ...
├── utils/                 # 工具函数
│   ├── logger.py
│   └── __init__.py
├── config.py              # 配置文件
├── write_case_ids_to_lark.py  # 飞书写入脚本
└── archive/               # 归档目录（已清理的文件）

```
