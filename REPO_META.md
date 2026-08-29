# GitHub 仓库元信息

## Description

中文人像、动漫与 MiniMax H3 提示词 MCP：可复现词库采样、严格参数校验、风险短语复检，以及默认隔离第三方 IP 的商用友好边界。

## About 长介绍

`cys-prompt-suite` 把写实人像 9 段式、动漫角色 6 段式和 MiniMax H3
T2VA/I2VA/FL2VA/L2VA/Ref2VA 提示词封装成 9 个 FastMCP 工具。它支持固定 seed
采样、首末帧时长对齐、结构化风险命中和确定性改写；所有检查结果都明确要求人工终审。

词库公开区分“8,865 个索引条目”和“3,455 个唯一字符串”。47 个第三方游戏 IP
家族默认不展示、不生成，确有授权时才允许显式启用。项目本地运行，无遥测、无 GPU
要求，并提供 pytest、stdio 往返、wheel 数据检查和 Python 3.10–3.12 CI。

## Topics

`mcp` `model-context-protocol` `fastmcp` `prompt-engineering` `chinese-prompts`
`comfyui` `minimax` `h3` `ai-safety` `python`

## 建议置顶信息

- 状态：Beta，不是平台认证的自动审核器。
- 安装：当前 README 只承诺从源码安装；确认发布 PyPI 后再增加 PyPI 文案。
- 商用：MIT 覆盖代码，数据、第三方 IP、模型与输出需分别评估。
