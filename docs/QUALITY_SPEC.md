# Quality hardening specification

## Objective

Make `cys-prompt-suite` a reproducible, installable and honestly documented MCP
server for Chinese portrait, anime and MiniMax H3 prompt composition. The package
must be safe by default for ordinary commercial workflows without claiming that
a heuristic scanner guarantees legal or platform approval.

## Tech stack

- Python 3.10+
- FastMCP 3.x
- setuptools build backend
- pytest for behavior and MCP integration tests
- Ruff for linting

## Commands

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
python -m ruff check .
python -m build
python -m cys_prompt_suite.server
```

## Project structure

```text
src/cys_prompt_suite/          package and MCP server
src/cys_prompt_suite/prompts/  prompt generators and bundled wordbanks
src/cys_prompt_suite/compliance/ deterministic heuristic rules
tests/                         pytest behavior and transport tests
docs/                          quality, provenance, and commercial-use notes
.github/workflows/             automated quality gates
```

## Code style

Use typed public signatures, explicit validation, deterministic return values and
small pure helpers. Reject unsupported values instead of silently changing the
caller's request.

```python
if mode not in SUPPORTED_MODES:
    raise ValueError(f"unsupported mode: {mode}")
```

## Testing strategy

- Unit tests cover validation, deterministic sampling, sanitization and every H3
  mode's structural contract.
- In-memory FastMCP tests verify tool registration and structured output.
- A stdio round trip uses the active interpreter, never an author-specific path.
- A wheel test confirms both JSON wordbanks are included in the built artifact.
- CI runs pytest and Ruff on supported Python versions.

## Boundaries

- Always: preserve public tool names, validate untrusted strings, include package
  data, test a built wheel, and describe compliance checks as heuristics.
- Ask first: publish to PyPI, push to GitHub, delete user data, or change the MIT
  license.
- Never: embed secrets, claim guaranteed platform approval, represent third-party
  game IP as cleared for commercial use, or silently ignore invalid options.

## Success criteria

- `pytest` collects real tests and passes.
- All nine MCP tools complete an in-memory or stdio round trip.
- H3 FL2VA/L2VA instructions use an explicit two-decimal duration and Ref2VA has
  no unresolved template placeholders.
- A non-editable wheel contains both JSON wordbanks and imports successfully.
- Default anime discovery excludes third-party game-IP families; authorized users
  can opt in explicitly.
- README claims match measured repository behavior and include limitations,
  privacy, provenance, development, and commercial-use guidance.

## Open questions

None blocking. Publishing and legal sign-off remain owner actions outside this
local hardening change.
