# Data provenance and maintenance

The repository bundles two JSON snapshots under
`src/cys_prompt_suite/prompts/data/`.

| File | Measured contents |
|---|---|
| `portrait_corpus.json` | 55 list categories, 2,646 indexed entries |
| `anime_lib.json` | 80 families plus global pools and 47 game-IP anchors |

Across both snapshots there are 8,865 indexed entries and 3,455 unique strings.
The larger number counts a string each time it is indexed in a category or
family; it is not a unique-vocabulary count. The runtime reports the same figures
through `get_wordbank_stats()`.

## What is and is not proven here

The current public repository does not include the original source documents or
the ingestion script that produced these snapshots. Consequently, the repository
alone cannot reproduce or independently verify every source and license claim.
The data should be treated as a maintained project snapshot, not as a legally
cleared public-domain dataset.

Some anime family keys name third-party games. Those names are excluded from
default discovery and generation requires `allow_third_party_ip=True`. This gate
prevents accidental use; it does not grant a trademark, copyright, character or
publicity-right license.

## Contribution requirements

For new data, a pull request should record:

- source URL or first-party source file;
- retrieval date and applicable terms or license;
- transformation and deduplication method;
- whether names, characters, brands or personal likenesses are present;
- before/after counts and a regression test.

Do not add scraped creative text, private prompt libraries, biometric data or
third-party character descriptions without documented authorization.
