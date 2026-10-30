# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> **Maintenance note:** this log was not kept current between `0.1` and `0.3`. The
> `0.4.0`–`0.4.2` and `Unreleased` sections were reconstructed from git history in
> October 2026; the `0.1` and `0.2` sections are retrospective summaries because no
> per-release record was ever written for them.

## [0.4.3]

### Added
- `iter_all()` and `get_all()` on all resources to load every page of list endpoints (stops at `quantity`, short pages or `max_items`; guards against endpoints that ignore paging).
- `File.update_and_wait()` updates files and waits for the background job, which the API starts only when more than one file is updated; raises `JobFailedException` for failed jobs.
- Opt-in `max_retries` / `retry_backoff_factor` on `Client` and `Client.create_client()` to retry GET/PUT/DELETE on HTTP 429/503 and connection errors, honouring `Retry-After`.

### Fixed
- Object-valued parameters such as `filter` are now JSON-encoded in GET and DELETE query strings, as the API expects.
- `File.update()` now JSON-encodes all object-valued form fields (`filter`, `location`, `metadataText`, `metadataSelection` and other metadata maps), not only `metadataStandard` / `metadataCustom`.
- `CustomMetadataBuilder` now loads all custom metadata fields instead of only the first page of 50.

## [0.4.2] - 2026-10-14

First public PyPI release. Includes the earlier internal `0.4.2` changes and the
public-release preparation below.

### Security
- Removed all hardcoded credentials from the repository ahead of the open-source release:
  - Test modules read the API key and host from `PIXXIO_TEST_API_KEY` / `PIXXIO_TEST_HOST` through `tests/credentials.py`.
  - Example scripts take credentials from `PIXXIO_API_KEY` / `PIXXIO_HOST` and fail with a clear message when neither the CLI flag nor the environment provides them.
  - `webhook_stub` requires `PIXXIO_WEBHOOK_SECRET` instead of falling back to a built-in signing secret.
  - Redacted the `applicationKey` values captured in `event_json_examples/` fixtures.
  - Replaced demo credentials in `docs/TEST_ENVIRONMENT.md` with placeholders.
  - Anonymized personal data in `event_json_examples/` fixtures and the webhook docs: real user logins, display names and internal user IDs became `demo_*` placeholders.
  - Removed internal hostnames: test and example hosts now come from `PIXXIO_TEST_HOST` / `PIXXIO_HOST` with no defaults, captured host headers in fixtures were replaced with `webhook.example.com`, and deployment docs use placeholders.
- Added `.env.example` documenting every supported environment variable.

### Added
- Added the MIT `LICENSE` file and declared `python_requires >= 3.10` in `setup.py`.
- Added a PEP 517 build configuration, PyPI README/Markdown description, repository and documentation links, search keywords, and SPDX MIT license metadata.
- Added `publish_pypi.ps1` and `requirements-release.txt` for validated wheel/source builds and PyPI uploads using an encrypted local Windows credential; Forgejo publishing remains unchanged.
- Real-world InDesign examples: `examples/analyze_indd_links_com.py`, `apply_pixxio_labels_to_indd.py`, `build_pixxio_image_mapping_csv.py`, `download_collection_assets.py` and `upload_changed_indd_files.py`.
- Webhook payload fixtures in `event_json_examples/` covering file, direct link, metadata, keyword, language, file state, collection, external share, marked-user and license events.
- `AGENTS.md` documentation contracts for the repository root and each major folder.
- `.vscode/settings.json` workspace settings and `diagnose_failing_files.py` helper.
- `tests/credentials.py` shared credential lookup and a complete `tests/README.md` inventory.

### Changed
- Parameterized `webhook_stub/docker-compose.yml` through a local `.env` (`PIXXIO_WEBHOOK_SECRET`, `STUB_HOST`, `STUB_NETWORK`) and added `webhook_stub/.env.example`; dropped the obsolete compose `version` key.
- Rewrote `README.md` against the current API surface: all 27 resource classes, payload builders, webhooks, and complete documentation/example/test indexes.
- Pointed installation, development, repository and issue links at the public GitHub repository and documented installation from PyPI.
- Anchored the `.gitignore` test patterns to the repository root so the test suite under `tests/` is no longer ignored in Git; distribution archives contain the library rather than the repository tests.
- Documented the Python 3.10+ requirement (the `metadata` module uses PEP 604 union syntax).
- Added `pywin32` to `requirements.txt`.
- Turned `docs/README.md` into a real documentation index.

### Removed
- Removed the internal push helper script from version control; it is now covered by the `push_*.bat` entry in `.gitignore`.
- Trimmed `.github/copilot-instructions.md` down to a pointer at the root `AGENTS.md`.

### Fixed

- List requests no longer send pagination parameters to endpoints that do not support them.
- `ReadOnlyResourceBase` gained opt-out pagination handling through the `_paged` flag.
- Disabled pagination for `DownloadFormat`, `FileState`, `LicenseRelease`, `ModelRelease`, `Portal` and `PropertyRelease`.

## [0.4.1] - 2026-05-04

### Fixed
- Refactored response field handling in the file convert path so conversion requests no longer carry an unsupported `responseFields` parameter.

### Documentation
- Expanded `docs/API_REFERENCE.md` and `docs/DEVELOPER_GUIDE.md` with builder usage for collections and the newer resources.
- Updated `examples/basic_usage.py` to the builder-based API.

## [0.4.0] - 2026-04-29

### Added
- Fluent payload builders plus `list()`, `create()` and `update()` convenience methods across the CRUD resources: `Collection`, `DirectLink`, `Directory`, `ExternalShare`, `File`, `License`, `LicenseRelease`, `Model`, `ModelRelease`, `Property`, `PropertyRelease`, `UploadLink`, `User` and `VariantStack`.
- `FileDeleteBuilder` and `File.delete()`.
- `CollectionDeleteBuilder` and `Collection.delete()`.
- Job helpers: `Job.get_status()`, `Job.abort()`, `wait_for_completion()` and `async_wait_for_completion()`.

### Changed
- Reworked response handling in `File` and improved metadata option processing.
- Improved docstrings across the resource modules.

## [0.3] - 2026-04-23

### Fixed
- Prevented automatic `responseFields` injection on specialized GET endpoints that do not support it.
- Added a shared base opt-out mechanism and applied it to:
  - `File.download()` convert endpoints
  - `Directory.get_tree()`
  - `Keyword.download()` CSV endpoint
  - `Synonym.get_columns()`
  - `PortalPage.get()` and `PortalUser.get()`

### Added
- Focused unit tests for response field injection behavior in `tests/response_fields_injection_checks.py`.
- Method-specific response field filtering (`GET_LIST` / `GET_SINGLE`).
- Webhook parser support for metadata field truncate, keyword added and keyword removed events.
- `_ResponseObject` string formatting, `to_dict()`, and graceful handling of missing attributes.

### Documentation
- Added developer guidance for specialized endpoint response field behavior.
- Added error handling notes for response field parameter mismatches.

## [0.2] - 2025-11-12

### Added
- Webhook parser (`pixxio_client/webhook_parser.py`) built around the generalized `EventData` model, plus `pixxio_client/webhook_middleware.py`.
- PIXXIO webhook stub application for local receiver testing, with Docker support, event storage and a web interface.
- HMAC-SHA256 webhook signature verification.
- `File.upload_url_and_wait()` for uploading an asset from a remote URL.
- `FileUpdateBuilder`, `FileUploadBuilder` and `File.update()`.
- Metadata value builders with field validation, bulk add/replace/remove and selection option lookup.
- Per-method response field filtering for `File`.

### Changed
- Added pagination support to `ReadOnlyResourceBase` and the metadata resources.
- Introduced query parameter transformation helpers.
- Consolidated all documentation under `docs/` and added the webhook guides in `docs/webhook/`.

### Fixed
- `CustomMetadata` and `StandardMetadata` now inherit from `ResourceBase`.
- Corrected package discovery in `setup.py`.
- The JSON `Accept` header is now sent with requests.

## [0.1] - 2025-10-02

### Added
- Initial release: `Client` and `Authentication`, `ReadOnlyResourceBase`, `ResourceBase`, `ResourceUploadMixin` and `ResourceJobMixin`.
- Resource classes for all endpoints: files, collections, users, directories, jobs, keywords, licenses, license releases, models, model releases, properties, property releases, variant stacks, upload links, direct links, external shares, portals, file states, download formats, permission groups and metadata.
- Custom exception hierarchy for HTTP status codes and business logic errors.
- OpenAPI-derived type hints, README, API reference and developer documentation.
- Example scripts and an integration test suite.
