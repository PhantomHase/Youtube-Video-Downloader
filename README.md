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
| **GUI Mode** | Beautiful dark-themed interface with drag & paste |
| **CLI Mode** | Fast terminal downloads with progress bar |
| **1000+ Sites** | YouTube, Vimeo, Twitter/X, TikTok, Bilibili, Dailymotion, Reddit, Twitch, SoundCloud, and [many more](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md) |
| **Resume** | Interrupted downloads resume from where they stopped |
| **Resolution** | Choose 144p up to 4K (2160p) |
| **Audio Extract** | Convert to MP3, M4A, WAV, FLAC, OPUS, AAC, OGG |
| **Metadata** | Auto-embeds thumbnail in audio files |
| **Concurrent** | Multi-threaded fragment downloads for speed |
| **Playlist** | Single video by default (add `--playlist` flag to change) |

## 📸 Screenshots

### GUI Mode
```
┌─────────────────────────────────────────────┐
│  ⬇  Youtube Video Downloader               │
│  YouTube & 1000+ sites • Video & Audio      │
│                                             │
│  🔗 Video URL:                              │
│  ┌─────────────────────────────────────┐    │
│  │ https://youtube.com/watch?v=...     │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  Mode: [video ▾]  Resolution: [1080 ▾]     │
│  📂 Save to: ~/Downloads/Youtube-Downloader │
│                                             │
│  [ ⬇  DOWNLOAD ]        [ ✕  CANCEL ]      │
│                                             │
│  ████████████████████░░░░░░  72.3%          │
│  45.2 MB / 62.5 MB  (3.2 MB/s)  ETA: 5s   │
│                                             │
│  [14:32:01] Starting video download...      │
│  [14:32:06] ✅ Download complete!           │
└─────────────────────────────────────────────┘
```

### CLI Mode
```
$ python app.py "https://youtube.com/watch?v=..."

  Starting video download...
  URL: https://youtube.com/watch?v=dQw4w9WgXcQ
  ████████████████████████████████████████ 100%  4.2 MB/s
  ✅ Done: Rick Astley - Never Gonna Give You Up
     Saved to: /home/user/Downloads/Youtube-Downloader/Rick Astley - Never Gonna Give You Up.mp4
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

### Install ffmpeg (for audio extraction)

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows (via Chocolatey)
choco install ffmpeg
```

## 🌍 Supported Sites (partial list)

YouTube • Vimeo • Twitter/X • TikTok • Instagram • Facebook • Reddit • Twitch • Dailymotion • Bilibili • SoundCloud • Spotify (metadata) • Bandcamp • Vimeo • Streamable • Rumble • Odysee • LBRY • NicoNico • and 1000+ more via yt-dlp.

Full list: https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md

## 🔄 Resume Support

Interrupted downloads automatically resume when you re-run the same command. yt-dlp detects partial `.part` files and continues from where it stopped. No extra flags needed.

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
