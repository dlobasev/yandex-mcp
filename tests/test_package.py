"""Tests for package structure and tool registration."""


def test_mcp_import():
    """mcp object is importable from the package root."""
    from yandex_mcp import mcp

    assert mcp is not None
    assert mcp.name == "yandex_mcp"


def test_all_47_tools_registered():
    """All 47 tools are registered with correct names."""
    from yandex_mcp import mcp

    tools = mcp._tool_manager._tools

    expected_tools = [
        "direct_get_campaigns",
        "direct_create_campaign",
        "direct_suspend_campaigns",
        "direct_resume_campaigns",
        "direct_archive_campaigns",
        "direct_unarchive_campaigns",
        "direct_delete_campaigns",
        "direct_update_campaign",
        "direct_get_adgroups",
        "direct_create_adgroup",
        "direct_update_adgroup",
        "direct_get_ads",
        "direct_create_text_ad",
        "direct_update_ad",
        "direct_moderate_ads",
        "direct_suspend_ads",
        "direct_resume_ads",
        "direct_archive_ads",
        "direct_unarchive_ads",
        "direct_delete_ads",
        "direct_get_keywords",
        "direct_add_keywords",
        "direct_set_keyword_bids",
        "direct_delete_keywords",
        "direct_get_statistics",
        "direct_upload_image",
        "direct_get_images",
        "direct_delete_images",
        "direct_create_sitelink_set",
        "direct_get_sitelink_sets",
        "direct_delete_sitelink_sets",
        "direct_create_callouts",
        "direct_get_callouts",
        "direct_delete_callouts",
        "metrika_get_counters",
        "metrika_get_counter",
        "metrika_create_counter",
        "metrika_delete_counter",
        "metrika_get_goals",
        "metrika_create_goal",
        "metrika_get_report",
        "metrika_get_report_by_time",
        "wordstat_top_requests",
        "wordstat_dynamics",
        "wordstat_regions",
        "wordstat_regions_tree",
        "wordstat_user_info",
    ]

    assert len(tools) == 47
    for name in expected_tools:
        assert name in tools, f"Missing tool: {name}"


def test_tool_annotations():
    """Destructive tools have destructiveHint=True, read-only tools have readOnlyHint=True."""
    from yandex_mcp import mcp

    tools = mcp._tool_manager._tools

    destructive = ["direct_delete_campaigns", "direct_delete_ads", "direct_delete_keywords",
                    "direct_delete_images", "direct_delete_sitelink_sets",
                    "direct_delete_callouts", "metrika_delete_counter"]
    for name in destructive:
        tool = tools[name]
        assert tool.annotations.destructiveHint is True, f"{name} should be destructive"

    readonly = ["direct_get_campaigns", "direct_get_ads", "direct_get_keywords",
                "direct_get_adgroups", "direct_get_statistics", "direct_get_images",
                "direct_get_sitelink_sets", "direct_get_callouts",
                "metrika_get_counters", "metrika_get_counter",
                "metrika_get_goals", "metrika_get_report", "metrika_get_report_by_time"]
    for name in readonly:
        tool = tools[name]
        assert tool.annotations.readOnlyHint is True, f"{name} should be read-only"