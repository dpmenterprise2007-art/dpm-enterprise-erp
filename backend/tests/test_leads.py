from datetime import datetime, timezone
from decimal import Decimal

from app.models import Lead
from app.routers.leads import calculate_lead_score


def test_lead_score_rewards_complete_high_value_enquiry() -> None:
    lead = Lead(
        contact_name="Test Contact",
        company_name="Test Company",
        phone="9999999999",
        email="test@example.com",
        requirement="Corporate office interior",
        estimated_value=Decimal("1500000"),
        follow_up_at=datetime(2026, 11, 20, tzinfo=timezone.utc),
    )
    assert calculate_lead_score(lead) == 90


def test_lead_score_handles_sparse_and_complete_leads() -> None:
    sparse = Lead(contact_name="Walk-in", estimated_value=Decimal("0"))
    assert calculate_lead_score(sparse) == 10

    complete = Lead(
        contact_name="Full",
        company_name="Company",
        phone="9999999999",
        email="full@example.com",
        requirement="Full turnkey project",
        estimated_value=Decimal("5000000"),
        follow_up_at=datetime(2026, 11, 20, tzinfo=timezone.utc),
    )
    assert calculate_lead_score(complete) == 90
