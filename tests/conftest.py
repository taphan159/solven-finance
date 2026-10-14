import os
import typing

import pytest


@pytest.fixture(autouse=True)
def setup_env() -> typing.Generator[None, None, None]:
    """Ensure SOLVEN_SEC_USER_AGENT is set for all tests."""
    os.environ["SOLVEN_SEC_USER_AGENT"] = "TestProject test@example.com"
    yield
    if "SOLVEN_SEC_USER_AGENT" in os.environ:
        del os.environ["SOLVEN_SEC_USER_AGENT"]
