from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from src.routers import swing_analysis

app = FastAPI(
    title="Golf Swing Analysis API",
    description="An API for analyzing and improving golf swings using video processing and AI models.",
    version="0.1.0",
)

# Create media directory structure
media_root = Path("media")
media_root.mkdir(exist_ok=True)

# Create subdirectories for different media types
(media_root / "uploads").mkdir(exist_ok=True)    # Original uploaded videos
(media_root / "frames").mkdir(exist_ok=True)     # Processed frames
(media_root / "analyses").mkdir(exist_ok=True)   # Analysis metadata

# Mount the media directory
app.mount("/media", StaticFiles(directory="media"), name="media")

# Include routers
app.include_router(swing_analysis.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)