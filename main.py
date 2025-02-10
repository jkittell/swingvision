from fastapi import FastAPI
from src.routers import swing_analysis

app = FastAPI(
    title="Golf Swing Analysis API",
    description="An API for analyzing and improving golf swings using video processing and AI models.",
    version="0.1.0",
)

app.include_router(swing_analysis.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)