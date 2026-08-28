# -*- coding: utf-8 -*-
"""
h3.py — 海螺3 (H3 / MiniMax) 视频提示词生成器

支持 5 种模式：
- T2VA / I2VA / FL2VA / L2VA ：基础音视频时间线（三核心字段 + 可选参考帧指令）
- Ref2VA ：全参考模式六段式（subject_definitions / summary / retention_analysis /
           detailed_description / overall_soundscape / non_diegetic_music）

结构严格遵循技能 references/base-en.txt 与 ref-en.txt；Ref2VA 舞蹈/转场实战遵循
ref2va-digital-human-zh.md。所有字段/段名/顺序不可调换。

范围红线（2026-08-26 主人明确）：本生成器只产出 舞蹈 / 转场 / 展示 / 走秀 等
健康向、非口播类视频；不生成「口播 / 讲解 / 讲课」类内容。
"""
from .prompts_data import H3_CONTENT_TYPES


def _fmt_time(seconds: float) -> str:
    """MM:SS.mmm 严格两位毫秒。"""
    m = int(seconds) // 60
    s = seconds - m * 60
    return f"{m:02d}:{s:06.3f}"


def _build_base(mode, imd, sound, music, first_frame_desc, last_frame_desc):
    """基础四模式装配。"""
    notes = []
    lines = []
    if mode == "I2VA":
        if not first_frame_desc:
            raise ValueError("I2VA 需要 first_frame_desc（首帧图描述）")
        lines.append(
            f"For the target video, at 0.00 seconds into the target video, "
            f"<Picture 1> (from [Shot 1]) is fully referenced.\n"
        )
        notes.append("I2VA：已写入首帧对齐指令，正文从 <Picture 1> 出发向前发展")
    elif mode == "FL2VA":
        if not (first_frame_desc and last_frame_desc):
            raise ValueError("FL2VA 需要 first_frame_desc 与 last_frame_desc（首/末帧）")
        lines.append(
            "How the reference pictures align with the target video — "
            f"Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; "
            f"Picture 2 (from Shot N) aligns with the {first_frame_desc} mark of the target video.\n"
        )
        notes.append("FL2VA：已写入首/末帧对齐指令，正文描述两帧间的连续运动路径")
    elif mode == "L2VA":
        if not last_frame_desc:
            raise ValueError("L2VA 需要 last_frame_desc（末帧图描述）")
        lines.append(
            "How the reference pictures align with the target video — "
            f"<Picture 1> (from [Shot N]) aligns with the {last_frame_desc} mark of the target video.\n"
        )
        notes.append("L2VA：已写入末帧对齐指令，正文推断合理前序状态并收敛到末帧")

    lines.append(f"integrated_multimodal_description: {imd or '[请填写音视频时间线描述]'}")
    lines.append(f"\noverall_soundscape: {sound or 'N/A'}")
    lines.append(f"\nnon_diegetic_music: {music or 'N/A'}")
    return "\n".join(lines), notes


def _build_ref2va_guided(content_type, character, scene1, scene2, outfit1, outfit2, retention_note):
    """Ref2VA 引导式（舞蹈/转场/展示/走秀）。输出标准六段式英文。"""
    notes = []
    ct_desc = H3_CONTENT_TYPES.get(content_type, H3_CONTENT_TYPES["dance"])
    char = character or "the young woman with long straight black hair, large round eyes, oval face, fair porcelain-pink skin"
    sc1 = scene1 or "a dusk warm-cloud sky"
    sc2 = scene2 or sc1
    o1 = outfit1 or "a teal-green floor-length traditional hanfu with a hairpin"
    o2 = outfit2 or o1

    is_transition = content_type == "transition" and scene2 and scene2 != sc1

    subject_definitions = (
        f"<Subject 1> is {char}, appearing in <Picture 1> and <Picture 2>.\n"
        f"<Picture 1> is the opening composition anchor of [Shot 1], showing <Subject 1> in {o1}, under {sc1}.\n"
        f"<Picture 2> is the ending visual target of the dance transition, showing <Subject 1> in {o2}, under {sc2}."
    )
    summary = (
        "[keyframe completion + reference generation] Generate a single medium-wide vertical (9:16) shot of "
        f"<Subject 1> performing a flowing graceful Chinese-style dance, beginning from <Picture 1>"
        + (" and smoothly transforming into the costume and scene of <Picture 2> through the dance motion."
           if is_transition else " and holding the pose with gentle continuation.")
    )
    retention = (
        f"<Subject 1> (appears in [Shot 1]): fully_preserved - retain facial identity, hairstyle, skin tone, and body shape; "
        "costume and background change intentionally as part of the transition.\n"
        f"<Picture 1> ([Shot 1] opening frame): fully_preserved - preserve the opening pose, costume, and background at the start.\n"
        f"<Picture 2> (ending visual target): partially_preserved - the {o2.split(' ')[-1]} dress and {sc2} appear by the end; "
        "the transition is continuous, not a hard cut."
    )
    if retention_note:
        retention += "\n" + retention_note

    detailed = (
        "The target video uses a cinematic, anime-realistic music-video style with warm brilliant lighting, "
        "suitable for a vertical Douyin frame.\n"
        f"[Shot 1] The video begins from <Picture 1>: <Subject 1> stands in a medium-wide full-body framing under {sc1}, "
        f"wearing the {o1.split(' ')[0]} hanfu. " + ct_desc +
        " The camera holds a static shot with a very slight slow push-in, keeping her full body and footwear visible. "
    )
    if is_transition:
        detailed += (
            "As the dance continues, her costume and the environment gradually shift: the first outfit dissolves into "
            f"{o2}, and {sc1} melts into {sc2}; the transformation flows with the dance step, seamless and without cuts. "
            "She completes a gentle spin, hair and ribbon tracing an arc, ending in the pose and scene of <Picture 2>."
        )
    else:
        detailed += "She completes a gentle spin and settles into a stable full-body pose, hair and ribbon tracing an arc."

    sound = "Soft fabric motion and gentle footsteps on the floor; a faint warm breeze through the scene, shifting into a crystalline shimmer."
    music = "A restrained erhu-led Chinese instrumental at a slow tempo, joined by soft percussion that swells gently with the dance turn."

    notes.append(f"Ref2VA 引导式 · 内容类型={content_type}（健康向非口播）")
    notes.append("严守合规：中远景全身、鞋履完整、无扭臀挑逗/胸臀特写/透视露点")
    notes.append("失败条件自检：fully_preserved 未与大动作冲突；镜头未下移到胸臀/腿部特写；无违规动作")

    sections = {
        "subject_definitions": subject_definitions,
        "summary": summary,
        "retention_analysis": retention,
        "detailed_description": detailed,
        "overall_soundscape": sound,
        "non_diegetic_music": music,
    }
    prompt = "\n\n".join(f"{k}:\n{v}" for k, v in sections.items())
    return prompt, sections, notes


def generate_h3_prompt(
    mode: str = "Ref2VA",
    # 基础模式字段
    integrated_multimodal_description: str | None = None,
    overall_soundscape: str | None = None,
    non_diegetic_music: str | None = None,
    first_frame_desc: str | None = None,
    last_frame_desc: str | None = None,
    # Ref2VA 引导式
    content_type: str = "dance",
    character: str | None = None,
    scene1: str | None = None,
    scene2: str | None = None,
    outfit1: str | None = None,
    outfit2: str | None = None,
    retention_note: str | None = None,
    # Ref2VA 原始字段（直接传入六段）
    subject_definitions: str | None = None,
    summary: str | None = None,
    retention_analysis: str | None = None,
    detailed_description: str | None = None,
) -> dict:
    """
    生成 H3 视频提示词。

    模式
    ----
    mode="T2VA"|"I2VA"|"FL2VA"|"L2VA" : 用 integrated_multimodal_description / overall_soundscape /
        non_diegetic_music（+ 可选 first_frame_desc / last_frame_desc）装配。
    mode="Ref2VA" : 若传 subject_definitions 等原始字段则原样装配六段；
        否则走引导式（content_type + character + scene1/2 + outfit1/2）生成舞蹈/转场模板。

    返回
    ----
    {"prompt": str, "sections": dict, "mode": str, "notes": list}
    """
    if mode in ("T2VA", "I2VA", "FL2VA", "L2VA"):
        if mode == "T2VA" and not integrated_multimodal_description:
            raise ValueError("T2VA 需要 integrated_multimodal_description")
        prompt, notes = _build_base(
            mode, integrated_multimodal_description, overall_soundscape,
            non_diegetic_music, first_frame_desc, last_frame_desc,
        )
        return {"prompt": prompt, "sections": {"body": prompt}, "mode": mode, "notes": notes}

    if mode == "Ref2VA":
        raw = all([subject_definitions, summary, retention_analysis, detailed_description])
        if raw:
            sections = {
                "subject_definitions": subject_definitions,
                "summary": summary,
                "retention_analysis": retention_analysis,
                "detailed_description": detailed_description,
                "overall_soundscape": overall_soundscape or "N/A",
                "non_diegetic_music": non_diegetic_music or "N/A",
            }
            prompt = "\n\n".join(f"{k}:\n{v}" for k, v in sections.items())
            return {
                "prompt": prompt, "sections": sections, "mode": "Ref2VA(raw)",
                "notes": ["Ref2VA 原始六段装配完成（段名/顺序严格遵循官方规范）"],
            }
        prompt, sections, notes = _build_ref2va_guided(
            content_type, character, scene1, scene2, outfit1, outfit2, retention_note,
        )
        return {"prompt": prompt, "sections": sections, "mode": f"Ref2VA({content_type})", "notes": notes}

    raise ValueError(f"未知 mode：{mode}（支持 T2VA/I2VA/FL2VA/L2VA/Ref2VA）")
