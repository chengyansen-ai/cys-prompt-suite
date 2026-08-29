import pytest

from cys_prompt_suite.prompts import anime, portrait, wordbank


def test_portrait_wordbank_sampling_is_reproducible() -> None:
    first = portrait.generate_portrait_prompt(use_wordbank=True, seed=17)
    second = portrait.generate_portrait_prompt(use_wordbank=True, seed=17)

    assert first["prompt"] == second["prompt"]
    assert len(first["sections"]) == 9


@pytest.mark.parametrize("composition", ["", "headshot", "FULL_BODY"])
def test_portrait_rejects_unknown_composition(composition: str) -> None:
    with pytest.raises(ValueError, match="composition"):
        portrait.generate_portrait_prompt(composition=composition)


def test_portrait_rejects_unknown_style_and_invalid_lora_strength() -> None:
    with pytest.raises(ValueError, match="style"):
        portrait.generate_portrait_prompt(style="不存在的风格")
    with pytest.raises(ValueError, match="lora_strength"):
        portrait.generate_portrait_prompt(use_lora=True, lora_strength=1.5)


def test_default_portrait_uses_neutral_commercial_safe_language() -> None:
    result = portrait.generate_portrait_prompt()

    assert "丰满胸部" not in result["prompt"]
    assert "完美臀线" not in result["prompt"]
    assert "致命吸引力" not in result["prompt"]


def test_anime_rejects_unknown_mode_and_art_style() -> None:
    with pytest.raises(ValueError, match="mode"):
        anime.generate_anime_prompt(mode="t_pose")
    with pytest.raises(ValueError, match="art_style"):
        anime.generate_anime_prompt(art_style="unknown")


def test_third_party_ip_families_require_explicit_opt_in() -> None:
    with pytest.raises(ValueError, match="third-party IP"):
        anime.generate_anime_prompt(family="原神")

    authorized = anime.generate_anime_prompt(
        family="原神", allow_third_party_ip=True, seed=3
    )
    assert authorized["prompt"]
    assert any("third-party IP" in note for note in authorized["notes"])


def test_family_discovery_is_commercial_safe_by_default() -> None:
    safe_families = wordbank.list_anime_families()
    all_families = wordbank.list_anime_families(include_third_party_ip=True)

    assert "原神" not in safe_families
    assert "原神" in all_families
    assert len(all_families) == 80


def test_wordbank_stats_match_bundled_data() -> None:
    stats = wordbank.get_wordbank_stats()

    assert stats["portrait_categories"] == 55
    assert stats["anime_families_total"] == 80
    assert stats["third_party_ip_families"] == 47
    assert stats["indexed_entries"] == 8865
    assert stats["unique_strings"] == 3455


def test_removed_neckline_terms_never_leave_an_empty_outfit() -> None:
    result = anime.generate_anime_prompt(outfit="露肩、抹胸、短裙")

    assert "服装：，" not in result["prompt"]
    assert "长款及踝" in result["prompt"]
