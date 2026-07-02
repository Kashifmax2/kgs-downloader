import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# yt-dlp Options for "Human-like" behavior
YDL_OPTIONS = {
    'format': 'best',
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
}

@app.route("/", methods=["GET"])
def root():
    return jsonify({"message": "Downloader API Active", "status": "ok"})

@app.route("/api/download", methods=["POST"])
def extract_video():
    data = request.get_json() or {}
    url = data.get('url')

    if not url:
        return jsonify({"detail": "URL is required"}), 400

    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            logger.info(f"Extracting info for: {url}")
            info = ydl.extract_info(url, download=False)
            
            # Fetch direct URL
            video_url = info.get('url')
            if not video_url and 'formats' in info:
                # Find best format if direct url not found
                for f in info['formats']:
                    if f.get('url'):
                        video_url = f['url']
                        break

            return jsonify({
                "title": info.get('title', 'Video'),
                "thumbnail": info.get('thumbnail'),
                "download_url": video_url,
                "duration": info.get('duration_string'),
                "error": None
            })

    except Exception as e:
        logger.error(f"Scraper Error: {str(e)}")
        return jsonify({"detail": f"Scraper Error: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)