# ReClip Project Overview

**ReClip** is a privacy-focused, self-hosted media retrieval tool. It provides a clean, distraction-free web interface for downloading video and audio from over 1,000 supported platforms (including YouTube, TikTok, Instagram, and Twitter/X) without tracking, advertisements, or external dependencies.

Its core philosophy is "simple utility": a single-file backend that bridges the power of `yt-dlp` to a user-friendly browser experience.

## Core Features

- **Multi-Platform Support:** Works with any site supported by `yt-dlp`.
- **Format Flexibility:** Allows downloading as high-quality MP4 video or extracted MP3 audio.
- **Resolution Control:** Provides a quality picker to select specific video resolutions (e.g., 1080p, 720p).
- **Batch Processing:** Supports pasting multiple URLs simultaneously for bulk information fetching.
- **Zero-Footprint Frontend:** A responsive UI built with vanilla HTML/CSS/JS, requiring no build steps or heavy frameworks.

## Core Architecture

- **Backend (Python/Flask):** 
    - `app.py` serves as the main entry point.
    - Uses `subprocess` to call `yt-dlp` for information retrieval and downloading.
    - Implements a simple job-based system with background threads for downloads.
    - Downloads are stored in a local `downloads/` directory.
- **Frontend (Vanilla HTML/CSS/JS):**
    - `templates/index.html` contains the entire frontend logic.
    - Communicates with the backend via a RESTful API.
- **Dependencies:**
    - `Flask`: Web framework.
    - `yt-dlp`: Core download engine.
    - `ffmpeg`: Required for media merging and extraction (external dependency).

## API Endpoints

- `GET /`: Serves the web interface.
- `POST /api/info`: Fetches metadata (title, thumbnail, formats) for a given URL.
- `POST /api/download`: Initiates a download job (MP4 or MP3).
- `GET /api/status/<job_id>`: Polls for the status of a specific job.
- `GET /api/file/<job_id>`: Serves the downloaded file once ready.

## Deployment & Setup

- `reclip.sh`: A shell script that checks for prerequisites (`python3`, `yt-dlp`, `ffmpeg`), sets up a Python virtual environment, installs dependencies, and runs the application.
- `Dockerfile`: Provides a containerized environment based on `python:3.12-slim`, including `ffmpeg` installation.

## Project Mandates

- **Documentation:** For every change made to this codebase, its specific intention and the change itself must be documented in the "Change Log" section of `GEMINI.md`. This ensures a clear, auditable history of the project's evolution and the reasoning behind each modification.
- **Version Tracking:** For every code change or feature implementation, the application version in the `Info` section of the Settings panel MUST be incremented by 0.1, and the "Last Updated" timestamp must be updated to the current date and time.
- **Auto-Build:** Every time code changes or feature implementations are finished and validated, the `reclip_desktop/build_app.py` script MUST be executed to rebuild the standalone macOS application bundle.

## Change Log

### 2026-04-25: UI Fixes & Versioning
- **Change:** Fixed WiFi icon cutoff by using a larger container and verified Material Symbol rendering.
- **Change:** Rewrote the "No WiFi" overlay transition logic to ensure smooth, slow (1.2s) blur effects.
- **Change:** Fixed visibility logic: "Rainbow Mode" and "Mysterious Button" now correctly show/hide in the Settings panel based on Developer Mode state.
- **Change:** Updated version tracking: incremented app version to `v1.5` and timestamp to `2026-04-25 15:30`.
- **Intention:** Addressing UI rendering issues and ensuring expected feature visibility and system state tracking.

### 2026-04-18: Desktop Application Conversion
- **Change:** Created `reclip_desktop/` directory and converted the project into a standalone Python desktop application.
- **Intention:** To provide a more integrated "native-like" experience using `pywebview` while reusing the existing backend logic and frontend UI.
- **Change:** Implemented `main.py` to orchestrate both the Flask server and the WebView window.
- **Intention:** To allow the application to run as a single process with a dedicated window instead of requiring a browser.
- **Change:** Optimized `app.py` in the desktop version with thread safety (Locking), robust file sanitization, extended timeouts, and automatic download cleanup.
- **Intention:** To ensure the desktop app is stable, secure, and performs well for longer download tasks, while preventing resource bloat.
- **Change:** Modified `app.py` and `main.py` for PyInstaller compatibility.
- **Intention:** To allow the application to be bundled into a single standalone executable file that correctly finds its template, static, and asset files at runtime.
- **Change:** Created `reclip_desktop/build_app.py`.
- **Intention:** To automate the creation of a standalone, single-file "Python App" bundle using `PyInstaller`.
- **Change:** Fixed `[Errno 2] No such file or directory: 'yt-dlp'` by calling `yt-dlp` as a Python module (`sys.executable -m yt_dlp`) and explicitly importing it for bundling.
- **Intention:** To ensure `yt-dlp` is always found and correctly bundled with the application, even if not in the system's `PATH`.

### 2026-04-23: Rebranding to ReClip 4K and persistence improvements
- **Change:** Renamed `ReClip Desktop` to `ReClip 4K` across all files, build scripts, and the UI.
- **Intention:** Rebranding for a more professional/powerful identity.
- **Change:** Renamed download folder to `media downloads` (or `Media Downloads` on macOS) and disabled automatic startup cleanup.
- **Intention:** To fulfill user request for persistence and better folder naming.
- **Change:** Modified `index.html` to disable automatic download triggering and added `target="_blank"` to the "Save" link.
- **Intention:** To fix the issue where the MP3 preview would take over the main window without an exit path.

### 2026-04-23: UI Cleanup and Performance Optimization
- **Change:** Removed footer platform links and the subtitle "Free media downloader" from `index.html`.
- **Intention:** To reduce visual noise and "grand distractions" as requested.
- **Change:** Optimized `yt-dlp` download speed by enabling `concurrent_fragment_downloads: 10`.
- **Intention:** To improve download performance through multi-threading.
- **Change:** Modified `main.py` to use `hidden_titlebar=True` and `easy_drag=True`.
- **Intention:** To create a transparent/unified title bar that matches the application's background on macOS.
- **Change:** Optimized download speed further by increasing `concurrent_fragment_downloads` to 32 and enabling `http_chunk_size` of 10MB, along with buffer size and retry adjustments.
- **Intention:** To achieve the "fastest" download speeds using maximum native `yt-dlp` parallelization.

### 2026-04-23: Bug Fix and UI Stability
- **Change:** Removed the unsupported `hidden_titlebar` argument from `webview.create_window` in `reclip_desktop/main.py`.
- **Intention:** To fix the `TypeError` crash on startup caused by using a non-existent parameter in `pywebview` 6.2.1.
- **Change:** Rebuilt the `ReClip 4K` application bundle.
- **Intention:** To ensure the distributed binary includes the fix and starts correctly.

### 2026-04-24: Final Polish & Settings Interface

### 2026-04-25: UI Polish, WiFi Transitions, & Versioning
- **Change:** Implemented a smooth, slow (1.2s) transition for the "No WiFi" overlay using backdrop-blur and opacity.
- **Change:** Updated the "No WiFi" icon to a Google Material Symbol while retaining the orange theme and glow; on connection restoration, it turns green before fading out.
- **Change:** Fixed visibility logic: "Rainbow Mode" and "Mysterious Button" are now properly scoped to Developer Mode and only appear when it is active.
- **Change:** Standardized version tracking: incremented app version to `v1.4` and updated the timestamp to `2026-04-25 15:00`.
- **Intention:** Delivering a polished, high-fidelity user experience with intuitive feedback.

### 2026-04-25: Advanced Audio Feedback & "Magic Chime"
- **Change:** Implemented a "magic chime" audio effect for the "Fetch" button using the Web Audio API.
- **Change:** Layered the `button` SFX with a modified `start` SFX (higher pitch, low-pass filter, and reverb with pre-delay).
- **Change:** Added a procedural reverb generator to the Audio Engine for immersive soundscapes.
- **Change:** Increased the "Fetch" chime volume by 50% and reverb intensity by 50%.
- **Intention:** Enhancing the "Fetch" interaction with a satisfying, high-fidelity "magic" feedback that signals the start of the retrieval process.
- **Change:** Integrated a "Settings" page accessible via an SF Symbol gear icon (􀣌) in the top left corner.
- **Change:** Implemented a sleek settings modal with blur effects, detailing storage locations and core engine versions.
- **Change:** Simplified window title and UI brand header to "ReClip" while maintaining "ReClip 8K" in technical metadata.
- **Change:** Optimized visual effects: fixed progress bar shine clipping and added continuous flickering 80px bloom.
- **Intention:** Providing a complete, professional, and accessible interface for production use.

---
### 2026-04-24: Bot Bypass & Production Readiness
- **Change:** Implemented automatic cookie extraction from local browsers (Safari, Chrome, etc.) to bypass YouTube's "Sign in to confirm you're not a bot" detection.
- **Change:** Finalized rebranding to **ReClip 8K** and updated build scripts for 100% standalone macOS operation.
- **Change:** Refined the brand header to simply "ReClip" for a cleaner UI, while maintaining the "ReClip 8K" window title and metadata.
- **Change:** Fixed progress bar "shine" clipping by isolating it to the downloading segment.
- **Change:** Replaced the download button bounce with a sleek, fast fade-out transition.
- **Change:** Fine-tuned the vertical shake to be ultra-subtle and verified 80px flickering bloom effect.
- **Intention:** Delivering a professional, high-fidelity, and visually synchronized user experience that bypasses platform restrictions.

---
### 2026-04-24: Settings Interface & Audio Feedback System
- **Change:** Integrated a Settings modal with a Dark Mode toggle (persisted via `localStorage`) and dropdowns for default video/audio format selection.
- **Change:** Implemented an audio feedback system triggered on button presses, link pasting, download initiation, and completion.
- **Change:** Created `reclip_desktop/assets/sounds/` and configured `reclip_desktop/build_app.py` to bundle these assets into the standalone macOS `.app` bundle.
- **Intention:** Enhancing the user experience with personalized settings and tactile, audible feedback for a more responsive and professional feel.
### 2026-04-24: UI Polish & Info Section
- **Change:** Added an "Info" section to the bottom of the Settings panel.
- **Intention:** To provide users with quick access to application versioning, update timestamps, known bugs, and supported link information.
- **Change:** App version set to `v1.0`.
- **Intention:** Standardizing version tracking.
---
### 2026-04-24: UI Fixes & Polish

- **Change:** Optimized progress bar updates to use direct DOM manipulation, preventing animation resets.
- **Change:** Refined download bar with a smooth `ease-in-out` transition and an intense, multi-layered green bloom/glow effect (radius up to 80px) with a subtle flicker animation.
- **Change:** Implemented top-to-bottom slide-in entry animation for download cards with a spring-like bounce effect (`cubic-bezier(0.175, 0.885, 0.32, 1.275)`).
- **Change:** Added interactive UI animations: fast shake for textarea on paste, spring bounce for "Fetch" button, and horizontal "swipe" transitions for the MP4/MP3 mode toggle.
- **Change:** Decoupled "shine" sweep animation for a continuous, polished visual effect.
- **Change:** Added high-fidelity transitions to UI chips and updated site metadata to ReClip 8K.
- **Intention:** Achieving production-grade visual quality and performance with immersive aesthetics and playful, native-feeling interactions.

---
### 2026-04-24: UI Overhaul & Reliability Improvements
- **Change:** Rebranded "ReClip 4K" to "ReClip 8K" across all scripts and UI.
- **Change:** Added enhanced green progress bar with "shine" sweep, glow effect, and real-time Mbps/Kbps speed display.
- **Change:** Fixed "ffmpeg not installed" error by dynamically injecting common macOS binary paths (`/opt/homebrew/bin`, etc.) into the environment at runtime.
- **Change:** Removed experimental "Morphing Blob" animations to maintain a cleaner, more stable interface.
- **Change:** Improved thread safety in download progress tracking and re-added filename collision handling.
- **Intention:** Modernizing the identity, providing reliable high-fidelity visual feedback, and ensuring robust file handling.

---
### 2026-04-24: Resolution deduplication, Thread safety
- **Change:** Modified `get_info` in `reclip_desktop/app.py` to deduplicate video formats by height.
- **Intention:** To remove duplicate resolution buttons (e.g., multiple 2160p options) for the same video.
- **Change:** Added thread safety to `jobs` dictionary in `reclip_desktop/app.py`.
- **Intention:** To prevent race conditions when handling multiple concurrent download requests.

---
### 2026-04-23: File Naming and UX Improvements
- **Change:** Updated file naming convention to `Video name - resolution.mp4` for videos and `Video name.mp3` for audio.
- **Intention:** To provide more descriptive filenames as requested.
- **Change:** Implemented a "Reveal in Folder" feature and disabled the automatic in-app media preview.
- **Intention:** To fix the "unescapable preview" issue and solve 4K playback lag by encouraging the use of native system players.
- **Change:** Added automatic folder opening and file selection upon download completion.
- **Intention:** To streamline the user workflow and provide immediate access to downloaded files.

### 2026-04-26: Code Cleanup & Optimization
- **Change:** Removed redundant root-level files (app.py, Dockerfile, etc.) and moved to trash.
- **Change:** Optimized reclip_desktop/app.py with cookie extraction, better logging, and streamlined logic.
- **Change:** Polished reclip_desktop/templates/index.html with cleaner CSS and simplified JavaScript.
- **Change:** Updated application version to v1.6 and timestamp to 2026-04-26 12:00.
- **Intention:** To maintain a clean, efficient codebase and improve the overall stability and performance of the desktop application.

### 2026-04-26: Restoration & Performance Optimization
- **Change:** Restored original rich UI features, including "Magic Chime" audio feedback, "Developer Mode" triggers, and detailed card animations.
- **Change:** Implemented persistent settings for Dark Mode, SFX volume, and default download format using localStorage.
- **Change:** Added backend persistence for the download directory using a config file (~/.reclip_config.json).
- **Change:** Optimized metadata retrieval speeds by refining yt-dlp extraction options (check_formats=False).
- **Change:** Improved startup speed by optimizing pywebview window initialization and Flask background threading.
- **Change:** Incremented application version to v1.7 and updated timestamp to 2026-04-26 13:00.
- **Intention:** To honor the request for feature preservation while delivering significant speed and persistence improvements.

### 2026-04-28: UX Reversion & Targeted High-Fidelity Additions
- **Change:** Reverted most UI "refinements" to match the original application state (v1.8), including vertical shake intensity and settings cog pivot.
- **Change:** Reverted backend cookie fallback logic to maintain original behavior.
- **Change:** Implemented a new horizontal layout for the "No WiFi" warning screen with enhanced transitions (blur, scale, and fade).
- **Change:** Upgraded the "Magic Chime" with layered audio, increased reverb (1.2), higher pitch (1.6), and a 120ms pre-delay.
- **Change:** Added a sophisticated transition for exiting the settings menu, including main wrapper un-blurring and modal scaling.
- **Change:** Ensured consistent button, start, and finish SFX across the application.
- **Change:** Incremented application version to `v2.1` and updated timestamp to `2026-04-28 10:30`.
- **Intention:** Honoring the user's preference for the original aesthetic while delivering requested high-fidelity interactions and functional improvements.
