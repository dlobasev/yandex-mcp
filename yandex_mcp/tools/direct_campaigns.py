"""Yandex Direct campaign management tools."""

import json

from yandex_mcp.client import api_client
from yandex_mcp.enums import ResponseFormat
from yandex_mcp.errors import handle_api_error
from yandex_mcp.formatters import format_campaigns_markdown
from yandex_mcp.models.direct import GetCampaignsInput, ManageCampaignInput, UpdateCampaignInput
from yandex_mcp.server import mcp
from yandex_mcp.tools._manage import execute_manage_operation


@mcp.tool(
    name="direct_get_campaigns",
    annotations={
        "title": "Get Yandex Direct Campaigns",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def direct_get_campaigns(params: GetCampaignsInput) -> str:
    """Get list of advertising campaigns from Yandex Direct.

    Retrieves campaigns with their settings, statistics, and current status.
    Supports filtering by IDs, states, statuses, and types.

    Args:
        params: Filter and pagination parameters

    Returns:
        Campaign list in markdown or JSON format
    """
    try:
        selection_criteria: dict = {}

        if params.campaign_ids:
            selection_criteria["Ids"] = params.campaign_ids
        if params.states:
            selection_criteria["States"] = [s.value for s in params.states]
        if params.statuses:
            selection_criteria["Statuses"] = [s.value for s in params.statuses]
        if params.types:
            selection_criteria["Types"] = [t.value for t in params.types]

        request_params = {
            "SelectionCriteria": selection_criteria,
            "FieldNames": [
                "Id", "Name", "Type", "State", "Status", "StatusPayment",
                "StartDate", "EndDate", "DailyBudget", "Statistics",
            ],
            "TextCampaignFieldNames": ["BiddingStrategy", "Settings"],
            "Page": {"Limit": params.limit, "Offset": params.offset},
        }

        result = await api_client.direct_request("campaigns", "get", request_params)
        campaigns = result.get("result", {}).get("Campaigns", [])

        if params.response_format == ResponseFormat.JSON:
            return json.dumps(
                {"campaigns": campaigns, "total": len(campaigns)},
                indent=2,
                ensure_ascii=False,
            )

        return format_campaigns_markdown(campaigns)

    except Exception as e:
        return handle_api_error(e)


@mcp.tool(
    name="direct_update_campaign",
    annotations={
        "title": "Update Yandex Direct Campaign",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def direct_update_campaign(params: UpdateCampaignInput) -> str:
    """Update campaign settings.

    Allows updating campaign name, daily budget, dates, and negative keywords.
    Only specified fields will be updated.

    Args:
        params: Campaign ID and fields to update

    Returns:
        Operation result
    """
    try:
        campaign_update: dict = {"Id": params.campaign_id}

        if params.name is not None:
            campaign_update["Name"] = params.name

        if params.daily_budget_amount is not None:
            campaign_update["DailyBudget"] = {
                "Amount": int(params.daily_budget_amount * 1_000_000),
                "Mode": params.daily_budget_mode.value if params.daily_budget_mode else "DISTRIBUTED",
            }

        if params.start_date is not None:
            campaign_update["StartDate"] = params.start_date

        if params.end_date is not None:
            campaign_update["EndDate"] = params.end_date

        if params.negative_keywords is not None:
            campaign_update["NegativeKeywords"] = {"Items": params.negative_keywords}

        request_params = {"Campaigns": [campaign_update]}

        result = await api_client.direct_request("campaigns", "update", request_params)
        update_results = result.get("result", {}).get("UpdateResults", [])

        errors: list[str] = []
        for r in update_results:
            if r.get("Errors"):
                errors.extend([e.get("Message", "Unknown error") for e in r["Errors"]])
            if r.get("Warnings"):
                errors.extend(
                    [f"Warning: {w.get('Message', 'Unknown warning')}" for w in r["Warnings"]]
                )

        if errors:
            return "Update completed with issues:\n" + "\n".join(f"- {e}" for e in errors)

        return f"Campaign {params.campaign_id} updated successfully."

    except Exception as e:
        return handle_api_error(e)


@mcp.tool(
    name="direct_suspend_campaigns",
    annotations={
        "title": "Suspend Yandex Direct Campaigns",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def direct_suspend_campaigns(params: ManageCampaignInput) -> str:
    """Suspend (pause) advertising campaigns.

    Suspended campaigns stop showing ads but retain all settings.
    Can be resumed later with direct_resume_campaigns.
    """
    return await execute_manage_operation(
        service="campaigns",
        method="suspend",
        ids=params.campaign_ids,
        ids_field="Ids",
        result_key="SuspendResults",
        entity_name="campaign",
        action_past_tense="suspended",
    )


@mcp.tool(
    name="direct_resume_campaigns",
    annotations={
        "title": "Resume Yandex Direct Campaigns",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def direct_resume_campaigns(params: ManageCampaignInput) -> str:
    """Resume suspended advertising campaigns.

    Resumes campaigns that were previously suspended.
    Campaigns will start showing ads again.
    """
    return await execute_manage_operation(
        service="campaigns",
        method="resume",
        ids=params.campaign_ids,
        ids_field="Ids",
        result_key="ResumeResults",
        entity_name="campaign",
        action_past_tense="resumed",
    )


@mcp.tool(
    name="direct_archive_campaigns",
    annotations={
        "title": "Archive Yandex Direct Campaigns",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def direct_archive_campaigns(params: ManageCampaignInput) -> str:
    """Archive advertising campaigns.

    Archived campaigns are hidden from the main list but can be restored.
    Use this for campaigns you no longer need but want to keep for reference.
    """
    return await execute_manage_operation(
        service="campaigns",
        method="archive",
        ids=params.campaign_ids,
        ids_field="Ids",
        result_key="ArchiveResults",
        entity_name="campaign",
        action_past_tense="archived",
    )


@mcp.tool(
    name="direct_unarchive_campaigns",
    annotations={
        "title": "Unarchive Yandex Direct Campaigns",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def direct_unarchive_campaigns(params: ManageCampaignInput) -> str:
    """Restore archived campaigns.

    Unarchives campaigns and makes them visible in the main campaign list.
    """
    return await execute_manage_operation(
        service="campaigns",
        method="unarchive",
        ids=params.campaign_ids,
        ids_field="Ids",
        result_key="UnarchiveResults",
        entity_name="campaign",
        action_past_tense="unarchived",
    )


@mcp.tool(
    name="direct_delete_campaigns",
    annotations={
        "title": "Delete Yandex Direct Campaigns",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def direct_delete_campaigns(params: ManageCampaignInput) -> str:
    """Delete advertising campaigns permanently.

    WARNING: This action is irreversible. Deleted campaigns cannot be restored.
    Consider archiving campaigns instead if you might need them later.
    """
    return await execute_manage_operation(
        service="campaigns",
        method="delete",
        ids=params.campaign_ids,
        ids_field="Ids",
        result_key="DeleteResults",
        entity_name="campaign",
        action_past_tense="deleted",
    )
