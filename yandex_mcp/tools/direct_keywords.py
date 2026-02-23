"""Yandex Direct keyword management tools."""

import json

from yandex_mcp.client import api_client
from yandex_mcp.enums import ResponseFormat
from yandex_mcp.errors import handle_api_error
from yandex_mcp.formatters import format_keywords_markdown
from yandex_mcp.enums import AutotargetingCategory
from yandex_mcp.models.direct import (
    AddKeywordsInput,
    GetKeywordsInput,
    ManageKeywordInput,
    SetAutotargetingInput,
    SetKeywordBidsInput,
)
from yandex_mcp.server import mcp
from yandex_mcp.tools._manage import execute_manage_operation


@mcp.tool(
    name="direct_get_keywords",
    annotations={
        "title": "Get Yandex Direct Keywords",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def direct_get_keywords(params: GetKeywordsInput) -> str:
    """Get list of keywords from Yandex Direct.

    Retrieves keywords with their bids and status.

    Args:
        params: Filter and pagination parameters

    Returns:
        Keywords list in markdown or JSON format
    """
    try:
        selection_criteria: dict = {}

        if params.campaign_ids:
            selection_criteria["CampaignIds"] = params.campaign_ids
        if params.adgroup_ids:
            selection_criteria["AdGroupIds"] = params.adgroup_ids
        if params.keyword_ids:
            selection_criteria["Ids"] = params.keyword_ids

        request_params = {
            "SelectionCriteria": selection_criteria,
            "FieldNames": ["Id", "Keyword", "AdGroupId", "CampaignId", "Bid", "State", "Status"],
            "Page": {"Limit": params.limit, "Offset": params.offset},
        }

        result = await api_client.direct_request("keywords", "get", request_params)
        keywords = result.get("result", {}).get("Keywords", [])

        if params.response_format == ResponseFormat.JSON:
            return json.dumps(
                {"keywords": keywords, "total": len(keywords)},
                indent=2,
                ensure_ascii=False,
            )

        return format_keywords_markdown(keywords)

    except Exception as e:
        return handle_api_error(e)


@mcp.tool(
    name="direct_add_keywords",
    annotations={
        "title": "Add Keywords to Yandex Direct",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def direct_add_keywords(params: AddKeywordsInput) -> str:
    """Add keywords to an ad group.

    Creates new keywords in the specified ad group.

    Args:
        params: Keywords to add

    Returns:
        Created keyword IDs
    """
    try:
        keywords_list = []
        for kw in params.keywords:
            keyword: dict = {"Keyword": kw, "AdGroupId": params.adgroup_id}
            if params.bid:
                keyword["Bid"] = int(params.bid * 1_000_000)
            keywords_list.append(keyword)

        request_params = {"Keywords": keywords_list}

        result = await api_client.direct_request("keywords", "add", request_params)
        add_results = result.get("result", {}).get("AddResults", [])

        success_ids = [r["Id"] for r in add_results if r.get("Id") and not r.get("Errors")]
        errors: list[str] = []
        for r in add_results:
            if r.get("Errors"):
                errors.extend([e.get("Message", "Unknown error") for e in r["Errors"]])

        response = f"Successfully added {len(success_ids)} keyword(s)."
        if success_ids:
            response += f"\nIDs: {', '.join(map(str, success_ids))}"
        if errors:
            response += "\n\nErrors:\n" + "\n".join(f"- {e}" for e in errors)

        return response

    except Exception as e:
        return handle_api_error(e)


@mcp.tool(
    name="direct_set_keyword_bids",
    annotations={
        "title": "Set Keyword Bids",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def direct_set_keyword_bids(params: SetKeywordBidsInput) -> str:
    """Set bids for keywords.

    Updates search and/or network bids for specified keywords.

    Args:
        params: Keyword bid settings

    Returns:
        Operation result
    """
    try:
        keyword_bids = []
        for kb in params.keyword_bids:
            bid_item: dict = {"KeywordId": kb.keyword_id}
            if kb.search_bid is not None:
                bid_item["SearchBid"] = int(kb.search_bid * 1_000_000)
            if kb.network_bid is not None:
                bid_item["NetworkBid"] = int(kb.network_bid * 1_000_000)
            keyword_bids.append(bid_item)

        request_params = {"KeywordBids": keyword_bids}

        result = await api_client.direct_request("keywordbids", "set", request_params)
        set_results = result.get("result", {}).get("SetResults", [])

        success = [
            r["KeywordId"]
            for r in set_results
            if r.get("KeywordId") and not r.get("Errors")
        ]

        return f"Successfully updated bids for {len(success)} keyword(s)."

    except Exception as e:
        return handle_api_error(e)


@mcp.tool(
    name="direct_set_autotargeting",
    annotations={
        "title": "Set Autotargeting Categories",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def direct_set_autotargeting(params: SetAutotargetingInput) -> str:
    """Set autotargeting categories for an ad group.

    Controls which query categories the autotargeting engine uses.
    For unified campaigns (ЕПК), updates the ---autotargeting keyword via v501 API.

    Categories:
    - exact: target queries closely matching the ad (целевые)
    - alternative: substitute product queries (альтернативные)
    - competitor: competitor mention queries (конкурентные)
    - broader: wider product interest queries (широкие)
    - accessory: related product queries (сопутствующие)

    Args:
        params: Ad group ID and category toggles

    Returns:
        Updated autotargeting state
    """
    try:
        # Find the ---autotargeting keyword for this ad group
        get_result = await api_client.direct_request(
            "keywords", "get",
            {
                "SelectionCriteria": {"AdGroupIds": [params.adgroup_id]},
                "FieldNames": ["Id", "Keyword"],
            },
            use_v501=True,
        )
        keywords = get_result.get("result", {}).get("Keywords", [])
        at_keyword = next(
            (kw for kw in keywords if kw.get("Keyword") == "---autotargeting"),
            None,
        )

        if not at_keyword:
            return (
                f"No autotargeting keyword found for ad group {params.adgroup_id}. "
                "Autotargeting may not be enabled for this group."
            )

        category_map = {
            AutotargetingCategory.EXACT: params.exact,
            AutotargetingCategory.ALTERNATIVE: params.alternative,
            AutotargetingCategory.COMPETITOR: params.competitor,
            AutotargetingCategory.BROADER: params.broader,
            AutotargetingCategory.ACCESSORY: params.accessory,
        }

        categories = [
            {"Category": cat.value, "Value": "YES" if enabled else "NO"}
            for cat, enabled in category_map.items()
        ]

        update_result = await api_client.direct_request(
            "keywords", "update",
            {"Keywords": [{"Id": at_keyword["Id"], "AutotargetingCategories": categories}]},
            use_v501=True,
        )
        update_results = update_result.get("result", {}).get("UpdateResults", [])

        errors: list[str] = []
        for r in update_results:
            if r.get("Errors"):
                errors.extend([e.get("Message", "Unknown error") for e in r["Errors"]])

        if errors:
            return "Failed to update autotargeting:\n" + "\n".join(f"- {e}" for e in errors)

        enabled = [cat.value for cat, on in category_map.items() if on]
        disabled = [cat.value for cat, on in category_map.items() if not on]
        return (
            f"Autotargeting updated for ad group {params.adgroup_id}.\n"
            f"Enabled: {', '.join(enabled) or 'none'}\n"
            f"Disabled: {', '.join(disabled) or 'none'}"
        )

    except Exception as e:
        return handle_api_error(e)


@mcp.tool(
    name="direct_delete_keywords",
    annotations={
        "title": "Delete Yandex Direct Keywords",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def direct_delete_keywords(params: ManageKeywordInput) -> str:
    """Delete keywords permanently.

    WARNING: This action is irreversible.
    """
    return await execute_manage_operation(
        service="keywords",
        method="delete",
        ids=params.keyword_ids,
        ids_field="Ids",
        result_key="DeleteResults",
        entity_name="keyword",
        action_past_tense="deleted",
    )
