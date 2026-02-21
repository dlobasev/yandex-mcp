"""Yandex Direct ad management tools."""

import json

from yandex_mcp.client import api_client
from yandex_mcp.enums import ResponseFormat
from yandex_mcp.errors import handle_api_error
from yandex_mcp.formatters import format_ads_markdown
from yandex_mcp.models.direct import (
    CreateTextAdInput,
    GetAdsInput,
    ManageAdInput,
    UpdateTextAdInput,
)
from yandex_mcp.server import mcp
from yandex_mcp.tools._manage import execute_manage_operation


@mcp.tool(
    name="direct_get_ads",
    annotations={
        "title": "Get Yandex Direct Ads",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def direct_get_ads(params: GetAdsInput) -> str:
    """Get list of ads from Yandex Direct.

    Retrieves ads with their content and moderation status.

    Args:
        params: Filter and pagination parameters

    Returns:
        Ads list in markdown or JSON format
    """
    try:
        selection_criteria: dict = {}

        if params.campaign_ids:
            selection_criteria["CampaignIds"] = params.campaign_ids
        if params.adgroup_ids:
            selection_criteria["AdGroupIds"] = params.adgroup_ids
        if params.ad_ids:
            selection_criteria["Ids"] = params.ad_ids
        if params.states:
            selection_criteria["States"] = [s.value for s in params.states]
        if params.statuses:
            selection_criteria["Statuses"] = [s.value for s in params.statuses]

        request_params = {
            "SelectionCriteria": selection_criteria,
            "FieldNames": [
                "Id", "AdGroupId", "CampaignId", "Type", "State", "Status",
                "StatusClarification",
            ],
            "TextAdFieldNames": ["Title", "Title2", "Text", "Href", "Mobile", "DisplayDomain"],
            "Page": {"Limit": params.limit, "Offset": params.offset},
        }

        result = await api_client.direct_request("ads", "get", request_params)
        ads = result.get("result", {}).get("Ads", [])

        if params.response_format == ResponseFormat.JSON:
            return json.dumps(
                {"ads": ads, "total": len(ads)},
                indent=2,
                ensure_ascii=False,
            )

        return format_ads_markdown(ads)

    except Exception as e:
        return handle_api_error(e)


@mcp.tool(
    name="direct_create_text_ad",
    annotations={
        "title": "Create Yandex Direct Text Ad",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def direct_create_text_ad(params: CreateTextAdInput) -> str:
    """Create a new text ad.

    Creates a text ad in the specified ad group.
    The ad will be in DRAFT status until moderated.

    Args:
        params: Ad content and settings

    Returns:
        Created ad ID
    """
    try:
        text_ad: dict = {
            "Title": params.title,
            "Text": params.text,
            "Href": params.href,
            "Mobile": "YES" if params.mobile else "NO",
        }

        if params.title2:
            text_ad["Title2"] = params.title2
        if params.ad_image_hash:
            text_ad["AdImageHash"] = params.ad_image_hash

        ad = {"AdGroupId": params.adgroup_id, "TextAd": text_ad}

        request_params = {"Ads": [ad]}

        result = await api_client.direct_request("ads", "add", request_params)
        add_results = result.get("result", {}).get("AddResults", [])

        if add_results and add_results[0].get("Id"):
            return (
                f"Ad created successfully. ID: {add_results[0]['Id']}\n\n"
                "Note: Submit for moderation using direct_moderate_ads."
            )

        errors: list[str] = []
        for r in add_results:
            if r.get("Errors"):
                errors.extend([e.get("Message", "Unknown error") for e in r["Errors"]])

        return "Failed to create ad:\n" + "\n".join(f"- {e}" for e in errors)

    except Exception as e:
        return handle_api_error(e)


@mcp.tool(
    name="direct_update_ad",
    annotations={
        "title": "Update Yandex Direct Ad",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def direct_update_ad(params: UpdateTextAdInput) -> str:
    """Update a text ad.

    Allows updating ad title, text, and landing page URL.
    Only specified fields will be updated.
    Note: Updated ad will need to be re-moderated.

    Args:
        params: Ad ID and fields to update

    Returns:
        Operation result
    """
    try:
        text_ad_update: dict = {}

        if params.title is not None:
            text_ad_update["Title"] = params.title
        if params.title2 is not None:
            text_ad_update["Title2"] = params.title2
        if params.text is not None:
            text_ad_update["Text"] = params.text
        if params.href is not None:
            text_ad_update["Href"] = params.href

        if not text_ad_update:
            return "No fields specified for update."

        ad_update = {"Id": params.ad_id, "TextAd": text_ad_update}

        request_params = {"Ads": [ad_update]}

        result = await api_client.direct_request("ads", "update", request_params)
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

        return (
            f"Ad {params.ad_id} updated successfully. "
            "Note: Submit for moderation using direct_moderate_ads."
        )

    except Exception as e:
        return handle_api_error(e)


# --- Manage operations ---


@mcp.tool(
    name="direct_moderate_ads",
    annotations={
        "title": "Submit Ads for Moderation",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def direct_moderate_ads(params: ManageAdInput) -> str:
    """Submit ads for moderation.

    Sends ads with DRAFT status to Yandex moderators for review.
    """
    return await execute_manage_operation(
        service="ads",
        method="moderate",
        ids=params.ad_ids,
        ids_field="Ids",
        result_key="ModerateResults",
        entity_name="ad",
        action_past_tense="submitted for moderation",
    )


@mcp.tool(
    name="direct_suspend_ads",
    annotations={
        "title": "Suspend Yandex Direct Ads",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def direct_suspend_ads(params: ManageAdInput) -> str:
    """Suspend (pause) ads."""
    return await execute_manage_operation(
        service="ads",
        method="suspend",
        ids=params.ad_ids,
        ids_field="Ids",
        result_key="SuspendResults",
        entity_name="ad",
        action_past_tense="suspended",
    )


@mcp.tool(
    name="direct_resume_ads",
    annotations={
        "title": "Resume Yandex Direct Ads",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def direct_resume_ads(params: ManageAdInput) -> str:
    """Resume suspended ads."""
    return await execute_manage_operation(
        service="ads",
        method="resume",
        ids=params.ad_ids,
        ids_field="Ids",
        result_key="ResumeResults",
        entity_name="ad",
        action_past_tense="resumed",
    )


@mcp.tool(
    name="direct_archive_ads",
    annotations={
        "title": "Archive Yandex Direct Ads",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def direct_archive_ads(params: ManageAdInput) -> str:
    """Archive ads.

    Archived ads are hidden from the main list but can be restored.
    """
    return await execute_manage_operation(
        service="ads",
        method="archive",
        ids=params.ad_ids,
        ids_field="Ids",
        result_key="ArchiveResults",
        entity_name="ad",
        action_past_tense="archived",
    )


@mcp.tool(
    name="direct_unarchive_ads",
    annotations={
        "title": "Unarchive Yandex Direct Ads",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def direct_unarchive_ads(params: ManageAdInput) -> str:
    """Restore archived ads.

    Unarchives ads and makes them visible in the main ad list.
    """
    return await execute_manage_operation(
        service="ads",
        method="unarchive",
        ids=params.ad_ids,
        ids_field="Ids",
        result_key="UnarchiveResults",
        entity_name="ad",
        action_past_tense="unarchived",
    )


@mcp.tool(
    name="direct_delete_ads",
    annotations={
        "title": "Delete Yandex Direct Ads",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def direct_delete_ads(params: ManageAdInput) -> str:
    """Delete ads permanently.

    WARNING: This action is irreversible.
    Consider archiving ads instead if you might need them later.
    """
    return await execute_manage_operation(
        service="ads",
        method="delete",
        ids=params.ad_ids,
        ids_field="Ids",
        result_key="DeleteResults",
        entity_name="ad",
        action_past_tense="deleted",
    )
