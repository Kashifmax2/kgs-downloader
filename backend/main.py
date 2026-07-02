import os
from urllib.parse import quote
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
import yt_dlp

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

COOKIE_PATH = os.path.join(os.getcwd(), "cookies.txt")

cookies_content = os.environ.get("COOKIES_CONTENT")
if cookies_content:
    try:
        with open(COOKIE_PATH, "w", encoding="utf-8") as f:
            f.write(cookies_content)
        print(f"SUCCESS: Cookies file created at {COOKIE_PATH}")
    except Exception as exc:
        print(f"ERROR: Failed to write cookies: {exc}")
else:
    if not os.path.exists(COOKIE_PATH):
        try:
            # Write a minimal Netscape-format header so yt-dlp won't reject the file when empty
            with open(COOKIE_PATH, "w", encoding="utf-8") as f:
                f.write("# Netscape HTTP Cookie File\n")
            print(f"INFO: Created cookies file with Netscape header at {COOKIE_PATH}")
        except Exception as exc:
            print(f"ERROR: Cannot create fallback cookies file: {exc}")
    else:
        # If the cookies file exists but is empty, add the minimal header to avoid yt-dlp format errors
        try:
            if os.path.getsize(COOKIE_PATH) == 0:
                with open(COOKIE_PATH, "w", encoding="utf-8") as f:
                    f.write("# Netscape HTTP Cookie File\n")
                print(f"INFO: Wrote Netscape header to existing empty cookies file at {COOKIE_PATH}")
            else:
                print("INFO: Using existing cookies file.")
        except Exception as exc:
            print(f"ERROR: Cannot inspect/fix existing cookies file: {exc}")

YDL_OPTIONS = {
    "format": "best",
    "quiet": False,
    "nocheckcertificate": True,
    "http_headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Referer": "https://www.tiktok.com/",
    },
}


def _looks_like_netscape_cookie_file(path: str) -> bool:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            head = f.read(2048)
            if not head:
                return False
            # Netscape format usually starts with this header
            if "# Netscape HTTP Cookie File" in head:
                return True
            # Or contains tab-separated lines with 7 fields (domain, flag, path, secure, expiration, name, value)
            for line in head.splitlines():
                if not line or line.startswith("#"):
                    continue
                parts = line.split("\t")
                if len(parts) >= 7:
                    return True
            return False
    except Exception:
        return False

@app.route("/", methods=["GET"])
def root():
    return jsonify({"message": "Downloader Active", "status": "ok"})

@app.route("/api/download", methods=["POST"])
def extract_video():
    data = request.get_json(silent=True) or {}
    url = data.get("url")
    if not url:
        return jsonify({"detail": "URL required"}), 400

    try:
        if not os.path.exists(COOKIE_PATH):
            return jsonify({"detail": "Cookies file missing on server"}), 500

        # Prepare options per-request so we only pass a cookiefile when valid
        options = dict(YDL_OPTIONS)
        if os.path.exists(COOKIE_PATH) and _looks_like_netscape_cookie_file(COOKIE_PATH):
            options["cookiefile"] = COOKIE_PATH

        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)

            # If the extractor returned a playlist or multiple entries, pick the first entry
            if isinstance(info, dict) and info.get("entries"):
                entries = [e for e in info.get("entries") if e]
                if not entries:
                    return jsonify({"detail": "No entries found in extractor result"}), 500
                info = entries[0]

            # Try top-level url first, then fall back to formats list
            video_url = None
            if isinstance(info, dict):
                video_url = info.get("url")
                if not video_url:
                    formats = info.get("formats") or []
                    # Choose best format by height then by tbr
                    best = None
                    for f in formats:
                        if not f or not f.get("url"):
                            continue
                        # prefer formats with video (vcodec not 'none')
                        if f.get("vcodec") == "none" and f.get("acodec") != "none":
                            # audio-only, skip
                            continue
                        if not best:
                            best = f
                            continue
                        # compare by height then tbr
                        h_best = best.get("height") or 0
                        h_f = f.get("height") or 0
                        if h_f != h_best:
                            if h_f > h_best:
                                best = f
                                continue
                        # fallback to tbr (total bitrate)
                        t_best = best.get("tbr") or 0
                        t_f = f.get("tbr") or 0
                        if t_f > t_best:
                            best = f
                    if best:
                        video_url = best.get("url")

            if not video_url:
                return jsonify({"detail": "Unable to extract video URL"}), 500

            return jsonify({
                "title": info.get("title"),
                "thumbnail": info.get("thumbnail"),
                "download_url": f"/api/proxy?url={quote(video_url, safe='')}"
            })
    except Exception as exc:
        return jsonify({"detail": str(exc)}), 500

@app.route("/api/proxy")
def proxy_video():
    url = request.args.get("url")
    if not url:
        return jsonify({"detail": "Missing URL"}), 400

    try:
        remote = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
            },
            allow_redirects=True,
            stream=True,
            timeout=60,
        )
        if remote.status_code != 200:
            return jsonify({"detail": f"Remote request failed with status {remote.status_code}"}), remote.status_code

        return Response(
            remote.iter_content(chunk_size=1024 * 1024),
            content_type=remote.headers.get("Content-Type", "application/octet-stream"),
            headers={"Content-Disposition": "attachment; filename=\"video.mp4\""},
        )
    except requests.RequestException as exc:
        return jsonify({"detail": str(exc)}), 502
    except Exception as exc:
        return jsonify({"detail": str(exc)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
