"""
server.py — cys-prompt-suite 一体化 MCP（FastMCP server）

把「中文提示词生成」与「平台合规校验」合成为一个可被任意 MCP 客户端/Agent 调用的服务，
并内置「生成即合规」闭环工具 generate_and_check。

暴露工具：
  生成类（复用 prompts 子包）
    1. generate_portrait_prompt — 写实人像 9 段式（词库 2646 条 / 55 分类）
    2. generate_anime_prompt    — 动漫角色 6 段式（80 家族五维池 + 全局池）
    3. generate_h3_prompt       — 海螺3 视频提示词
  校验类（复用 compliance 子包）
    4. check_prompt             — 合规扫描
    5. self_check_list          — 发布自检清单
    6. explain_rule             — 规则解释
    7. list_platforms           — 四平台差异
  闭环类（aggregator）
    8. generate_and_check       — 生成并自动过合规校验（生成即合规）
    9. list_prompt_options      — 列出可用选项（含词库分类/家族清单）

运行：python -m cys_prompt_suite.server   （stdio 传输）
"""
from fastmcp import FastMCP

from . import aggregator as _agg
from .compliance import checker as _checker
from .prompts import anime as _anime
from .prompts import h3 as _h3
from .prompts import portrait as _portrait
from .prompts import prompts_data
from .prompts import wordbank as _wordbank

mcp = FastMCP("cys-prompt-suite")


# ============================ 生成类 ============================

@mcp.tool()
def generate_portrait_prompt(
    character: str = "20岁成年亚洲女性",
    composition: str = "full_body",
    motion_migration: bool = False,
    style: str | None = None,
    scene: str | None = None,
    shoes: str | None = None,
    use_lora: bool = False,
    lora_name: str | None = None,
    lora_strength: float = 0.6,
    extra_clothing: str | None = None,
    extra_env: str | None = None,
    use_wordbank: bool = False,
    palette: str | None = None,
    seed: int | None = None,
) -> dict:
    """生成写实人像提示词（迁移01 中文 9 段式）。

    适用于 ComfyUI / Krea2 写实人像出图。默认无负向、CFG=1.0；背景绚丽；
    动作迁移版套 T-pose 硬约束（头≤25%/腿≥65%/鞋履≥6%）。
    use_wordbank=True 时从 2646 条扩展词库采样服装/鞋履/背景/配色/饰品。
    """
    return _portrait.generate_portrait_prompt(
        character=character, composition=composition, motion_migration=motion_migration,
        style=style, scene=scene, shoes=shoes, use_lora=use_lora, lora_name=lora_name,
        lora_strength=lora_strength, extra_clothing=extra_clothing, extra_env=extra_env,
        use_wordbank=use_wordbank, palette=palette, seed=seed,
    )


@mcp.tool()
def generate_anime_prompt(
    family: str = "国风仙侠",
    mode: str = "showcase",
    art_style: str = "cel_shading",
    character: str | None = None,
    outfit: str | None = None,
    shoes: str | None = None,
    background: str | None = None,
    use_lora: bool = False,
    lora_name: str | None = None,
    lora_strength: float = 0.6,
    use_wordbank: bool = True,
    seed: int | None = None,
    allow_third_party_ip: bool = False,
) -> dict:
    """生成动漫/二次元角色提示词（迁移2 中文 6 段式 + Danbooru tag）。

    默认成年(18)、长款覆盖端庄、领口双清、背景绚丽无移动物。
    use_wordbank=True 时按家族从 80 家族与全局池采样服装/背景/鞋履/饰品/配色。
    """
    return _anime.generate_anime_prompt(
        family=family, mode=mode, art_style=art_style, character=character,
        outfit=outfit, shoes=shoes, background=background, use_lora=use_lora,
        lora_name=lora_name, lora_strength=lora_strength,
        use_wordbank=use_wordbank, seed=seed,
        allow_third_party_ip=allow_third_party_ip,
    )


@mcp.tool()
def generate_h3_prompt(
    mode: str = "Ref2VA",
    integrated_multimodal_description: str | None = None,
    overall_soundscape: str | None = None,
    non_diegetic_music: str | None = None,
    first_frame_desc: str | None = None,
    last_frame_desc: str | None = None,
    duration_seconds: float | None = None,
    content_type: str = "dance",
    character: str | None = None,
    scene1: str | None = None,
    scene2: str | None = None,
    outfit1: str | None = None,
    outfit2: str | None = None,
    retention_note: str | None = None,
    subject_definitions: str | None = None,
    summary: str | None = None,
    retention_analysis: str | None = None,
    detailed_description: str | None = None,
) -> dict:
    """生成海螺3 (H3 / MiniMax) 视频提示词（T2VA/I2VA/FL2VA/L2VA/Ref2VA）。

    范围红线：只产出 舞蹈/转场/展示/走秀 等健康向非口播内容。
    """
    return _h3.generate_h3_prompt(
        mode=mode,
        integrated_multimodal_description=integrated_multimodal_description,
        overall_soundscape=overall_soundscape,
        non_diegetic_music=non_diegetic_music,
        first_frame_desc=first_frame_desc,
        last_frame_desc=last_frame_desc,
        duration_seconds=duration_seconds,
        content_type=content_type,
        character=character,
        scene1=scene1, scene2=scene2,
        outfit1=outfit1, outfit2=outfit2,
        retention_note=retention_note,
        subject_definitions=subject_definitions,
        summary=summary,
        retention_analysis=retention_analysis,
        detailed_description=detailed_description,
    )


@mcp.tool()
def list_prompt_options() -> dict:
    """列出可用选项：写实风格预设、动漫家族、动漫画风、H3 内容类型。"""
    return {
        "portrait_styles": list(prompts_data.STYLE_PRESETS.keys()),
        "anime_families": {k: v["note"] for k, v in prompts_data.ANIME_FAMILIES.items()},
        "anime_art_styles": list(prompts_data.ANIME_ART_STYLES.keys()),
        "h3_content_types": list(prompts_data.H3_CONTENT_TYPES.keys()),
        "h3_modes": ["T2VA", "I2VA", "FL2VA", "L2VA", "Ref2VA"],
        "wordbank_portrait_categories": _wordbank.get_portrait_categories(),
        "wordbank_anime_families": _wordbank.list_anime_families(),
        "third_party_ip_families": sorted(_wordbank.THIRD_PARTY_IP_FAMILIES),
        "wordbank_stats": _wordbank.get_wordbank_stats(),
    }


# ============================ 校验类 ============================

@mcp.tool()
def check_prompt(prompt: str, content_type: str = "anime", platform: str = "douyin") -> dict:
    """校验提示词/文案是否触碰平台合规红线（精确短语 + 结构化规则）。"""
    return _checker.check_text(prompt, content_type=content_type, platform=platform)


@mcp.tool()
def self_check_list(content_type: str = "anime", platform: str = "douyin") -> dict:
    """返回发布前自检清单（通用 + 类型专属 + 平台提示）。"""
    return _checker.self_check_list(content_type=content_type, platform=platform)


@mcp.tool()
def explain_rule(rule_id: str) -> dict:
    """解释某条规则或黑名单（如 BANNED / C-SEXACT / A-LOLI / R-PORTRAIT-RIGHT）。"""
    r = _checker.explain_rule(rule_id)
    if r is None:
        return {"error": f"未找到规则 {rule_id}"}
    return r


@mcp.tool()
def list_platforms() -> dict:
    """列出支持的发布渠道及需要复核的 AI 标识提醒。"""
    return _checker.list_platforms()


# ============================ 闭环类 ============================

@mcp.tool()
def generate_and_check(
    kind: str = "portrait",
    compliance_type: str | None = None,
    platform: str = "douyin",
    seed: int | None = None,
    use_wordbank: bool = True,
    # —— 生成器常用参数（按 kind 透传，None 不传）——
    character: str | None = None,
    composition: str | None = None,
    motion_migration: bool = False,
    style: str | None = None,
    scene: str | None = None,
    shoes: str | None = None,
    use_lora: bool = False,
    lora_name: str | None = None,
    lora_strength: float = 0.6,
    extra_clothing: str | None = None,
    extra_env: str | None = None,
    palette: str | None = None,
    family: str | None = None,
    mode: str | None = None,
    art_style: str | None = None,
    outfit: str | None = None,
    background: str | None = None,
    allow_third_party_ip: bool = False,
    content_type: str | None = None,
    h3_mode: str | None = None,
    duration_seconds: float | None = None,
    integrated_multimodal_description: str | None = None,
    overall_soundscape: str | None = None,
    non_diegetic_music: str | None = None,
    first_frame_desc: str | None = None,
    last_frame_desc: str | None = None,
    scene1: str | None = None,
    scene2: str | None = None,
    outfit1: str | None = None,
    outfit2: str | None = None,
    retention_note: str | None = None,
    subject_definitions: str | None = None,
    summary: str | None = None,
    retention_analysis: str | None = None,
    detailed_description: str | None = None,
) -> dict:
    """生成提示词并自动过合规校验，形成「生成即合规」闭环。

    先调对应生成器产出提示词，再用合规扫描器校验；若命中硬性违规，
    自动清洗命中的精确短语/规则词并复检，返回安全改写后的提示词与自检清单。

    Args:
        kind: "portrait" / "anime" / "h3"
        compliance_type: 合规内容类型（real/anime/common/any）；缺省按 kind 推断
        platform: douyin / kuaishou / shipinhao / xiaohongshu
        seed: 随机种子（保证可复现）
        use_wordbank: 是否启用扩展词库采样
        character/composition/motion_migration/style/scene/shoes/use_lora/...: 写实生成器参数
        family/mode/art_style/outfit/background: 动漫生成器参数
        content_type/h3_mode: H3 生成器参数
    Returns:
        {kind, prompt, compliance, passed, needs_sanitize, sanitized_terms,
         safe_prompt, safe_compliance, safe_passed, self_check, notes}
    """
    common = {
        "character": character,
        "use_lora": use_lora,
        "lora_name": lora_name,
        "lora_strength": lora_strength,
        "use_wordbank": use_wordbank,
    }
    if kind == "portrait":
        gen = {
            **common,
            "composition": composition,
            "motion_migration": motion_migration,
            "style": style,
            "scene": scene,
            "shoes": shoes,
            "extra_clothing": extra_clothing,
            "extra_env": extra_env,
            "palette": palette,
        }
    elif kind == "anime":
        gen = {
            **common,
            "family": family,
            "mode": mode,
            "art_style": art_style,
            "outfit": outfit,
            "shoes": shoes,
            "background": background,
            "allow_third_party_ip": allow_third_party_ip,
        }
    elif kind == "h3":
        gen = {
            "mode": h3_mode,
            "content_type": content_type,
            "character": character,
            "duration_seconds": duration_seconds,
            "integrated_multimodal_description": integrated_multimodal_description,
            "overall_soundscape": overall_soundscape,
            "non_diegetic_music": non_diegetic_music,
            "first_frame_desc": first_frame_desc,
            "last_frame_desc": last_frame_desc,
            "scene1": scene1,
            "scene2": scene2,
            "outfit1": outfit1,
            "outfit2": outfit2,
            "retention_note": retention_note,
            "subject_definitions": subject_definitions,
            "summary": summary,
            "retention_analysis": retention_analysis,
            "detailed_description": detailed_description,
        }
    else:
        gen = {}
    gen = {key: value for key, value in gen.items() if value is not None}
    return _agg.generate_and_check(
        kind=kind, compliance_type=compliance_type, platform=platform,
        seed=seed, **gen,
    )


def main():
    mcp.run()


if __name__ == "__main__":
    main()
