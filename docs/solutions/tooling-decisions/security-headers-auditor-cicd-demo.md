---
title: Security Headers Auditor CI/CD demo posture
date: 2026-06-09
category: docs/solutions/tooling-decisions
module: secure-cicd-demo
problem_type: tooling_decision
component: tooling
severity: medium
applies_when:
  - Building small cybersecurity take-home projects where CI/CD evidence matters more than application complexity
  - Demonstrating security-focused GitHub Actions without introducing cloud credentials or external runtime services
tags: [github-actions, ghcr, fastapi, security-headers, ci-cd]
---

# Security Headers Auditor CI/CD demo posture

## Context

The assignment asks for a public GitHub repository that demonstrates a working GitHub Actions pipeline with testing, security checks, and a real deploy step. The application can be simple, but the repository needs visible successful workflow runs and clear written communication.

## Guidance

Use a small FastAPI "Security Headers Auditor" API that analyzes caller-supplied HTTP response headers. Do not fetch target URLs from the app. The API remains deterministic, easy to test, and avoids turning a demo into a server-side request forgery risk.

Keep runtime and development dependencies separate:

```text
requirements.txt       # FastAPI and Uvicorn only
requirements-dev.txt   # pytest, httpx, ruff, bandit, pip-audit
```

Use GitHub Actions to show the security posture:

- CI runs Ruff, Bandit, pytest, and `pip-audit`.
- CodeQL uploads Python code scanning results.
- The release workflow publishes a container to GitHub Container Registry on `main`, version tags, and manual dispatch.
- Workflows use least-privilege permissions and the built-in `GITHUB_TOKEN`.

## Why This Matters

The evaluator can inspect the Actions tab and see real runs for test, security, build, and deploy behavior. The application itself supports the security theme without adding risky network behavior, databases, authentication, or cloud credentials that would distract from the CI/CD objective.

This also gives the README a strong story: the app avoids SSRF by design, the pipeline performs multiple security checks, and the container runs as a non-root user.

## When to Apply

- The assignment or demo evaluates pipeline quality more than app complexity.
- You need a cybersecurity-themed Python app with deterministic tests.
- You want a real deploy artifact without maintaining cloud infrastructure.

## Examples

For deployment evidence, publish these GHCR tags:

```text
ghcr.io/<owner>/<repo>:latest
ghcr.io/<owner>/<repo>:sha-<commit>
ghcr.io/<owner>/<repo>:<version>
```

For the app boundary, accept this shape:

```json
{
  "target": "example.com",
  "headers": {
    "Content-Security-Policy": "default-src 'self'",
    "X-Content-Type-Options": "nosniff"
  }
}
```

Avoid this shape for the baseline:

```json
{
  "url": "https://example.com"
}
```

URL fetching can be a later feature only with explicit SSRF controls, allowlists, timeouts, and tests.

## Related

- `docs/plans/2026-06-09-001-feat-security-headers-auditor-plan.md`
