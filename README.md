# ReClip 4K

This is the desktop version of ReClip, wrapped in a native window using `pywebview`.

## Setup

1. **Install Prerequisites:**
   Ensure you have `yt-dlp` and `ffmpeg` installed on your system.

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the App:**
   ```bash
   python main.py
   ```

## Optimization & Fixes
- **Thread Safety:** Uses `threading.Lock` to manage job states safely.
- **Media Downloads:** Downloads are stored in a `media downloads/` directory (or `~/Downloads/Media Downloads` on macOS).
- **Persistent Storage:** Downloads are NOT cleared on startup, allowing you to build your collection.
- **Improved Sanitization:** File names are more robustly sanitized for cross-platform compatibility.
- **Extended Timeout:** Download timeout increased to 10 minutes to support larger files.
- **Integrated UI:** Runs the Flask backend and a WebView window in a single process.
