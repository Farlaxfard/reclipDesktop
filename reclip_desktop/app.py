import os
import sys
import uuid
import glob
import json
import subprocess
import threading
import shutil
import time
import logging
import yt_dlp
from flask import Flask, request, jsonify, send_file, render_template, send_from_directory

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_base_path():
    """Returns the base path of the application."""
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

_BASE_PATH = get_base_path()
_CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".reclip_config.json")

def load_config():
    defaults = {"download_dir": os.path.expanduser("~/Downloads")}
    try:
        if os.path.exists(_CONFIG_FILE):
            with open(_CONFIG_FILE, 'r') as f:
                return {**defaults, **json.load(f)}
    except: pass
    return defaults

def save_config(config):
    try:
        with open(_CONFIG_FILE, 'w') as f:
            json.dump(config, f)
    except: pass

_CURRENT_CONFIG = load_config()

app = Flask(__name__, 
            template_folder=os.path.join(_BASE_PATH, "templates"),
            static_folder=os.path.join(_BASE_PATH, "static"))

jobs = {}
cancelled_jobs = set()
jobs_lock = threading.Lock() 

def get_download_dir():
    return _CURRENT_CONFIG["download_dir"]

def ensure_ffmpeg_in_path():
    """Ensures ffmpeg is available in the system PATH."""
    paths_to_add = [_BASE_PATH, "/opt/homebrew/bin", "/usr/local/bin"]
    current_path = os.environ.get("PATH", "")
    for p in paths_to_add:
        if p not in current_path and os.path.exists(p):
            current_path = p + os.path.pathsep + current_path
    os.environ["PATH"] = current_path

def get_ffmpeg_path():
    """Locates the ffmpeg executable."""
    bundled_ffmpeg = os.path.join(_BASE_PATH, "ffmpeg")
    if os.path.exists(bundled_ffmpeg):
        return bundled_ffmpeg
    return shutil.which("ffmpeg")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dev_mode")
def dev_mode():
    is_dark = request.args.get("dark") == "true"
    return render_template("dev_mode.html", is_dark=is_dark)

@app.route("/assets/<path:filename>")
def serve_assets(filename):
    return send_from_directory(os.path.join(_BASE_PATH, "assets"), filename)

@app.route("/api/info", methods=["POST"])
def get_info():
    data = request.json
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    # Optimization: removed extract_flat='in_playlist' as it causes missing format info for single videos
    ydl_opts = {
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'check_formats': False,
        'cookiesfrombrowser': ('chrome', 'safari', 'firefox', 'edge'),
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        def get_res_label(h):
            if h >= 4320: return f"{h}p 8K"
            if h >= 2160: return f"{h}p 4K"
            if h >= 1440: return f"{h}p 2K"
            if h >= 1080: return f"{h}p Full HD"
            if h >= 720: return f"{h}p HD"
            return f"{h}p"

        unique_formats = {}
        for f in info.get("formats", []):
            height = f.get("height")
            if height and f.get("vcodec", "none") != "none":
                if "storyboard" in f.get("format_note", "").lower() or "storyboard" in f.get("format_id", "").lower():
                    continue
                if height not in unique_formats:
                    unique_formats[height] = {
                        "id": f["format_id"],
                        "label": get_res_label(height),
                        "height": height,
                    }
        
        formats = sorted(unique_formats.values(), key=lambda x: x["height"], reverse=True)

        return jsonify({
            "title": info.get("title", ""),
            "thumbnail": info.get("thumbnail", ""),
            "duration": info.get("duration"),
            "uploader": info.get("uploader", ""),
            "formats": formats,
        })
    except Exception as e:
        logger.error(f"Error fetching info for {url}: {e}")
        return jsonify({"error": str(e)}), 400

@app.route("/api/download", methods=["POST"])
def start_download():
    data = request.json
    url = data.get("url", "").strip()
    format_choice = data.get("format", "video")
    format_id = data.get("format_id")
    title = data.get("title", "")
    resolution_label = data.get("resolution_label")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    job_id = uuid.uuid4().hex[:10]
    with jobs_lock:
        jobs[job_id] = {"status": "downloading", "url": url, "title": title, "progress": 0, "speed": "0 MB/s"}

    threading.Thread(target=run_download, args=(job_id, url, format_choice, format_id, resolution_label), daemon=True).start()
    return jsonify({"job_id": job_id})

def run_download(job_id, url, format_choice, format_id, resolution_label=None):
    download_dir = get_download_dir()
    ensure_ffmpeg_in_path()
    
    with jobs_lock:
        job = jobs.get(job_id)
    if not job: return

    out_template = os.path.join(download_dir, f"{job_id}.%(ext)s")
    
    def progress_hook(d):
        with jobs_lock:
            if job_id in cancelled_jobs:
                raise Exception("CANCELLED")
        
        if d['status'] == 'downloading':
            p = d.get('_percent_str', '0%').replace('%', '')
            try:
                prog = float(p)
            except:
                prog = 0
            speed = d.get('_speed_str', '0 MB/s')
            with jobs_lock:
                job['progress'] = prog
                job['speed'] = speed

    ydl_opts = {
        'outtmpl': out_template,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'merge_output_format': 'mp4',
        'ffmpeg_location': get_ffmpeg_path(),
        'concurrent_fragment_downloads': 32,
        'http_chunk_size': 10485760,
        'buffer_size': 16384,
        'fragment_retries': 10,
        'socket_timeout': 30,
        'progress_hooks': [progress_hook],
        'cookiesfrombrowser': ('chrome', 'safari', 'firefox', 'edge'),
    }

    if format_choice == "audio":
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    elif format_id:
        ydl_opts['format'] = f"{format_id}+bestaudio/best"
    else:
        ydl_opts['format'] = "bestvideo+bestaudio/best"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        with jobs_lock:
            files = glob.glob(os.path.join(download_dir, f"{job_id}.*"))
            if not files:
                job.update({"status": "error", "error": "No file found after download"})
                return

            target_ext = ".mp3" if format_choice == "audio" else ".mp4"
            target_files = [f for f in files if f.endswith(target_ext)]
            chosen = target_files[0] if target_files else files[0]

            for f in files:
                if f != chosen:
                    try: os.remove(f)
                    except OSError: pass

            ext = os.path.splitext(chosen)[1]
            safe_title = "".join(c for c in job.get("title", "download") if c.isalnum() or c in (" ", "-", "_")).strip()[:100]
            filename = f"{safe_title} - {resolution_label}{ext}" if format_choice == "video" and resolution_label else f"{safe_title}{ext}"
            
            final_path = os.path.join(download_dir, filename)
            counter = 1
            while os.path.exists(final_path):
                base, fext = os.path.splitext(filename)
                final_path = os.path.join(download_dir, f"{base} ({counter}){fext}")
                counter += 1
            
            os.rename(chosen, final_path)
            job.update({"status": "done", "file": final_path, "filename": os.path.basename(final_path)})

    except Exception as e:
        logger.error(f"Download failed for {job_id}: {e}")
        with jobs_lock:
            if str(e) == "CANCELLED":
                job["status"] = "cancelled"
                for f in glob.glob(os.path.join(download_dir, f"{job_id}.*")):
                    try: os.remove(f)
                    except: pass
            else:
                job.update({"status": "error", "error": str(e)})

@app.route("/api/status/<job_id>")
def check_status(job_id):
    with jobs_lock:
        job = jobs.get(job_id)
    if not job: return jsonify({"error": "Job not found"}), 404
    return jsonify(job)

@app.route("/api/cancel/<job_id>", methods=["POST"])
def cancel_job(job_id):
    with jobs_lock:
        if job_id in jobs:
            cancelled_jobs.add(job_id)
            return jsonify({"success": True})
    return jsonify({"error": "Job not found"}), 404

@app.route("/api/reveal/<job_id>", methods=["POST"])
def reveal_file(job_id):
    with jobs_lock:
        job = jobs.get(job_id)
    if not job or job["status"] != "done": return jsonify({"error": "File not ready"}), 404
    
    file_path = job.get("file")
    if not file_path or not os.path.exists(file_path): return jsonify({"error": "File not found"}), 404
    
    try:
        if sys.platform == "darwin": subprocess.run(["open", "-R", file_path])
        elif sys.platform == "win32": subprocess.run(["explorer", "/select,", os.path.normpath(file_path)])
        else: subprocess.run(["xdg-open", os.path.dirname(file_path)])
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/config/set_directory", methods=["POST"])
def set_directory():
    new_dir = request.json.get("directory")
    if not new_dir or not os.path.isdir(new_dir): return jsonify({"error": "Invalid directory"}), 400
    with jobs_lock:
        _CURRENT_CONFIG["download_dir"] = new_dir
        save_config(_CURRENT_CONFIG)
    return jsonify({"success": True, "directory": _CURRENT_CONFIG["download_dir"]})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 8899)))
