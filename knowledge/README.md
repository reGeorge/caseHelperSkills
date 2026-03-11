# SDET 轻量级知识库 (Knowledge Base)

## 🎯 核心定位
此目录作为自动化测试平台的**本地标准数据仓库**，保存高度稳定的公共前置步骤、清理步骤以及其他会被反复引入的通用逻辑。
与 `sandbox/`（随意丢弃的临时文件）不同，这里的 JSON 文件是**可读的、受版本控制的**，专门供脚本和 Agent 进行复用。

## ⚙️ 维护与同步流程（单向拉取闭环）
为了确保公共用例始终与线上执行环境保持一致，维护原则是：**“线上平台唯一真相源，本地定期同步持久化”**。

1. **发现与修改**：当接口有变、流程变更时，直接在 SDET 平台对应公共用例上修改并调试通过。
2. **变更配置**：如果新增了公共用例，在 `knowledge/common_cases_manifest.json` 中配置映射关系（"本地别名": 平台用例ID）。
3. **执行同步**：在命令行运行 `python scripts/sync/sync_knowledge_from_platform.py`。
4. **人工审核**：执行 `git diff knowledge`，直观检查变更的字段（例如 URL、参数）。
5. **提交入库**：确认无误后通过 `git commit` 将最新版知识库固定下来。

## 📄 数据规范结构
每个 `xxx.json` 保存一个标准用例（包含核心步骤），结构保证 AI 能够轻松理解和提取：
* `case_id`: 对应平台唯一ID（便于回溯）
* `name`: 用例名称短语
* `description`: 清晰地描述何时使用以及有何依赖
	* 若平台描述为空，同步脚本会初始化为“依赖入参/输出变量/功能说明”的签名式文案
* `case_variables` / `inputs`: 输入变量列表，包含 `name`、`value`、`note`、`note_source`
	* 平台已维护 `note` 时：`note_source = platform`
	* 平台 `note` 为空时：脚本会按变量名规则初始化（如 username/password/token），`note_source = inferred`
	* 无法推断时：`note_source = empty`（建议平台后续补齐备注）
* `sync_metadata.note_initialized_count`: 本次同步中自动初始化备注的数量
* `steps`: JSON Array，描述所有核心 API 请求的关键要素（method, url, query, body, variable_extracts 等）。

## 💡 AI 使用指南
如果你是 Agent，在需要获取“登录步骤”、“开户步骤”供新的用例生成时：
- 请先读取 `knowledge/common_cases_manifest.json` 查看可用名称。
- 再去 `knowledge/common_cases/<name>.json` 提取所需内容直接植入新生成的 Payload 中。