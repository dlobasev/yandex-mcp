"""Integration tests for Yandex Wordstat API tools."""

import json

from tests.conftest import requires_direct

from yandex_mcp.models.wordstat import WordstatTopRequestsInput, WordstatUserInfoInput
from yandex_mcp.tools.wordstat import wordstat_top_requests, wordstat_user_info


@requires_direct
async def test_top_requests_markdown():
    """Get top requests returns valid markdown with query data."""
    result = await wordstat_top_requests(
        WordstatTopRequestsInput(phrase="yandex", num_phrases=5)
    )
    assert isinstance(result, str)
    assert "API Error" not in result
    assert "Wordstat" in result


@requires_direct
async def test_top_requests_json():
    """Get top requests returns valid JSON with topRequests array."""
    result = await wordstat_top_requests(
        WordstatTopRequestsInput(phrase="yandex", num_phrases=5, response_format="json")
    )
    assert isinstance(result, str)
    assert "API Error" not in result
    data = json.loads(result)
    assert "topRequests" in data
    assert "totalCount" in data


@requires_direct
async def test_user_info():
    """User info returns quota information."""
    result = await wordstat_user_info(WordstatUserInfoInput())
    assert isinstance(result, str)
    assert "API Error" not in result
    assert "Daily" in result or "daily" in result