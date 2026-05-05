import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from metis.auth.router import router as auth_router

app = FastAPI(title="METIS", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.get("/ping")
def ping():
    return {"status": "ok"}
