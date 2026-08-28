# -*- coding: utf-8 -*-
"""
aggregator.py — cys-prompt-suite 闭环聚合层（「生成即合规」）

把「提示词生成」与「合规校验」串成一个自动闭环：
  1) 调对应生成器产出提示词
  2) 用合规扫描器校验（命中违规项 + 严重度 + 建议）
  3) 若未通过，自动清洗命中的精确短语/规则词，复检直到通过或给出安全改写

对外暴露 generate_and_check（套件主工具）及 audit_prompt（纯校验）。
"""
import inspect

from .prompts import portrait, anime, h3
from .compliance import checker
from .compliance.rules import BANNED_PHRASES, RULES


def _sanitize(text: str):
    """闭环自校正：移除命中的精确短语与规则 pattern（仅作兜底，生成器已内置安全约束）。"""
    removed = []
    out = text
    for ph in BANNED_PHRASES:
        if ph and ph in out:
            out = out.replace(ph, "")
            removed.append(ph)
    for r in RULES:
        for p in r.get("patterns", []) or []:
            if p and p in out:
                out = out.replace(p, "")
                removed.append(p)
    return out, removed


# kind -> 默认合规类型（生成器无负向，但仍按内容类型过平台红线）
_KIND_DEFAULT_CT = {"portrait": "real", "anime": "anime", "h3": "common"}


def generate_and_check(
    kind: str = "portrait",
    compliance_type: str | None = None,
    platform: str = "douyin",
    seed: int | None = None,
    **gen_kwargs,
) -> dict:
    """
    生成提示词并自动过合规校验，形成「生成即合规」闭环。

    Args:
        kind: "portrait" / "anime" / "h3"
        compliance_type: 合规内容类型（real/anime/common/any）；缺省按 kind 推断
        platform: douyin / kuaishou / shipinhao / xiaohongshu
        seed: 随机种子（传给生成器，保证可复现）
        **gen_kwargs: 透传给对应生成器的参数（如 family/mode/style/use_wordbank...）

    Returns:
        {kind, prompt, compliance, passed, needs_sanitize, sanitized_terms,
         safe_prompt, safe_compliance, safe_passed, self_check, notes}
    """
    ct = compliance_type or _KIND_DEFAULT_CT.get(kind, "common")

    # 按目标生成器签名过滤透传参数，避免不相关参数引发 TypeError
    def _bind(fn, kwargs):
        params = inspect.signature(fn).parameters
        return {k: v for k, v in kwargs.items() if k in params}

    if kind == "portrait":
        gen = portrait.generate_portrait_prompt(seed=seed, **_bind(portrait.generate_portrait_prompt, gen_kwargs))
    elif kind == "anime":
        gen = anime.generate_anime_prompt(seed=seed, **_bind(anime.generate_anime_prompt, gen_kwargs))
    elif kind == "h3":
        gen = h3.generate_h3_prompt(**_bind(h3.generate_h3_prompt, gen_kwargs))
    else:
        raise ValueError(f"未知 kind：{kind}（支持 portrait/anime/h3）")

    prompt = gen["prompt"]
    rep = checker.check_text(prompt, content_type=ct, platform=platform)

    safe_prompt = prompt
    sanitized = []
    if not rep["summary"]["passed"]:
        safe_prompt, sanitized = _sanitize(prompt)
        rep2 = checker.check_text(safe_prompt, content_type=ct, platform=platform)
    else:
        rep2 = rep

    return {
        "kind": kind,
        "prompt": prompt,
        "compliance": rep,
        "passed": rep["summary"]["passed"],
        "needs_sanitize": not rep["summary"]["passed"],
        "sanitized_terms": sanitized,
        "safe_prompt": safe_prompt,
        "safe_compliance": rep2,
        "safe_passed": rep2["summary"]["passed"],
        "self_check": checker.self_check_list(content_type=ct, platform=platform),
        "notes": gen.get("notes", []),
    }


def audit_prompt(prompt: str, compliance_type: str = "anime", platform: str = "douyin") -> dict:
    """纯校验：对已有提示词/文案做合规扫描（不生成）。"""
    return checker.check_text(prompt, content_type=compliance_type, platform=platform)
