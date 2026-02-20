"""Yandex Direct statistics report tool."""

import json

from yandex_mcp.client import api_client
from yandex_mcp.config import DIRECT_REPORT_MAX_ROWS
from yandex_mcp.enums import ResponseFormat
from yandex_mcp.errors import handle_api_error
from yandex_mcp.models.direct import DirectReportInput
from yandex_mcp.server import mcp


@mcp.tool(
    name="direct_get_statistics",
    annotations={
        "title": "Get Yandex Direct Statistics",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def direct_get_statistics(params: DirectReportInput) -> str:
    """Get campaign statistics report from Yandex Direct.

    Retrieves performance statistics for campaigns, ads, or keywords.

    Report types:
    - ACCOUNT_PERFORMANCE_REPORT - Account level stats
    - CAMPAIGN_PERFORMANCE_REPORT - Campaign level stats (default)
    - AD_PERFORMANCE_REPORT - Ad level stats
    - ADGROUP_PERFORMANCE_REPORT - Ad group level stats
    - CRITERIA_PERFORMANCE_REPORT - Keyword level stats

    Common fields:
    - CampaignName, CampaignId - Campaign info
    - Impressions, Clicks, Cost - Basic metrics
    - Ctr, AvgCpc, ConversionRate - Calculated metrics
    - Date - For daily breakdown

    Args:
        params: Report parameters including date range and fields

    Returns:
        Statistics report in markdown or JSON format
    """
    try:
        report_def: dict = {
            "SelectionCriteria": {
                "DateFrom": params.date_from,
                "DateTo": params.date_to,
            },
            "FieldNames": params.field_names,
            "ReportName": f"Report_{params.date_from}_{params.date_to}",
            "ReportType": params.report_type,
            "DateRangeType": "CUSTOM_DATE",
            "Format": "TSV",
            "IncludeVAT": "YES" if params.include_vat else "NO",
            "IncludeDiscount": "NO",
        }

        if params.campaign_ids:
            report_def["SelectionCriteria"]["Filter"] = [
                {
                    "Field": "CampaignId",
                    "Operator": "IN",
                    "Values": [str(cid) for cid in params.campaign_ids],
                }
            ]

        response = await api_client.direct_report_request(report_def)

        if response.status_code == 200:
            lines = response.text.strip().split("\n")
            if len(lines) < 2:
                return "No data found for the specified period."

            header = lines[0].split("\t")
            data_rows = [line.split("\t") for line in lines[1:] if line.strip()]

            if params.response_format == ResponseFormat.JSON:
                result = [dict(zip(header, row, strict=False)) for row in data_rows]
                return json.dumps(
                    {"data": result, "total": len(result)},
                    indent=2,
                    ensure_ascii=False,
                )

            md_lines = ["# Direct Statistics Report\n"]
            md_lines.append(f"**Period**: {params.date_from} — {params.date_to}")
            md_lines.append(f"**Report type**: {params.report_type}\n")

            md_lines.append("| " + " | ".join(header) + " |")
            md_lines.append("| " + " | ".join(["---"] * len(header)) + " |")

            for row in data_rows[:DIRECT_REPORT_MAX_ROWS]:
                md_lines.append("| " + " | ".join(row) + " |")

            if len(data_rows) > DIRECT_REPORT_MAX_ROWS:
                md_lines.append(
                    f"\n*...and {len(data_rows) - DIRECT_REPORT_MAX_ROWS} more rows*"
                )

            return "\n".join(md_lines)

        elif response.status_code in (201, 202):
            return "Report is being generated. Please try again in a few seconds."

        else:
            response.raise_for_status()
            return "Unexpected response from Reports API."

    except Exception as e:
        return handle_api_error(e)
