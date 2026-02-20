"""Pydantic input models for Yandex Direct API tools."""


from pydantic import Field

from yandex_mcp.enums import (
    AdState,
    AdStatus,
    CampaignState,
    CampaignStatus,
    CampaignType,
    DailyBudgetMode,
    ResponseFormat,
)
from yandex_mcp.models.common import StrictModel


class GetCampaignsInput(StrictModel):
    """Input for getting campaigns list."""

    campaign_ids: list[int] | None = Field(
        default=None,
        description="Filter by specific campaign IDs",
    )
    states: list[CampaignState] | None = Field(
        default=None,
        description="Filter by campaign states: ON, OFF, SUSPENDED, ENDED, CONVERTED, ARCHIVED",
    )
    statuses: list[CampaignStatus] | None = Field(
        default=None,
        description="Filter by campaign statuses: ACCEPTED, DRAFT, MODERATION, REJECTED",
    )
    types: list[CampaignType] | None = Field(
        default=None,
        description="Filter by campaign types",
    )
    limit: int = Field(
        default=100,
        ge=1,
        le=10000,
        description="Maximum number of campaigns to return",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Offset for pagination",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'",
    )


class ManageCampaignInput(StrictModel):
    """Input for managing campaign state (suspend/resume/archive/unarchive/delete)."""

    campaign_ids: list[int] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Campaign IDs to manage (max 10 per request)",
    )


class UpdateCampaignInput(StrictModel):
    """Input for updating campaign settings."""

    campaign_id: int = Field(
        ...,
        description="Campaign ID to update",
    )
    name: str | None = Field(
        default=None,
        max_length=255,
        description="New campaign name",
    )
    daily_budget_amount: float | None = Field(
        default=None,
        gt=0,
        description="Daily budget in currency units (will be converted to micros)",
    )
    daily_budget_mode: DailyBudgetMode | None = Field(
        default=None,
        description="Daily budget mode: STANDARD or DISTRIBUTED",
    )
    start_date: str | None = Field(
        default=None,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Campaign start date (YYYY-MM-DD)",
    )
    end_date: str | None = Field(
        default=None,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Campaign end date (YYYY-MM-DD)",
    )
    negative_keywords: list[str] | None = Field(
        default=None,
        description="Campaign-level negative keywords",
    )


class GetAdGroupsInput(StrictModel):
    """Input for getting ad groups."""

    campaign_ids: list[int] | None = Field(
        default=None,
        description="Filter by campaign IDs",
    )
    adgroup_ids: list[int] | None = Field(
        default=None,
        description="Filter by specific ad group IDs",
    )
    limit: int = Field(
        default=100,
        ge=1,
        le=10000,
        description="Maximum number of ad groups to return",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Offset for pagination",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'",
    )


class CreateAdGroupInput(StrictModel):
    """Input for creating an ad group."""

    campaign_id: int = Field(
        ...,
        description="Campaign ID to create ad group in",
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Ad group name",
    )
    region_ids: list[int] = Field(
        ...,
        min_length=1,
        description="List of region IDs for targeting (e.g., 225 for Russia, 213 for Moscow)",
    )
    negative_keywords: list[str] | None = Field(
        default=None,
        description="Group-level negative keywords",
    )


class UpdateAdGroupInput(StrictModel):
    """Input for updating an ad group."""

    adgroup_id: int = Field(
        ...,
        description="Ad group ID to update",
    )
    name: str | None = Field(
        default=None,
        max_length=255,
        description="New ad group name",
    )
    region_ids: list[int] | None = Field(
        default=None,
        min_length=1,
        description="New list of region IDs for targeting",
    )
    negative_keywords: list[str] | None = Field(
        default=None,
        description="Group-level negative keywords",
    )
    tracking_params: str | None = Field(
        default=None,
        description="Tracking parameters for all ads in group",
    )


class GetAdsInput(StrictModel):
    """Input for getting ads."""

    campaign_ids: list[int] | None = Field(
        default=None,
        description="Filter by campaign IDs",
    )
    adgroup_ids: list[int] | None = Field(
        default=None,
        description="Filter by ad group IDs",
    )
    ad_ids: list[int] | None = Field(
        default=None,
        description="Filter by specific ad IDs",
    )
    states: list[AdState] | None = Field(
        default=None,
        description="Filter by ad states",
    )
    statuses: list[AdStatus] | None = Field(
        default=None,
        description="Filter by ad statuses",
    )
    limit: int = Field(
        default=100,
        ge=1,
        le=10000,
        description="Maximum number of ads to return",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Offset for pagination",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'",
    )


class CreateTextAdInput(StrictModel):
    """Input for creating a text ad."""

    adgroup_id: int = Field(
        ...,
        description="Ad group ID to create ad in",
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=56,
        description="Ad title (max 56 characters)",
    )
    title2: str | None = Field(
        default=None,
        max_length=30,
        description="Second title (max 30 characters)",
    )
    text: str = Field(
        ...,
        min_length=1,
        max_length=81,
        description="Ad text (max 81 characters)",
    )
    href: str = Field(
        ...,
        description="Landing page URL",
    )
    mobile: bool = Field(
        default=False,
        description="Whether this is a mobile ad",
    )


class UpdateTextAdInput(StrictModel):
    """Input for updating a text ad."""

    ad_id: int = Field(
        ...,
        description="Ad ID to update",
    )
    title: str | None = Field(
        default=None,
        max_length=56,
        description="New ad title (max 56 characters)",
    )
    title2: str | None = Field(
        default=None,
        max_length=30,
        description="New second title (max 30 characters)",
    )
    text: str | None = Field(
        default=None,
        max_length=81,
        description="New ad text (max 81 characters)",
    )
    href: str | None = Field(
        default=None,
        description="New landing page URL",
    )


class ManageAdInput(StrictModel):
    """Input for managing ad state (suspend/resume/archive/unarchive/delete/moderate)."""

    ad_ids: list[int] = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Ad IDs to manage",
    )


class GetKeywordsInput(StrictModel):
    """Input for getting keywords."""

    campaign_ids: list[int] | None = Field(
        default=None,
        description="Filter by campaign IDs",
    )
    adgroup_ids: list[int] | None = Field(
        default=None,
        description="Filter by ad group IDs",
    )
    keyword_ids: list[int] | None = Field(
        default=None,
        description="Filter by specific keyword IDs",
    )
    limit: int = Field(
        default=100,
        ge=1,
        le=10000,
        description="Maximum number of keywords to return",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Offset for pagination",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'",
    )


class AddKeywordsInput(StrictModel):
    """Input for adding keywords."""

    adgroup_id: int = Field(
        ...,
        description="Ad group ID to add keywords to",
    )
    keywords: list[str] = Field(
        ...,
        min_length=1,
        max_length=200,
        description="List of keywords to add",
    )
    bid: float | None = Field(
        default=None,
        gt=0,
        description="Bid for all keywords in currency units",
    )


class KeywordBidItem(StrictModel):
    """Single keyword bid setting."""

    keyword_id: int = Field(
        ...,
        description="Keyword ID",
    )
    search_bid: float | None = Field(
        default=None,
        gt=0,
        description="Search bid in currency units",
    )
    network_bid: float | None = Field(
        default=None,
        gt=0,
        description="Network bid in currency units",
    )


class SetKeywordBidsInput(StrictModel):
    """Input for setting keyword bids."""

    keyword_bids: list[KeywordBidItem] = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="List of keyword bid settings",
    )


class ManageKeywordInput(StrictModel):
    """Input for managing keywords (suspend/resume/delete)."""

    keyword_ids: list[int] = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Keyword IDs to manage",
    )


class DirectReportInput(StrictModel):
    """Input for Direct statistics report."""

    report_type: str = Field(
        default="CAMPAIGN_PERFORMANCE_REPORT",
        description=(
            "Report type: ACCOUNT_PERFORMANCE_REPORT, CAMPAIGN_PERFORMANCE_REPORT, "
            "AD_PERFORMANCE_REPORT, etc."
        ),
    )
    date_from: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Report start date (YYYY-MM-DD)",
    )
    date_to: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Report end date (YYYY-MM-DD)",
    )
    field_names: list[str] = Field(
        default_factory=lambda: ["CampaignName", "Impressions", "Clicks", "Cost"],
        description="Fields to include in report",
    )
    campaign_ids: list[int] | None = Field(
        default=None,
        description="Filter by campaign IDs",
    )
    include_vat: bool = Field(
        default=True,
        description="Include VAT in cost values",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'",
    )
