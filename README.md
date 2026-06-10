# Secure CI/CD Demo

A small Python FastAPI application with a browser UI that audits common HTTP response security headers.

The application is intentionally simple because this repository is mainly a CI/CD security demo: tests, static analysis, dependency auditing, CodeQL code scanning, Dependabot, and container publishing with GitHub Actions.

## Evaluator Quick Links

- Repository: [jayceparabellum/secure-cicd-demo](https://github.com/jayceparabellum/secure-cicd-demo)
- Actions tab: [GitHub Actions runs](https://github.com/jayceparabellum/secure-cicd-demo/actions)
- Recent successful CI run: [CI #27243381545](https://github.com/jayceparabellum/secure-cicd-demo/actions/runs/27243381545)
- Recent successful CodeQL run: [CodeQL #27243381534](https://github.com/jayceparabellum/secure-cicd-demo/actions/runs/27243381534)
- Recent successful container release run: [Release Container #27243381521](https://github.com/jayceparabellum/secure-cicd-demo/actions/runs/27243381521)
- Published container image: [GHCR package](https://github.com/jayceparabellum/secure-cicd-demo/pkgs/container/secure-cicd-demo)
- Browser UI when running locally: `http://127.0.0.1:8000`
- API docs when running locally: `http://127.0.0.1:8000/docs`
- Main endpoint to review: `POST /analyze`

## What The App Does

`POST /analyze` accepts a JSON object containing HTTP response headers and returns:

- a score from `0` to `100`
- summary counts for passed, weak, and missing headers
- findings with recommendations for each audited header

Audited headers:

- `Strict-Transport-Security`
- `Content-Security-Policy`
- `X-Content-Type-Options`
- `X-Frame-Options`
- `Referrer-Policy`
- `Permissions-Policy`

The app does not fetch target URLs. Callers supply headers directly. This avoids turning the demo into a server-side request forgery risk and keeps tests deterministic.

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000` to use the browser UI, or check `http://127.0.0.1:8000/health`.

## Example Request

```bash
curl -s -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "target": "example.com",
    "headers": {
      "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
      "Content-Security-Policy": "default-src '\''self'\''",
      "X-Content-Type-Options": "nosniff",
      "X-Frame-Options": "DENY",
      "Referrer-Policy": "strict-origin-when-cross-origin",
      "Permissions-Policy": "geolocation=()"
    }
  }'
```

## Test And Security Checks

```bash
ruff check .
bandit -r app -ll
pytest -q
pip-audit -r requirements.txt
```

## Run With Docker

```bash
docker build -t secure-cicd-demo .
docker run --rm -p 8000:8000 secure-cicd-demo
```

Then check:

```bash
curl http://127.0.0.1:8000/health
```

## CI/CD Pipeline

This repository uses GitHub Actions:

- `.github/workflows/ci.yml` runs Ruff, Bandit, pytest, and `pip-audit`.
- `.github/workflows/codeql.yml` runs CodeQL static analysis for Python and uploads code scanning results.
- `.github/workflows/release-container.yml` builds the container image, scans it with Trivy, publishes it to GitHub Container Registry, and attests the published image digest.
- `.github/dependabot.yml` keeps Python dependencies and GitHub Actions updated.

The workflows use least-privilege `GITHUB_TOKEN` permissions and do not require custom repository secrets.

## Deployment

The deploy step publishes a container image to GitHub Container Registry.

On pushes to `main`, the release workflow publishes:

```text
ghcr.io/jayceparabellum/secure-cicd-demo:latest
ghcr.io/jayceparabellum/secure-cicd-demo:sha-<commit>
```

On version tags such as `v1.0.0`, it also publishes:

```text
ghcr.io/jayceparabellum/secure-cicd-demo:1.0.0
```

If anonymous pull access is required for review, the first GHCR package may need to be made public in GitHub's package settings after it is created.

The release workflow also publishes build provenance and SBOM attestations for the image. After the image is pushed, GitHub records an artifact attestation for the published image digest.

## Security Choices

- The app analyzes caller-supplied headers only and does not fetch URLs, reducing SSRF risk.
- CI uses Bandit for Python security linting.
- CI uses `pip-audit` for known vulnerable Python dependencies.
- CodeQL provides static code analysis and code scanning alerts.
- The release workflow scans the built container image with Trivy before pushing to GHCR.
- The Trivy action is pinned to a full commit SHA to reduce third-party action supply-chain risk.
- The release workflow publishes SBOM/provenance metadata and records a GitHub artifact attestation for the image digest.
- The Docker container runs as a non-root user.
- GitHub Actions workflows declare least-privilege permissions.
- Dependabot monitors Python dependencies and GitHub Actions.

## Repository Hardening

The repository is configured with additional GitHub security controls:

- `main` uses branch protection with pull requests required before merge.
- CI and CodeQL checks are required before protected-branch updates.
- Force pushes and branch deletion are blocked on `main`.
- Dependabot alerts and security updates are enabled.
- Secret scanning and push protection are enabled.
- Default GitHub Actions token permissions are read-only at the repository level.
- The GHCR publishing job uses a `ghcr` environment for future deployment protection rules.

## Reproduce The Pipeline

1. Open a pull request to run CI and CodeQL on the proposed change.
2. Merge or push to `main` to run CI, CodeQL, and container publishing.
3. Use `workflow_dispatch` from the Actions tab to manually re-run workflows when needed.
