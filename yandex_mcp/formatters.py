"""Markdown formatters for API responses."""

from typing import Any

from yandex_mcp.config import (
    METRIKA_COUNTER_GOALS_PREVIEW_LIMIT,
    METRIKA_REPORT_MAX_ROWS,
)


def format_campaigns_markdown(campaigns: list[dict[str, Any]]) -> str:
    """Format campaigns list as markdown."""
    if not campaigns:
        return "No campaigns found."

    lines = ["# Campaigns\n"]
    for camp in campaigns:
        lines.append(f"## {camp.get('Name', 'Unnamed')} (ID: {camp.get('Id')})")
        lines.append(f"- **Type**: {camp.get('Type', 'N/A')}")
        lines.append(f"- **State**: {camp.get('State', 'N/A')}")
        lines.append(f"- **Status**: {camp.get('Status', 'N/A')}")

        if camp.get("DailyBudget"):
            budget = camp["DailyBudget"]
            amount = budget.get("Amount", 0) / 1_000_000
            lines.append(f"- **Daily Budget**: {amount:.2f} ({budget.get('Mode', 'N/A')})")

        if camp.get("Statistics"):
            stats = camp["Statistics"]
            lines.append(f"- **Clicks**: {stats.get('Clicks', 0)}")
            lines.append(f"- **Impressions**: {stats.get('Impressions', 0)}")

        lines.append("")

    return "\n".join(lines)


def format_ads_markdown(ads: list[dict[str, Any]]) -> str:
    """Format ads list as markdown."""
    if not ads:
        return "No ads found."

    lines = ["# Ads\n"]
    for ad in ads:
        ad_id = ad.get("Id")
        lines.append(f"## Ad ID: {ad_id}")
        lines.append(f"- **AdGroup ID**: {ad.get('AdGroupId')}")
        lines.append(f"- **Campaign ID**: {ad.get('CampaignId')}")
        lines.append(f"- **State**: {ad.get('State', 'N/A')}")
        lines.append(f"- **Status**: {ad.get('Status', 'N/A')}")

        if ad.get("TextAd"):
            text_ad = ad["TextAd"]
            lines.append(f"- **Title**: {text_ad.get('Title', 'N/A')}")
            lines.append(f"- **Title2**: {text_ad.get('Title2', 'N/A')}")
            lines.append(f"- **Text**: {text_ad.get('Text', 'N/A')}")
            lines.append(f"- **Href**: {text_ad.get('Href', 'N/A')}")

        lines.append("")

    return "\n".join(lines)


def format_adgroups_markdown(groups: list[dict[str, Any]]) -> str:
    """Format ad groups list as markdown."""
    if not groups:
        return "No ad groups found."

    lines = ["# Ad Groups\n"]
    for group in groups:
        lines.append(f"## {group.get('Name', 'Unnamed')} (ID: {group.get('Id')})")
        lines.append(f"- **Campaign ID**: {group.get('CampaignId')}")
        lines.append(f"- **Type**: {group.get('Type', 'N/A')}")
        lines.append(f"- **Status**: {group.get('Status', 'N/A')}")

        region_ids = group.get("RegionIds", [])
        if region_ids:
            lines.append(f"- **Regions**: {', '.join(map(str, region_ids))}")

        lines.append("")

    return "\n".join(lines)


def format_keywords_markdown(keywords: list[dict[str, Any]]) -> str:
    """Format keywords list as markdown."""
    if not keywords:
        return "No keywords found."

    lines = ["# Keywords\n"]
    for kw in keywords:
        lines.append(f"## {kw.get('Keyword', 'N/A')} (ID: {kw.get('Id')})")
        lines.append(f"- **AdGroup ID**: {kw.get('AdGroupId')}")
        lines.append(f"- **State**: {kw.get('State', 'N/A')}")
        lines.append(f"- **Status**: {kw.get('Status', 'N/A')}")

        bid = kw.get("Bid", 0)
        if bid:
            lines.append(f"- **Bid**: {bid / 1_000_000:.2f}")

        lines.append("")

    return "\n".join(lines)


def format_metrika_counters_markdown(counters: list[dict[str, Any]]) -> str:
    """Format Metrika counters as markdown."""
    if not counters:
        return "No counters found."

    lines = ["# Metrika Counters\n"]
    for counter in counters:
        lines.append(f"## {counter.get('name', 'Unnamed')} (ID: {counter.get('id')})")

        site = counter.get("site2", {}).get("site", "N/A")
        lines.append(f"- **Site**: {site}")
        lines.append(f"- **Status**: {counter.get('status', 'N/A')}")
        lines.append(f"- **Code Status**: {counter.get('code_status', 'N/A')}")
        lines.append(f"- **Owner**: {counter.get('owner_login', 'N/A')}")

        if counter.get("favorite"):
            lines.append("- **Favorite**: yes")

        lines.append("")

    return "\n".join(lines)


def format_metrika_report_markdown(data: dict[str, Any]) -> str:
    """Format Metrika report data as markdown."""
    lines = ["# Metrika Report\n"]

    query = data.get("query", {})
    lines.append("## Query Parameters")
    lines.append(f"- **Period**: {query.get('date1', 'N/A')} — {query.get('date2', 'N/A')}")

    if query.get("dimensions"):
        lines.append(f"- **Dimensions**: {', '.join(query['dimensions'])}")
    if query.get("metrics"):
        lines.append(f"- **Metrics**: {', '.join(query['metrics'])}")

    lines.append("")

    totals = data.get("totals", [])
    if totals:
        lines.append("## Totals")
        metrics = query.get("metrics", [])
        for i, total in enumerate(totals):
            metric_name = metrics[i] if i < len(metrics) else f"Metric {i + 1}"
            lines.append(f"- **{metric_name}**: {total:,.2f}")
        lines.append("")

    rows = data.get("data", [])
    if rows:
        lines.append(f"## Data ({len(rows)} rows)")
        for row in rows[:METRIKA_REPORT_MAX_ROWS]:
            dims = row.get("dimensions", [])
            metrics_vals = row.get("metrics", [])

            dim_str = (
                " / ".join(
                    str(d.get("name", d.get("id", "N/A"))) if isinstance(d, dict) else str(d)
                    for d in dims
                )
                if dims
                else "Total"
            )

            metrics_str = ", ".join(f"{v:,.2f}" for v in metrics_vals)
            lines.append(f"- **{dim_str}**: {metrics_str}")

        if len(rows) > METRIKA_REPORT_MAX_ROWS:
            lines.append(f"\n*...and {len(rows) - METRIKA_REPORT_MAX_ROWS} more rows*")

    return "\n".join(lines)


def format_metrika_counter_detail_markdown(counter: dict[str, Any]) -> str:
    """Format a single Metrika counter detail as markdown."""
    lines = [f"# Counter: {counter.get('name', 'Unnamed')} (ID: {counter.get('id')})"]
    lines.append("\n## Basic Info")
    lines.append(f"- **Site**: {counter.get('site2', {}).get('site', 'N/A')}")
    lines.append(f"- **Status**: {counter.get('status', 'N/A')}")
    lines.append(f"- **Code Status**: {counter.get('code_status', 'N/A')}")
    lines.append(f"- **Owner**: {counter.get('owner_login', 'N/A')}")
    lines.append(f"- **Created**: {counter.get('create_time', 'N/A')}")

    if counter.get("webvisor"):
        webvisor = counter["webvisor"]
        lines.append("\n## Webvisor")
        lines.append(f"- **Version**: {webvisor.get('wv_version', 'N/A')}")
        lines.append(f"- **Enabled**: {webvisor.get('arch_enabled', False)}")

    goals = counter.get("goals", [])
    if goals:
        lines.append(f"\n## Goals ({len(goals)})")
        for goal in goals[:METRIKA_COUNTER_GOALS_PREVIEW_LIMIT]:
            lines.append(f"- {goal.get('name', 'Unnamed')} (ID: {goal.get('id')})")

    return "\n".join(lines)
