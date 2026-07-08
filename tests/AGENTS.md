# AGENTS.md - tests

## Purpose
- Own test coverage for client behavior, resource contracts, and parser functionality.

## Ownership
- Test modules under tests/.

## Local Contracts
- Tests should validate real client behavior, not implementation internals when avoidable.
- Prefer deterministic tests with explicit setup and clear assertions.
- Keep fixture usage aligned with event_json_examples and in-repo test data.

## Work Guidance
- Add or update targeted tests for each behavior change.
- Reuse existing test patterns before introducing new helper abstractions.

## Verification
- Run affected tests first.
- Run full pytest when modifying shared client or parser behavior.

## Child DOX Index
- None.
