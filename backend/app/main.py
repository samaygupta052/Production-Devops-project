from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router
from .config import APP_NAME

app = FastAPI(title=APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
