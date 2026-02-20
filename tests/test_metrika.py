"""Integration tests for Yandex Metrika API tools."""

import json

from tests.conftest import requires_metrika

from yandex_mcp.models.metrika import GetCountersInput, GetGoalsInput
from yandex_mcp.tools.metrika_counters import metrika_get_counters
from yandex_mcp.tools.metrika_goals import metrika_get_goals


@requires_metrika
async def test_get_counters_markdown():
    """Get counters returns valid markdown response."""
    result = await metrika_get_counters(GetCountersInput())
    assert isinstance(result, str)
    assert "Counters" in result or "No counters found" in result
    assert "API Error" not in result


@requires_metrika
async def test_get_counters_json():
    """Get counters returns valid JSON with counter list."""
    result = await metrika_get_counters(GetCountersInput(response_format="json"))
    assert isinstance(result, str)
    assert "API Error" not in result
    data = json.loads(result)
    assert "counters" in data
    assert "total" in data
    assert isinstance(data["counters"], list)


@requires_metrika
async def test_get_goals_for_first_counter():
    """Get goals for a real counter returns valid response."""
    # First get a counter ID
    counters_result = await metrika_get_counters(GetCountersInput(response_format="json"))
    data = json.loads(counters_result)
    counters = data.get("counters", [])
    if not counters:
        return  # No counters — nothing to test

    counter_id = counters[0]["id"]
    result = await metrika_get_goals(GetGoalsInput(counter_id=counter_id))
    assert isinstance(result, str)
    assert "API Error" not in result
    # Either has goals or says none configured
    assert "Goals" in result or "No goals" in result