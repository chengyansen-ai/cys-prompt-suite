# -*- coding: utf-8 -*-
"""cys-compliance-mcp — AI 内容合规校验 MCP 包。

把主人的平台合规知识（平台合规通用 + 二次元内容边界 + 真人边界 + banned-words）
封装为可被任意 MCP 客户端/Agent 调用的合规护栏。
"""
__version__ = "0.1.0"

from . import checker, rules  # noqa: F401
