"""Enums for Yandex MCP Server."""

from enum import Enum


class ResponseFormat(str, Enum):
    """Output format for tool responses."""

    MARKDOWN = "markdown"
    JSON = "json"


class CampaignState(str, Enum):
    """Campaign state filter."""

    ON = "ON"
    OFF = "OFF"
    SUSPENDED = "SUSPENDED"
    ENDED = "ENDED"
    CONVERTED = "CONVERTED"
    ARCHIVED = "ARCHIVED"


class CampaignStatus(str, Enum):
    """Campaign status filter."""

    ACCEPTED = "ACCEPTED"
    DRAFT = "DRAFT"
    MODERATION = "MODERATION"
    REJECTED = "REJECTED"


class CampaignType(str, Enum):
    """Campaign type filter."""

    TEXT_CAMPAIGN = "TEXT_CAMPAIGN"
    DYNAMIC_TEXT_CAMPAIGN = "DYNAMIC_TEXT_CAMPAIGN"
    MOBILE_APP_CAMPAIGN = "MOBILE_APP_CAMPAIGN"
    CPM_BANNER_CAMPAIGN = "CPM_BANNER_CAMPAIGN"
    SMART_CAMPAIGN = "SMART_CAMPAIGN"
    UNIFIED_CAMPAIGN = "UNIFIED_CAMPAIGN"


class AdState(str, Enum):
    """Ad state filter."""

    ON = "ON"
    OFF = "OFF"
    OFF_BY_MONITORING = "OFF_BY_MONITORING"
    SUSPENDED = "SUSPENDED"
    ARCHIVED = "ARCHIVED"


class AdStatus(str, Enum):
    """Ad status filter."""

    ACCEPTED = "ACCEPTED"
    DRAFT = "DRAFT"
    MODERATION = "MODERATION"
    PREACCEPTED = "PREACCEPTED"
    REJECTED = "REJECTED"


class DailyBudgetMode(str, Enum):
    """Daily budget spending mode."""

    STANDARD = "STANDARD"
    DISTRIBUTED = "DISTRIBUTED"


class MetrikaGroupType(str, Enum):
    """Time grouping for Metrika reports."""

    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"
    HOUR = "hour"
    MINUTE = "minute"
