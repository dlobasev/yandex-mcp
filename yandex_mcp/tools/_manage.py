"""Generic manage operation helper for Direct API entities."""

from yandex_mcp.client import api_client
from yandex_mcp.errors import handle_api_error


async def execute_manage_operation(
    *,
    service: str,
    method: str,
    ids: list[int],
    ids_field: str,
    result_key: str,
    entity_name: str,
    action_past_tense: str,
) -> str:
    """Execute a generic manage operation (suspend/resume/archive/unarchive/delete/moderate).

    Args:
        service: API service name (e.g., "campaigns", "ads", "keywords")
        method: API method name (e.g., "suspend", "resume", "archive")
        ids: List of entity IDs to operate on
        ids_field: Field name in SelectionCriteria (e.g., "Ids")
        result_key: Key in result dict (e.g., "SuspendResults")
        entity_name: Human-readable entity name for messages (e.g., "campaign", "ad")
        action_past_tense: Past tense action for messages (e.g., "suspended", "resumed")

    Returns:
        Formatted operation result message
    """
    try:
        request_params = {"SelectionCriteria": {ids_field: ids}}
        result = await api_client.direct_request(service, method, request_params)
        operation_results = result.get("result", {}).get(result_key, [])

        success = [r["Id"] for r in operation_results if r.get("Id") and not r.get("Errors")]
        errors: list[str] = []
        for r in operation_results:
            if r.get("Errors"):
                errors.extend(
                    f"ID {r.get('Id', '?')}: {e.get('Message', 'Unknown error')}"
                    for e in r["Errors"]
                )

        response = f"Successfully {action_past_tense} {len(success)} {entity_name}(s)."
        if errors:
            response += "\n\nErrors:\n" + "\n".join(f"- {e}" for e in errors)

        return response
    except Exception as e:
        return handle_api_error(e)
