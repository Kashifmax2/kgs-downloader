from flask import Flask, request, jsonify
from flask_cors import CORS
import requests  # <-- Humne yt-dlp ki jagah requests use kiya hai
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/", methods=["GET"])
def root():
    return jsonify({"message": "Video Downloader API is running", "status": "ok"})

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"})

@app.route("/api/download", methods=["POST"])
def extract_video():
    data = request.get_json() or {}
    url = data.get('url')

    if not url:
        return jsonify({"detail": "URL is required"}), 400

    # Cobalt API ka istemal (Sabse stable aur fast)
    api_url = "https://api.cobalt.tools/api/json"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "url": url,
        "isAudioOnly": False,
        "disableMetadata": True
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        result = response.json()

        if response.status_code != 200 or result.get("status") == "error":
            return jsonify({"detail": result.get("text", "Error occurred")}), 400

        # API se milne wala data return kar rahe hain
        return jsonify({
            "title": result.get("picker", [{}])[0].get("name", "Video"),
            "download_url": result.get("url"),
            "format": "mp4"
        })

    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        return jsonify({"detail": f"API Error: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)