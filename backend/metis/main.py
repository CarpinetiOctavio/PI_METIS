import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from metis.api.v1.analysis import router as analysis_router
from metis.api.v1.history import router as history_router
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
app.include_router(analysis_router, prefix="/api/v1")
app.include_router(history_router, prefix="/api/v1")


@app.get("/ping")
def ping():
    return {"status": "ok"}
