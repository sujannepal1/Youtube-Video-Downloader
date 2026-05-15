# YT Audio Dataset

Download YouTube audio tracks and store their metadata in a database for music classification.

## Architecture

```
yt-audio-dataset/
│
├── app/
│   ├── main.py          # FastAPI entry point
│   ├── routes.py        # API routes
│   ├── schemas.py       # Request / response models
│   ├── database.py      # DB connection (SQLAlchemy)
│   └── config.py        # Pydantic settings
│
├── worker/
│   ├── celery_app.py    # Celery configuration
│   ├── tasks.py         # Background download jobs
│   └── utils.py         # yt-dlp helpers (metadata + audio)
│
├── models/
│   └── song.py          # SQLAlchemy Song model + save_song()
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Quick start

```bash
# 1. Copy and (optionally) edit environment variables
cp .env.example .env

# 2. Build and start all services
docker compose up --build
```

The API will be available at **http://localhost:8000**.  
Interactive docs: **http://localhost:8000/docs**

## API

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/download` | Enqueue a single download job |
| `POST` | `/api/bulk-download` | Enqueue multiple download jobs at once |
| `GET`  | `/api/status/{task_id}` | Poll task status |
| `GET`  | `/api/songs` | List all downloaded songs |
| `GET`  | `/api/songs/{id}` | Get a single song by ID |

### Example – submit a download

```bash
curl -X POST http://localhost:8000/api/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "labels": ["happy"]}'
```

Response:
```json
{"task_id": "abc123...", "status": "queued"}
```

### Example – bulk-submit multiple downloads

```bash
curl -X POST http://localhost:8000/api/bulk-download \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"url": "https://www.youtube.com/watch?v=video1", "labels": ["happy"]},
      {"url": "https://www.youtube.com/watch?v=video2", "labels": ["sad"]},
      {"url": "https://www.youtube.com/watch?v=video3", "labels": ["angry"]}
    ]
  }'
```

Response:
```json
{
  "total": 3,
  "enqueued": [
    {"task_id": "abc1...", "status": "queued"},
    {"task_id": "abc2...", "status": "queued"},
    {"task_id": "abc3...", "status": "queued"}
  ]
}
```

## Services

| Service | Image | Port |
|---------|-------|------|
| `api` | local build | 8000 |
| `worker` | local build | – |
| `db` | postgres:15 | 5432 |
| `redis` | redis:7-alpine | 6379 |

