# -*- coding: utf-8 -*-
"""cys-prompt-suite — 中文提示词工程师 + 合规校验 一体化 MCP。

把主人的三个提示词技能（迁移01 写实人像 / 迁移2 动漫角色 / h3 海螺3视频）
与平台合规护栏合成为一个 MCP：生成提示词后自动过合规校验，形成「生成即合规」闭环。
内置 4371 条扩展词库（prompts/data/*.json）。
"""
__version__ = "0.1.0"

from . import aggregator, prompts, compliance  # noqa: F401
