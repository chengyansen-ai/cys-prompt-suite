from importlib import resources


def test_bundled_wordbanks_are_available_as_package_resources() -> None:
    data = resources.files("cys_prompt_suite.prompts").joinpath("data")

    assert data.joinpath("portrait_corpus.json").is_file()
    assert data.joinpath("anime_lib.json").is_file()
