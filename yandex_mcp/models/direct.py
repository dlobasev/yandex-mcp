"""Pydantic input models for Yandex Direct API tools."""


from pydantic import Field, field_validator, model_validator

from yandex_mcp.enums import (
    AdImageAssociation,
    AdImageType,
    AdState,
    AdStatus,
    CampaignState,
    CampaignStatus,
    CampaignType,
    DailyBudgetMode,
    NetworkStrategyType,
    ResponseFormat,
    SearchStrategyType,
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


class CampaignGoalItem(StrictModel):
    """A campaign goal with its conversion value."""

    goal_id: int = Field(
        ...,
        description="Yandex Metrica goal ID",
    )
    value: float = Field(
        ...,
        gt=0,
        description="Conversion value in currency units (will be converted to micros)",
    )


class CreateCampaignInput(StrictModel):
    """Input for creating a new Unified Performance Campaign (ЕПК).

    Strategy parameters are flat for LLM-friendliness.
    Required sub-params depend on the chosen strategy and are validated automatically.
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Campaign name",
    )
    start_date: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Campaign start date (YYYY-MM-DD)",
    )

    # --- Strategy fields ---
    search_strategy: SearchStrategyType = Field(
        default=SearchStrategyType.HIGHEST_POSITION,
        description=(
            "Search bidding strategy: "
            "HIGHEST_POSITION (manual bids, default), "
            "WB_MAXIMUM_CLICKS (auto, requires weekly_spend_limit), "
            "AVERAGE_CPC (auto, requires average_cpc), "
            "AVERAGE_CPA (auto, requires average_cpa + goal_id), "
            "PAY_FOR_CONVERSION (auto, requires pay_for_conversion_cpa + goal_id), "
            "SERVING_OFF (disable search)"
        ),
    )
    network_strategy: NetworkStrategyType = Field(
        default=NetworkStrategyType.SERVING_OFF,
        description=(
            "Network bidding strategy: "
            "NETWORK_DEFAULT (use search bids), "
            "MAXIMUM_COVERAGE (max impressions), "
            "WB_MAXIMUM_CLICKS (auto, requires weekly_spend_limit), "
            "AVERAGE_CPC (auto, requires network_average_cpc), "
            "SERVING_OFF (disable network, default)"
        ),
    )

    # --- Strategy sub-parameters ---
    weekly_spend_limit: float | None = Field(
        default=None,
        gt=0,
        description=(
            "Weekly spend limit in currency units. "
            "Required for WB_MAXIMUM_CLICKS strategy."
        ),
    )
    bid_ceiling: float | None = Field(
        default=None,
        gt=0,
        description="Max CPC bid ceiling in currency units (optional for WB_MAXIMUM_CLICKS).",
    )
    average_cpc: float | None = Field(
        default=None,
        gt=0,
        description="Target average CPC in currency units. Required for AVERAGE_CPC search strategy.",
    )
    average_cpa: float | None = Field(
        default=None,
        gt=0,
        description="Target average CPA in currency units. Required for AVERAGE_CPA search strategy.",
    )
    goal_id: int | None = Field(
        default=None,
        description=(
            "Yandex Metrica goal ID. "
            "Required for AVERAGE_CPA and PAY_FOR_CONVERSION strategies."
        ),
    )
    pay_for_conversion_cpa: float | None = Field(
        default=None,
        gt=0,
        description=(
            "Amount to pay per conversion in currency units. "
            "Required for PAY_FOR_CONVERSION strategy."
        ),
    )
    network_average_cpc: float | None = Field(
        default=None,
        gt=0,
        description="Target average CPC for network. Required for AVERAGE_CPC network strategy.",
    )

    # --- Optional campaign fields ---
    end_date: str | None = Field(
        default=None,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Campaign end date (YYYY-MM-DD)",
    )
    daily_budget_amount: float | None = Field(
        default=None,
        gt=0,
        description="Daily budget in currency units",
    )
    daily_budget_mode: DailyBudgetMode = Field(
        default=DailyBudgetMode.DISTRIBUTED,
        description="Daily budget mode: STANDARD or DISTRIBUTED",
    )
    negative_keywords: list[str] | None = Field(
        default=None,
        description="Campaign-level negative keywords",
    )
    time_zone: str | None = Field(
        default=None,
        description="Time zone (e.g., 'Europe/Moscow'). Defaults to account time zone.",
    )
    counter_ids: list[int] | None = Field(
        default=None,
        description="Yandex Metrica counter IDs to link to this campaign",
    )
    excluded_sites: list[str] | None = Field(
        default=None,
        description="List of sites to exclude from ad network placements",
    )
    blocked_ips: list[str] | None = Field(
        default=None,
        max_length=25,
        description="List of IP addresses to block from seeing ads (max 25)",
    )
    goals: list[CampaignGoalItem] | None = Field(
        default=None,
        description="Campaign goals with conversion values (shown as 'Ключевые цели' in UI)",
    )

    @model_validator(mode="after")
    def validate_strategy_params(self) -> "CreateCampaignInput":
        """Validate that required sub-parameters are provided for each strategy."""
        if self.search_strategy == SearchStrategyType.WB_MAXIMUM_CLICKS:
            if self.weekly_spend_limit is None:
                raise ValueError(
                    "weekly_spend_limit is required for WB_MAXIMUM_CLICKS search strategy"
                )
        elif self.search_strategy == SearchStrategyType.AVERAGE_CPC:
            if self.average_cpc is None:
                raise ValueError(
                    "average_cpc is required for AVERAGE_CPC search strategy"
                )
        elif self.search_strategy == SearchStrategyType.AVERAGE_CPA:
            if self.average_cpa is None:
                raise ValueError(
                    "average_cpa is required for AVERAGE_CPA search strategy"
                )
            if self.goal_id is None:
                raise ValueError(
                    "goal_id is required for AVERAGE_CPA search strategy"
                )
        elif self.search_strategy == SearchStrategyType.PAY_FOR_CONVERSION:
            if self.pay_for_conversion_cpa is None:
                raise ValueError(
                    "pay_for_conversion_cpa is required for PAY_FOR_CONVERSION search strategy"
                )
            if self.goal_id is None:
                raise ValueError(
                    "goal_id is required for PAY_FOR_CONVERSION search strategy"
                )

        if self.network_strategy == NetworkStrategyType.WB_MAXIMUM_CLICKS:
            if self.weekly_spend_limit is None:
                raise ValueError(
                    "weekly_spend_limit is required for WB_MAXIMUM_CLICKS network strategy"
                )
        elif self.network_strategy == NetworkStrategyType.AVERAGE_CPC:
            if self.network_average_cpc is None:
                raise ValueError(
                    "network_average_cpc is required for AVERAGE_CPC network strategy"
                )

        return self


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
    ad_image_hash: str | None = Field(
        default=None,
        description="Hash of an uploaded ad image to attach (from direct_upload_image)",
    )
    sitelink_set_id: int | None = Field(
        default=None,
        description="Sitelink set ID to attach (from direct_create_sitelink_set)",
    )
    ad_extension_ids: list[int] | None = Field(
        default=None,
        max_length=50,
        description="Callout extension IDs to attach (from direct_create_callouts, max 50)",
    )
    display_url_path: str | None = Field(
        default=None,
        max_length=20,
        description="Display URL path shown in the ad (e.g., 'sale/phones', max 20 chars)",
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
    sitelink_set_id: int | None = Field(
        default=None,
        description="New sitelink set ID to attach",
    )
    ad_extension_ids: list[int] | None = Field(
        default=None,
        max_length=50,
        description=(
            "Callout extension IDs to SET on the ad (replaces all existing callouts). "
            "Uses CalloutSetting with SET operation internally."
        ),
    )
    ad_image_hash: str | None = Field(
        default=None,
        description="New image hash to attach (from direct_upload_image)",
    )
    display_url_path: str | None = Field(
        default=None,
        max_length=20,
        description="New display URL path (max 20 chars)",
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


class SetAutotargetingInput(StrictModel):
    """Input for setting autotargeting categories on an ad group.

    Controls which query categories the autotargeting engine targets.
    All default to True (matching Yandex Direct defaults for new groups).
    """

    adgroup_id: int = Field(
        ...,
        description="Ad group ID to configure autotargeting for",
    )
    exact: bool = Field(
        default=True,
        description="Target exact (целевые) queries — closely matching the ad",
    )
    alternative: bool = Field(
        default=True,
        description="Target alternative (альтернативные) queries — substitute products",
    )
    competitor: bool = Field(
        default=True,
        description="Target competitor (конкурентные) queries — competitor mentions",
    )
    broader: bool = Field(
        default=True,
        description="Target broader (широкие) queries — wider product interest",
    )
    accessory: bool = Field(
        default=True,
        description="Target accessory (сопутствующие) queries — related products",
    )


# --- AdImage models ---


class UploadImageInput(StrictModel):
    """Input for uploading an ad image."""

    image_data: str = Field(
        ...,
        min_length=1,
        description="Base64-encoded image data (JPG, PNG, or GIF)",
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Image name for reference",
    )
    image_type: AdImageType = Field(
        default=AdImageType.REGULAR,
        description=(
            "Image type: REGULAR (1:1 to 3:4, 450-5000px), "
            "WIDE (16:9, min 1080x607), "
            "FIXED_IMAGE (exact sizes for banner ads)"
        ),
    )


class GetImagesInput(StrictModel):
    """Input for getting ad image metadata."""

    ad_image_hashes: list[str] | None = Field(
        default=None,
        description="Filter by specific image hashes",
    )
    associated: AdImageAssociation | None = Field(
        default=None,
        description="Filter by association status: YES (linked to ads) or NO (not linked)",
    )
    limit: int = Field(
        default=100,
        ge=1,
        le=10000,
        description="Maximum number of images to return",
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


class DeleteImagesInput(StrictModel):
    """Input for deleting ad images."""

    ad_image_hashes: list[str] = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Image hashes to delete (images must not be attached to ads)",
    )


# --- Sitelink models ---


class SitelinkItem(StrictModel):
    """Single sitelink within a set."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=30,
        description="Sitelink title (max 30 chars)",
    )
    href: str | None = Field(
        default=None,
        max_length=1024,
        description="Sitelink URL (one of href or turbo_page_id required)",
    )
    turbo_page_id: int | None = Field(
        default=None,
        description="Turbo page ID (one of href or turbo_page_id required)",
    )
    description: str | None = Field(
        default=None,
        max_length=60,
        description="Sitelink description for extended format (max 60 chars)",
    )

    @model_validator(mode="after")
    def validate_href_or_turbo(self) -> "SitelinkItem":
        if self.href is None and self.turbo_page_id is None:
            raise ValueError("Either href or turbo_page_id must be provided")
        return self


class CreateSitelinkSetInput(StrictModel):
    """Input for creating a sitelink set."""

    sitelinks: list[SitelinkItem] = Field(
        ...,
        min_length=1,
        max_length=8,
        description="List of sitelinks (1-8 per set)",
    )


class GetSitelinkSetsInput(StrictModel):
    """Input for getting sitelink sets."""

    sitelink_set_ids: list[int] = Field(
        ...,
        min_length=1,
        description="Sitelink set IDs to retrieve",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'",
    )


class DeleteSitelinkSetsInput(StrictModel):
    """Input for deleting sitelink sets."""

    sitelink_set_ids: list[int] = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Sitelink set IDs to delete (must not be attached to ads)",
    )


# --- Callout (AdExtension) models ---


class CreateCalloutsInput(StrictModel):
    """Input for creating callout extensions."""

    callout_texts: list[str] = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Callout texts to create (each max 25 chars)",
    )

    @field_validator("callout_texts")
    @classmethod
    def validate_callout_lengths(cls, texts: list[str]) -> list[str]:
        for text in texts:
            if len(text) > 25:
                raise ValueError(
                    f"Callout text exceeds 25 chars ({len(text)}): '{text}'"
                )
        return texts


class GetCalloutsInput(StrictModel):
    """Input for getting callout extensions."""

    callout_ids: list[int] | None = Field(
        default=None,
        description="Filter by specific callout IDs (omit to get all)",
    )
    limit: int = Field(
        default=100,
        ge=1,
        le=10000,
        description="Maximum number of callouts to return",
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


class DeleteCalloutsInput(StrictModel):
    """Input for deleting callout extensions."""

    callout_ids: list[int] = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Callout IDs to delete (must not be attached to ads)",
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
