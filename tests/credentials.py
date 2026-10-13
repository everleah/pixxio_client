"""Credentials and endpoints for the live PIXXIO test environment.

Nothing is stored in the repository. Provide the values through the environment:

* ``PIXXIO_TEST_API_KEY`` - API key for the test environment (required).
* ``PIXXIO_TEST_HOST`` - host of the test system (required).

See ``docs/TEST_ENVIRONMENT.md`` for how to obtain access.
"""

from __future__ import annotations

import os

API_KEY_ENV_VAR = "PIXXIO_TEST_API_KEY"
HOST_ENV_VAR = "PIXXIO_TEST_HOST"


def _require(env_var: str, purpose: str) -> str:
    value = os.environ.get(env_var)
    if not value:
        raise RuntimeError(
            f"{env_var} is not set. Configure the test {purpose} before running this "
            "script; see docs/TEST_ENVIRONMENT.md."
        )
    return value


def require_api_key() -> str:
    """Return the test API key, raising a helpful error when it is not configured."""
    return _require(API_KEY_ENV_VAR, "API key")


def require_test_host() -> str:
    """Return the test host, raising a helpful error when it is not configured."""
    return _require(HOST_ENV_VAR, "host")
