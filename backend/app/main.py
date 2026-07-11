from fastapi import FastAPI

app = FastAPI(
    title="CramWise API",
    version="1.0.0",
    description="AI-powered Academic Knowledge Platform"
)


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