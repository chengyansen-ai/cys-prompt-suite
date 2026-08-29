import pytest

from cys_prompt_suite.prompts import h3


def test_t2va_preserves_the_three_core_field_order() -> None:
    result = h3.generate_h3_prompt(
        mode="T2VA",
        integrated_multimodal_description="A calm continuous camera move.",
        overall_soundscape="Soft room tone.",
        non_diegetic_music="N/A",
    )

    prompt = result["prompt"]
    assert prompt.index("integrated_multimodal_description:") < prompt.index(
        "overall_soundscape:"
    ) < prompt.index("non_diegetic_music:")


def test_i2va_anchors_and_describes_the_opening_reference() -> None:
    result = h3.generate_h3_prompt(
        mode="I2VA",
        first_frame_desc="an adult dancer standing beneath a red lantern",
        integrated_multimodal_description="She raises one sleeve in a continuous motion.",
    )

    assert "0.00 seconds" in result["prompt"]
    assert "an adult dancer standing beneath a red lantern" in result["prompt"]


def test_fl2va_uses_explicit_duration_and_both_frame_descriptions() -> None:
    result = h3.generate_h3_prompt(
        mode="FL2VA",
        duration_seconds=8,
        first_frame_desc="a closed black umbrella beside a bicycle",
        last_frame_desc="the same umbrella open above the cyclist",
        integrated_multimodal_description="she opens the umbrella in one continuous shot",
    )

    assert "8.00-second mark" in result["prompt"]
    assert "a closed black umbrella" in result["prompt"]
    assert "the same umbrella open" in result["prompt"]
    assert "first_frame_desc mark" not in result["prompt"]


def test_l2va_requires_duration() -> None:
    with pytest.raises(ValueError, match="duration_seconds"):
        h3.generate_h3_prompt(
            mode="L2VA",
            last_frame_desc="a settled final composition",
            integrated_multimodal_description="the movement converges on the image",
        )


def test_ref2va_guided_has_no_unrendered_placeholders() -> None:
    result = h3.generate_h3_prompt(
        mode="Ref2VA",
        content_type="transition",
        outfit1="a teal hanfu",
        outfit2="a gold embroidered hanfu",
        scene1="a mountain terrace at dusk",
        scene2="a moonlit palace courtyard",
    )

    assert "{o2" not in result["prompt"]
    assert list(result["sections"]) == [
        "subject_definitions",
        "summary",
        "retention_analysis",
        "detailed_description",
        "overall_soundscape",
        "non_diegetic_music",
    ]


def test_ref2va_non_transition_does_not_claim_costume_or_scene_changes() -> None:
    result = h3.generate_h3_prompt(mode="Ref2VA", content_type="showcase")

    retention = result["sections"]["retention_analysis"]
    assert "change intentionally" not in retention
    assert "fully_preserved" in retention


def test_ref2va_rejects_partial_raw_sections() -> None:
    with pytest.raises(ValueError, match="all four raw Ref2VA sections"):
        h3.generate_h3_prompt(mode="Ref2VA", subject_definitions="only one section")


def test_h3_rejects_unknown_content_type() -> None:
    with pytest.raises(ValueError, match="content_type"):
        h3.generate_h3_prompt(mode="Ref2VA", content_type="lecture")
