# TranslateSub

Real-time Discord voice channel translator with on-screen subtitles.

Captures audio from a Discord voice channel via WebRTC, transcribes speech with Whisper, translates it with Google Translate, and displays subtitles on your desktop.

## Features

- **Per-user attribution** — shows who said what
- **Real-time subtitles** — floating overlay on your desktop
- **Resizable & scrollable** — drag to resize, scroll for history, remembers position
- **System tray** — start/stop from tray, switch STT models
- **60+ languages** — auto-detect source, translate to any target language
- **Low latency** — CPU-only with int8 quantization, no GPU needed

## Requirements

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- A Discord account (for self-bot token)
- Linux (tested on Kubuntu/KDE Plasma)

## Quick Start

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/translatesub.git
cd translatesub

# Create venv and install dependencies
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
uv pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# Run
python main.py --token YOUR_TOKEN --channel CHANNEL_ID --target en
```

## Getting Your Discord Token

> **Warning:** Using a self-bot is against Discord's Terms of Service. Use at your own risk.

1. Open Discord in your browser (not the desktop app)
2. Press `F12` to open Developer Tools
3. Go to the **Network** tab
4. Click any request and find the `authorization` header
5. Copy the token value

## Getting a Voice Channel ID

1. In Discord, go to **User Settings → Advanced → Enable Developer Mode**
2. Right-click any voice channel → **Copy Channel ID**

## Usage

```bash
# Basic usage
python main.py --token YOUR_TOKEN --channel 123456789 --target en

# With options
python main.py \
    --token YOUR_TOKEN \
    --channel 123456789 \
    --target tr \
    --model small

# List all options
python main.py --help
```

### CLI Options

| Flag | Default | Description |
|------|---------|-------------|
| `--token` | (required) | Discord user token |
| `--channel` | (required) | Voice channel ID |
| `--target` | `en` | Target language code |
| `--model` | `base` | STT model: `base`, `small`, `medium`, `large-v3` |

### Common Language Codes

| Code | Language |
|------|----------|
| `en` | English |
| `tr` | Turkish |
| `ja` | Japanese |
| `es` | Spanish |
| `de` | German |
| `fr` | French |
| `ru` | Russian |
| `ar` | Arabic |

## Environment Variables

Instead of passing args every time, you can set environment variables:

```bash
export TRANSLATESUB_TOKEN=your_token_here
export TRANSLATESUB_CHANNEL=123456789
export TRANSLATESUB_TARGET=en
export TRANSLATESUB_MODEL=base

python main.py
```

## Kubuntu Desktop Integration

Install as a KDE app:

```bash
chmod +x install.sh
./install.sh
```

This creates a launcher in your KDE app menu.

## Configuration

Use `~/.config/translatesub.json`:

```json
{
    "token": "your_token",
    "channel": 123456789,
    "target": "en",
    "model": "base"
}
```

Or run the interactive setup:

```bash
./translatesub-launcher --setup
```

## How It Works

```
Discord Voice Channel (WebRTC)
    │
    ▼
discord.py-self + discord-native-voice
    │  (connects as your alt account, receives Opus audio per-user)
    ▼
Opus → PCM decode → 48kHz stereo → 16kHz mono resample
    │
    ▼
Silero VAD (voice activity detection)
    │  (filters out silence)
    ▼
faster-whisper (speech-to-text)
    │  (base model, int8 quantized, CPU)
    ▼
Google Translate (via translators lib)
    │  (auto-detect source → target language)
    ▼
PyQt6 Subtitle Overlay
    (scrollable, resizable, remembers position)
```

## Architecture

```
translatesub/
├── main.py              # Entry point + CLI
├── discord_client.py    # Discord voice receive via WebRTC
├── pipeline.py          # Thread orchestration (VAD → STT → translate)
├── vad.py               # Silero voice activity detection
├── transcriber.py       # faster-whisper speech-to-text
├── translator.py        # Google Translate wrapper
├── overlay.py           # PyQt6 floating subtitle overlay
├── tray.py              # System tray icon + controls
├── requirements.txt     # Dependencies
├── install.sh           # KDE desktop installer
├── translateSub.desktop # .desktop file
├── icon.svg             # App icon
└── config.example.json  # Example config
```

## License

MIT
