from types import SimpleNamespace

from app.core.security import create_access_token, decode_access_token, hash_password, verify_password


def test_password_hash_round_trip() -> None:
    password = "StrongPass123!"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True


def test_access_token_round_trip() -> None:
    settings = SimpleNamespace(
        jwt_secret_key="sjFhukbXZhnym2azkdIf1Kw4WuxPmqhNQSliDv5SMql",
        jwt_algorithm="HS256",
        jwt_access_token_expire_minutes=60,
    )
    token = create_access_token(subject="admin", settings=settings)
    payload = decode_access_token(token, settings)
    assert payload["sub"] == "admin"
