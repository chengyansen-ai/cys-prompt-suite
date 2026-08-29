"""
aggregator.py — cys-prompt-suite 闭环聚合层（「生成即合规」）

把「提示词生成」与「合规校验」串成一个自动闭环：
  1) 调对应生成器产出提示词
  2) 用合规扫描器校验（命中违规项 + 严重度 + 建议）
  3) 若命中阻断规则，替换已命中的精确短语并复检

对外暴露 generate_and_check（套件主工具）及 audit_prompt（纯校验）。
"""
import inspect
import re
import unicodedata

from .compliance import checker
from .compliance.rules import RULESET_INFO
from .prompts import anime, h3, portrait

_REPLACEMENT_GROUPS = {
    "舒展转身": {"扭臀", "顶胯", "扭胯", "蹭腿", "抚摸身体"},
    "自然面向镜头": {"向镜头挑逗", "舔唇", "媚眼", "挑逗"},
    "端庄长款服装": {
        "透视装", "透视露点", "超高开叉", "仅内衣", "比基尼", "露脐", "透视",
        "裸体", "全裸", "半裸", "裸露", "走光", "露点",
    },
    "健康向表达": {"福利", "私密", "深夜", "懂的都懂", "性暗示", "情色", "色情", "淫秽"},
    "中远景全身构图": {"胸特写", "臀特写", "巨乳特写", "臀部特写", "腿根", "裙底", "胸臀特写"},
}
_REPLACEMENTS = {
    term: replacement
    for replacement, terms in _REPLACEMENT_GROUPS.items()
    for term in terms
}


def _sanitize(text: str, report: dict):
    """Rewrite only terms reported by the checker, then normalize punctuation."""
    removed = []
    out = unicodedata.normalize("NFKC", text)
    matched = {
        term
        for violation in report["violations"]
        for term in violation.get("matched", [])
    }
    for term in sorted(matched, key=len, reverse=True):
        if term in out:
            out = out.replace(term, _REPLACEMENTS.get(term, "健康向表达"))
            removed.append(term)
    for replacement in _REPLACEMENT_GROUPS:
        out = re.sub(f"(?:{re.escape(replacement)}){{2,}}", replacement, out)
    out = re.sub(r"([，、；。])\1+", r"\1", out)
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
    if kind not in _KIND_DEFAULT_CT:
        raise ValueError(f"未知 kind：{kind}（支持 portrait/anime/h3）")
    ct = compliance_type or _KIND_DEFAULT_CT[kind]

    # 按目标生成器签名验证透传参数，拼写错误必须显式失败。
    def _bind(fn, kwargs):
        params = inspect.signature(fn).parameters
        unsupported = sorted(set(kwargs) - set(params))
        if unsupported:
            raise ValueError(
                "unsupported generator argument(s): " + ", ".join(unsupported)
            )
        return {k: v for k, v in kwargs.items() if k in params}

    if kind == "portrait":
        gen = portrait.generate_portrait_prompt(seed=seed, **_bind(portrait.generate_portrait_prompt, gen_kwargs))
    elif kind == "anime":
        gen = anime.generate_anime_prompt(seed=seed, **_bind(anime.generate_anime_prompt, gen_kwargs))
    elif kind == "h3":
        gen = h3.generate_h3_prompt(**_bind(h3.generate_h3_prompt, gen_kwargs))

    prompt = gen["prompt"]
    rep = checker.check_text(prompt, content_type=ct, platform=platform)

    safe_prompt = prompt
    sanitized = []
    if not rep["summary"]["passed"]:
        safe_prompt, sanitized = _sanitize(prompt, rep)
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
        "requires_human_review": True,
        "ruleset": RULESET_INFO.copy(),
        "sanitization_status": "rewritten_and_rechecked" if sanitized else "not_needed",
        "self_check": checker.self_check_list(content_type=ct, platform=platform),
        "notes": gen.get("notes", []),
    }


def audit_prompt(prompt: str, compliance_type: str = "anime", platform: str = "douyin") -> dict:
    """纯校验：对已有提示词/文案做合规扫描（不生成）。"""
    return checker.check_text(prompt, content_type=compliance_type, platform=platform)
