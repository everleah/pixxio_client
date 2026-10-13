# PIXXIO Python Client — Documentation Index

Durable documentation for the PIXXIO Python client. Start with the
[project README](../README.md) for installation, a quick start and the resource overview.

## Reference

| Document | Description |
|----------|-------------|
| [API_REFERENCE.md](API_REFERENCE.md) | `Client`, `Authentication`, base classes, resource classes, builders, response field filtering, logging and best practices |
| [TYPE_SYSTEM.md](TYPE_SYSTEM.md) | Type hints, `PIXXIOResponse`, `JobStatus`/`JobInfo` and the OpenAPI-derived types |
| [ERROR_HANDLING.md](ERROR_HANDLING.md) | Exception hierarchy, HTTP status mapping, recovery patterns and debugging |

## Guides

| Document | Description |
|----------|-------------|
| [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) | Architecture, resource/mixin patterns and the resource change workflow |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution guidelines, environment setup and review expectations |
| [METADATA_BUILDERS.md](METADATA_BUILDERS.md) | Building standard and custom metadata payloads with the metadata builders |
| [ASYNC_OPERATIONS.md](ASYNC_OPERATIONS.md) | How-to guide for synchronous and asynchronous job tracking, including patterns, best practices and troubleshooting |
| [ASYNC_JOBS.md](ASYNC_JOBS.md) | Feature reference for job tracking: job states, `JobInfo`, progress callbacks, job abortion and the `Job`/`ResourceJobMixin` methods |

## Testing

| Document | Description |
|----------|-------------|
| [TEST_ENVIRONMENT.md](TEST_ENVIRONMENT.md) | Live test environment details, credentials, ready-to-run scenarios and safety rules for the shared system |
| [tests/README.md](../tests/README.md) | Test suite inventory and instructions for individual test modules |

## Webhooks

| Document | Description |
|----------|-------------|
| [webhook/README.md](webhook/README.md) | Parser overview, event structure and field access patterns |
| [webhook/QUICK_START.md](webhook/QUICK_START.md) | Five-minute introduction to parsing PIXXIO webhooks |
| [webhook/PARSER_IMPLEMENTATION.md](webhook/PARSER_IMPLEMENTATION.md) | Parser architecture, usage patterns and migration notes |
| [webhook/USAGE_EXAMPLES.md](webhook/USAGE_EXAMPLES.md) | Practical handlers: logging, metadata handling, SQLAlchemy and FastAPI |

Related material outside this folder:

- [webhook_stub/](../webhook_stub/README.md) — FastAPI receiver for local webhook testing, with its own setup, deployment, usage and security docs.
- [event_json_examples/](../event_json_examples) — captured webhook payload fixtures used by the parser tests.

## Related

- [Root README](../README.md) — installation, quick start, resource and builder overview
- [CHANGELOG](../CHANGELOG.md) — release history
- [examples/](../examples) — runnable example scripts, including the InDesign/COM workflows
- [AGENTS.md](../AGENTS.md) — repository documentation contracts
