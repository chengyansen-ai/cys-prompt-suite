# Commercial-use guidance

The MIT license permits commercial use of the repository's code, subject to its
notice and warranty terms. That is not a blanket clearance for every bundled
term, user input, generated image/video or downstream model.

Before commercial deployment, review at least these independent layers:

1. **Code and dependencies** — preserve license notices, pin versions and review
   dependency licenses and vulnerabilities for the version you ship.
2. **Bundled data** — consult `DATA_PROVENANCE.md`. The current snapshot has
   provenance limitations and contains opt-in third-party game names.
3. **Inputs and likenesses** — obtain rights for faces, logos, private data,
   reference media, music, fonts and user-provided assets.
4. **Models and services** — follow the license and commercial terms of every
   image/video model, API and hosting provider used downstream.
5. **Outputs and distribution** — perform human review for IP, privacy, safety,
   advertising and platform rules; add AI-content labels where required.

The compliance module is deterministic and useful as a regression guard, but it
is a small heuristic phrase scanner. `safe_passed=true` only means the configured
phrases were not present after scanning. It is not legal advice, platform
approval or a guarantee that content is safe to publish.

For higher-risk launches, obtain a current legal and platform-policy review in
the target jurisdiction and product category.
