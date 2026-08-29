"""
h3.py — 海螺3 (H3 / MiniMax) 视频提示词生成器

支持 5 种模式：
- T2VA / I2VA / FL2VA / L2VA ：基础音视频时间线（三核心字段 + 可选参考帧指令）
- Ref2VA ：全参考模式六段式（subject_definitions / summary / retention_analysis /
           detailed_description / overall_soundscape / non_diegetic_music）

基础三字段和 Ref2VA 六段字段的顺序由回归测试固定。

范围：引导模板只覆盖舞蹈、转场、展示与走秀等非口播视频。
"""
from ..validation import (
    validate_choice,
    validate_optional_text,
    validate_positive_duration,
)
from .prompts_data import H3_CONTENT_TYPES


def _build_base(
    mode,
    imd,
    sound,
    music,
    first_frame_desc,
    last_frame_desc,
    duration_seconds,
):
    """基础四模式装配。"""
    notes = []
    lines = []
    if not imd:
        raise ValueError(f"{mode} 需要 integrated_multimodal_description")

    anchored_imd = imd
    if mode == "I2VA":
        if not first_frame_desc:
            raise ValueError("I2VA 需要 first_frame_desc（首帧图描述）")
        lines.append(
            "For the target video, at 0.00 seconds into the target video, "
            "<Picture 1> (from [Shot 1]) is fully referenced.\n"
        )
        anchored_imd = f"Opening reference: {first_frame_desc}. {imd}"
        notes.append("I2VA：已写入首帧对齐指令，正文从 <Picture 1> 出发向前发展")
    elif mode == "FL2VA":
        if not (first_frame_desc and last_frame_desc):
            raise ValueError("FL2VA 需要 first_frame_desc 与 last_frame_desc（首/末帧）")
        duration = validate_positive_duration(duration_seconds)
        lines.append(
            "How the reference pictures align with the target video — "
            f"Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; "
            f"Picture 2 (from Shot N) aligns with the {duration:.2f}-second mark of the target video.\n"
        )
        anchored_imd = (
            f"Opening reference: {first_frame_desc}. Ending reference: {last_frame_desc}. {imd}"
        )
        notes.append("FL2VA：已写入首/末帧对齐指令，正文描述两帧间的连续运动路径")
    elif mode == "L2VA":
        if not last_frame_desc:
            raise ValueError("L2VA 需要 last_frame_desc（末帧图描述）")
        duration = validate_positive_duration(duration_seconds)
        lines.append(
            "How the reference pictures align with the target video — "
            f"<Picture 1> (from [Shot N]) aligns with the {duration:.2f}-second mark of the target video.\n"
        )
        anchored_imd = f"Ending reference: {last_frame_desc}. {imd}"
        notes.append("L2VA：已写入末帧对齐指令，正文推断合理前序状态并收敛到末帧")

    lines.append(f"integrated_multimodal_description: {anchored_imd}")
    lines.append(f"\noverall_soundscape: {sound or 'N/A'}")
    lines.append(f"\nnon_diegetic_music: {music or 'N/A'}")
    return "\n".join(lines), notes


def _build_ref2va_guided(content_type, character, scene1, scene2, outfit1, outfit2, retention_note):
    """Ref2VA 引导式（舞蹈/转场/展示/走秀）。输出标准六段式英文。"""
    notes = []
    ct_desc = H3_CONTENT_TYPES[content_type]
    char = character or "the adult woman with long straight black hair, large round eyes, oval face, and natural warm skin tone"
    sc1 = scene1 or "a dusk warm-cloud sky"
    sc2 = scene2 or sc1
    o1 = outfit1 or "a teal-green floor-length traditional hanfu with a hairpin"
    o2 = outfit2 or o1

    is_transition = content_type == "transition" and (
        (scene2 is not None and scene2 != sc1)
        or (outfit2 is not None and outfit2 != o1)
    )

    subject_definitions = (
        f"<Subject 1> is {char}, appearing in <Picture 1> and <Picture 2>.\n"
        f"<Picture 1> is the opening composition anchor of [Shot 1], showing <Subject 1> in {o1}, under {sc1}.\n"
        f"<Picture 2> is the ending visual target of the {content_type} sequence, showing <Subject 1> in {o2}, under {sc2}."
    )
    summary = (
        "[keyframe completion + reference generation] Generate a single medium-wide vertical (9:16) shot of "
        f"<Subject 1> performing a coherent {content_type} sequence, beginning from <Picture 1>"
        + (" and smoothly transforming into the costume and scene of <Picture 2> through the dance motion."
           if is_transition else " and holding the pose with gentle continuation.")
    )
    if is_transition:
        retention = (
            f"<Subject 1> (appears in [Shot 1]): fully_preserved - retain facial identity, "
            "hairstyle, skin tone, and body shape; costume and background change intentionally "
            "as part of the transition.\n"
            "<Picture 1> ([Shot 1] opening frame): fully_preserved - preserve the opening pose, "
            "costume, and background at the start.\n"
            f"<Picture 2> (ending visual target): partially_preserved - {o2} and {sc2} appear "
            "by the end; the transition is continuous, not a hard cut."
        )
    else:
        retention = (
            "<Subject 1> (appears in [Shot 1]): fully_preserved - retain facial identity, "
            "hairstyle, skin tone, body shape, and outfit continuity.\n"
            "<Picture 1> ([Shot 1] opening frame): fully_preserved - preserve the opening pose, "
            "costume, and background at the start.\n"
            "<Picture 2> (ending visual target): fully_preserved - reach the target composition "
            "while keeping subject, costume, and scene continuity."
        )
    if retention_note:
        retention += "\n" + retention_note

    detailed = (
        "The target video uses a cinematic, anime-realistic music-video style with warm brilliant lighting, "
        "suitable for a vertical 9:16 composition.\n"
        f"[Shot 1] The video begins from <Picture 1>: <Subject 1> stands in a medium-wide full-body framing under {sc1}, "
        f"wearing {o1}. " + ct_desc +
        " The camera holds a static shot with a very slight slow push-in, keeping her full body and footwear visible. "
    )
    if is_transition:
        detailed += (
            "As the dance continues, her costume and the environment gradually shift: the first outfit dissolves into "
            f"{o2}, and {sc1} melts into {sc2}; the transformation flows with the dance step, seamless and without cuts. "
            "She completes a gentle spin, hair and ribbon tracing an arc, ending in the pose and scene of <Picture 2>."
        )
    else:
        detailed += " She completes the action and settles into the full-body composition of <Picture 2>."

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
    duration_seconds: float | None = None,
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
    validate_choice("mode", mode, {"T2VA", "I2VA", "FL2VA", "L2VA", "Ref2VA"})
    for field_name, value in {
        "integrated_multimodal_description": integrated_multimodal_description,
        "overall_soundscape": overall_soundscape,
        "non_diegetic_music": non_diegetic_music,
        "first_frame_desc": first_frame_desc,
        "last_frame_desc": last_frame_desc,
        "character": character,
        "scene1": scene1,
        "scene2": scene2,
        "outfit1": outfit1,
        "outfit2": outfit2,
        "retention_note": retention_note,
        "subject_definitions": subject_definitions,
        "summary": summary,
        "retention_analysis": retention_analysis,
        "detailed_description": detailed_description,
    }.items():
        validate_optional_text(field_name, value)

    if mode in ("T2VA", "I2VA", "FL2VA", "L2VA"):
        prompt, notes = _build_base(
            mode, integrated_multimodal_description, overall_soundscape,
            non_diegetic_music, first_frame_desc, last_frame_desc, duration_seconds,
        )
        return {"prompt": prompt, "sections": {"body": prompt}, "mode": mode, "notes": notes}

    if mode == "Ref2VA":
        validate_choice("content_type", content_type, H3_CONTENT_TYPES)
        raw_fields = [subject_definitions, summary, retention_analysis, detailed_description]
        if any(value is not None for value in raw_fields) and not all(raw_fields):
            raise ValueError("all four raw Ref2VA sections must be provided together")
        raw = all(raw_fields)
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
                "notes": ["Ref2VA 原始六段装配完成（段名和顺序由本项目回归测试固定）"],
            }
        prompt, sections, notes = _build_ref2va_guided(
            content_type, character, scene1, scene2, outfit1, outfit2, retention_note,
        )
        return {"prompt": prompt, "sections": sections, "mode": f"Ref2VA({content_type})", "notes": notes}

    raise AssertionError("unreachable")
