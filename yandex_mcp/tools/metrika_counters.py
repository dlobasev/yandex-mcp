"""Yandex Metrika counter management tools."""

import json

from yandex_mcp.client import api_client
from yandex_mcp.enums import ResponseFormat
from yandex_mcp.errors import handle_api_error
from yandex_mcp.formatters import (
    format_metrika_counter_detail_markdown,
    format_metrika_counters_markdown,
)
from yandex_mcp.models.metrika import (
    CreateCounterInput,
    DeleteCounterInput,
    GetCounterInput,
    GetCountersInput,
)
from yandex_mcp.server import mcp


@mcp.tool(
    name="metrika_get_counters",
    annotations={
        "title": "Get Yandex Metrika Counters",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def metrika_get_counters(params: GetCountersInput) -> str:
    """Get list of Metrika counters (tags).

    Retrieves all counters accessible to the user.

    Args:
        params: Filter parameters

    Returns:
        Counters list in markdown or JSON format
    """
    try:
        query_params: dict = {}
        if params.favorite is not None:
            query_params["favorite"] = str(params.favorite).lower()
        if params.search_string:
            query_params["search_string"] = params.search_string

        result = await api_client.metrika_request(
            "/management/v1/counters",
            params=query_params,
        )

        counters = result.get("counters", [])

        if params.response_format == ResponseFormat.JSON:
            return json.dumps(
                {"counters": counters, "total": result.get("rows", len(counters))},
                indent=2,
                ensure_ascii=False,
            )

        return format_metrika_counters_markdown(counters)

    except Exception as e:
        return handle_api_error(e)


@mcp.tool(
    name="metrika_get_counter",
    annotations={
        "title": "Get Yandex Metrika Counter Details",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def metrika_get_counter(params: GetCounterInput) -> str:
    """Get detailed information about a specific counter.

    Retrieves full counter settings including code options, webvisor, and grants.

    Args:
        params: Counter ID

    Returns:
        Counter details in markdown or JSON format
    """
    try:
        result = await api_client.metrika_request(
            f"/management/v1/counter/{params.counter_id}",
        )

        counter = result.get("counter", {})

        if params.response_format == ResponseFormat.JSON:
            return json.dumps(counter, indent=2, ensure_ascii=False)

        return format_metrika_counter_detail_markdown(counter)

    except Exception as e:
        return handle_api_error(e)


@mcp.tool(
    name="metrika_create_counter",
    annotations={
        "title": "Create Yandex Metrika Counter",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def metrika_create_counter(params: CreateCounterInput) -> str:
    """Create a new Metrika counter.

    Creates a counter for tracking website statistics.

    Args:
        params: Counter name and site URL

    Returns:
        Created counter ID and tracking code
    """
    try:
        data = {
            "counter": {
                "name": params.name,
                "site2": {"site": params.site},
            }
        }

        result = await api_client.metrika_request(
            "/management/v1/counters",
            method="POST",
            data=data,
        )

        counter = result.get("counter", {})
        counter_id = counter.get("id")

        return f"""Counter created successfully!

**ID**: {counter_id}
**Name**: {counter.get('name')}
**Site**: {counter.get('site2', {}).get('site')}

Add this tracking code to your website:
```html
<!-- Yandex.Metrika counter -->
<script type="text/javascript">
   (function(m,e,t,r,i,k,a){{m[i]=m[i]||function(){{(m[i].a=m[i].a||[]).push(arguments)}};
   m[i].l=1*new Date();
   for (var j = 0; j < document.scripts.length; j++) {{if (document.scripts[j].src === r) {{ return; }}}}
   k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)}})
   (window, document, "script", "https://mc.yandex.ru/metrika/tag.js", "ym");

   ym({counter_id}, "init", {{
        clickmap:true,
        trackLinks:true,
        accurateTrackBounce:true
   }});
</script>
```"""

    except Exception as e:
        return handle_api_error(e)


@mcp.tool(
    name="metrika_delete_counter",
    annotations={
        "title": "Delete Yandex Metrika Counter",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def metrika_delete_counter(params: DeleteCounterInput) -> str:
    """Delete a Metrika counter.

    WARNING: This action is irreversible. All historical data will be lost.

    Args:
        params: Counter ID to delete

    Returns:
        Operation result
    """
    try:
        await api_client.metrika_request(
            f"/management/v1/counter/{params.counter_id}",
            method="DELETE",
        )

        return f"Counter {params.counter_id} deleted successfully."

    except Exception as e:
        return handle_api_error(e)
