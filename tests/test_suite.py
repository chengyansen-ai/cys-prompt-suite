# -*- coding: utf-8 -*-
"""cys-prompt-suite 测试：生成器 + 闭环合规校准 + server 冒烟（不依赖 fastmcp 的纯逻辑部分）。"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from cys_prompt_suite import aggregator
from cys_prompt_suite.prompts import portrait, anime, h3


def hdr(t): print("\n" + "=" * 70 + "\n" + t + "\n" + "=" * 70)


# 1) 三个生成器在套件内正常产出
hdr("1) 套件内三生成器产出")
p = portrait.generate_portrait_prompt(composition="full_body", use_wordbank=True, seed=1)
a = anime.generate_anime_prompt(family="敦煌飞天", use_wordbank=True, seed=1)
hh = h3.generate_h3_prompt(mode="Ref2VA", content_type="dance")
assert p["prompt"] and a["prompt"] and hh["prompt"]
print("[portrait 段数]", len(p["sections"]), "| [anime 段数]", len(a["sections"]))
print("[h3 mode]", hh["mode"])

# 2) 闭环：正常生成应直接通过合规（生成即合规）
hdr("2) 闭环校准：正常生成直接通过合规")
r_p = aggregator.generate_and_check(kind="portrait", compliance_type="real", platform="douyin",
                                    composition="full_body", use_wordbank=True, seed=5)
r_a = aggregator.generate_and_check(kind="anime", compliance_type="anime", platform="douyin",
                                    family="赛博朋克", use_wordbank=True, seed=5)
r_h = aggregator.generate_and_check(kind="h3", compliance_type="common", platform="douyin",
                                    mode="Ref2VA", content_type="catwalk")
assert r_p["passed"] is True, f"portrait 应直接通过，实际 violations={r_p['compliance']['violations']}"
assert r_a["passed"] is True, f"anime 应直接通过，实际 violations={r_a['compliance']['violations']}"
assert r_h["passed"] is True, f"h3 应直接通过，实际 violations={r_h['compliance']['violations']}"
print("[portrait] passed=", r_p["passed"], "| [anime] passed=", r_a["passed"], "| [h3] passed=", r_h["passed"])

# 3) 闭环：注入违规词应触发自动清洗并复检通过
hdr("3) 闭环自校正：注入违规词 -> 自动清洗 -> 复检通过")
bad = aggregator.generate_and_check(kind="portrait", compliance_type="real", platform="douyin",
                                    composition="full_body", extra_env="扭臀顶胯向镜头挑逗", seed=9)
assert bad["needs_sanitize"] is True, "应触发清洗"
assert bad["safe_passed"] is True, f"清洗后应通过，实际 safe_violations={bad['safe_compliance']['violations']}"
assert "扭臀" not in bad["safe_prompt"] and "顶胯" not in bad["safe_prompt"]
print("[命中清洗词]", bad["sanitized_terms"])
print("[safe_passed]", bad["safe_passed"])

# 4) 纯校验
hdr("4) 纯校验 audit_prompt")
rep = aggregator.audit_prompt("少女扭臀顶胯向镜头挑逗，穿比基尼，透视露点", "anime", "douyin")
assert rep["summary"]["passed"] is False
print("[block]", rep["summary"]["block_count"])

# 5) 词库规模自检
hdr("5) 词库规模自检")
from cys_prompt_suite.prompts import wordbank
cats = wordbank.get_portrait_categories()
fams = wordbank.list_anime_families()
assert len(cats) >= 40, f"写实分类应≥40，实际 {len(cats)}"
assert len(fams) >= 10, f"动漫家族应≥10，实际 {len(fams)}"
print(f"[写实分类] {len(cats)} 类 | [动漫家族] {len(fams)} 族")

print("\n✅ cys-prompt-suite 测试全部通过（生成+闭环校准）")
