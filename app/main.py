from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field

FindingStatus = Literal["passed", "weak", "missing"]


class AnalyzeRequest(BaseModel):
    target: str | None = Field(default=None, examples=["example.com"])
    headers: dict[str, str] = Field(default_factory=dict)


class Finding(BaseModel):
    header: str
    status: FindingStatus
    message: str
    recommendation: str


class Summary(BaseModel):
    passed: int
    weak: int
    missing: int


class AnalyzeResponse(BaseModel):
    target: str | None
    score: int
    summary: Summary
    findings: list[Finding]


app = FastAPI(
    title="Security Headers Auditor",
    description="Audit caller-supplied HTTP response headers for common security protections.",
)


def normalize_headers(headers: dict[str, str]) -> dict[str, str]:
    return {name.strip().lower(): value.strip() for name, value in headers.items()}


def find_header(headers: dict[str, str], header_name: str) -> str | None:
    value = headers.get(header_name.lower())
    return value if value else None


def finding(
    header: str,
    status: FindingStatus,
    message: str,
    recommendation: str,
) -> Finding:
    return Finding(
        header=header,
        status=status,
        message=message,
        recommendation=recommendation,
    )


def audit_hsts(headers: dict[str, str]) -> Finding:
    header = "Strict-Transport-Security"
    value = find_header(headers, header)
    if value is None:
        return finding(
            header,
            "missing",
            "HSTS is not configured.",
            "Add Strict-Transport-Security with a long max-age.",
        )

    lowered = value.lower()
    if "max-age=" not in lowered:
        return finding(
            header,
            "weak",
            "HSTS is present without max-age.",
            "Set max-age to at least 31536000 seconds.",
        )

    try:
        max_age_part = next(
            part for part in lowered.split(";") if part.strip().startswith("max-age=")
        )
        max_age = int(max_age_part.split("=", 1)[1].strip())
    except (StopIteration, ValueError):
        return finding(
            header,
            "weak",
            "HSTS max-age is not a valid integer.",
            "Use max-age=31536000 or greater.",
        )

    if max_age < 31_536_000:
        return finding(
            header,
            "weak",
            "HSTS max-age is shorter than one year.",
            "Use max-age=31536000 or greater.",
        )

    return finding(
        header,
        "passed",
        "HSTS is configured with a strong max-age.",
        "Keep HSTS enabled for HTTPS sites.",
    )


def audit_csp(headers: dict[str, str]) -> Finding:
    header = "Content-Security-Policy"
    value = find_header(headers, header)
    if value is None:
        return finding(
            header,
            "missing",
            "Content Security Policy is not configured.",
            "Add a restrictive CSP such as default-src 'self'.",
        )

    lowered = value.lower()
    weak_directives = ["'unsafe-inline'", "'unsafe-eval'", "default-src *"]
    if any(directive in lowered for directive in weak_directives):
        return finding(
            header,
            "weak",
            "CSP contains a permissive directive.",
            "Remove unsafe directives and restrict sources.",
        )

    return finding(
        header,
        "passed",
        "CSP is present without obvious unsafe directives.",
        "Keep refining CSP for the application asset model.",
    )


def audit_content_type_options(headers: dict[str, str]) -> Finding:
    header = "X-Content-Type-Options"
    value = find_header(headers, header)
    if value is None:
        return finding(
            header,
            "missing",
            "MIME sniffing protection is not configured.",
            "Set X-Content-Type-Options to nosniff.",
        )

    if value.lower() != "nosniff":
        return finding(
            header,
            "weak",
            "X-Content-Type-Options is not set to nosniff.",
            "Use X-Content-Type-Options: nosniff.",
        )

    return finding(
        header,
        "passed",
        "MIME sniffing protection is enabled.",
        "Keep nosniff enabled.",
    )


def audit_frame_options(headers: dict[str, str]) -> Finding:
    header = "X-Frame-Options"
    value = find_header(headers, header)
    if value is None:
        return finding(
            header,
            "missing",
            "Clickjacking protection is not configured.",
            "Set X-Frame-Options to DENY or SAMEORIGIN.",
        )

    if value.upper() not in {"DENY", "SAMEORIGIN"}:
        return finding(
            header,
            "weak",
            "X-Frame-Options uses an unsupported or weak value.",
            "Use DENY or SAMEORIGIN.",
        )

    return finding(
        header,
        "passed",
        "Clickjacking protection is configured.",
        "Keep frame protection enabled.",
    )


def audit_referrer_policy(headers: dict[str, str]) -> Finding:
    header = "Referrer-Policy"
    value = find_header(headers, header)
    if value is None:
        return finding(
            header,
            "missing",
            "Referrer policy is not configured.",
            "Use strict-origin-when-cross-origin or stricter.",
        )

    policy = value.lower()
    strong_values = {
        "no-referrer",
        "same-origin",
        "strict-origin",
        "strict-origin-when-cross-origin",
    }
    if policy not in strong_values:
        return finding(
            header,
            "weak",
            "Referrer policy may expose more information than needed.",
            "Use strict-origin-when-cross-origin or stricter.",
        )

    return finding(
        header,
        "passed",
        "Referrer policy is restrictive.",
        "Keep a restrictive referrer policy.",
    )


def audit_permissions_policy(headers: dict[str, str]) -> Finding:
    header = "Permissions-Policy"
    value = find_header(headers, header)
    if value is None:
        return finding(
            header,
            "missing",
            "Permissions Policy is not configured.",
            "Disable unused browser features, for example geolocation=().",
        )

    lowered = value.lower()
    if not lowered or "=*" in lowered or "=(*)" in lowered:
        return finding(
            header,
            "weak",
            "Permissions Policy appears overly broad.",
            "Restrict powerful browser features to only what is required.",
        )

    return finding(
        header,
        "passed",
        "Permissions Policy is configured.",
        "Keep browser feature permissions restrictive.",
    )


AUDIT_RULES = [
    audit_hsts,
    audit_csp,
    audit_content_type_options,
    audit_frame_options,
    audit_referrer_policy,
    audit_permissions_policy,
]


def calculate_score(findings: list[Finding]) -> int:
    if not findings:
        return 0

    points = {"passed": 1.0, "weak": 0.5, "missing": 0.0}
    earned = sum(points[item.status] for item in findings)
    return round((earned / len(findings)) * 100)


@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "app": "Security Headers Auditor",
        "message": "Submit caller-supplied HTTP response headers to POST /analyze.",
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_headers(request: AnalyzeRequest) -> AnalyzeResponse:
    headers = normalize_headers(request.headers)
    findings = [rule(headers) for rule in AUDIT_RULES]
    summary = Summary(
        passed=sum(item.status == "passed" for item in findings),
        weak=sum(item.status == "weak" for item in findings),
        missing=sum(item.status == "missing" for item in findings),
    )

    return AnalyzeResponse(
        target=request.target,
        score=calculate_score(findings),
        summary=summary,
        findings=findings,
    )
