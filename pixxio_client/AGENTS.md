# AGENTS.md - pixxio_client package

## Purpose
- Own the Python API client implementation for PIXXIO endpoints.
- Keep endpoint resources aligned with openapi.json and runtime behavior.

## Ownership
- Resource classes in this folder.
- Shared client behavior in _base.py and response handling utilities.

## Local Contracts
- Keep one resource class per endpoint and keep class naming singular.
- Ensure NAME matches endpoint path conventions.
- Reuse ReadOnlyResourceBase, ResourceBase, and ResourceUploadMixin instead of duplicating HTTP logic.
- Route all HTTP calls through client.session.
- Use objectified responses and preserve 204 -> SimpleNamespace(success=True).
- Keep endpoint paging behavior aligned with API constraints; disable paging per resource when API rejects paging params.

## Work Guidance
- Validate endpoint behavior against openapi.json before changes.
- Prefer minimal, backward-compatible edits.
- Override base methods only for endpoint-specific differences.
- Keep path composition explicit (for example: f"{self.endpoint_base}/...").

## Verification
- Run targeted tests covering changed resources.
- For broad client changes, run pytest from repository root.

## Child DOX Index
- None.
