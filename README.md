# Youtube Video Downloader

> Download video/audio from **YouTube** and **1000+ sites** with one simple command.
> GUI + CLI interface. Resume support. Resolution picker. Audio extraction.

```
████████╗██╗   ██╗████████╗    ██████╗ ██╗     ██╗
╚══██╔══╝╚██╗ ██╔╝╚══██╔══╝    ██╔══██╗██║     ██║
   ██║    ╚████╔╝    ██║       ██║  ██║██║     ██║
   ██║     ╚██╔╝     ██║       ██║  ██║██║     ██║
   ██║      ██║      ██║       ██████╔╝███████╗███████╗
   ╚═╝      ╚═╝      ╚═╝       ╚═════╝ ╚══════╝╚══════╝
```

## ⚡ Quick Start

```bash
# Install
pip install -r requirements.txt

# Launch GUI
python app.py

# One-liner download (just paste the link!)
python app.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Download audio only
python app.py "URL" --audio

# Pick resolution
python app.py "URL" --res 720
```

## 🎯 Features

| Feature | Description |
|---------|-------------|
| **One Command** | Just paste the URL — `python app.py "LINK"` |
| **GUI Mode** | Dark-themed tkinter interface with progress tracking |
| **CLI Mode** | Fast terminal downloads with progress bar |
| **1000+ Sites** | YouTube, Vimeo, Twitter/X, TikTok, Bilibili, Dailymotion, Reddit, Twitch, SoundCloud, and [many more](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md) |
| **Resume** | Interrupted downloads resume from where they stopped |
| **Resolution** | Choose 144p up to 4K (2160p) |
| **Audio Extract** | Convert to MP3, M4A, WAV, FLAC, OPUS, AAC, OGG |
| **Metadata** | Auto-embeds thumbnail in audio files |
| **Concurrent** | Multi-threaded fragment downloads for speed |
| **Safe Filenames** | Auto-sanitizes special characters in titles |

## 📸 Screenshots

### GUI Mode
```
┌──────────────────────────────────────────────────┐
│  ⬇  Youtube Video Downloader                    │
│  YouTube & 1000+ sites • Video & Audio           │
│                                                  │
│  🔗 Video URL:                                   │
│  ┌──────────────────────────────────────────┐    │
│  │ https://youtube.com/watch?v=...          │    │
│  └──────────────────────────────────────────┘    │
│                                                  │
│  Mode: [video ▾]  Resolution: [1080 ▾]          │
│  Audio fmt: [mp3 ▾]                              │
│  📂 Save to: ~/Downloads/Youtube-Downloader      │
│                                                  │
│  [ ⬇  DOWNLOAD ]            [ ✕  CANCEL ]       │
│  [ ℹ  Fetch Video Info ]                         │
│                                                  │
│  ████████████████████░░░░░░  72.3%               │
│  45.2 MB / 62.5 MB  (3.2 MB/s)  ETA: 5m 03s    │
│                                                  │
│  Log:                                            │
│  [14:32:01] Starting video download...           │
│  [14:32:01] URL: https://youtube.com/watch?v=... │
│  [14:32:01] Resolution: 1080p                    │
│  [14:32:06] ✅ Download complete: Video Title    │
│  [14:32:06]    Saved to: /path/to/file.mp4      │
└──────────────────────────────────────────────────┘
```

### CLI Mode
```
$ python app.py "https://youtube.com/watch?v=dQw4w9WgXcQ"

  ████████████████████████████████████████ 100%  4.2 MB/s
  ✅ Done: Rick Astley - Never Gonna Give You Up
     Saved to: ~/Downloads/Youtube-Downloader/Rick Astley - Never Gonna Give You Up [dQw4w9WgXcQ].mp4
```

## 🔧 Usage

### GUI Mode (default)
```bash
python app.py
```

### CLI Mode
```bash
# Basic download
python app.py "URL"

# Audio extraction
python app.py "URL" --audio
python app.py "URL" --audio --audio-format wav

# Specific resolution
python app.py "URL" --res 720
python app.py "URL" --res 1080

# Custom output directory
python app.py "URL" --dir ~/Videos

# Combine options
python app.py "URL" --res 1080 --dir ~/Movies
```

### CLI Options
```
positional arguments:
  url                   Video URL to download

options:
  --audio               Extract audio only
  --res {2160,1440,1080,720,480,360,240,144}
                        Video resolution
  --audio-format {mp3,m4a,wav,flac,opus,aac,ogg}
                        Audio format (default: mp3)
  --dir DIR             Output directory
```

## 📦 Requirements

- **Python 3.8+**
- **yt-dlp** — the download engine (supports 1000+ sites)
- **ffmpeg** — for audio extraction and video merging (optional but recommended)
- **tkinter** — for GUI mode (usually bundled with Python; see below if missing)

### Install ffmpeg (required for audio extraction)

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows (via Chocolatey)
choco install ffmpeg
```

### Install tkinter (if missing)

```bash
# Ubuntu/Debian
sudo apt install python3-tk

# macOS
brew install python-tk

# Windows: reinstall Python with "tcl/tk and IDLE" checked
```

> **Note:** GUI mode requires a display (X11/Wayland on Linux, desktop on Windows/macOS).
> On headless servers, only CLI mode is available — but tkinter must still be installed
> since it's imported at startup.

## 🌍 Supported Sites (partial list)

YouTube • Vimeo • Twitter/X • TikTok • Instagram • Facebook • Reddit • Twitch • Dailymotion • Bilibili • SoundCloud • Spotify (metadata) • Bandcamp • Streamable • Rumble • Odysee • LBRY • NicoNico • and 1000+ more via yt-dlp.

Full list: https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md

## 🔄 Resume Support

Interrupted downloads automatically resume when you re-run the same command. yt-dlp detects partial `.part` files and continues from where it stopped. No extra flags needed.

## 📁 Output Format

Downloaded files are saved as:
```
Video Title [VIDEO_ID].mp4
```

The video ID is included in the filename to avoid collisions when downloading different videos with the same title. Filenames are automatically sanitized to remove characters that are invalid on Windows (`/ \ : * ? " < > |`).

## 🏗️ Project Structure

```
Youtube-Video-Downloader/
├── app.py              # Main application (GUI + CLI)
├── requirements.txt    # Python dependencies
├── README.md           # This file
├── LICENSE             # MIT License
└── .gitignore          # Git ignore rules
```

## 🤝 Contributing

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Open a Pull Request

## 📝 License

MIT License — see [LICENSE](LICENSE) for details.

## 🙏 Credits

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — the powerful download engine
- [youtube-dl](https://github.com/ytdl-org/youtube-dl) — the original project
- [tkinter](https://docs.python.org/3/library/tkinter.html) — built-in Python GUI toolkit
