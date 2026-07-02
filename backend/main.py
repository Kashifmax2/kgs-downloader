from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # CORS middleware automatic handle ho jayega

@app.route("/", methods=["GET"])
def root():
    return jsonify({"message": "Video Downloader API is running", "status": "ok"})

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"})

@app.route("/api/download", methods=["POST"])
def extract_video():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"detail": "URL is required"}), 400

    url = data['url'].strip()
    if not url:
        return jsonify({"detail": "URL is required"}), 400

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
                return jsonify({"detail": "Could not extract video information"}), 404

            # Direct download URL
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
        logger.error(f"Error: {str(e)}")
        return jsonify({"detail": f"An error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)