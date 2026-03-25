import logging

from fastapi import FastAPI

from src.api.routers.auth_router import router as auth_router
from src.api.routers.role_router import router as role_router
from src.api.routers.user_router import router as user_router

logging.basicConfig(
    level=logging.DEBUG,
    filename="sso.log",
    filemode="a",
    datefmt="%Y-%m-%d %H:%M:%S",
    format="[%(asctime)s] %(levelname)s %(message)s",
)

app = FastAPI()
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(role_router)
