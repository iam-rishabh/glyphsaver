#!/usr/bin/env bash
# Installs glyphsaver for the current user. No Pillow, no image folder —
# glyphs are pure vector code.
set -e

APP_DIR="$HOME/.local/share/glyphsaver"
SERVICE_DIR="$HOME/.config/systemd/user"

echo "==> Checking dependencies..."
MISSING=()
python3 -c "import tkinter" 2>/dev/null || MISSING+=("python3-tk")
command -v xprintidle >/dev/null 2>&1 || MISSING+=("xprintidle")

if [ ${#MISSING[@]} -ne 0 ]; then
    echo "Installing missing packages: ${MISSING[*]}"
    sudo apt update
    sudo apt install -y "${MISSING[@]}"
else
    echo "All dependencies already installed."
fi

echo "==> Copying files to $APP_DIR"
mkdir -p "$APP_DIR"
cp "$(dirname "$0")/glyphsaver.py" "$APP_DIR/"
cp "$(dirname "$0")/idle_watcher.py" "$APP_DIR/"
cp -r "$(dirname "$0")/glyphs" "$APP_DIR/"
chmod +x "$APP_DIR/glyphsaver.py" "$APP_DIR/idle_watcher.py"

echo "==> Installing systemd user service"
mkdir -p "$SERVICE_DIR"
cp "$(dirname "$0")/systemd/glyphsaver.service" "$SERVICE_DIR/"
sed -i "s|%h|$HOME|g" "$SERVICE_DIR/glyphsaver.service"

systemctl --user daemon-reload
systemctl --user enable --now glyphsaver.service

echo ""
echo "Done!"
echo "  - Available glyphs: python3 $APP_DIR/glyphsaver.py list"
echo "  - Runs automatically after 5 minutes idle (default glyph: heart-eyes)."
echo "  - Check status:    systemctl --user status glyphsaver.service"
echo "  - Run manually:    python3 $APP_DIR/glyphsaver.py run heart-eyes --mouth"
