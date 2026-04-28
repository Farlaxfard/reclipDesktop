import uuid
import glob
import json
import subprocess
import threading
import yt_dlp
import sys
import os
from flask import Flask, request, jsonify, send_file, render_template

app = Flask(__name__)
DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

jobs = {}
jobs_lock = threading.Lock()

def run_download(job_id, url, format_choice, format_id, resolution_label=None):
    with jobs_lock:
        job = jobs.get(job_id)
    if not job:
        return

    out_template = os.path.join(DOWNLOAD_DIR, f"{job_id}.%(ext)s")

    cmd = [sys.executable, "-m", "yt_dlp", "--no-playlist", "-o", out_template]

    if format_choice == "audio":
        cmd += ["-x", "--audio-format", "mp3"]
    elif format_id:
        cmd += ["-f", f"{format_id}+bestaudio/best", "--merge-output-format", "mp4"]
    else:
        cmd += ["-f", "bestvideo+bestaudio/best", "--merge-output-format", "mp4"]

    cmd.append(url)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            with jobs_lock:
                job["status"] = "error"
                job["error"] = result.stderr.strip().split("\n")[-1]
            return

        files = glob.glob(os.path.join(DOWNLOAD_DIR, f"{job_id}.*"))
        if not files:
            with jobs_lock:
                job["status"] = "error"
                job["error"] = "Download completed but no file was found"
            return

        if format_choice == "audio":
            target = [f for f in files if f.endswith(".mp3")]
            chosen = target[0] if target else files[0]
        else:
            target = [f for f in files if f.endswith(".mp4")]
            chosen = target[0] if target else files[0]

        for f in files:
            if f != chosen:
                try:
                    os.remove(f)
                except OSError:
                    pass

        with jobs_lock:
            job["status"] = "done"
            job["file"] = chosen
            ext = os.path.splitext(chosen)[1]
            title = job.get("title", "").strip()
            
            if title:
                # Sanitize title
                safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "-", "_")).strip()[:100]
                if format_choice == "video" and resolution_label:
                    job["filename"] = f"{safe_title} - {resolution_label}{ext}"
                else:
                    job["filename"] = f"{safe_title}{ext}"
            else:
                job["filename"] = os.path.basename(chosen)
            
            # Final rename to the friendly filename
            final_path = os.path.join(DOWNLOAD_DIR, job["filename"])
            # Handle potential name collisions
            counter = 1
            while os.path.exists(final_path):
                base, fext = os.path.splitext(job["filename"])
                if " (" in base and base.endswith(")"):
                    base = base.rsplit(" (", 1)[0]
                final_path = os.path.join(DOWNLOAD_DIR, f"{base} ({counter}){fext}")
                counter += 1
            
            os.rename(chosen, final_path)
            job["file"] = final_path
            job["filename"] = os.path.basename(final_path)

    except subprocess.TimeoutExpired:
        with jobs_lock:
            job["status"] = "error"
            job["error"] = "Download timed out (5 min limit)"
    except Exception as e:
        with jobs_lock:
            job["status"] = "error"
            job["error"] = str(e)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/info", methods=["POST"])
def get_info():
    data = request.json
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    cmd = [sys.executable, "-m", "yt_dlp", "--no-playlist", "-j", url]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            return jsonify({"error": result.stderr.strip().split("\n")[-1]}), 400

        info = json.loads(result.stdout)

        def get_res_label(h):
            if h >= 4320: return f"{h}p 8K"
            if h >= 2160: return f"{h}p 4K"
            if h >= 1440: return f"{h}p 2K"
            if h >= 1080: return f"{h}p Full HD"
            if h >= 720: return f"{h}p HD"
            return f"{h}p"

        # Instead of 'best_by_height', let's collect ALL video formats that are not storyboard/non-video
        formats = []
        for f in info.get("formats", []):
            height = f.get("height")
            if height and f.get("vcodec", "none") != "none":
                # Skip storyboard/non-video formats
                if "storyboard" in f.get("format_note", "").lower() or "storyboard" in f.get("format_id", "").lower():
                    continue
                
                # Check for standard wide/tall aspect ratios to avoid weird formats like 3840x1920
                width = f.get("width")
                if width and height:
                    ratio = width / height
                    # Standard video ratios are usually between 1.33 and 2.4.
                    # 3840/1920 = 2.0, which is technically standard-ish (ultrawide). 
                    # If you got that, it was the format's actual height/width.
                
                formats.append({
                    "id": f["format_id"],
                    "label": get_res_label(height),
                    "height": height,
                })
        
        # Sort by height descending
        formats.sort(key=lambda x: x["height"], reverse=True)

        return jsonify({
            "title": info.get("title", ""),
            "thumbnail": info.get("thumbnail", ""),
            "duration": info.get("duration"),
            "uploader": info.get("uploader", ""),
            "formats": formats,
        })
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Timed out fetching video info"}), 400
    except Exception as e:
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
    jobs[job_id] = {"status": "downloading", "url": url, "title": title}

    thread = threading.Thread(target=run_download, args=(job_id, url, format_choice, format_id, resolution_label))
    thread.daemon = True
    thread.start()

    return jsonify({"job_id": job_id})


@app.route("/api/status/<job_id>")
def check_status(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify({
        "status": job["status"],
        "error": job.get("error"),
        "filename": job.get("filename"),
    })


@app.route("/api/file/<job_id>")
def download_file(job_id):
    job = jobs.get(job_id)
    if not job or job["status"] != "done":
        return jsonify({"error": "File not ready"}), 404
    return send_file(job["file"], as_attachment=True, download_name=job["filename"])


if __name__ == "__main__":
    app.run(port=5000)
