"""Credentials and endpoints for the live PIXXIO test environment.

Nothing is stored in the repository. Provide the values through the environment:

* ``PIXXIO_TEST_API_KEY`` - API key for the test environment (required).
* ``PIXXIO_TEST_HOST`` - test host, defaults to the shared demo system.

See ``docs/TEST_ENVIRONMENT.md`` for how to obtain credentials.
"""

from __future__ import annotations

import os

DEFAULT_TEST_HOST = "hoerl-demo.px.media"

API_KEY_ENV_VAR = "PIXXIO_TEST_API_KEY"
HOST_ENV_VAR = "PIXXIO_TEST_HOST"


def require_api_key(env_var: str = API_KEY_ENV_VAR) -> str:
    """Return the test API key, raising a helpful error when it is not configured."""
    api_key = os.environ.get(env_var)
    if not api_key:
        raise RuntimeError(
            f"{env_var} is not set. Configure the PIXXIO test environment before "
            "running this script; see docs/TEST_ENVIRONMENT.md."
        )
    return api_key


def test_host() -> str:
    """Return the test host, falling back to the shared demo environment."""
    return os.environ.get(HOST_ENV_VAR) or DEFAULT_TEST_HOST
