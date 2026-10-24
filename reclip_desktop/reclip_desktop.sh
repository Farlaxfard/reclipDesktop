#!/bin/bash
set -e
cd "$(dirname "$0")"

# Check for python3
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed."
    exit 1
fi

# Set up virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv and install dependencies
source venv/bin/activate
echo "Installing/updating dependencies..."
pip install -q -r requirements.txt

echo ""
echo "Launching ReClip 8K..."
echo ""
python3 main.py
