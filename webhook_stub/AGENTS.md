# AGENTS.md - webhook_stub

## Purpose
- Own local webhook receiver stub and related deployment/test assets.

## Ownership
- Application code, container files, and operational docs under webhook_stub/.

## Local Contracts
- Keep local run paths (Windows batch and shell scripts) working for developer testing.
- Keep Docker and compose definitions consistent with documented startup flows.
- Preserve signature/security test behavior unless intentionally changed.
- Read secrets (for example the webhook signing secret) from the environment; never hardcode them in code, compose files or docs.

## Work Guidance
- Prefer explicit configuration and reproducible local startup commands.
- Update README/SETUP/TROUBLESHOOTING docs together when runtime behavior changes.

## Verification
- Run relevant webhook_stub tests when modifying app or signature handling.
- Validate container startup commands when touching Docker or compose files.

## Child DOX Index
- None.
