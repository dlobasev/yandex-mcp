"""Yandex Direct sitelink management tools."""

import json

from yandex_mcp.client import api_client
from yandex_mcp.enums import ResponseFormat
from yandex_mcp.errors import handle_api_error
from yandex_mcp.formatters import format_sitelink_sets_markdown
from yandex_mcp.models.direct import (
    CreateSitelinkSetInput,
    DeleteSitelinkSetsInput,
    GetSitelinkSetsInput,
)
from yandex_mcp.server import mcp


@mcp.tool(
    name="direct_create_sitelink_set",
    annotations={
        "title": "Create Yandex Direct Sitelink Set",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def direct_create_sitelink_set(params: CreateSitelinkSetInput) -> str:
    """Create a sitelink set for ads.

    Creates a set of 1-8 sitelinks (quick links shown below the ad).
    Returns the set ID which can be used in direct_create_text_ad (sitelink_set_id).

    Sitelink sets are immutable — to change sitelinks, create a new set.

    Args:
        params: List of sitelinks with titles, URLs, and optional descriptions

    Returns:
        Created sitelink set ID
    """
    try:
        sitelinks = []
        for sl in params.sitelinks:
            item: dict = {"Title": sl.title}
            if sl.href is not None:
                item["Href"] = sl.href
            if sl.turbo_page_id is not None:
                item["TurboPageId"] = sl.turbo_page_id
            if sl.description is not None:
                item["Description"] = sl.description
            sitelinks.append(item)

        request_params = {
            "SitelinksSets": [{"Sitelinks": sitelinks}],
        }

        result = await api_client.direct_request("sitelinks", "add", request_params)
        add_results = result.get("result", {}).get("AddResults", [])

        if add_results and add_results[0].get("Id"):
            set_id = add_results[0]["Id"]
            return (
                f"Sitelink set created successfully. ID: {set_id}\n"
                f"Contains {len(params.sitelinks)} sitelink(s).\n\n"
                "Use this ID in direct_create_text_ad (sitelink_set_id parameter)."
            )

        errors: list[str] = []
        for r in add_results:
            if r.get("Errors"):
                errors.extend([e.get("Message", "Unknown error") for e in r["Errors"]])

        return "Failed to create sitelink set:\n" + "\n".join(f"- {e}" for e in errors)

    except Exception as e:
        return handle_api_error(e)


@mcp.tool(
    name="direct_get_sitelink_sets",
    annotations={
        "title": "Get Yandex Direct Sitelink Sets",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def direct_get_sitelink_sets(params: GetSitelinkSetsInput) -> str:
    """Get sitelink sets by IDs.

    Retrieves sitelink sets with their titles, URLs, and descriptions.

    Args:
        params: Sitelink set IDs and output format

    Returns:
        Sitelink sets in markdown or JSON format
    """
    try:
        request_params = {
            "SelectionCriteria": {"Ids": params.sitelink_set_ids},
            "FieldNames": ["Id", "Sitelinks"],
            "SitelinkFieldNames": ["Title", "Href", "Description", "TurboPageId"],
        }

        result = await api_client.direct_request("sitelinks", "get", request_params)
        sets = result.get("result", {}).get("SitelinksSets", [])

        if params.response_format == ResponseFormat.JSON:
            return json.dumps(
                {"sitelink_sets": sets, "total": len(sets)},
                indent=2,
                ensure_ascii=False,
            )

        return format_sitelink_sets_markdown(sets)

    except Exception as e:
        return handle_api_error(e)


@mcp.tool(
    name="direct_delete_sitelink_sets",
    annotations={
        "title": "Delete Yandex Direct Sitelink Sets",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def direct_delete_sitelink_sets(params: DeleteSitelinkSetsInput) -> str:
    """Delete sitelink sets.

    Sets attached to ads cannot be deleted.
    Detach the set from ads first by updating the ad.

    Args:
        params: Sitelink set IDs to delete

    Returns:
        Operation result
    """
    try:
        request_params = {
            "SelectionCriteria": {"Ids": params.sitelink_set_ids},
        }

        result = await api_client.direct_request("sitelinks", "delete", request_params)
        delete_results = result.get("result", {}).get("DeleteResults", [])

        success_count = sum(
            1 for r in delete_results
            if r.get("Id") and not r.get("Errors")
        )
        errors: list[str] = []
        for r in delete_results:
            if r.get("Errors"):
                errors.extend(
                    f"ID {r.get('Id', '?')}: {e.get('Message', 'Unknown error')}"
                    for e in r["Errors"]
                )

        response = f"Successfully deleted {success_count} sitelink set(s)."
        if errors:
            response += "\n\nErrors:\n" + "\n".join(f"- {e}" for e in errors)

        return response

    except Exception as e:
        return handle_api_error(e)
