"""
anime.py — 迁移2 动漫角色 6 段式提示词生成器

输出规则（严守技能「交付格式与背景铁律」+ 统一安全铁律）：
- 只输出 AI 可识别的提示词正文（中文分段 + Danbooru 英文 tag），不含元信息。
- 背景必须「绚丽场景」，不单调。
- CFG=1.0 无负向；安全只靠正向约束。
- 统一安全铁律：长裙覆盖、领口双清（U形领/坦领/V领/挂脖/露肩/抹胸）、背景无移动物。
- 范围红线：不做幼态+暴露/挑逗；默认成年(18)、健康向。
- 扩展词库（data/anime_lib.json，80 家族五维池 + 全局扩展池）：
  use_wordbank=True 时按家族采样服装/背景/鞋履/饰品/配色（池空回退全局池），产出家族一致且更丰富。
"""
from ..validation import validate_choice, validate_lora_strength, validate_optional_text
from .prompts_data import (
    ANIME_ART_STYLES,
    ANIME_DEFAULT_FACE,
    ANIME_FAMILIES,
    ANIME_QUALITY_HEAD,
)
from .wordbank import (
    ANIME_LIB_FAMILIES,
    is_third_party_ip_family,
    sample_anime,
    sample_anime_colors,
    sample_anime_global,
)

# 领口风险词（从汉服组合层与词池双清，v2.4 定版）
NECKLINE_RISK = ["U形领", "一字领", "袒领", "坦领", "V领", "挂脖", "露肩", "抹胸",
                 "露脐", "开衩", "紧身", "泳装", "短裙", "绝对领域", "LOLITA", "吊带"]

# 软覆盖约束（v2.4 英文骨架，绝不用 floor-reaching/long flowing/ceremonial 之类诱发露腿）
SOFT_COVERAGE_EN = "elegant and graceful long traditional garment, modest, dignified, tasteful full coverage"

# 绚丽静态背景池（按形制绑定，剔除移动物/动物；作为无词库池家族的兜底）
SAFE_BG = {
    "国风仙侠": "悬浮仙山云海，层云如浪，远处琼楼玉宇在霞光中若隐若现，灵气光粒漂浮",
    "国漫漫剧风": "古典园林仙境，亭台水榭，桃花纷落，暖光透过花枝",
    "东方龙女": "碧海龙宫，珊瑚玉柱，珍珠光晕，静水倒影无波澜",
    "敦煌飞天": "敦煌穹顶藻井，流光壁画，星河环绕，祥云静止",
    "现代都市": "霓虹都市天际线，冷蓝数据空间，玻璃幕墙折射光带",
    "赛博朋克": "赛博明制殿宇，全息汉纹，冷紫数据流，无活物",
    "九尾狐妖": "青丘狐域，红绫悬空，月下竹林，静谧狐火",
    "武侠剑修": "青山松风，古寺石阶，远山如黛，云雾缭绕无飞鸟",
    "朱雀神女": "赤金星坛，星河天阶，凰羽纹石柱，静谧神光",
    "暗黑魔女": "暗月魔殿，玄色晶柱，幽蓝符文，静止夜雾",
    "花仙精灵": "花神之境，百花悬浮，星屑草坪，柔光弥漫",
}


def _clean_neckline(text: str, notes: list):
    """剔除领口/暴露风险词（按 逗号/顿号 切分，移除含风险词的整段）。"""
    import re
    toks = re.split(r"[，、]", text)
    cleaned = []
    for t in toks:
        t = t.strip()
        if not t:
            continue
        hit = [w for w in NECKLINE_RISK if w in t]
        if hit:
            notes.append(f"已剔除领口/暴露风险词「{hit[0]}」")
            continue
        cleaned.append(t)
    return "、".join(cleaned)


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
    """
    生成迁移2 动漫角色 6 段式提示词。

    参数
    ----
    family       : 家族（见 ANIME_FAMILIES / 词库 14 家族之一）
    mode         : "showcase"（纯展示版）或 "motion_migration"（动作迁移版 T-pose）
    art_style    : 画风签名键（见 ANIME_ART_STYLES）
    character    : 自定义段1 人设（默认明确为成年角色）
    outfit       : 自定义段4 服装（中文形制，默认长裙覆盖）
    shoes        : 自定义鞋履（默认绣花鞋/云头履，底部完整）
    background   : 自定义段6 背景（默认按家族绑定绚丽静态背景）
    use_lora     : 是否叠加角色 LoRA
    lora_name    : LoRA 触发词
    lora_strength: 建议权重（默认 0.6）
    use_wordbank : True 时按家族采样服装/背景/鞋履/饰品/配色（池空回退全局池）
    seed         : 随机种子（保证可复现；仅 use_wordbank 时生效）

    返回
    ----
    {"prompt": str, "sections": dict, "notes": list}
    """
    validate_choice("family", family, ANIME_LIB_FAMILIES)
    validate_choice("mode", mode, {"showcase", "motion_migration"})
    validate_choice("art_style", art_style, ANIME_ART_STYLES)
    validate_lora_strength(lora_strength)
    for field_name, value in {
        "character": character,
        "outfit": outfit,
        "shoes": shoes,
        "background": background,
        "lora_name": lora_name,
    }.items():
        validate_optional_text(field_name, value)
    if is_third_party_ip_family(family) and not allow_third_party_ip:
        raise ValueError(
            f"family '{family}' is a third-party IP family; set allow_third_party_ip=True "
            "only after confirming your authorization"
        )

    notes = []
    fam = ANIME_FAMILIES.get(family, {"head": "", "note": "扩展词库家族"})
    head_feat = fam["head"]
    is_migration = mode == "motion_migration"
    if is_third_party_ip_family(family):
        notes.append("third-party IP family enabled explicitly; commercial authorization is the caller's responsibility")

    # —— 词库采样（家族五维池，池空回退全局扩展池）——
    wb_outfit = wb_bg = wb_shoes = wb_acc = wb_color = None
    if use_wordbank:
        po = sample_anime(family, "outfit", 2, seed=seed) or sample_anime_global("outfit", 2, seed=seed)
        wb_outfit = "、".join(po) if po else None
        pb = sample_anime(family, "bg", 1, seed=seed) or sample_anime_global("bg", 1, seed=seed)
        wb_bg = pb[0] if pb else None
        ps = sample_anime(family, "shoes", 1, seed=seed) or sample_anime_global("shoes", 1, seed=seed)
        wb_shoes = ps[0] if ps else None
        pa = sample_anime(family, "acc", 2, seed=seed) or sample_anime_global("acc", 2, seed=seed)
        wb_acc = "、".join(pa) if pa else None
        pc = sample_anime_colors(1, seed=seed)
        wb_color = pc[0] if pc else None
        notes.append(
            f"已启用扩展词库并按家族/全局池采样：服装/背景/鞋履/饰品/配色由词库填充（seed={seed}）"
        )

    # —— 段1 人设 ——
    char_desc = character or f"20岁成年女性角色，{ANIME_DEFAULT_FACE}"
    s1 = f"人物设定：{char_desc}，全身立绘，国风玄幻题材" + (f"，{head_feat}" if head_feat else "")

    # —— 段2 画风签名 ——
    style_tag = ANIME_ART_STYLES[art_style]
    s2 = f"画风：赛璐璐平涂({style_tag})，柔光，线条简洁干净"

    # —— 段3 面容发型 ——
    face = "瓜子脸大圆眼，漆黑长直发垂肩，清透明亮" + (f"，{head_feat}" if head_feat else "")
    s3 = f"面容发型：{face}，表情自然、视线平视镜头"

    # —— 段4 服装 ——（中文形制 + 软覆盖约束，领口风险词双清）
    safe_default_outfit = f"中国风长裙形制，长款及踝覆盖端庄，{SOFT_COVERAGE_EN}"
    if outfit:
        outfit_clean = _clean_neckline(outfit, notes)
        if not outfit_clean:
            outfit_clean = safe_default_outfit
            notes.append("自定义服装中的风险片段全部被移除，已回退到端庄长款服装")
        s4 = f"服装：{outfit_clean}，整体端庄协调"
    elif wb_outfit:
        outfit_clean = _clean_neckline(wb_outfit, notes)
        if not outfit_clean:
            outfit_clean = safe_default_outfit
        color_kw = f"{wb_color}色调，" if wb_color else ""
        s4 = f"服装：{color_kw}{outfit_clean}，长款及踝覆盖端庄，{SOFT_COVERAGE_EN}"
    else:
        s4 = f"服装：{safe_default_outfit}"
    shoe_desc = shoes or wb_shoes or "端庄云头履"
    s4 += f"，鞋履为{shoe_desc}并完整入镜"
    if wb_acc:
        s4 += f"，缀以{wb_acc}"
    if use_lora:
        s4 += f"，{lora_name or 'lora'} 触发词" if lora_name else "，角色LoRA"
        notes.append(f"角色 LoRA 权重建议 ≤ {lora_strength}，防止挤压动漫画风")

    # —— 段5 姿态 ——
    if is_migration:
        s5 = ("姿态：standing, full-body shot, feet fully visible, no cropping at the feet, "
              "shoes clearly shown, visible ground below the feet, feet not touching bottom edge, "
              "shot with room to breathe；全身垂直站立面向镜头，双脚并拢重心居中，"
              "双手自然垂落身体两侧，头部占比≤25%画面高度，腿+鞋≥65%画面高度")
    else:
        s5 = "姿态：自然全身站姿，双脚微错落，双手自然垂落或一手轻抚，非严格军事立正但全身完整"

    # —— 段6 环境 + 画质 tag ——
    bg = background or wb_bg or SAFE_BG.get(family, SAFE_BG["国风仙侠"])
    if is_migration:
        s6 = (f"场景：{bg}，光影柔和，前景虚化形成画框\n"
              f"画质tag：{ANIME_QUALITY_HEAD}, (full-body shot:1.2), (long legs:1.1), detailed background")
    else:
        s6 = (f"场景：{bg}，光影层次丰富，前景虚化形成画质画框\n"
              f"画质tag：{ANIME_QUALITY_HEAD}, (full-body shot:1.2), (1girl:1.1), (solo:1.2), detailed background")

    sections = {
        "人设": s1, "画风": s2, "面容发型": s3, "服装": s4, "姿态": s5, "环境画质": s6,
    }
    prompt = "\n".join(sections.values())

    notes.append("CFG=1.0 无负向；安全靠正向约束（长款覆盖/领口双清/日本8词防切脚）")
    notes.append("启发式扫描不能替代人工审核；发布前须复核权利、素材授权与渠道 AI 标识要求")
    if is_migration:
        notes.append("动作迁移版：已写入成年角色、长款覆盖、全身垂直与鞋履完整约束")

    return {"prompt": prompt, "sections": sections, "notes": notes}
