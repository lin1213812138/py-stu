import pytest
from app.core.security import hash_password, verify_password, decode_token, create_access_token, create_refresh_token
from uuid import uuid4


def test_password_hash_and_verify():
    hashed = hash_password("test123")
    assert verify_password("test123", hashed)
    assert not verify_password("wrong", hashed)


def test_access_token():
    uid = uuid4()
    token = create_access_token(uid, "alice", "user")
    payload = decode_token(token)
    assert payload["sub"] == str(uid)
    assert payload["username"] == "alice"
    assert payload["role"] == "user"
    assert payload["type"] == "access"


def test_refresh_token():
    uid = uuid4()
    token = create_refresh_token(uid)
    payload = decode_token(token)
    assert payload["sub"] == str(uid)
    assert payload["type"] == "refresh"
