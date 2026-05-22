import os
from pathlib import Path
from uuid import UUID, uuid4

import pytest

ROOT = Path(__file__).resolve().parent.parent
os.environ.setdefault("PRIVATE_KEY_PATH", str(ROOT / "keys" / "private.pem"))
os.environ.setdefault("PUBLIC_KEY_PATH", str(ROOT / "keys" / "public.pem"))
os.environ.setdefault("CLIENT_ID", "test-client")
os.environ.setdefault("ISSUER_URL", "https://test.sso")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://test:test@localhost:5432/test",
)

from src.data.models.role import Role  # noqa: E402
from src.data.models.user import User  # noqa: E402
from src.services.security_service import create_jwt  # noqa: E402


@pytest.fixture
def admin_role() -> Role:
    role = Role("admin", "Administrator")
    role.id = uuid4()
    return role


@pytest.fixture
def member_role() -> Role:
    role = Role("member", "Standard member")
    role.id = uuid4()
    return role


def make_user(
    login: str = "alice",
    password: str = "secret123",
    *,
    roles: list[Role] | None = None,
    user_id: UUID | None = None,
) -> User:
    user = User(login, password, "Alice", "Smith", "alice@example.com")
    user.id = user_id or uuid4()
    user.roles = list(roles or [])
    return user


async def token_for_user(user: User, token_type: str = "access") -> str:
    if token_type == "access":
        payload = {"id": str(user.id), "roles": [r.name for r in user.roles]}
    else:
        payload = {"id": str(uuid4()), "user_id": str(user.id)}
    return await create_jwt(payload, token_type)
