# Changelog

All notable changes to this project will be documented in this file.

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

### Documentation
- Added developer guidance for specialized endpoint response field behavior.
- Added error handling notes for response field parameter mismatches.
