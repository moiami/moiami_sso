from fastapi.security import OAuth2PasswordBearer

SCHEME = OAuth2PasswordBearer(tokenUrl="login")
SECRET_KEY = (
    "M&6u_hdJ-)Qvx:yGkN+2|1a917e3c181d9399a72327e00f78ff8a9992aeea|3ae318fbdc247ce171ea90c244cc46e4"
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_MINUTES = 10080

DB_URL = "postgresql+asyncpg://postgres:root@db:5432/postgres"

ADMIN_USERNAME = "admin"
