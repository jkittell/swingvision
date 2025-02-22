# SwingVision

A modern golf swing analysis application that allows users to upload and review golf swing videos.

## Features

- Video upload via drag-and-drop interface
- Supported formats: MP4, MOV
- Real-time video playback
- Dark-themed modern UI
- MinIO integration for video storage

## Tech Stack

### Frontend
- Next.js with TypeScript
- Tailwind CSS for styling
- React-dropzone for file uploads

### Backend
- FastAPI
- MinIO for video storage
- SQLAlchemy with CrateDB

## Setup

1. Start the backend:
```bash
cd swingvision
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. Start the frontend:
```bash
cd frontend
npm install
npm run dev
```

3. Configure MinIO:
- Ensure MinIO is running on port 9000
- Default credentials: minioadmin/minioadmin
- Bucket name: swingvision-videos

## API Endpoints

- `POST /api/v1/videos/`: Upload a video file
- `GET /api/v1/videos/`: List all videos
- `GET /api/v1/videos/{video_id}`: Get specific video
- `DELETE /api/v1/videos/{video_id}`: Delete a video

## Development

The application uses a modular architecture:
- Frontend components are in `frontend/src/components/`
- Backend routes are in `src/routers/`
- Database models in `src/models/`
- API schemas in `src/schemas/`