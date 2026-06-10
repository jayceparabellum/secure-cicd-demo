from typing import Literal

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
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

INDEX_HTML = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Security Headers Auditor</title>
    <style>
      :root {
        color-scheme: light;
        --bg: #f5f7fb;
        --panel: #ffffff;
        --ink: #18202f;
        --muted: #667085;
        --line: #d9e0ea;
        --accent: #0f766e;
        --accent-strong: #0b5f59;
        --warn: #b45309;
        --bad: #b42318;
        --good: #087443;
        --soft-good: #e8f7ef;
        --soft-warn: #fff4df;
        --soft-bad: #ffefed;
        --shadow: 0 20px 50px rgba(24, 32, 47, 0.08);
      }

      * {
        box-sizing: border-box;
      }

      body {
        margin: 0;
        min-height: 100vh;
        background:
          linear-gradient(180deg, #eef3f8 0%, var(--bg) 44%, #ffffff 100%);
        color: var(--ink);
        font-family:
          Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
          "Segoe UI", sans-serif;
      }

      header {
        border-bottom: 1px solid var(--line);
        background: rgba(255, 255, 255, 0.84);
        backdrop-filter: blur(14px);
      }

      .shell {
        width: min(1120px, calc(100% - 32px));
        margin: 0 auto;
      }

      .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        min-height: 72px;
      }

      .brand {
        display: flex;
        align-items: center;
        gap: 12px;
        min-width: 0;
      }

      .mark {
        display: grid;
        width: 42px;
        height: 42px;
        place-items: center;
        border-radius: 8px;
        background: var(--accent);
        color: #ffffff;
        font-weight: 800;
      }

      h1 {
        margin: 0;
        font-size: 22px;
        line-height: 1.15;
      }

      .subtle {
        margin: 4px 0 0;
        color: var(--muted);
        font-size: 14px;
      }

      .status {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        min-height: 36px;
        padding: 0 12px;
        border: 1px solid var(--line);
        border-radius: 8px;
        background: #ffffff;
        color: var(--muted);
        font-size: 14px;
        white-space: nowrap;
      }

      .dot {
        width: 9px;
        height: 9px;
        border-radius: 999px;
        background: #98a2b3;
      }

      .dot.ok {
        background: var(--good);
      }

      main {
        padding: 36px 0 44px;
      }

      .layout {
        display: grid;
        grid-template-columns: minmax(0, 1.08fr) minmax(320px, 0.92fr);
        gap: 22px;
        align-items: start;
      }

      .panel {
        border: 1px solid var(--line);
        border-radius: 8px;
        background: var(--panel);
        box-shadow: var(--shadow);
      }

      .panel-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        padding: 18px 20px;
        border-bottom: 1px solid var(--line);
      }

      h2 {
        margin: 0;
        font-size: 17px;
        line-height: 1.25;
      }

      .panel-body {
        padding: 20px;
      }

      label {
        display: block;
        margin-bottom: 8px;
        color: #344054;
        font-size: 14px;
        font-weight: 650;
      }

      input,
      textarea {
        width: 100%;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        background: #ffffff;
        color: var(--ink);
        font: inherit;
        outline: none;
      }

      input {
        height: 42px;
        padding: 0 12px;
      }

      textarea {
        min-height: 260px;
        resize: vertical;
        padding: 12px;
        font-family:
          "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
        font-size: 13px;
        line-height: 1.5;
      }

      input:focus,
      textarea:focus {
        border-color: var(--accent);
        box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.14);
      }

      .field {
        margin-bottom: 18px;
      }

      .toolbar {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
      }

      button,
      a.button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 40px;
        padding: 0 14px;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        background: #ffffff;
        color: #344054;
        cursor: pointer;
        font: inherit;
        font-weight: 650;
        text-decoration: none;
      }

      button.primary {
        border-color: var(--accent);
        background: var(--accent);
        color: #ffffff;
      }

      button.primary:hover {
        background: var(--accent-strong);
      }

      button:hover,
      a.button:hover {
        border-color: #94a3b8;
      }

      .score-card {
        display: grid;
        grid-template-columns: 130px 1fr;
        gap: 18px;
        align-items: center;
      }

      .score-ring {
        display: grid;
        width: 128px;
        height: 128px;
        place-items: center;
        border-radius: 50%;
        background:
          conic-gradient(var(--accent) calc(var(--score) * 1%), #e6ebf2 0);
      }

      .score-inner {
        display: grid;
        width: 98px;
        height: 98px;
        place-items: center;
        border-radius: 50%;
        background: #ffffff;
        box-shadow: inset 0 0 0 1px var(--line);
      }

      .score-value {
        font-size: 32px;
        font-weight: 800;
      }

      .summary {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 10px;
        margin-top: 14px;
      }

      .metric {
        padding: 12px;
        border: 1px solid var(--line);
        border-radius: 8px;
        background: #fafbfc;
      }

      .metric strong {
        display: block;
        font-size: 22px;
      }

      .metric span {
        color: var(--muted);
        font-size: 13px;
      }

      .findings {
        display: grid;
        gap: 10px;
        margin-top: 18px;
      }

      .finding {
        padding: 14px;
        border: 1px solid var(--line);
        border-radius: 8px;
        background: #ffffff;
      }

      .finding-top {
        display: flex;
        justify-content: space-between;
        gap: 10px;
        align-items: center;
      }

      .finding h3 {
        margin: 0;
        font-size: 15px;
      }

      .badge {
        min-width: 72px;
        padding: 5px 8px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 800;
        text-align: center;
        text-transform: uppercase;
      }

      .badge.passed {
        background: var(--soft-good);
        color: var(--good);
      }

      .badge.weak {
        background: var(--soft-warn);
        color: var(--warn);
      }

      .badge.missing {
        background: var(--soft-bad);
        color: var(--bad);
      }

      .finding p {
        margin: 10px 0 0;
        color: var(--muted);
        font-size: 14px;
        line-height: 1.45;
      }

      .error {
        display: none;
        margin-top: 12px;
        padding: 12px;
        border: 1px solid #fecaca;
        border-radius: 8px;
        background: #fff1f2;
        color: var(--bad);
        font-size: 14px;
      }

      .empty {
        border: 1px dashed #cbd5e1;
        border-radius: 8px;
        padding: 22px;
        color: var(--muted);
        text-align: center;
      }

      @media (max-width: 860px) {
        .layout,
        .score-card {
          grid-template-columns: 1fr;
        }

        .topbar {
          align-items: flex-start;
          flex-direction: column;
          padding: 16px 0;
        }
      }
    </style>
  </head>
  <body>
    <header>
      <div class="shell topbar">
        <div class="brand">
          <div class="mark">SH</div>
          <div>
            <h1>Security Headers Auditor</h1>
            <p class="subtle">Score caller-supplied HTTP response headers without fetching URLs.</p>
          </div>
        </div>
        <div class="status" id="serviceStatus"><span class="dot"></span><span>Checking service</span></div>
      </div>
    </header>

    <main class="shell">
      <div class="layout">
        <section class="panel">
          <div class="panel-header">
            <h2>Audit Input</h2>
            <a class="button" href="/docs">API Docs</a>
          </div>
          <div class="panel-body">
            <div class="field">
              <label for="target">Target label</label>
              <input id="target" value="example.com" autocomplete="off">
            </div>
            <div class="field">
              <label for="headers">Response headers</label>
              <textarea id="headers" spellcheck="false"></textarea>
            </div>
            <div class="toolbar">
              <button class="primary" id="analyzeButton" type="button">Analyze Headers</button>
              <button id="sampleStrong" type="button">Strong Sample</button>
              <button id="sampleWeak" type="button">Weak Sample</button>
              <button id="clearButton" type="button">Clear</button>
            </div>
            <div class="error" id="errorBox"></div>
          </div>
        </section>

        <section class="panel">
          <div class="panel-header">
            <h2>Audit Results</h2>
          </div>
          <div class="panel-body" id="results">
            <div class="empty">Run an audit to see score, counts, findings, and recommendations.</div>
          </div>
        </section>
      </div>
    </main>

    <script>
      const strongHeaders = `Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=()`;

      const weakHeaders = `Content-Security-Policy: default-src 'self' 'unsafe-inline'
X-Frame-Options: ALLOWALL
Referrer-Policy: unsafe-url`;

      const headersInput = document.querySelector("#headers");
      const targetInput = document.querySelector("#target");
      const results = document.querySelector("#results");
      const errorBox = document.querySelector("#errorBox");
      const statusBox = document.querySelector("#serviceStatus");

      headersInput.value = strongHeaders;

      function parseHeaders(text) {
        const headers = {};
        for (const rawLine of text.split(/\\r?\\n/)) {
          const line = rawLine.trim();
          if (!line) continue;
          const separator = line.indexOf(":");
          if (separator === -1) {
            throw new Error(`Header line is missing a colon: ${line}`);
          }
          const name = line.slice(0, separator).trim();
          const value = line.slice(separator + 1).trim();
          if (!name) {
            throw new Error("Header name cannot be empty.");
          }
          headers[name] = value;
        }
        return headers;
      }

      function escapeHtml(value) {
        return String(value)
          .replace(/&/g, "&amp;")
          .replace(/</g, "&lt;")
          .replace(/>/g, "&gt;")
          .replace(/"/g, "&quot;")
          .replace(/'/g, "&#039;");
      }

      function showError(message) {
        errorBox.textContent = message;
        errorBox.style.display = "block";
      }

      function clearError() {
        errorBox.textContent = "";
        errorBox.style.display = "none";
      }

      function renderResults(data) {
        const findings = data.findings
          .map((item) => `
            <article class="finding">
              <div class="finding-top">
                <h3>${escapeHtml(item.header)}</h3>
                <span class="badge ${escapeHtml(item.status)}">${escapeHtml(item.status)}</span>
              </div>
              <p>${escapeHtml(item.message)}</p>
              <p><strong>Recommendation:</strong> ${escapeHtml(item.recommendation)}</p>
            </article>
          `)
          .join("");

        results.innerHTML = `
          <div class="score-card">
            <div class="score-ring" style="--score: ${data.score}">
              <div class="score-inner">
                <div class="score-value">${data.score}</div>
              </div>
            </div>
            <div>
              <h2>${escapeHtml(data.target || "Untitled audit")}</h2>
              <p class="subtle">Score is based on passed, weak, and missing security headers.</p>
              <div class="summary">
                <div class="metric"><strong>${data.summary.passed}</strong><span>Passed</span></div>
                <div class="metric"><strong>${data.summary.weak}</strong><span>Weak</span></div>
                <div class="metric"><strong>${data.summary.missing}</strong><span>Missing</span></div>
              </div>
            </div>
          </div>
          <div class="findings">${findings}</div>
        `;
      }

      async function analyze() {
        clearError();
        let headers;
        try {
          headers = parseHeaders(headersInput.value);
        } catch (error) {
          showError(error.message);
          return;
        }

        const response = await fetch("/analyze", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            target: targetInput.value.trim() || null,
            headers,
          }),
        });

        if (!response.ok) {
          showError(`Audit failed with HTTP ${response.status}.`);
          return;
        }

        renderResults(await response.json());
      }

      async function checkHealth() {
        try {
          const response = await fetch("/health");
          if (!response.ok) throw new Error("Health check failed");
          statusBox.innerHTML = '<span class="dot ok"></span><span>Service online</span>';
        } catch {
          statusBox.innerHTML = '<span class="dot"></span><span>Service unavailable</span>';
        }
      }

      document.querySelector("#analyzeButton").addEventListener("click", analyze);
      document.querySelector("#sampleStrong").addEventListener("click", () => {
        targetInput.value = "example.com";
        headersInput.value = strongHeaders;
        analyze();
      });
      document.querySelector("#sampleWeak").addEventListener("click", () => {
        targetInput.value = "legacy.example";
        headersInput.value = weakHeaders;
        analyze();
      });
      document.querySelector("#clearButton").addEventListener("click", () => {
        targetInput.value = "";
        headersInput.value = "";
        results.innerHTML = '<div class="empty">Run an audit to see score, counts, findings, and recommendations.</div>';
        clearError();
      });

      checkHealth();
      analyze();
    </script>
  </body>
</html>
"""


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


@app.get("/", response_class=HTMLResponse)
def read_root() -> str:
    return INDEX_HTML


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
