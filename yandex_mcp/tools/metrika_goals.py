"""Yandex Metrika goal management tools."""

import json

from yandex_mcp.client import api_client
from yandex_mcp.enums import ResponseFormat
from yandex_mcp.errors import handle_api_error
from yandex_mcp.models.metrika import CreateGoalInput, GetGoalsInput
from yandex_mcp.server import mcp


@mcp.tool(
    name="metrika_get_goals",
    annotations={
        "title": "Get Yandex Metrika Goals",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def metrika_get_goals(params: GetGoalsInput) -> str:
    """Get goals for a Metrika counter.

    Retrieves all configured goals for tracking conversions.

    Args:
        params: Counter ID

    Returns:
        Goals list in markdown or JSON format
    """
    try:
        result = await api_client.metrika_request(
            f"/management/v1/counter/{params.counter_id}/goals",
        )

        goals = result.get("goals", [])

        if params.response_format == ResponseFormat.JSON:
            return json.dumps(
                {"goals": goals, "total": len(goals)},
                indent=2,
                ensure_ascii=False,
            )

        if not goals:
            return "No goals configured for this counter."

        lines = [f"# Goals for Counter {params.counter_id}\n"]
        for goal in goals:
            lines.append(f"## {goal.get('name', 'Unnamed')} (ID: {goal.get('id')})")
            lines.append(f"- **Type**: {goal.get('type', 'N/A')}")

            conditions = goal.get("conditions", [])
            if conditions:
                lines.append("- **Conditions**:")
                for cond in conditions:
                    lines.append(
                        f"  - {cond.get('type', 'N/A')}: "
                        f"{cond.get('url', cond.get('value', 'N/A'))}"
                    )

            lines.append("")

        return "\n".join(lines)

    except Exception as e:
        return handle_api_error(e)


@mcp.tool(
    name="metrika_create_goal",
    annotations={
        "title": "Create Yandex Metrika Goal",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def metrika_create_goal(params: CreateGoalInput) -> str:
    """Create a new goal for a Metrika counter.

    Goals track conversions like page visits, form submissions, clicks, etc.

    Args:
        params: Goal settings

    Returns:
        Created goal ID
    """
    try:
        conditions = [cond.model_dump(exclude_none=True) for cond in params.conditions]

        data = {
            "goal": {
                "name": params.name,
                "type": params.goal_type,
                "conditions": conditions,
            }
        }

        result = await api_client.metrika_request(
            f"/management/v1/counter/{params.counter_id}/goals",
            method="POST",
            data=data,
        )

        goal = result.get("goal", {})

        return (
            f"Goal created successfully!\n\n"
            f"**ID**: {goal.get('id')}\n"
            f"**Name**: {goal.get('name')}\n"
            f"**Type**: {goal.get('type')}"
        )

    except Exception as e:
        return handle_api_error(e)
