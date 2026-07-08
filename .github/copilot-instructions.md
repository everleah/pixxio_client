# PIXXIO API Python Client - Copilot Instructions

## Scope
- Python client for PIXXIO REST API.
- Resource-oriented architecture; one class per endpoint.
- `openapi.json` is the source of truth.

## Must-Follow Rules
- Reuse base classes in `_base.py`:
  - `ReadOnlyResourceBase` for read-only behavior.
  - `ResourceBase` for CRUD behavior.
  - `ResourceUploadMixin` when upload support is needed.
- Route all HTTP calls through `client.session`.
- Keep resource class names singular; `NAME` must match endpoint path.
- Use base behavior by default; override methods only for endpoint-specific differences.
- Build custom paths with explicit endpoint composition (for example `f"{self.endpoint_base}/..."`).
- Use `response_fields` helpers for response field filtering.

## Response Expectations
- Use objectified responses via existing response utilities.
- Missing attributes should resolve to `None` through `_ResponseObject` behavior.
- 204 responses should map to `SimpleNamespace(success=True)`.

## Resource Change Workflow
1. Validate endpoint contract in `openapi.json`.
2. Mirror existing patterns in `pixxio_client/`.
3. Override only the methods required by API differences.

## Webhook Guidance
- Use `pixxio_client/webhook_parser.py` for webhook payload parsing.
- Prefer snake_case fields in Python usage (camelCase compatibility remains available).
- Keep webhook behavior aligned with docs under `docs/webhook/` and existing tests.

## Critical Project Notes
- `setup.py` currently has a package discovery bug:
  - Current: `find_packages(include=["celum_client*"])`
  - Expected: `find_packages(include=["pixxio_client*"])`
- Invalid API keys currently fail at runtime (no early auth validation).
- Use `files={"file": file_handle}` with `ResourceUploadMixin` uploads.
- Use custom exception hierarchy from `exceptions.py` for API error handling.
- Dynamic webhook fields may need `# type: ignore[attr-defined]`.