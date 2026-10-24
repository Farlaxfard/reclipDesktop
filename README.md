# ReClip 8K

A privacy-focused, standalone desktop media retrieval application with a sleek native UI powered by `pywebview`, `Flask`, and `yt-dlp`.

## Project Structure

```text
reclipDesktop/
├── reclip_desktop/
│   ├── assets/             # Audio feedback sound effects
│   │   └── sounds/         # MP3 audio cues (button, finish, paste, start)
│   ├── static/             # Fonts, icons, and UI assets
│   │   ├── fonts/          # Bundled web fonts
│   │   ├── cog.png         # Settings gear icon
│   │   ├── favicon.svg     # Favicon
│   │   ├── icon.icns       # macOS application icon bundle
│   │   ├── icon.png        # Application icon (PNG)
│   │   └── icon.svg        # Application icon (SVG)
│   ├── templates/          # Frontend templates
│   │   ├── index.html      # Main user interface
│   │   └── dev_mode.html   # Developer settings interface
│   ├── app.py              # Flask backend server & yt-dlp downloader engine
│   ├── build_app.py        # PyInstaller build automation script
│   ├── main.py             # Desktop application entry point (pywebview + Flask)
│   ├── reclip_desktop.sh   # Launcher script with automatic venv setup
│   └── requirements.txt    # Desktop application Python dependencies
├── GEMINI.md               # Project architecture, guidelines, mandates, & changelog
├── LICENSE                 # License file
├── README.md               # Project documentation
└── requirements.txt        # Root-level requirements specification
```

## Prerequisites

- **Python 3.10+**
- **FFmpeg**: Required for media extraction and merging (`brew install ffmpeg` on macOS)
- **yt-dlp**: Required for media retrieval (`brew install yt-dlp` or installed via pip)

## Setup & Running

### Option 1: Quick Launch Script (macOS / Linux)
```bash
./reclip_desktop/reclip_desktop.sh
```

### Option 2: Manual Setup
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Launch the application:**
   ```bash
   python3 reclip_desktop/main.py
   ```

## Building the Standalone macOS App Bundle

To compile and package ReClip into a standalone `.app` bundle:

```bash
python3 reclip_desktop/build_app.py
```

The resulting `ReClip8K.app` bundle will be created in `reclip_desktop/dist/`.

## Key Features

- **Native Desktop Integration:** Single-process desktop window using `pywebview` with unified styling.
- **Audio Feedback Engine:** Web Audio API sound cues for button interactions, paste events, and completions.
- **Persistent Downloads:** Media saved to customizable folders (defaulting to `~/Downloads`) with duplicate filename handling.
- **Multi-Platform Support:** High-resolution video and audio downloads powered by `yt-dlp`.
- **Customizable Experience:** Built-in settings modal with Dark Mode toggle and default format options.
