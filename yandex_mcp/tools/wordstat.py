"""Yandex Wordstat API tools."""

import json
from typing import Any

from yandex_mcp.client import api_client
from yandex_mcp.enums import ResponseFormat
from yandex_mcp.errors import handle_api_error
from yandex_mcp.formatters import (
    format_wordstat_dynamics_markdown,
    format_wordstat_regions_markdown,
    format_wordstat_top_requests_markdown,
)
from yandex_mcp.models.wordstat import (
    WordstatDynamicsInput,
    WordstatRegionsInput,
    WordstatRegionsTreeInput,
    WordstatTopRequestsInput,
    WordstatUserInfoInput,
)
from yandex_mcp.server import mcp


@mcp.tool(
    name="wordstat_top_requests",
    annotations={
        "title": "Get Popular Queries from Yandex Wordstat",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def wordstat_top_requests(params: WordstatTopRequestsInput) -> str:
    """Get popular search queries containing a phrase from Yandex Wordstat.

    Returns top queries and associated phrases with their search frequency
    for the last 30 days. Supports Yandex query language operators.

    Examples:
    - phrase="buy laptop" — queries containing "buy laptop"
    - phrase='"buy laptop"' — exact match only
    - phrase="+buy +laptop" — both words required

    Args:
        params: Search phrase(s) and filters

    Returns:
        Top requests with counts in markdown or JSON format
    """
    try:
        data: dict[str, Any] = {}
        if params.phrase is not None:
            data["phrase"] = params.phrase
        if params.phrases is not None:
            data["phrases"] = params.phrases
        data["numPhrases"] = params.num_phrases
        if params.regions is not None:
            data["regions"] = params.regions
        if params.devices is not None:
            data["devices"] = params.devices

        result = await api_client.wordstat_request("/v1/topRequests", data=data)

        if params.response_format == ResponseFormat.JSON:
            return json.dumps(result, indent=2, ensure_ascii=False)

        return format_wordstat_top_requests_markdown(result)

    except Exception as e:
        return handle_api_error(e)


@mcp.tool(
    name="wordstat_dynamics",
    annotations={
        "title": "Get Query Dynamics from Yandex Wordstat",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def wordstat_dynamics(params: WordstatDynamicsInput) -> str:
    """Get frequency dynamics of a search query over time.

    Returns how the number of queries changed over the specified period.
    Only the + operator is allowed in the phrase.

    Date constraints:
    - daily: last 60 days only
    - weekly: from_date must be Monday, to_date must be Sunday
    - monthly: from_date must be 1st, to_date must be last day of month

    Args:
        params: Phrase, period type, and date range

    Returns:
        Time series with count and share in markdown or JSON format
    """
    try:
        data: dict[str, Any] = {
            "phrase": params.phrase,
            "period": params.period,
            "fromDate": params.from_date,
        }
        if params.to_date is not None:
            data["toDate"] = params.to_date
        if params.regions is not None:
            data["regions"] = params.regions
        if params.devices is not None:
            data["devices"] = params.devices

        result = await api_client.wordstat_request("/v1/dynamics", data=data)

        if params.response_format == ResponseFormat.JSON:
            return json.dumps(result, indent=2, ensure_ascii=False)

        return format_wordstat_dynamics_markdown(result)

    except Exception as e:
        return handle_api_error(e)


@mcp.tool(
    name="wordstat_regions",
    annotations={
        "title": "Get Regional Distribution from Yandex Wordstat",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def wordstat_regions(params: WordstatRegionsInput) -> str:
    """Get regional distribution of search queries for the last 30 days.

    Returns how queries are distributed across regions with affinity index.
    Affinity index > 100 means the region has higher interest than average.

    Args:
        params: Phrase and region granularity

    Returns:
        Regional distribution with counts and affinity in markdown or JSON format
    """
    try:
        data: dict[str, Any] = {
            "phrase": params.phrase,
            "regionType": params.region_type,
        }
        if params.devices is not None:
            data["devices"] = params.devices

        result = await api_client.wordstat_request("/v1/regions", data=data)

        if params.response_format == ResponseFormat.JSON:
            return json.dumps(result, indent=2, ensure_ascii=False)

        return format_wordstat_regions_markdown(result)

    except Exception as e:
        return handle_api_error(e)


@mcp.tool(
    name="wordstat_regions_tree",
    annotations={
        "title": "Get Regions Tree from Yandex Wordstat",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def wordstat_regions_tree(params: WordstatRegionsTreeInput) -> str:
    """Get the full tree of supported regions for Wordstat filtering.

    Returns region IDs that can be used in regions parameter of other Wordstat tools.
    Does not consume daily quota.

    Returns:
        Regions tree in JSON format
    """
    try:
        result = await api_client.wordstat_request("/v1/getRegionsTree")
        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        return handle_api_error(e)


@mcp.tool(
    name="wordstat_user_info",
    annotations={
        "title": "Get Yandex Wordstat User Info and Quotas",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def wordstat_user_info(params: WordstatUserInfoInput) -> str:
    """Get current user info and API quota status.

    Shows daily quota limit, remaining requests, and rate limits.
    Does not consume daily quota.

    Returns:
        User info with quota details
    """
    try:
        result = await api_client.wordstat_request("/v1/userInfo")
        info = result.get("userInfo", result)

        return (
            f"# Wordstat User Info\n\n"
            f"- **Login**: {info.get('login', 'N/A')}\n"
            f"- **Requests per second**: {info.get('limitPerSecond', 'N/A')}\n"
            f"- **Daily limit**: {info.get('dailyLimit', 'N/A')}\n"
            f"- **Daily remaining**: {info.get('dailyLimitRemaining', 'N/A')}"
        )

    except Exception as e:
        return handle_api_error(e)
