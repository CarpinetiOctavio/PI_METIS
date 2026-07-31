import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from metis.api.v1.analysis import router as analysis_router
from metis.api.v1.history import router as history_router
from metis.auth.router import router as auth_router

app = FastAPI(title="METIS", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    # F10 (docs/frontend/informe-diagnostico-ui-rota.md): el default hardcodeado
    # apuntaba a :3000, un puerto que ningún escenario real usa (dev sirve en
    # :5173, nginx en :80) — invisible mientras el proxy de Vite mantenga todo
    # same-origin, pero rompería CORS por completo el día que se corra sin él.
    # .env/.env.example ya fijan FRONTEND_ORIGIN=http://localhost:5173 en la
    # práctica; este default ahora coincide con eso y con el de FRONTEND_URL
    # (auth/router.py, auth/email.py) para el mismo escenario de desarrollo.
    allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")],
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
