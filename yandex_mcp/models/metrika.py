"""Pydantic input models for Yandex Metrika API tools."""

from pydantic import Field

from yandex_mcp.enums import MetrikaGroupType, ResponseFormat
from yandex_mcp.models.common import StrictModel


class GetCountersInput(StrictModel):
    """Input for getting Metrika counters."""

    favorite: bool | None = Field(
        default=None,
        description="Filter by favorite status",
    )
    search_string: str | None = Field(
        default=None,
        description="Search string to filter counters by name or site",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'",
    )


class GetCounterInput(StrictModel):
    """Input for getting single counter details."""

    counter_id: int = Field(
        ...,
        description="Metrika counter ID",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'",
    )


class DeleteCounterInput(StrictModel):
    """Input for deleting a Metrika counter."""

    counter_id: int = Field(
        ...,
        description="Metrika counter ID to delete",
    )


class CreateCounterInput(StrictModel):
    """Input for creating a Metrika counter."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Counter name",
    )
    site: str = Field(
        ...,
        description="Website URL",
    )


class GetGoalsInput(StrictModel):
    """Input for getting counter goals."""

    counter_id: int = Field(
        ...,
        description="Metrika counter ID",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'",
    )


class GoalCondition(StrictModel):
    """Single goal condition."""

    type: str = Field(
        ...,
        description="Condition type: exact, contain, regex, action",
    )
    url: str | None = Field(
        default=None,
        description="URL pattern for URL-type goals",
    )
    value: str | None = Field(
        default=None,
        description="Value for action/event-type goals",
    )


class CreateGoalInput(StrictModel):
    """Input for creating a goal."""

    counter_id: int = Field(
        ...,
        description="Metrika counter ID",
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Goal name",
    )
    goal_type: str = Field(
        ...,
        description="Goal type: url, action, phone, email, messenger, etc.",
    )
    conditions: list[GoalCondition] = Field(
        ...,
        description="Goal conditions, e.g., [{'type': 'exact', 'url': '/thank-you'}]",
    )


class MetrikaReportInput(StrictModel):
    """Input for Metrika statistics report."""

    counter_id: int = Field(
        ...,
        description="Metrika counter ID",
    )
    metrics: list[str] = Field(
        default_factory=lambda: ["ym:s:visits", "ym:s:users", "ym:s:bounceRate"],
        description="Metrics to retrieve (e.g., ym:s:visits, ym:s:users, ym:s:pageviews)",
    )
    dimensions: list[str] | None = Field(
        default=None,
        description="Dimensions for grouping (e.g., ym:s:date, ym:s:trafficSource)",
    )
    date1: str | None = Field(
        default=None,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Start date (YYYY-MM-DD), defaults to 7 days ago",
    )
    date2: str | None = Field(
        default=None,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="End date (YYYY-MM-DD), defaults to today",
    )
    filters: str | None = Field(
        default=None,
        description="Filter expression (e.g., ym:s:trafficSource=='organic')",
    )
    sort: str | None = Field(
        default=None,
        description="Sort field with optional '-' prefix for descending",
    )
    limit: int = Field(
        default=100,
        ge=1,
        le=100000,
        description="Maximum rows to return",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'",
    )


class MetrikaByTimeInput(StrictModel):
    """Input for time-based Metrika report."""

    counter_id: int = Field(
        ...,
        description="Metrika counter ID",
    )
    metrics: list[str] = Field(
        default_factory=lambda: ["ym:s:visits"],
        description="Metrics to retrieve",
    )
    dimensions: list[str] | None = Field(
        default=None,
        description="Dimensions for grouping",
    )
    date1: str | None = Field(
        default=None,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Start date (YYYY-MM-DD)",
    )
    date2: str | None = Field(
        default=None,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="End date (YYYY-MM-DD)",
    )
    group: MetrikaGroupType = Field(
        default=MetrikaGroupType.DAY,
        description="Time grouping: day, week, month, quarter, year, hour, minute",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'",
    )
