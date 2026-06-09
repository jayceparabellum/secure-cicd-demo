from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_read_root() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["app"] == "Security Headers Auditor"


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_strong_headers_returns_perfect_score() -> None:
    response = client.post(
        "/analyze",
        json={
            "target": "example.com",
            "headers": {
                "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
                "Content-Security-Policy": "default-src 'self'",
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "Referrer-Policy": "strict-origin-when-cross-origin",
                "Permissions-Policy": "geolocation=()",
            },
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["target"] == "example.com"
    assert body["score"] == 100
    assert body["summary"] == {"passed": 6, "weak": 0, "missing": 0}
    assert all(item["status"] == "passed" for item in body["findings"])


def test_analyze_missing_headers_returns_missing_findings() -> None:
    response = client.post("/analyze", json={"headers": {}})

    body = response.json()
    assert response.status_code == 200
    assert body["score"] == 0
    assert body["summary"] == {"passed": 0, "weak": 0, "missing": 6}
    assert {item["header"] for item in body["findings"]} == {
        "Strict-Transport-Security",
        "Content-Security-Policy",
        "X-Content-Type-Options",
        "X-Frame-Options",
        "Referrer-Policy",
        "Permissions-Policy",
    }


def test_header_matching_is_case_insensitive() -> None:
    response = client.post(
        "/analyze",
        json={
            "headers": {
                "strict-transport-security": "max-age=31536000",
                "content-security-policy": "default-src 'self'",
                "x-content-type-options": "nosniff",
                "x-frame-options": "sameorigin",
                "referrer-policy": "same-origin",
                "permissions-policy": "camera=()",
            },
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["summary"]["passed"] == 6
    assert body["score"] == 100


def test_weak_csp_with_unsafe_inline_is_marked_weak() -> None:
    response = client.post(
        "/analyze",
        json={
            "headers": {
                "Content-Security-Policy": "default-src 'self' 'unsafe-inline'",
            },
        },
    )

    body = response.json()
    csp_finding = next(
        item for item in body["findings"] if item["header"] == "Content-Security-Policy"
    )
    assert response.status_code == 200
    assert csp_finding["status"] == "weak"
    assert body["summary"]["weak"] == 1
