"""Yandex Direct ad group management tools."""

import json

from yandex_mcp.client import api_client
from yandex_mcp.enums import ResponseFormat
from yandex_mcp.errors import handle_api_error
from yandex_mcp.formatters import format_adgroups_markdown
from yandex_mcp.models.direct import CreateAdGroupInput, GetAdGroupsInput, UpdateAdGroupInput
from yandex_mcp.server import mcp


@mcp.tool(
    name="direct_get_adgroups",
    annotations={
        "title": "Get Yandex Direct Ad Groups",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def direct_get_adgroups(params: GetAdGroupsInput) -> str:
    """Get list of ad groups from Yandex Direct.

    Retrieves ad groups with their settings and targeting information.

    Args:
        params: Filter and pagination parameters

    Returns:
        Ad groups list in markdown or JSON format
    """
    try:
        selection_criteria: dict = {}

        if params.campaign_ids:
            selection_criteria["CampaignIds"] = params.campaign_ids
        if params.adgroup_ids:
            selection_criteria["Ids"] = params.adgroup_ids

        request_params = {
            "SelectionCriteria": selection_criteria,
            "FieldNames": [
                "Id", "Name", "CampaignId", "RegionIds", "Type", "Status", "ServingStatus",
            ],
            "Page": {"Limit": params.limit, "Offset": params.offset},
        }

        result = await api_client.direct_request("adgroups", "get", request_params)
        groups = result.get("result", {}).get("AdGroups", [])

        if params.response_format == ResponseFormat.JSON:
            return json.dumps(
                {"ad_groups": groups, "total": len(groups)},
                indent=2,
                ensure_ascii=False,
            )

        return format_adgroups_markdown(groups)

    except Exception as e:
        return handle_api_error(e)


@mcp.tool(
    name="direct_create_adgroup",
    annotations={
        "title": "Create Yandex Direct Ad Group",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def direct_create_adgroup(params: CreateAdGroupInput) -> str:
    """Create a new ad group in a campaign.

    Creates an ad group with specified name and targeting regions.

    Args:
        params: Ad group settings

    Returns:
        Created ad group ID
    """
    try:
        adgroup: dict = {
            "Name": params.name,
            "CampaignId": params.campaign_id,
            "RegionIds": params.region_ids,
        }

        if params.negative_keywords:
            adgroup["NegativeKeywords"] = {"Items": params.negative_keywords}

        request_params = {"AdGroups": [adgroup]}

        result = await api_client.direct_request("adgroups", "add", request_params)
        add_results = result.get("result", {}).get("AddResults", [])

        if add_results and add_results[0].get("Id"):
            return f"Ad group created successfully. ID: {add_results[0]['Id']}"

        errors: list[str] = []
        for r in add_results:
            if r.get("Errors"):
                errors.extend([e.get("Message", "Unknown error") for e in r["Errors"]])

        return "Failed to create ad group:\n" + "\n".join(f"- {e}" for e in errors)

    except Exception as e:
        return handle_api_error(e)


@mcp.tool(
    name="direct_update_adgroup",
    annotations={
        "title": "Update Yandex Direct Ad Group",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def direct_update_adgroup(params: UpdateAdGroupInput) -> str:
    """Update ad group settings.

    Allows updating ad group name, regions, negative keywords, and tracking params.
    Only specified fields will be updated.

    Args:
        params: Ad group ID and fields to update

    Returns:
        Operation result
    """
    try:
        adgroup_update: dict = {"Id": params.adgroup_id}

        if params.name is not None:
            adgroup_update["Name"] = params.name

        if params.region_ids is not None:
            adgroup_update["RegionIds"] = params.region_ids

        if params.negative_keywords is not None:
            adgroup_update["NegativeKeywords"] = {"Items": params.negative_keywords}

        if params.tracking_params is not None:
            adgroup_update["TrackingParams"] = params.tracking_params

        request_params = {"AdGroups": [adgroup_update]}

        result = await api_client.direct_request("adgroups", "update", request_params)
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

        return f"Ad group {params.adgroup_id} updated successfully."

    except Exception as e:
        return handle_api_error(e)
