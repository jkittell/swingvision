from fastapi import FastAPI
from src.routers.video import router as video_router
from src.config import Base, engine
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="SwingVision API",
    description="An AI-powered golf swing analysis application that helps golfers improve their game through detailed video analysis and personalized feedback.",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
Base.metadata.create_all(bind=engine)

# Include routers with API versioning
app.include_router(video_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)