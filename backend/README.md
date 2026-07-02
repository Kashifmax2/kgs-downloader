# Video Downloader API

FastAPI backend using yt-dlp to extract video download links.

## Local Development

1. Create a virtual environment:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the server:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

4. The API will be available at `http://localhost:8000`

## API Endpoints

### GET /
Health check endpoint.

### GET /health
Returns `{"status": "healthy"}`

### POST /api/download
Extract video download information from a URL.

**Request Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=..."
}
```

**Response:**
```json
{
  "title": "Video Title",
  "thumbnail": "https://...",
  "duration": "5:32",
  "download_url": "https://...",
  "format": "mp4",
  "quality": "best"
}
```

## Deployment

### Render (Free Tier)

1. Connect your repository to Render
2. Use the `render.yaml` file or:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. Set environment to Docker or use nixpacks.toml

### Railway

1. Connect your repository to Railway
2. Railway will auto-detect Python and use nixpacks.toml
3. The app will deploy automatically

### Fly.io

1. Install flyctl: `curl -L https://fly.io/install.sh | sh`
2. Login: `fly auth login`
3. Launch: `fly launch`

## Environment Variables

No environment variables required for basic operation.

## Supported Platforms

yt-dlp supports 1000+ sites including:
- YouTube
- TikTok
- Instagram
- Facebook
- Twitter/X
- Vimeo
- Dailymotion
- And many more...
