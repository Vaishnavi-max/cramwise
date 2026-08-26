from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.upload import router as upload_router
from app.routers.notes import router as notes_router


# ==========================================================
# CREATE FASTAPI APP
# ==========================================================

app = FastAPI(
    title="CramWise API",
    description="Backend API for the CramWise academic preparation platform.",
    version="1.0.0",
)


# ==========================================================
# CORS
# ==========================================================

# React/Vite runs on port 5173 during development.
#
# FastAPI runs on port 8000.
#
# Since these are different origins, the browser needs
# permission to allow the React frontend to communicate
# with this backend.

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================================
# ROUTERS
# ==========================================================

app.include_router(
    upload_router
)

app.include_router(
    notes_router
)


# ==========================================================
# ROOT
# ==========================================================

@app.get("/")
def root():
    return {
        "message": "Welcome to CramWise!"
    }


# ==========================================================
# HEALTH CHECK
# ==========================================================

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }