# Secure CI/CD Demo

A small FastAPI service that demonstrates a security-minded CI/CD baseline with automated tests, dependency updates, CodeQL scanning, and container publishing to GitHub Container Registry.

## Project Structure

```text
secure-cicd-demo/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml
│   │   ├── codeql.yml
│   │   └── release-container.yml
│   └── dependabot.yml
├── app/
│   ├── main.py
│   └── __init__.py
├── tests/
│   └── test_main.py
├── Dockerfile
├── .dockerignore
├── requirements.txt
├── README.md
└── LICENSE
```

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://localhost:8000` or check `http://localhost:8000/health`.

## Test

```bash
pytest
```

## Build Container

```bash
docker build -t secure-cicd-demo .
docker run --rm -p 8000:8000 secure-cicd-demo
```

## CI/CD

- `ci.yml` installs dependencies and runs the test suite on pushes and pull requests.
- `codeql.yml` runs CodeQL analysis for Python on pushes, pull requests, and a weekly schedule.
- `release-container.yml` publishes tagged releases to GitHub Container Registry.
- `dependabot.yml` keeps Python packages, Docker base images, and GitHub Actions current.
