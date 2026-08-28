# -*- coding: utf-8 -*-
"""
portrait.py — 迁移01 写实人像 9 段式提示词生成器

输出规则（严守技能「交付格式与背景铁律」）：
- 只输出 AI 可识别的提示词正文（中文分段 + 可选英文摄影尾参），不含任何元信息/注释/分类标签。
- 背景必须「绚丽场景」，不单调（段8 模板）。
- CFG=1.0 无负向：本生成器不产出任何 negative prompt（头身比/鞋履靠正向段9 约束兜底）。
- 扩展词库（data/portrait_corpus.json，2646 条 / 55 类，含新增 风格_全球美学·配色_风格方案·环境_画框感 等）：
  use_wordbank=True 时按需采样服装/鞋履/背景/配色/饰品。
"""
from .prompts_data import (
    PORTRAIT_FACE_FULL, PORTRAIT_FACE_LITE, PORTRAIT_MAKEUP, PORTRAIT_BODY,
    PORTRAIT_DECOR, PORTRAIT_JEWELRY_DEFAULT,
    PORTRAIT_POSE_MIGRATION, PORTRAIT_POSE_FREE, PORTRAIT_POSE_HALFBODY,
    PORTRAIT_CAM_MIGRATION, PORTRAIT_CAM_HALFBODY, PORTRAIT_CAM_FREE,
    STYLE_PRESETS, SHOES_TEMPLATE, ENV_FRAME_DEFAULT, ENV_MID_DEFAULT,
    ENV_SKY_DEFAULT, ENV_PARTICLES_DEFAULT,
)
from .wordbank import sample_portrait, sample_portrait_color


def _shoes_str(shoes: str | None, preset_shoes: str | None) -> str:
    """鞋履四要素：优先调用方显式传入，其次风格预设，再回退默认。"""
    if shoes:
        return shoes
    if preset_shoes:
        return preset_shoes
    return SHOES_TEMPLATE.format(
        color="裸粉", material="漆面", style="尖头细高跟鞋", detail="细跟"
    )


def _wb_shoes(style: str | None, seed: int | None) -> str:
    """从词库抽鞋履：国风优先鞋履_国风，否则高跟/平底。"""
    if style and "国风" in style:
        pool = sample_portrait("鞋履_国风", 1, seed=seed)
        if pool:
            return f"{pool[0]}，平底，绣纹滚边，清晰完整地展示在画面最底部"
    for cat in ("鞋履_高跟", "鞋履_平底", "鞋履_国风"):
        pool = sample_portrait(cat, 1, seed=seed)
        if pool:
            return f"裸粉色{pool[0]}，漆面光泽，细跟，清晰完整地展示在画面最底部"
    return SHOES_TEMPLATE.format(color="裸粉", material="漆面", style="尖头细高跟鞋", detail="细跟")


def generate_portrait_prompt(
    character: str = "20岁亚洲年轻女性",
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
    face_lite: bool = True,
    use_wordbank: bool = False,
    palette: str | None = None,
    seed: int | None = None,
) -> dict:
    """
    生成迁移01 写实人像 9 段式提示词。

    参数
    ----
    character        : 人设（段1），如 "20岁亚洲年轻女性"
    composition      : "full_body"（动作迁移源图）或 "half_body"（抖音成片/半身参考）
    motion_migration : True 时套用动作迁移硬约束（T-pose/头≤25%/腿≥65%/鞋履≥6%）
    style            : 风格预设名（见 STYLE_PRESETS：唐风/月夜欧式/现代都市/国风仙侠）
    scene            : 自定义段8 场景（覆盖预设）
    shoes            : 自定义鞋履四要素（覆盖预设）
    use_lora         : 是否叠加角色 LoRA（cys001/cheng002 等）
    lora_name        : LoRA 触发词
    lora_strength    : 建议权重（默认 0.6，避免头部放大偏置）
    extra_clothing   : 段7 自定义服装补充
    extra_env        : 段8 自定义环境补充
    face_lite        : 是否用精简版面容（头身比修正优先 True）
    use_wordbank     : True 时从扩展词库(2646条)采样服装/鞋履/背景/配色/饰品，产出更丰富
    palette          : 指定写实配色分类名（如 "色彩_红色系"），覆盖自动配色
    seed             : 随机种子（保证可复现；仅 use_wordbank 时生效）

    返回
    ----
    {"prompt": str, "sections": dict, "notes": list}
    """
    is_full = composition == "full_body"
    preset = STYLE_PRESETS.get(style) if style else None
    notes = []

    # —— 词库采样（仅在启用且对应项无显式/预设值时）——
    wb_color = None
    wb_bottom = None
    wb_shoes = None
    wb_scene = None
    wb_acc = None
    if use_wordbank:
        if palette and palette.startswith("色彩_"):
            pc = sample_portrait(palette, 1, seed=seed)
            wb_color = pc[0] if pc else None
        else:
            wb_color = sample_portrait_color(seed=seed)
        if not extra_clothing and not preset:
            for cat in ("服装_裙装", "服装_下装", "服装_国风形制"):
                pb = sample_portrait(cat, 1, seed=seed)
                if pb:
                    wb_bottom = pb[0]
                    break
        if not shoes and not (preset and preset.get("shoes")):
            wb_shoes = _wb_shoes(style, seed)
        if not scene and not preset:
            pbg = sample_portrait("背景", 1, seed=seed)
            if pbg:
                wb_scene = pbg[0]
        pa = sample_portrait("饰品_头饰", 1, seed=seed) or sample_portrait("饰品_项链", 1, seed=seed)
        if pa:
            wb_acc = pa[0]
        notes.append("已启用扩展词库(2646条)采样：服装/鞋履/背景/配色/饰品由词库随机填充（seed=%s）" % seed)

    # —— 鞋履统一解析（显式 > 预设 > 词库采样 > 默认）——
    if shoes:
        shoes_s = shoes
    elif preset and preset.get("shoes"):
        shoes_s = preset["shoes"]
    elif wb_shoes:
        shoes_s = wb_shoes
    else:
        shoes_s = _shoes_str(None, None)

    # —— 段1 人物 ——
    if is_full:
        s1 = f"人物：{character}，全身垂直站立照，{'标准采集站姿' if motion_migration else '自然挺拔站姿'}，展现完美身材比例"
    else:
        s1 = f"人物：{character}，上半身中景构图（取景至腰部以上），正面半身站姿，展现完美肩颈线条"

    # —— 段2 面容（角色 LoRA 时强制精简版反转头部偏置）——
    if use_lora:
        face = PORTRAIT_FACE_LITE
        notes.append(f"已叠加角色 LoRA（{lora_name or '未命名'}），面容用精简版以反转头部放大偏置；"
                     f"建议权重 ≤ {lora_strength}")
    else:
        face = PORTRAIT_FACE_LITE if face_lite else PORTRAIT_FACE_FULL

    # —— 段3 妆容 / 段4 身材（真实感内核，整段复用）——
    s3 = f"妆容：{PORTRAIT_MAKEUP}"
    s4 = f"身材：{PORTRAIT_BODY}"

    # —— 段5 装饰 ——
    decor = PORTRAIT_DECOR.format(jewelry=PORTRAIT_JEWELRY_DEFAULT)
    if wb_acc:
        decor = decor.rstrip("，整体装饰提升时尚感和精致度，每个细节都散发致命吸引力") + f"，{wb_acc}点缀，整体装饰提升时尚感和精致度"
    s5 = f"装饰：{decor}"

    # —— 段6 动作 ——
    if is_full:
        if motion_migration:
            s6 = "动作：" + PORTRAIT_POSE_MIGRATION.format(shoes=shoes_s)
        else:
            s6 = "动作：" + PORTRAIT_POSE_FREE.format(shoes=shoes_s)
    else:
        s6 = "动作：" + PORTRAIT_POSE_HALFBODY

    # —— 段7 服装 ——
    if is_full:
        top = extra_clothing or (preset.get('top') if preset else "修身针织上衣勾勒腰线")
        bottom = preset.get('bottom') if preset else (wb_bottom or "高腰垂坠长裙及踝，裙摆微A字占据画面4/5")
        s7 = f"服装：视觉重心在下半身：{top}，{bottom}，贴合身体曲线展现身材优势，{shoes_s}，清晰完整地展示在画面最底部"
    else:
        cat = style or "当代风尚"
        color = preset.get('colors', '裸粉') if preset else (wb_color or "裸粉")
        material = "真丝" if preset else "针织"
        s7 = f"服装：{cat}风格·{color}{material}材质利落剪裁，细节精致；下半身与{shoes_s}协调搭配(鞋履不入镜)"

    # —— 段8 环境（必须绚丽）——
    if scene:
        env_scene = scene
    elif preset:
        env_scene = preset['scene']
    elif wb_scene:
        env_scene = f"{wb_scene}，绚丽光影与氛围感拉满，画面层次丰富"
    else:
        env_scene = "月夜欧式露台，雕花石栏环绕，远处城市灯火与河面倒影，夜空星河低垂，微凉夜风拂动纱幔"
    if extra_env:
        env_scene = env_scene + "，" + extra_env
    colors = preset.get('colors', '月银、雾蓝与暖金') if preset else (wb_color or "月银、雾蓝与暖金")
    style_kw = preset.get('style', '欧式浪漫') if preset else "时尚大片"
    s8 = (f"环境：{env_scene}，{ENV_FRAME_DEFAULT}，{ENV_MID_DEFAULT}，{ENV_SKY_DEFAULT}，"
          f"{ENV_PARTICLES_DEFAULT}，整体色调以{colors}为主{style_kw}")

    # —— 段9 摄像 ——
    if is_full and motion_migration:
        s9 = "摄像：" + PORTRAIT_CAM_MIGRATION
        notes.append("动作迁移版：段9 已强约束 头≤25% / 腿≥65% / 鞋履≥6% / 无畸变 / T-pose 垂直")
    elif is_full:
        s9 = "摄像：" + PORTRAIT_CAM_FREE.format(
            light=preset.get('light', '冷月侧光') if preset else '电影感主光',
            light_en=preset.get('light_en', 'cinematic key light') if preset else 'cinematic key light',
            quality="电影感打光", color=colors, atmosphere=preset.get('atmosphere', '静谧清冷') if preset else '干净通透',
            style=style_kw, mood=preset.get('mood', '优雅神秘') if preset else '自然高级',
        )
    else:
        s9 = "摄像：" + PORTRAIT_CAM_HALFBODY

    # 角色 LoRA 反转补偿：强化下半身与鞋履占比
    if use_lora:
        s7 = s7 + "（角色LoRA反转补偿：视觉重心压在下半身，鞋履完整入镜兜底）"
        notes.append("已对段7/段9 加 token 反转补偿头部偏置；出图时建议 cys001 权重≤0.6、关闭 Anything_to_Real_Characters")

    sections = {
        "人物": s1, "面容": f"面容：{face}", "妆容": s3, "身材": s4,
        "装饰": s5, "动作": s6, "服装": s7, "环境": s8, "摄像": s9,
    }
    prompt = "\n".join(sections.values())

    if not motion_migration and is_full:
        notes.append("非动作迁移全身照：未加 T-pose 硬约束，可按自由范式调整姿态")
    notes.append("CFG 锁定 1.0、无负向提示词；发布前须过合规校验（cys-compliance-mcp）")

    return {"prompt": prompt, "sections": sections, "notes": notes}
