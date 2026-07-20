from fastapi import FastAPI
from app.routers.upload import router as upload_router
app = FastAPI(
    title="CramWise API",
    version="1.0.0",
    description="AI-powered Academic Knowledge Platform"
)


app.include_router(upload_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to CramWise!"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }