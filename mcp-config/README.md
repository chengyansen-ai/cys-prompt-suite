# cys-prompt-suite · MCP 客户端接入（Claude Desktop / Cursor）

`cys-prompt-suite` 是一个 stdio MCP server，暴露 **9 个工具**（生成即合规闭环）：

| 工具 | 说明 |
|------|------|
| `generate_portrait_prompt` | 写实人像 9 段式（迁移01） |
| `generate_anime_prompt` | 动漫角色 6 段式（迁移2，支持 80 家族词库） |
| `generate_h3_prompt` | 海螺3 H3 T2VA/Ref2VA 提示词（健康向非口播） |
| `list_prompt_options` | 列出可用 风格/家族/画风/平台/配色 选项 |
| `generate_and_check` | **生成 → 自动合规校验 → 未过则清洗复检** 闭环主入口 |
| `check_prompt` | 纯合规校验 |
| `self_check_list` | 发布前自检清单 |
| `explain_rule` | 解释某条规则 |
| `list_platforms` | 列出支持平台 |

## 前置：已可运行（本地 editable 安装）

```bash
# 已安装进 WorkBuddy 隔离 venv（含 fastmcp 3.4.7）
C:\Users\MSI\.workbuddy\binaries\python\envs\default\Scripts\python.exe -m pip install -e .
# 验证（应返回 9 个工具）
C:\Users\MSI\.workbuddy\binaries\python\envs\default\Scripts\python.exe -m cys_prompt_suite.server
```

## Claude Desktop

把本目录 `claude_desktop_config.json` 的内容**合并**进
`%APPDATA%\Claude\claude_desktop_config.json`（保留已有的其它 server 项），重启 Claude Desktop 即可在工具区看到 `cys-prompt-suite`。

## Cursor

把本目录 `cursor_mcp.json` 的内容保存为项目根目录的 `.cursor/mcp.json`
（或从 Cursor → Settings → MCP → Add new MCP server 粘贴 command/args），
然后刷新 MCP 面板，连接 `cys-prompt-suite`。

## 开源发布后（PyPI 可装时）可改用

```json
{ "mcpServers": { "cys-prompt-suite": { "command": "uvx", "args": ["cys-prompt-suite"] } } }
```

## 两个独立组件（如需单独接入）

| 组件 | 命令 | 工具 |
|------|------|------|
| cys-prompt-mcp | `... -m cys_prompt_mcp.server` | 4（3 生成器 + list_prompt_options） |
| cys-compliance-mcp | `... -m cys_compliance_mcp.server` | 4（check/self_check/explain/list_platforms） |

> 三个 server 共用同一套词库与规则；日常用 `cys-prompt-suite` 一个即可（已内聚前两者全部工具）。
