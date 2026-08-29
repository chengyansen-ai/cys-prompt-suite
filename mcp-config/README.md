# MCP 客户端接入

先在一个 Python 3.10+ 环境中安装本项目，再让客户端使用同一个 Python 解释器启动服务。

```bash
python -m pip install -e .
python -m cys_prompt_suite.server
```

本目录的两个 JSON 是通用模板。若客户端找不到包，把 `command` 中的 `python` 换成该
虚拟环境解释器的绝对路径：Windows 通常为 `.venv\Scripts\python.exe`，macOS/Linux
通常为 `.venv/bin/python`。

## Claude Desktop

把 `claude_desktop_config.json` 的 `mcpServers` 项合并进现有配置，不要覆盖其他服务。
保存后完全退出并重新打开客户端。

## Cursor

把 `cursor_mcp.json` 保存为项目的 `.cursor/mcp.json`，或在 MCP 设置中添加相同的
command 和 args。确认客户端环境没有把提示词、密钥或私人素材发送到未审核的服务。

连接后应看到 9 个工具。可先调用 `list_prompt_options`，再调用
`generate_and_check`；`requires_human_review` 始终为 `true`。
