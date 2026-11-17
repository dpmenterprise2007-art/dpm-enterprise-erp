from app.security import hash_password, verify_password


def test_password_hash_round_trip() -> None:
    encoded = hash_password("Dpm-ERP-Test-Password-123!")
    assert encoded != "Dpm-ERP-Test-Password-123!"
    assert verify_password("Dpm-ERP-Test-Password-123!", encoded)
    assert not verify_password("wrong-password", encoded)
