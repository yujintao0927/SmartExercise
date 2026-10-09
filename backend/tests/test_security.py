"""T-23 安全工具测试。"""
import jwt

from app.config import SECRET_KEY
from app.security import create_token, hash_password, verify_password


def test_hash_and_verify():
    h = hash_password("123456")
    assert verify_password("123456", h)
    assert not verify_password("wrong", h)


def test_create_token():
    token = create_token(1, "user")
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    assert payload["sub"] == "1"
    assert payload["role"] == "user"
