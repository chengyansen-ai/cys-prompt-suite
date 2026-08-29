"""
checker.py — 合规扫描逻辑

对输入文本做精确短语匹配（白名单式，避免单字误伤），结合结构化规则库，
输出违规项、严重度、命中词与改写建议，并支持发布自检清单与规则解释。
"""
import unicodedata

from ..validation import validate_choice, validate_optional_text
from .rules import (
    BANNED_PHRASES,
    PLATFORMS,
    RULES,
    RULESET_INFO,
    SELF_CHECK_ANIME,
    SELF_CHECK_COMMON,
    SELF_CHECK_REAL,
)

# content_type -> 适用的规则 scope
_SCOPE_MAP = {
    "real": "real",
    "anime": "anime",
    "common": "common",
    "any": None,  # 全部规则
}


def _norm(text: str) -> str:
    return unicodedata.normalize("NFKC", text).casefold()


def _validate_context(content_type: str, platform: str) -> None:
    validate_choice("content_type", content_type, _SCOPE_MAP)
    validate_choice("platform", platform, PLATFORMS)


def check_text(text: str, content_type: str = "anime", platform: str = "douyin") -> dict:
    """扫描文本，返回违规项与建议。

    Args:
        text: 待校验的提示词 / 文案 / 标题
        content_type: "real"(真人写实) / "anime"(二次元) / "common"(通用) / "any"(全规则)
        platform: douyin/kuaishou/shipinhao/xiaohongshu
    """
    _validate_context(content_type, platform)
    if text is None:
        raise ValueError("text must be a string")
    validate_optional_text("text", text)
    scope = _SCOPE_MAP[content_type]
    norm = _norm(text)
    violations = []
    claimed_terms = set()

    # 1) 结构化规则优先，确保一个精确命中词只归属一条规则。
    for r in RULES:
        if scope is not None and r["scope"] != "common" and r["scope"] != scope:
            continue
        if not r["patterns"]:
            continue  # 无 pattern 的规则（如 AI标识/肖像权）由自检清单覆盖，不靠文本匹配
        hits = [
            p for p in r["patterns"]
            if _norm(p) in norm and _norm(p) not in claimed_terms
        ]
        if hits:
            claimed_terms.update(_norm(p) for p in hits)
            violations.append({
                "rule_id": r["id"],
                "category": r["category"],
                "severity": r["severity"],
                "matched": hits,
                "suggestion": r["suggestion"],
            })

    # 2) 黑名单仅补充尚未被结构化规则认领的精确短语，并合并为一项。
    banned_hits = [
        phrase for phrase in BANNED_PHRASES
        if _norm(phrase) in norm and _norm(phrase) not in claimed_terms
    ]
    if banned_hits:
        claimed_terms.update(_norm(p) for p in banned_hits)
        violations.append({
            "rule_id": "BANNED",
            "category": "精确短语黑名单",
            "severity": "block",
            "matched": banned_hits,
            "suggestion": "替换为健康、客观且不聚焦敏感身体部位的表达",
        })

    blocks = [v for v in violations if v["severity"] == "block"]
    warns = [v for v in violations if v["severity"] == "warn"]
    pf = PLATFORMS[platform]

    summary = {
        "passed": len(blocks) == 0,
        "block_count": len(blocks),
        "warn_count": len(warns),
        "platform": pf["name"],
        "ai_label_required": True,
        "requires_human_review": True,
        "message": (
            "启发式扫描未命中阻断规则；仍须人工复核权利、画面、语境与 AI 标识要求"
            if not blocks else
            f"发现 {len(blocks)} 项预设阻断规则命中；须修改、复检并人工终审"
        ),
    }
    return {"summary": summary, "violations": violations, "ruleset": RULESET_INFO.copy()}


def self_check_list(content_type: str = "anime", platform: str = "douyin") -> dict:
    """返回发布自检清单（通用 + 类型专属 + 平台提示）。"""
    _validate_context(content_type, platform)
    scope = _SCOPE_MAP[content_type]
    items = list(SELF_CHECK_COMMON)
    if scope in (None, "real"):
        items += SELF_CHECK_REAL
    if scope in (None, "anime"):
        items += SELF_CHECK_ANIME
    pf = PLATFORMS[platform]
    return {
        "platform": pf["name"],
        "ai_label": pf["ai_label"],
        "ruleset": RULESET_INFO.copy(),
        "requires_human_review": True,
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
    return {**PLATFORMS, "_ruleset": RULESET_INFO.copy()}
