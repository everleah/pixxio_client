# AGENTS.md - event_json_examples

## Purpose
- Provide webhook event JSON fixtures for parser tests and documentation examples.

## Ownership
- JSON payload fixtures in event_json_examples/.

## Local Contracts
- Keep fixtures as representative API payload snapshots.
- Preserve existing naming pattern for discoverability and traceability.
- Avoid changing fixture semantics unless parser behavior or API contract requires it.
- Strip credentials before committing: replace any `applicationKey`, token, secret or
  authorization value with a placeholder (captured payloads otherwise publish live keys).

## Work Guidance
- Add new fixtures as additive changes when introducing new event fields/types.
- Keep files valid JSON and avoid editor auto-format churn across unrelated fixtures.

## Verification
- Run webhook parser tests that consume updated fixtures.

## Child DOX Index
- None.
