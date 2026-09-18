import os
import sys
import argparse
import threading

os.environ["AV_NO_OPUS"] = "1"

if not os.environ.get("QT_QPA_PLATFORM"):
    os.environ["QT_QPA_PLATFORM"] = "xcb"

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from overlay import SubtitleOverlay
from tray import TrayIcon
from pipeline import Pipeline
from discord_client import DiscordVoiceClient


def main():
    parser = argparse.ArgumentParser(description="TranslateSub - Discord voice translator")
    parser.add_argument("--token", default=os.environ.get("TRANSLATESUB_TOKEN", ""),
                        help="Discord user token (or set TRANSLATESUB_TOKEN)")
    parser.add_argument("--channel", type=int, default=int(os.environ.get("TRANSLATESUB_CHANNEL", "0")),
                        help="Voice channel ID (or set TRANSLATESUB_CHANNEL)")
    parser.add_argument("--model", default=os.environ.get("TRANSLATESUB_MODEL", "base"),
                        choices=["base", "small", "medium", "large-v3"],
                        help="Whisper STT model size (default: base)")
    parser.add_argument("--target", default=os.environ.get("TRANSLATESUB_TARGET", "en"),
                        help="Target language code (default: en)")
    parser.add_argument("--minimized", action="store_true", help="Start minimized to tray")
    args = parser.parse_args()

    if not args.token or not args.channel:
        print("Error: --token and --channel are required")
        print("Usage: translatesub --token YOUR_TOKEN --channel CHANNEL_ID")
        print("Or set TRANSLATESUB_TOKEN and TRANSLATESUB_CHANNEL environment variables")
        sys.exit(1)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("TranslateSub")
    app.setApplicationDisplayName("TranslateSub")

    overlay = SubtitleOverlay()
    tray = TrayIcon()

    pipeline = Pipeline(
        overlay=overlay,
        model_size=args.model,
        target_lang=args.target,
        on_status=lambda s: print(f"[TranslateSub] {s}", flush=True),
    )

    discord_client = DiscordVoiceClient(
        token=args.token,
        channel_id=args.channel,
        on_audio_callback=pipeline.on_discord_audio,
        on_status=lambda s: print(f"[TranslateSub] {s}", flush=True),
    )

    def on_start():
        tray.set_running(True)
        threading.Thread(target=pipeline.start, daemon=True).start()
        discord_client.start()

    def on_stop():
        pipeline.stop()
        discord_client.stop()
        tray.set_running(False)

    tray.signals.start.connect(on_start)
    tray.signals.stop.connect(on_stop)
    tray.signals.quit.connect(lambda: (pipeline.stop(), discord_client.stop(), app.quit()))
    tray.signals.model_changed.connect(pipeline.change_model)

    tray.show()

    QTimer.singleShot(500, on_start)

    if not args.minimized:
        tray.show_message("TranslateSub", "Translating Discord VC. Check tray to stop.")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
