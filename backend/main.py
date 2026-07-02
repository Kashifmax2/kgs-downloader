from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Video Downloader API",
    description="Extract video download links using yt-dlp",
    version="1.0.0"
)

# CORS configuration for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DownloadRequest(BaseModel):
    url: str


class DownloadResponse(BaseModel):
    title: str
    thumbnail: str | None = None
    duration: str | None = None
    download_url: str
    format: str = "mp4"
    quality: str = "best"


@app.get("/")
async def root():
    return {"message": "Video Downloader API is running", "status": "ok"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/api/download", response_model=DownloadResponse)
async def extract_video(request: DownloadRequest):
    """
    Extract direct download URL from a video platform URL.
    Uses yt-dlp to extract video information without downloading.
    """
    if not request.url or not request.url.strip():
        raise HTTPException(status_code=400, detail="URL is required")

    url = request.url.strip()

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'format': 'best[ext=mp4]/best',
        'extract_flat': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info(f"Extracting info for URL: {url}")
            info = ydl.extract_info(url, download=False)

            if not info:
                raise HTTPException(
                    status_code=404,
                    detail="Could not extract video information"
                )

            # Get the direct download URL
            download_url = info.get('url')
            if not download_url:
                # Try to get URL from requested_formats
                if 'requested_formats' in info:
                    for fmt in info['requested_formats']:
                        if fmt.get('url'):
                            download_url = fmt['url']
                            break

                # Fallback to entries if it's a playlist
                if not download_url and 'entries' in info:
                    entries = list(info['entries'])
                    if entries and entries[0]:
                        download_url = entries[0].get('url')

            if not download_url:
                raise HTTPException(
                    status_code=404,
                    detail="Could not extract download URL"
                )

            # Format duration
            duration = None
            if info.get('duration'):
                seconds = int(info['duration'])
                minutes, secs = divmod(seconds, 60)
                hours, mins = divmod(minutes, 60)
                if hours > 0:
                    duration = f"{hours}:{mins:02d}:{secs:02d}"
                else:
                    duration = f"{mins}:{secs:02d}"

            return DownloadResponse(
                title=info.get('title', 'Untitled Video'),
                thumbnail=info.get('thumbnail'),
                duration=duration,
                download_url=download_url,
                format="mp4",
                quality=info.get('format_note', 'best')
            )

    except yt_dlp.utils.DownloadError as e:
        logger.error(f"Download error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Could not process video URL: {str(e)}"
        )
    except yt_dlp.utils.ExtractorError as e:
        logger.error(f"Extractor error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Could not extract video: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
