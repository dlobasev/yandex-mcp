"""Shared fixtures for integration tests."""

import os
from pathlib import Path

import pytest

# Load .env file if it exists
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


def has_direct_token() -> bool:
    return bool(os.environ.get("YANDEX_DIRECT_TOKEN") or os.environ.get("YANDEX_TOKEN"))


def has_metrika_token() -> bool:
    return bool(os.environ.get("YANDEX_METRIKA_TOKEN") or os.environ.get("YANDEX_TOKEN"))


requires_direct = pytest.mark.skipif(
    not has_direct_token(),
    reason="YANDEX_DIRECT_TOKEN or YANDEX_TOKEN not set",
)

requires_metrika = pytest.mark.skipif(
    not has_metrika_token(),
    reason="YANDEX_METRIKA_TOKEN or YANDEX_TOKEN not set",
)