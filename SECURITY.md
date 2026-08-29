# Security policy

## Supported versions

Security fixes are made on the latest released minor version. This project is
currently beta software; pin a reviewed version in production rather than
installing an unpinned branch.

## Reporting a vulnerability

Prefer GitHub's private vulnerability reporting for this repository. If that is
not enabled, open an issue containing only a minimal, non-sensitive description
and ask the maintainer for a private channel. Never post secrets, personal data,
private prompts or working exploit details in a public issue.

## Runtime and data boundary

The package itself performs local prompt composition and deterministic text
matching. It contains no telemetry, credential collection or outbound network
request. The MCP host, model provider and downstream image/video services are
separate trust boundaries and may receive the prompts submitted through them.

Do not place API keys, personal data, unlicensed face images or confidential
material in prompt arguments. Review dependency updates and generated output
before production use.
