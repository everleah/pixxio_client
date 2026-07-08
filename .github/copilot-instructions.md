# PIXXIO API Python Client - Copilot Instructions

## Project Overview
This repository is a Python client library for the PIXXIO DAM REST API.

- The client is resource-oriented: each API endpoint maps to a resource class.
- The project is in early development; some resources may still be missing.
- Treat `openapi.json` as the source of truth for endpoint contracts.

## Core Architecture

### Base Classes
- `ReadOnlyResourceBase` in `_base.py`: shared GET and response parsing logic.
- `ResourceBase`: extends read-only behavior with POST, PUT, DELETE support.
- `ResourceUploadMixin`: adds file upload support via `upload()`.

### Client Model
- `Client` manages session, auth, and URL composition.
- `Authentication` handles bearer token auth.
- Request base format: `{host}/api/{version}/{resource_name}`.
- Route all requests through `client.session`.

### Response Model
- `Objectifier` converts JSON to `SimpleNamespace`-style objects.
- `_ResponseObject` returns `None` for missing attributes.
- 204 responses should map to `SimpleNamespace(success=True)`.

## Resource Conventions

### Naming
- Resource class names are singular (for example: `File`, `User`, `Keyword`).
- `NAME` must match the API endpoint path (often plural).
- Module filenames are lowercase and aligned to the resource (for example `files.py`).

### Implementation Pattern
- Use base class behavior by default.
- Override only when endpoint behavior differs from standard REST.
- For custom routes, use explicit endpoint construction such as `f"{self.endpoint_base}/..."`.

### Response Field Filtering
- Use `response_fields` to limit returned payload fields.
- Configure with `set_response_fields()` or `set_response_field()`.

## Workflow Guidance

### When Adding or Updating a Resource
1. Verify endpoint details in `openapi.json`.
2. Mirror existing resource patterns in `pixxio_client/`.
3. Override specific HTTP methods only when required.

### Build
```bash
build_wheel.bat
```

### Key Dependencies
- `requests`, `python-dateutil`, `pytz`, `dateparser`
- `requests-toolbelt` for uploads

## API-Specific Notes
- Some operations are async and return `jobID`.
- API supports response field filtering via `responseFields`.
- API supports complex filter objects for search/list endpoints.

## Webhook Parser Status
Webhook parsing is implemented and generalized in `pixxio_client/webhook_parser.py`.

- Supports schema-agnostic event parsing with flexible event data access.
- Supports snake_case access while preserving original camelCase compatibility.
- Includes helper event-type checks (for example file, metadata, language, state, keywords).
- Reference docs live under `docs/webhook/`.
- Regression coverage includes `tests/test_webhook_parser_generalized.py` and payload batch tests.

## Important Notes
- `setup.py` currently includes a package discovery bug:
  - Current: `find_packages(include=["celum_client*"])`
  - Expected: `find_packages(include=["pixxio_client*"])`
- Invalid API keys currently fail at runtime (no early auth validation).
- For uploads, use `files={"file": file_handle}` with `ResourceUploadMixin`.
- API exception handling should use the custom hierarchy in `exceptions.py`.
- For dynamic webhook fields, type checkers may need `# type: ignore[attr-defined]`.