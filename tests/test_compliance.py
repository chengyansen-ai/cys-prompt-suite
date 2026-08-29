import pytest

from cys_prompt_suite import aggregator
from cys_prompt_suite.compliance import checker


def test_compliance_normalizes_fullwidth_text() -> None:
    report = checker.check_text("成年角色但标注为ｌｏｌｉ", content_type="anime")

    assert report["summary"]["passed"] is False
    assert any(v["rule_id"] == "A-LOLI" for v in report["violations"])


@pytest.mark.parametrize("content_type", ["", "photo", "ANIME"])
def test_compliance_rejects_unknown_content_type(content_type: str) -> None:
    with pytest.raises(ValueError, match="content_type"):
        checker.check_text("普通文本", content_type=content_type)


def test_compliance_rejects_unknown_platform() -> None:
    with pytest.raises(ValueError, match="platform"):
        checker.check_text("普通文本", platform="unknown")


def test_compliance_rejects_missing_text() -> None:
    with pytest.raises(ValueError, match="text"):
        checker.check_text(None)  # type: ignore[arg-type]


def test_platform_listing_keeps_direct_platform_keys() -> None:
    platforms = checker.list_platforms()

    assert platforms["douyin"]["name"] == "抖音"
    assert platforms["_ruleset"]["status"] == "heuristic"


def test_blacklist_hits_are_grouped_and_structural_hits_are_not_duplicated() -> None:
    report = checker.check_text("扭臀顶胯并向镜头挑逗", content_type="anime")

    matched_terms = [
        term for violation in report["violations"] for term in violation["matched"]
    ]
    assert len(matched_terms) == len(set(matched_terms))
    assert report["summary"]["block_count"] == 2


def test_generate_and_check_rewrites_blocked_phrases_and_requires_review() -> None:
    result = aggregator.generate_and_check(
        kind="portrait",
        extra_env="扭臀顶胯向镜头挑逗",
        seed=9,
    )

    assert result["needs_sanitize"] is True
    assert result["safe_passed"] is True
    assert result["requires_human_review"] is True
    assert "扭臀" not in result["safe_prompt"]
    assert "顶胯" not in result["safe_prompt"]
    assert "舒展转身" in result["safe_prompt"]
    assert result["ruleset"]["last_reviewed"] == "2026-08-28"


def test_generate_and_check_rejects_unknown_generator_arguments() -> None:
    with pytest.raises(ValueError, match="unsupported generator argument"):
        aggregator.generate_and_check(kind="portrait", typo_parameter="ignored before")
