import PyInstaller.__main__
import os
import sys
import shutil
import subprocess

# Define paths for assets, templates, and static files
base_dir = os.path.dirname(os.path.abspath(__file__))

# Find ffmpeg binary
ffmpeg_path = shutil.which("ffmpeg")
if not ffmpeg_path and sys.platform == "darwin":
    # Common homebrew path if not in env
    test_path = "/opt/homebrew/bin/ffmpeg"
    if os.path.exists(test_path):
        ffmpeg_path = test_path

if not ffmpeg_path:
    print("Error: ffmpeg not found. Please install ffmpeg or put it in your PATH.")
    sys.exit(1)

print(f"Bundling ffmpeg from: {ffmpeg_path}")

# Clean up previous build artifacts
build_folders = ['build', 'dist']
for folder in build_folders:
    path = os.path.join(base_dir, folder)
    if os.path.exists(path):
        print(f"Cleaning up {folder}...")
        shutil.rmtree(path)

add_data = [
    (os.path.join(base_dir, "templates"), "templates"),
    (os.path.join(base_dir, "static"), "static"),
    (os.path.join(base_dir, "assets"), "assets"),
    (os.path.join(base_dir, "assets/sounds"), "assets/sounds"),
]

binaries = [
    (ffmpeg_path, "."),
]

# Common PyInstaller arguments
args = [
    os.path.join(base_dir, "main.py"),
    "--name=ReClip8K",
    "--windowed", # No console window
    "--noconfirm", # Overwrite output directory without asking
    "--clean",     # Clean PyInstaller cache before building
]

# Add data files
for src, dest in add_data:
    args.append(f"--add-data={src}{os.path.pathsep}{dest}")

# Add binaries (ffmpeg)
for src, dest in binaries:
    args.append(f"--add-binary={src}{os.path.pathsep}{dest}")

# Icon handling
if sys.platform == "darwin":
    # macOS requires .icns for the bundle icon
    icon_path = os.path.join(base_dir, "static", "icon.icns")
    if not os.path.exists(icon_path):
        # Fallback to .png if .icns isn't there (PyInstaller + Pillow can sometimes convert)
        icon_path = os.path.join(base_dir, "static", "icon.png")
else:
    icon_path = os.path.join(base_dir, "static", "icon.png")

if os.path.exists(icon_path):
    print(f"Using icon: {icon_path}")
    args.append(f"--icon={icon_path}")
else:
    print("Warning: No icon file found.")

# macOS specific options
if sys.platform == "darwin":
    args.append("--osx-bundle-identifier=com.reclip.8k")
    # A .app bundle IS a directory, so --onedir is the correct/preferred mode for macOS bundles
    args.append("--onedir")
else:
    args.append("--onefile")

print(f"Starting build with arguments: {' '.join(args)}")

# Run PyInstaller
PyInstaller.__main__.run(args)

print("\nBuild complete!")
if sys.platform == "darwin":
    dist_path = os.path.join(base_dir, 'dist')
    print(f"Your macOS app is located at: {os.path.join(dist_path, 'ReClip8K.app')}")
    # The actual folder containing the app is `dist`
    subprocess.run(["open", dist_path])
else:
    dist_path = os.path.join(base_dir, 'dist')
    print(f"Your executable is located at: {dist_path}")
    # Simple open for Linux/Windows
    if sys.platform == "win32":
        os.startfile(dist_path)
    else:
        subprocess.run(["xdg-open", dist_path])
