# -*- coding: utf-8 -*-
"""
checker.py — 合规扫描逻辑

对输入文本做精确短语匹配（白名单式，避免单字误伤），结合结构化规则库，
输出违规项、严重度、命中词与改写建议，并支持发布自检清单与规则解释。
"""
import re
from .rules import (
    RULES, BANNED_PHRASES, PLATFORMS, SELF_CHECK_COMMON, SELF_CHECK_REAL, SELF_CHECK_ANIME,
)

# content_type -> 适用的规则 scope
_SCOPE_MAP = {
    "real": "real",
    "anime": "anime",
    "common": "common",
    "any": None,  # 全部规则
}


def _norm(text: str) -> str:
    return text.lower()


def check_text(text: str, content_type: str = "anime", platform: str = "douyin") -> dict:
    """扫描文本，返回违规项与建议。

    Args:
        text: 待校验的提示词 / 文案 / 标题
        content_type: "real"(真人写实) / "anime"(二次元) / "common"(通用) / "any"(全规则)
        platform: douyin/kuaishou/shipinhao/xiaohongshu
    """
    scope = _SCOPE_MAP.get(content_type, "anime")
    norm = _norm(text)
    violations = []

    # 1) 精确短语黑名单（通用级，命中即记录）
    for ph in BANNED_PHRASES:
        if ph.lower() in norm:
            violations.append({
                "rule_id": "BANNED",
                "category": "精确短语黑名单",
                "severity": "block",
                "matched": [ph],
                "suggestion": "删除/替换该精确短语，改写为健康向表达",
            })

    # 2) 结构化规则
    for r in RULES:
        if scope is not None and r["scope"] != "common" and r["scope"] != scope:
            continue
        if not r["patterns"]:
            continue  # 无 pattern 的规则（如 AI标识/肖像权）由自检清单覆盖，不靠文本匹配
        hits = [p for p in r["patterns"] if p.lower() in norm]
        if hits:
            violations.append({
                "rule_id": r["id"],
                "category": r["category"],
                "severity": r["severity"],
                "matched": hits,
                "suggestion": r["suggestion"],
            })

    blocks = [v for v in violations if v["severity"] == "block"]
    warns = [v for v in violations if v["severity"] == "warn"]
    pf = PLATFORMS.get(platform, PLATFORMS["douyin"])

    summary = {
        "passed": len(blocks) == 0,
        "block_count": len(blocks),
        "warn_count": len(warns),
        "platform": pf["name"],
        "platform_tolerance": pf["tolerance"],
        "ai_label_required": True,
        "message": (
            "通过：未发现硬性违规，但仍须打AI标识并过自检清单"
            if not blocks else
            f"不通过：发现 {len(blocks)} 项硬性违规（限流/下架/处罚风险），须修改后重检"
        ),
    }
    return {"summary": summary, "violations": violations}


def self_check_list(content_type: str = "anime", platform: str = "douyin") -> dict:
    """返回发布自检清单（通用 + 类型专属 + 平台提示）。"""
    scope = _SCOPE_MAP.get(content_type, "anime")
    items = list(SELF_CHECK_COMMON)
    if scope in (None, "real"):
        items += SELF_CHECK_REAL
    if scope in (None, "anime"):
        items += SELF_CHECK_ANIME
    pf = PLATFORMS.get(platform, PLATFORMS["douyin"])
    return {
        "platform": pf["name"],
        "ai_label": pf["ai_label"],
        "tolerance": pf["tolerance"],
        "checklist": [{"item": it, "done": False} for it in items],
    }


def explain_rule(rule_id: str) -> dict | None:
    """解释某条规则（含黑名单说明）。"""
    if rule_id == "BANNED":
        return {
            "rule_id": "BANNED", "category": "精确短语黑名单", "severity": "block",
            "desc": "命中 banned-words 精确短语（单字'裸'会误伤裸色/裸妆，故用多字精确短语白名单式匹配）",
            "phrases": BANNED_PHRASES,
        }
    for r in RULES:
        if r["id"] == rule_id:
            return r
    return None


def list_platforms() -> dict:
    return PLATFORMS
