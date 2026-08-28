# -*- coding: utf-8 -*-
"""cys-prompt-mcp — 中文提示词工程师 MCP 包。

封装主人三个提示词技能（迁移01 写实人像 / 迁移2 动漫角色 / h3 海螺3视频）
为可被任意 MCP 客户端/Agent 调用的工具，并内置 4371 条扩展词库（data/*.json）。
"""
__version__ = "0.2.0"

from . import portrait, anime, h3, prompts_data, wordbank  # noqa: F401
