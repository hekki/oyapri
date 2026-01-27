from fastapi import FastAPI

from app.api import router

app = FastAPI(title="oyapri")
app.include_router(router)
