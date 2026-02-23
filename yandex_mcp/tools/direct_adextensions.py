"""Yandex Direct ad extension (callout) management tools."""

import json

from yandex_mcp.client import api_client
from yandex_mcp.enums import ResponseFormat
from yandex_mcp.errors import handle_api_error
from yandex_mcp.formatters import format_callouts_markdown
from yandex_mcp.models.direct import (
    CreateCalloutsInput,
    DeleteCalloutsInput,
    GetCalloutsInput,
)
from yandex_mcp.server import mcp


@mcp.tool(
    name="direct_create_callouts",
    annotations={
        "title": "Create Yandex Direct Callout Extensions",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def direct_create_callouts(params: CreateCalloutsInput) -> str:
    """Create callout extensions (уточнения).

    Callouts are short text snippets shown below ads (e.g., "Free shipping",
    "24/7 support"). Each callout is max 25 characters.

    Returns IDs which can be used in direct_create_text_ad (ad_extension_ids).

    Args:
        params: List of callout texts to create

    Returns:
        Created callout IDs
    """
    try:
        ad_extensions = [
            {"Callout": {"CalloutText": text}}
            for text in params.callout_texts
        ]

        request_params = {"AdExtensions": ad_extensions}

        result = await api_client.direct_request("adextensions", "add", request_params)
        add_results = result.get("result", {}).get("AddResults", [])

        created_ids: list[int] = []
        errors: list[str] = []
        for i, r in enumerate(add_results):
            if r.get("Id"):
                created_ids.append(r["Id"])
            if r.get("Errors"):
                text = params.callout_texts[i] if i < len(params.callout_texts) else "?"
                errors.extend(
                    f'"{text}": {e.get("Message", "Unknown error")}'
                    for e in r["Errors"]
                )

        parts: list[str] = []
        if created_ids:
            ids_str = ", ".join(str(i) for i in created_ids)
            parts.append(
                f"Created {len(created_ids)} callout(s). IDs: {ids_str}\n\n"
                "Use these IDs in direct_create_text_ad (ad_extension_ids parameter)."
            )
        if errors:
            parts.append("Errors:\n" + "\n".join(f"- {e}" for e in errors))

        return "\n\n".join(parts) if parts else "No callouts created."

    except Exception as e:
        return handle_api_error(e)


@mcp.tool(
    name="direct_get_callouts",
    annotations={
        "title": "Get Yandex Direct Callout Extensions",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def direct_get_callouts(params: GetCalloutsInput) -> str:
    """Get callout extensions (уточнения).

    Retrieves callouts with their texts and moderation status.
    Omit callout_ids to get all callouts.

    Args:
        params: Filter and pagination parameters

    Returns:
        Callouts list in markdown or JSON format
    """
    try:
        selection_criteria: dict = {
            "Types": ["CALLOUT"],
            "States": ["ON"],
        }

        if params.callout_ids:
            selection_criteria["Ids"] = params.callout_ids

        request_params = {
            "SelectionCriteria": selection_criteria,
            "FieldNames": ["Id", "Type", "Status", "Associated"],
            "CalloutFieldNames": ["CalloutText"],
            "Page": {"Limit": params.limit, "Offset": params.offset},
        }

        result = await api_client.direct_request("adextensions", "get", request_params)
        extensions = result.get("result", {}).get("AdExtensions", [])

        if params.response_format == ResponseFormat.JSON:
            return json.dumps(
                {"callouts": extensions, "total": len(extensions)},
                indent=2,
                ensure_ascii=False,
            )

        return format_callouts_markdown(extensions)

    except Exception as e:
        return handle_api_error(e)


@mcp.tool(
    name="direct_delete_callouts",
    annotations={
        "title": "Delete Yandex Direct Callout Extensions",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def direct_delete_callouts(params: DeleteCalloutsInput) -> str:
    """Delete callout extensions.

    Callouts attached to ads cannot be deleted.
    Detach from ads first by updating the ad.

    Args:
        params: Callout IDs to delete

    Returns:
        Operation result
    """
    try:
        request_params = {
            "SelectionCriteria": {"Ids": params.callout_ids},
        }

        result = await api_client.direct_request("adextensions", "delete", request_params)
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

        response = f"Successfully deleted {success_count} callout(s)."
        if errors:
            response += "\n\nErrors:\n" + "\n".join(f"- {e}" for e in errors)

        return response

    except Exception as e:
        return handle_api_error(e)
