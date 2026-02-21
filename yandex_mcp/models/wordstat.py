"""Pydantic input models for Yandex Wordstat API tools."""

from pydantic import Field

from yandex_mcp.enums import ResponseFormat
from yandex_mcp.models.common import StrictModel


class WordstatTopRequestsInput(StrictModel):
    """Input for getting popular search queries."""

    phrase: str | None = Field(
        default=None,
        description="Single phrase to search for popular queries",
    )
    phrases: list[str] | None = Field(
        default=None,
        max_length=128,
        description="Multiple phrases to search (max 128)",
    )
    num_phrases: int = Field(
        default=50,
        ge=1,
        le=2000,
        description="Number of results per phrase (default 50, max 2000)",
    )
    regions: list[int] | None = Field(
        default=None,
        description="Region IDs to filter (from wordstat_regions_tree)",
    )
    devices: list[str] | None = Field(
        default=None,
        description="Device filter: all, desktop, phone, tablet",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'",
    )


class WordstatDynamicsInput(StrictModel):
    """Input for getting query frequency dynamics over time."""

    phrase: str = Field(
        ...,
        description="Query phrase (only + operator allowed)",
    )
    period: str = Field(
        default="monthly",
        description="Period: monthly, weekly, or daily",
    )
    from_date: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Start date (YYYY-MM-DD)",
    )
    to_date: str | None = Field(
        default=None,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="End date (YYYY-MM-DD), defaults to current period end",
    )
    regions: list[int] | None = Field(
        default=None,
        description="Region IDs to filter",
    )
    devices: list[str] | None = Field(
        default=None,
        description="Device filter: all, desktop, phone, tablet",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'",
    )


class WordstatRegionsInput(StrictModel):
    """Input for getting regional distribution of queries."""

    phrase: str = Field(
        ...,
        description="Query phrase",
    )
    region_type: str = Field(
        default="all",
        description="Region granularity: cities, regions, or all",
    )
    devices: list[str] | None = Field(
        default=None,
        description="Device filter: all, desktop, phone, tablet",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'",
    )


class WordstatRegionsTreeInput(StrictModel):
    """Input for getting the regions tree (no parameters needed)."""


class WordstatUserInfoInput(StrictModel):
    """Input for getting user quota info (no parameters needed)."""
