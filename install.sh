#!/bin/bash
set -e

APPDIR="$HOME/translatesub"
DEST="$HOME/.local/share/applications"
ICONDST="$HOME/.local/share/icons"

echo "=== TranslateSub Installer ==="
echo ""

# Make launcher executable
chmod +x "$APPDIR/translatesub-launcher"

# Install .desktop file
mkdir -p "$DEST"
cp "$APPDIR/translateSub.desktop" "$DEST/translateSub.desktop"
chmod +x "$DEST/translateSub.desktop"

# Install icon
mkdir -p "$ICONDST"
cp "$APPDIR/icon.svg" "$ICONDST/translatesub.svg"

# Update desktop database
update-desktop-database "$DEST" 2>/dev/null || true

echo "Installed! TranslateSub should appear in your app launcher."
echo ""
echo "To run from terminal:"
echo "  $APPDIR/translatesub-launcher --token YOUR_TOKEN --channel CHANNEL_ID"
echo ""
echo "Or set env vars in ~/.bashrc:"
echo "  export TRANSLATESUB_TOKEN=your_token"
echo "  export TRANSLATESUB_CHANNEL=channel_id"
echo "Then just run: translatesub-launcher"
