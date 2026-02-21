"""Integration tests for Yandex Direct API tools."""

import json

from tests.conftest import requires_direct

from yandex_mcp.models.direct import GetCampaignsInput, GetImagesInput
from yandex_mcp.tools.direct_campaigns import direct_get_campaigns
from yandex_mcp.tools.direct_images import direct_get_images


@requires_direct
async def test_get_campaigns_markdown():
    """Get campaigns returns valid markdown response."""
    result = await direct_get_campaigns(GetCampaignsInput(limit=5))
    assert isinstance(result, str)
    # Either has campaigns or says none found — both are valid
    assert "Campaigns" in result or "No campaigns found" in result
    assert "API Error" not in result


@requires_direct
async def test_get_campaigns_json():
    """Get campaigns returns valid JSON response."""
    result = await direct_get_campaigns(
        GetCampaignsInput(limit=5, response_format="json")
    )
    assert isinstance(result, str)
    assert "API Error" not in result
    data = json.loads(result)
    assert "campaigns" in data
    assert "total" in data
    assert isinstance(data["campaigns"], list)


@requires_direct
async def test_get_images_markdown():
    """Get images returns valid markdown response."""
    result = await direct_get_images(GetImagesInput(limit=5))
    assert isinstance(result, str)
    assert "Images" in result or "No images found" in result
    assert "API Error" not in result


@requires_direct
async def test_get_images_json():
    """Get images returns valid JSON response."""
    result = await direct_get_images(
        GetImagesInput(limit=5, response_format="json")
    )
    assert isinstance(result, str)
    assert "API Error" not in result
    data = json.loads(result)
    assert "images" in data
    assert "total" in data
    assert isinstance(data["images"], list)