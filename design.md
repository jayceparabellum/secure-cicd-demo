# Design Notes

## Purpose

Secure CI/CD Demo is primarily a pipeline demonstration, so the interface is intentionally lightweight. The UI exists to make the Security Headers Auditor easy to demo in a browser while keeping the API and CI/CD workflows as the main focus.

## Product Shape

The app audits caller-supplied HTTP response headers. Users paste headers into the browser UI, click **Analyze Headers**, and receive:

- an overall score
- passed, weak, and missing counts
- per-header findings
- practical recommendations

The app does not fetch remote URLs. That is a deliberate security choice to avoid introducing server-side request forgery risk into a CI/CD demo.

## UI Goals

- Make the local demo understandable in under a minute.
- Preserve the existing `POST /analyze` API contract.
- Avoid a frontend build system or extra runtime dependencies.
- Keep the visual design professional but quiet, closer to a security tool than a marketing page.
- Make strong and weak sample data available for quick proof during review.

## Layout

The page uses a two-column layout on desktop:

- **Audit Input** on the left for target label, pasted headers, and action buttons.
- **Audit Results** on the right for score, summary metrics, and findings.

On smaller screens, the layout collapses into a single column so the tool remains usable on narrow browser windows.

## Visual Style

The design uses a restrained palette:

- white panels on a light gray-blue background
- teal as the primary action and score color
- green, amber, and red status colors for passed, weak, and missing findings

Panels use small-radius borders, clear spacing, and simple status badges so the page reads like an operational security utility.

## Interaction Model

The browser UI is a thin client over the existing API:

1. Parse pasted `Header-Name: value` lines in the browser.
2. Submit JSON to `POST /analyze`.
3. Render the returned score, summary, and findings.

The **Strong Sample** and **Weak Sample** buttons populate example inputs and immediately run the audit. This gives reviewers a fast way to see both successful and risky results.

## Accessibility And Usability

- Form controls have visible labels.
- Buttons use clear command text.
- Status badges use text as well as color.
- The service status indicator checks `GET /health`.
- Error messages are shown inline when pasted header lines are malformed.

## Known Tradeoffs

- The UI is embedded directly in `app/main.py` to keep the project small.
- There is no separate frontend framework, bundler, or static asset pipeline.
- The UI is meant for demonstration and local review, not as a full production console.

If this were production work, the UI would likely move into separate templates or static assets, add fuller accessibility testing, and include more robust client-side validation and error states.
