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
    "geo_bypass": True,
    "http_headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
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


def _build_format_options(info):
    formats = info.get("formats") or []
    best = {}
    ext_priority = {"mp4": 0, "m4a": 1, "webm": 2, "flac": 3, "mp3": 4, "unknown": 10}

    for fmt in formats:
        if not fmt or not fmt.get("url"):
            continue

        acodec = fmt.get("acodec")
        vcodec = fmt.get("vcodec")
        if acodec == "none" and vcodec == "none":
            continue

        if vcodec != "none" and acodec != "none":
            media_type = "combined"
        elif vcodec != "none":
            media_type = "video"
        else:
            media_type = "audio"

        height = fmt.get("height")
        if height:
            quality = f"{height}p"
        else:
            quality = fmt.get("format_note") or fmt.get("format_id") or "audio"

        ext = fmt.get("ext") or "unknown"
        fps = fmt.get("fps")

        if media_type == "audio":
            label = f"audio"
            if fmt.get("abr"):
                label += f" {int(fmt.get('abr'))}kbps"
            label += f" · {ext}"
        elif media_type == "video":
            label = f"{quality} video"
            if fps:
                label += f" {fps}fps"
            label += f" · {ext}"
        else:
            label = f"{quality}"
            if fps:
                label += f" {fps}fps"
            label += f" · {ext}"

        format_id = fmt.get("format_id") or f"{quality}-{media_type}-{ext}"
        key = (quality, media_type)

        score = (
            0 if media_type == "combined" else 1 if media_type == "video" else 2,
            height or 0,
            fmt.get("tbr") or 0,
            fmt.get("abr") or 0,
            -ext_priority.get(ext, 10),
        )

        candidate = best.get(key)
        if candidate is None or score > candidate["score"]:
            raw_url = fmt.get("url")
            best[key] = {
                "label": label,
                "quality": quality,
                "ext": ext,
                "format_id": format_id,
                "height": height or 0,
                "tbr": fmt.get("tbr") or fmt.get("abr") or 0,
                "url": raw_url,
                "proxy_url": f"/api/proxy?url={quote(raw_url, safe='')}",
                "media_type": media_type,
                "score": score,
            }

    options = [value for value in best.values()]
    options.sort(key=lambda item: (
        0 if item["media_type"] == "combined" else 1 if item["media_type"] == "video" else 2,
        -item["height"],
        -item["tbr"],
    ))
    for option in options:
        option.pop("score", None)
    return options


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

        # Prepare options per-request and pass cookiefile if any cookies are available
        options = dict(YDL_OPTIONS)
        if os.path.exists(COOKIE_PATH) and os.path.getsize(COOKIE_PATH) > 0:
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

            formats = []
            if isinstance(info, dict):
                formats = _build_format_options(info)

            selected_format = None
            selected_id = data.get("format_id")
            if selected_id and formats:
                for fmt in formats:
                    if fmt["format_id"] == selected_id:
                        selected_format = fmt
                        break

            if not selected_format and formats:
                selected_format = formats[0]

            download_url = selected_format["proxy_url"] if selected_format else f"/api/proxy?url={quote(video_url, safe='')}"
            result_quality = selected_format["quality"] if selected_format else "best"

            return jsonify({
                "title": info.get("title"),
                "thumbnail": info.get("thumbnail"),
                "download_url": download_url,
                "direct_url": selected_format["url"] if selected_format else video_url,
                "proxy_url": selected_format["proxy_url"] if selected_format else (f"/api/proxy?url={quote(video_url, safe='')}" if video_url else None),
                "formats": formats,
                "quality": result_quality,
                "selected_format_id": selected_format["format_id"] if selected_format else None,
            })
    except Exception as exc:
        error_text = str(exc)
        if "sign in to confirm" in error_text.lower() or "cookies-from-browser" in error_text.lower() or "pass cookies" in error_text.lower():
            return jsonify({
                "detail": "YouTube requires login cookies for this video. Set COOKIES_CONTENT with browser-exported cookies.txt on the backend."
            }), 500
        return jsonify({"detail": error_text}), 500

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
