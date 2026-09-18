#!/bin/bash
CONFIG="$HOME/.config/translatesub.json"
mkdir -p "$(dirname "$CONFIG")"

if [ -f "$CONFIG" ] && [ "$1" != "--set" ]; then
    echo "Current config:"
    cat "$CONFIG"
    echo ""
    echo "To change: translatesub-config --set"
    exit 0
fi

echo "=== TranslateSub Configuration ==="
echo ""

read -p "Discord token: " token
read -p "Voice channel ID: " channel
read -p "Target language (default: en): " target
target="${target:-en}"
read -p "STT model (default: base): " model
model="${model:-base}"

cat > "$CONFIG" << EOF
{
    "token": "$token",
    "channel": $channel,
    "target": "$target",
    "model": "$model"
}
EOF

echo ""
echo "Config saved to $CONFIG"
echo "Run: translatesub-launcher"
