from fastapi import FastAPI
from app.api.routers.AuthRouter import router
import logging

logging.basicConfig(level=logging.DEBUG, filename="sso.log", filemode="a", datefmt='%Y-%m-%d %H:%M:%S',format="[%(asctime)s] %(levelname)s %(message)s")

app = FastAPI()
app.include_router(router)