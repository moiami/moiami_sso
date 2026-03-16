from fastapi import FastAPI
from app.api.routers.AuthRouter import router as auth_router
from app.api.routers.UserRouter import router as user_router
import logging

logging.basicConfig(level=logging.DEBUG, filename="sso.log", filemode="a", datefmt='%Y-%m-%d %H:%M:%S',format="[%(asctime)s] %(levelname)s %(message)s")

app = FastAPI()
app.include_router(auth_router)
app.include_router(user_router)