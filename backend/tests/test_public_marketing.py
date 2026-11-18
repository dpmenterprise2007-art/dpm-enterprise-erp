from pydantic import ValidationError
import pytest

from app.routers.public_marketing import (
    PublicEnquiry, public_site, robots_txt, sitemap_xml, marketing_status
)


def test_public_enquiry_validates_minimum_contact_and_requirement():
    payload = PublicEnquiry(
        contact_name="Test Buyer",
        phone="9999999999",
        requirement="Corporate office interior project",
        website="",
    )
    assert payload.contact_name == "Test Buyer"


def test_public_enquiry_rejects_short_requirement():
    with pytest.raises(ValidationError):
        PublicEnquiry(contact_name="AB", phone="9999999999", requirement="short")


def test_public_site_has_enquiry_form_and_site_visit_fee():
    page = public_site().body.decode()
    assert 'id="lead"' in page
    assert "/api/v1/public/enquiries" in page
    assert "₹5,000 + 18% GST" in page
    assert "022 69719769" in page


def test_robots_excludes_private_api_and_points_to_sitemap():
    body = robots_txt().body.decode()
    assert "Disallow: /api/" in body
    assert "Sitemap: https://dpm-enterprise-erp-preview.onrender.com/sitemap.xml" in body


def test_sitemap_contains_only_existing_public_landing_route():
    body = sitemap_xml().body.decode()
    assert "https://dpm-enterprise-erp-preview.onrender.com/site" in body
    assert "/contact" not in body
    assert "/api/" not in body
    assert "/login" not in body


def test_marketing_status_does_not_claim_social_is_connected():
    status = marketing_status()
    assert status["public_site"] == "ready"
    assert status["public_enquiry_api"] == "ready"
    assert status["social_publishing"] == "not_connected"
