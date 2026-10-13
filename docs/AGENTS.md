# AGENTS.md - docs

## Purpose
- Own durable user and developer documentation for the PIXXIO client.

## Ownership
- Markdown documentation in this folder except child webhook docs scope.

## Local Contracts
- Keep docs consistent with current client behavior and openapi.json.
- Document only supported behavior already present in code or API contracts.
- When behavior changes, update affected docs in the same change set.
- `README.md` is this folder's index; update it whenever a document is added, renamed or removed.

## Work Guidance
- Prefer concise, task-oriented sections with concrete examples.
- Preserve existing document structure unless a restructure is requested.
- Cross-reference webhook-specific material to docs/webhook where applicable.

## Verification
- Manually verify links and command snippets touched by edits.
- Ensure examples are syntactically valid for Python client usage.

## Child DOX Index
- docs/webhook/AGENTS.md: Webhook parser and webhook event docs.
