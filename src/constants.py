import os

from fastapi.security import OAuth2PasswordBearer
from pathlib import Path


def key_load(file_path: str) -> str:
    path = Path(file_path)
    if not path.exists():
        raise Exception
    res = ''
    with open(path, "r", encoding="utf-8") as f:
        res = f.read().strip()
    return res


PRIVATE_KEY = key_load(os.getenv("PRIVATE_KEY_PATH"))
PUBLIC_KEY = key_load(os.getenv("PUBLIC_KEY_PATH"))
SCHEME = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)
CLIENT_ID = os.getenv("CLIENT_ID", "caddy-portal")
ISSUER_URL = os.getenv("ISSUER_URL", "https://sso.com")
ALGORITHM = "RS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 5
REFRESH_TOKEN_EXPIRE_MINUTES = 100
DB_URL = os.getenv("DATABASE_URL", "")
ADMIN_USERNAME = "admin"
