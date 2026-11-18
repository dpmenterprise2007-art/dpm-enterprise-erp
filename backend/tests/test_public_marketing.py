from fastapi import HTTPException
from pydantic import ValidationError
import pytest

from app.routers.public_marketing import PublicEnquiry, robots_txt, sitemap_xml, marketing_status


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


def test_robots_excludes_private_api_and_points_to_sitemap():
    response = robots_txt()
    assert "Disallow: /api/" in response.body.decode()
    assert "Sitemap: https://www.dpmenterprise.in/sitemap.xml" in response.body.decode()


def test_sitemap_contains_only_public_routes():
    response = sitemap_xml()
    body = response.body.decode()
    assert "https://www.dpmenterprise.in/contact" in body
    assert "/api/" not in body
    assert "/login" not in body


def test_marketing_status_does_not_claim_social_is_connected():
    status = marketing_status()
    assert status["public_enquiry_api"] == "ready"
    assert status["social_publishing"] == "not_connected"
