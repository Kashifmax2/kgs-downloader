from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import logging
import os  # <-- Dynamic Port ke liye add kiya

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}) # CORS ko poori tarah open kar diya

@app.route("/", methods=["GET"])
def root():
    return jsonify({"message": "Video Downloader API is running", "status": "ok"})

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"})

@app.route("/api/download", methods=["GET", "POST", "OPTIONS"])
def extract_video():
    # CORS Options pre-flight request handle karne ke liye
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    # GET aur POST dono tareeqon se data read karne ka mechanism
    if request.method == "POST":
        data = request.get_json() or {}
        url = data.get('url', '')
    else:
        url = request.args.get('url', '')

    if not url:
        return jsonify({"detail": "URL is required"}), 400

    url = url.strip()

    # yt-dlp ke options ko update kiya taake TikTok/YouTube blocks bypass ho sakein
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'format': 'best[ext=mp4]/best',
        'extract_flat': False,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info(f"Extracting info for URL: {url}")
            info = ydl.extract_info(url, download=False)

            if not info:
                return jsonify({"detail": "Could not extract video information"}), 404

            # Direct download URL extraction logic
            download_url = info.get('url')
            if not download_url:
                if 'requested_formats' in info:
                    for fmt in info['requested_formats']:
                        if fmt.get('url'):
                            download_url = fmt['url']
                            break
                if not download_url and 'entries' in info:
                    entries = list(info['entries'])
                    if entries and entries[0]:
                        download_url = entries[0].get('url')

            if not download_url:
                return jsonify({"detail": "Could not extract download URL"}), 404

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

            return jsonify({
                "title": info.get('title', 'Untitled Video'),
                "thumbnail": info.get('thumbnail'),
                "duration": duration,
                "download_url": download_url,
                "format": "mp4",
                "quality": info.get('format_note', 'best')
            })

    except Exception as e:
        logger.error(f"Error extracting video: {str(e)}")
        return jsonify({"detail": f"Scraper Error: {str(e)}"}), 500

if __name__ == "__main__":
    # Cloud (Railway) par dynamic port uthane ke liye change kiya
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)