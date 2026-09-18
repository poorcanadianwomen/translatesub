#!/bin/bash
set -e

echo "=== TranslateSub Builder ==="
echo ""

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv
fi

source .venv/bin/activate

echo "Installing dependencies..."
uv pip install -r requirements.txt
uv pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

echo "Building with PyInstaller..."
uv pip install pyinstaller
pyinstaller translatesub.spec --clean --noconfirm

echo ""
echo "Done! Binary at: dist/translatesub/translatesub"
echo "Run with: ./dist/translatesub/translatesub"
