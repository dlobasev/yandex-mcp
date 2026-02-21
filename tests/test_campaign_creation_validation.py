"""Unit tests for CreateCampaignInput strategy validation."""

import pytest

from yandex_mcp.models.direct import CreateCampaignInput


def test_default_strategy_no_extra_params():
    """Minimal campaign creation with defaults (HIGHEST_POSITION + SERVING_OFF)."""
    inp = CreateCampaignInput(name="Test", start_date="2026-03-01")
    assert inp.search_strategy.value == "HIGHEST_POSITION"
    assert inp.network_strategy.value == "SERVING_OFF"


def test_wb_maximum_clicks_requires_weekly_spend():
    """WB_MAXIMUM_CLICKS without weekly_spend_limit raises ValueError."""
    with pytest.raises(ValueError, match="weekly_spend_limit"):
        CreateCampaignInput(
            name="Test",
            start_date="2026-03-01",
            search_strategy="WB_MAXIMUM_CLICKS",
        )


def test_wb_maximum_clicks_with_spend():
    """WB_MAXIMUM_CLICKS with weekly_spend_limit passes validation."""
    inp = CreateCampaignInput(
        name="Test",
        start_date="2026-03-01",
        search_strategy="WB_MAXIMUM_CLICKS",
        weekly_spend_limit=1000.0,
    )
    assert inp.weekly_spend_limit == 1000.0


def test_average_cpc_requires_average_cpc():
    """AVERAGE_CPC without average_cpc raises ValueError."""
    with pytest.raises(ValueError, match="average_cpc"):
        CreateCampaignInput(
            name="Test",
            start_date="2026-03-01",
            search_strategy="AVERAGE_CPC",
        )


def test_average_cpc_with_value():
    """AVERAGE_CPC with average_cpc passes validation."""
    inp = CreateCampaignInput(
        name="Test",
        start_date="2026-03-01",
        search_strategy="AVERAGE_CPC",
        average_cpc=30.0,
    )
    assert inp.average_cpc == 30.0


def test_average_cpa_requires_both_params():
    """AVERAGE_CPA without average_cpa raises ValueError."""
    with pytest.raises(ValueError, match="average_cpa"):
        CreateCampaignInput(
            name="Test",
            start_date="2026-03-01",
            search_strategy="AVERAGE_CPA",
            goal_id=12345,
        )


def test_average_cpa_requires_goal_id():
    """AVERAGE_CPA without goal_id raises ValueError."""
    with pytest.raises(ValueError, match="goal_id"):
        CreateCampaignInput(
            name="Test",
            start_date="2026-03-01",
            search_strategy="AVERAGE_CPA",
            average_cpa=50.0,
        )


def test_average_cpa_with_all_params():
    """AVERAGE_CPA with both params passes validation."""
    inp = CreateCampaignInput(
        name="Test",
        start_date="2026-03-01",
        search_strategy="AVERAGE_CPA",
        average_cpa=50.0,
        goal_id=12345,
    )
    assert inp.average_cpa == 50.0
    assert inp.goal_id == 12345


def test_pay_for_conversion_requires_cpa():
    """PAY_FOR_CONVERSION without pay_for_conversion_cpa raises ValueError."""
    with pytest.raises(ValueError, match="pay_for_conversion_cpa"):
        CreateCampaignInput(
            name="Test",
            start_date="2026-03-01",
            search_strategy="PAY_FOR_CONVERSION",
            goal_id=12345,
        )


def test_pay_for_conversion_requires_goal_id():
    """PAY_FOR_CONVERSION without goal_id raises ValueError."""
    with pytest.raises(ValueError, match="goal_id"):
        CreateCampaignInput(
            name="Test",
            start_date="2026-03-01",
            search_strategy="PAY_FOR_CONVERSION",
            pay_for_conversion_cpa=100.0,
        )


def test_pay_for_conversion_with_all_params():
    """PAY_FOR_CONVERSION with both params passes validation."""
    inp = CreateCampaignInput(
        name="Test",
        start_date="2026-03-01",
        search_strategy="PAY_FOR_CONVERSION",
        pay_for_conversion_cpa=100.0,
        goal_id=12345,
    )
    assert inp.pay_for_conversion_cpa == 100.0


def test_network_wb_maximum_clicks_requires_weekly_spend():
    """Network WB_MAXIMUM_CLICKS without weekly_spend_limit raises ValueError."""
    with pytest.raises(ValueError, match="weekly_spend_limit"):
        CreateCampaignInput(
            name="Test",
            start_date="2026-03-01",
            network_strategy="WB_MAXIMUM_CLICKS",
        )


def test_network_average_cpc_requires_param():
    """Network AVERAGE_CPC without network_average_cpc raises ValueError."""
    with pytest.raises(ValueError, match="network_average_cpc"):
        CreateCampaignInput(
            name="Test",
            start_date="2026-03-01",
            network_strategy="AVERAGE_CPC",
        )


def test_network_average_cpc_with_value():
    """Network AVERAGE_CPC with network_average_cpc passes validation."""
    inp = CreateCampaignInput(
        name="Test",
        start_date="2026-03-01",
        network_strategy="AVERAGE_CPC",
        network_average_cpc=20.0,
    )
    assert inp.network_average_cpc == 20.0


def test_serving_off_no_extra_params():
    """SERVING_OFF strategy requires no extra parameters."""
    inp = CreateCampaignInput(
        name="Test",
        start_date="2026-03-01",
        search_strategy="SERVING_OFF",
        network_strategy="SERVING_OFF",
    )
    assert inp.search_strategy.value == "SERVING_OFF"
    assert inp.network_strategy.value == "SERVING_OFF"


def test_optional_campaign_fields():
    """Optional fields are accepted correctly."""
    inp = CreateCampaignInput(
        name="Full Campaign",
        start_date="2026-03-01",
        end_date="2026-12-31",
        daily_budget_amount=1000.0,
        daily_budget_mode="DISTRIBUTED",
        negative_keywords=["free", "cheap"],
        time_zone="Europe/Moscow",
        counter_ids=[12345678],
        excluded_sites=["example.com"],
        blocked_ips=["1.2.3.4"],
    )
    assert inp.end_date == "2026-12-31"
    assert inp.daily_budget_amount == 1000.0
    assert inp.negative_keywords == ["free", "cheap"]
    assert inp.counter_ids == [12345678]


def test_invalid_date_format():
    """Invalid date format is rejected."""
    with pytest.raises(ValueError):
        CreateCampaignInput(
            name="Test",
            start_date="01-03-2026",
        )