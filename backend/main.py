import os
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

# 1. Cookie Path define karo
COOKIE_PATH = os.path.join(os.getcwd(), "cookies.txt")

# 2. File creation logic (Logs ke saath)
cookies_content = os.environ.get("COOKIES_CONTENT")
if cookies_content:
    try:
        with open(COOKIE_PATH, "w", encoding="utf-8") as f:
            f.write(cookies_content)
        print(f"SUCCESS: Cookies file created at {COOKIE_PATH}")
    except Exception as e:
        print(f"ERROR: Failed to write cookies: {e}")
else:
    print("WARNING: COOKIES_CONTENT variable not found in Railway!")

YDL_OPTIONS = {
    'format': 'best',
    'quiet': False, # Debugging ke liye False kiya hai, logs mein dikhega
    'nocheckcertificate': True,
    'cookiefile': COOKIE_PATH, # Ab absolute path use ho raha hai
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'Referer': 'https://www.tiktok.com/',
    }
}

@app.route("/", methods=["GET"])
def root():
    return jsonify({"message": "Downloader Active", "status": "ok"})

@app.route("/api/download", methods=["POST"])
def extract_video():
    data = request.get_json() or {}
    url = data.get('url')
    if not url: return jsonify({"detail": "URL required"}), 400

    try:
        # Check if file exists just before using
        if not os.path.exists(COOKIE_PATH):
            return jsonify({"detail": "Cookies file missing on server"}), 500
            
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url')
            return jsonify({
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail'),
                "download_url": f"/api/proxy?url={video_url}" 
            })
    except Exception as e:
        return jsonify({"detail": str(e)}), 500

@app.route("/api/proxy")
def proxy_video():
    url = request.args.get('url')
    if not url: return "Missing URL", 400
    # ... (rest of the proxy code remains same) ...
    import requests
    headers = {'Referer': 'https://www.tiktok.com/', 'User-Agent': 'Mozilla/5.0'}
    req = requests.get(url, headers=headers, stream=True)
    return Response(
        req.iter_content(chunk_size=1024*1024),
        content_type=req.headers.get('Content-Type'),
        headers={'Content-Disposition': 'attachment; filename="video.mp4"'}
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)