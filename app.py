#!/usr/bin/env python3
"""
Youtube Video Downloader
========================
Download video/audio from YouTube and 1000+ sites with a simple GUI.
Uses yt-dlp as the backend engine.

Usage:
    python app.py                  # Launch GUI
    python app.py "URL"            # Quick download (default: best quality)
    python app.py "URL" --audio    # Extract audio only
    python app.py "URL" --res 720  # Download at 720p
"""

import argparse
import json
import os
import re
import sys
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

try:
    import yt_dlp
except ImportError:
    print("ERROR: yt-dlp is not installed. Run: pip install yt-dlp")
    sys.exit(1)


# ─── Configuration ───────────────────────────────────────────────────────────

DEFAULT_DOWNLOAD_DIR = str(Path.home() / "Downloads" / "Youtube-Downloader")
SUPPORTED_AUDIO_FORMATS = ["mp3", "m4a", "wav", "flac", "opus", "aac", "ogg"]
RESOLUTIONS = ["2160", "1440", "1080", "720", "480", "360", "240", "144"]


# ─── Core Download Engine ────────────────────────────────────────────────────

class DownloadEngine:
    """Wrapper around yt-dlp with progress tracking and resume support."""

    def __init__(self, output_dir=None, on_progress=None, on_complete=None, on_error=None):
        self.output_dir = output_dir or DEFAULT_DOWNLOAD_DIR
        self.on_progress = on_progress or (lambda *a: None)
        self.on_complete = on_complete or (lambda *a: None)
        self.on_error = on_error or (lambda *a: None)
        self._cancelled = False
        os.makedirs(self.output_dir, exist_ok=True)

    def cancel(self):
        self._cancelled = True

    def _progress_hook(self, d):
        if self._cancelled:
            raise yt_dlp.utils.DownloadCancelled("Download cancelled by user")

        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            downloaded = d.get("downloaded_bytes", 0)
            speed = d.get("speed", 0) or 0
            eta = d.get("eta", 0) or 0
            percent = (downloaded / total * 100) if total else 0
            self.on_progress(percent, downloaded, total, speed, eta)
        elif d["status"] == "finished":
            self.on_progress(100, 0, 0, 0, 0)

    def fetch_info(self, url):
        """Fetch video metadata without downloading."""
        opts = {"quiet": True, "no_warnings": True, "skip_download": True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)

    def get_available_formats(self, url):
        """Return list of available formats for a URL."""
        info = self.fetch_info(url)
        formats = []
        if info and "formats" in info:
            for f in info["formats"]:
                formats.append({
                    "format_id": f.get("format_id", ""),
                    "ext": f.get("ext", ""),
                    "resolution": f.get("resolution", "audio only"),
                    "height": f.get("height"),
                    "fps": f.get("fps"),
                    "filesize": f.get("filesize") or f.get("filesize_approx", 0),
                    "vcodec": f.get("vcodec", "none"),
                    "acodec": f.get("acodec", "none"),
                    "note": f.get("format_note", ""),
                })
        return info, formats

    def download(self, url, resolution=None, audio_only=False, audio_format="mp3",
                 embed_thumbnail=True, keep_video=False):
        """Download a video or extract audio."""
        self._cancelled = False

        outtmpl = os.path.join(self.output_dir, "%(title)s.%(ext)s")

        if audio_only:
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": outtmpl,
                "progress_hooks": [self._progress_hook],
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": audio_format,
                    "preferredquality": "192",
                }],
                "writethumbnail": embed_thumbnail,
                "postprocessors_args": {},
                "keepvideo": keep_video,
                "noplaylist": True,
                "retries": 10,
                "fragment_retries": 10,
                "continuedl": True,  # Resume support
                "concurrent_fragment_downloads": 4,
            }
            if embed_thumbnail:
                ydl_opts["postprocessors"].append({
                    "key": "EmbedThumbnail",
                    "already_have_thumbnail": False,
                })
        else:
            fmt = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
            if resolution:
                fmt = (
                    f"bestvideo[height<={resolution}][ext=mp4]+bestaudio[ext=m4a]/"
                    f"bestvideo[height<={resolution}]+bestaudio/"
                    f"best[height<={resolution}]/best"
                )

            ydl_opts = {
                "format": fmt,
                "outtmpl": outtmpl,
                "progress_hooks": [self._progress_hook],
                "merge_output_format": "mp4",
                "noplaylist": True,
                "retries": 10,
                "fragment_retries": 10,
                "continuedl": True,  # Resume support
                "concurrent_fragment_downloads": 4,
                "writesubtitles": False,
                "writeautomaticsub": False,
            }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                # For audio, the extension changes after postprocessing
                if audio_only:
                    base = os.path.splitext(filename)[0]
                    filename = f"{base}.{audio_format}"
                self.on_complete(filename, info.get("title", "Unknown"))
                return filename
        except Exception as e:
            self.on_error(str(e))
            raise


# ─── GUI Application ─────────────────────────────────────────────────────────

class DownloaderApp:
    """Tkinter-based GUI for the downloader."""

    def __init__(self, root):
        self.root = root
        self.root.title("Youtube Video Downloader")
        self.root.geometry("750x620")
        self.root.minsize(650, 550)
        self.root.configure(bg="#1a1a2e")

        self.engine = None
        self.downloading = False
        self.download_dir = DEFAULT_DOWNLOAD_DIR

        self._build_ui()

    # ── UI Construction ──────────────────────────────────────────────────

    def _build_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#1a1a2e")
        style.configure("TLabel", background="#1a1a2e", foreground="#e0e0e0",
                         font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10, "bold"))
        style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"),
                         foreground="#e94560", background="#1a1a2e")
        style.configure("Status.TLabel", font=("Segoe UI", 9),
                         foreground="#aaaaaa", background="#1a1a2e")
        style.configure("Green.TButton", foreground="white", background="#00b894")
        style.configure("Red.TButton", foreground="white", background="#d63031")

        # ── Header ──
        header = ttk.Label(self.root, text="⬇  Youtube Video Downloader", style="Header.TLabel")
        header.pack(pady=(18, 2))

        subtitle = ttk.Label(self.root, text="YouTube & 1000+ sites  •  Video & Audio  •  Resume support",
                             style="Status.TLabel")
        subtitle.pack(pady=(0, 12))

        # ── URL Input ──
        url_frame = ttk.Frame(self.root)
        url_frame.pack(fill="x", padx=24, pady=4)

        ttk.Label(url_frame, text="🔗 Video URL:").pack(anchor="w")
        self.url_var = tk.StringVar()
        url_entry = tk.Entry(url_frame, textvariable=self.url_var, font=("Consolas", 11),
                             bg="#16213e", fg="#e0e0e0", insertbackground="#e0e0e0",
                             relief="flat", bd=8)
        url_entry.pack(fill="x", pady=(4, 0))
        url_entry.bind("<Return>", lambda e: self._start_download())

        # ── Options Row ──
        opts_frame = ttk.Frame(self.root)
        opts_frame.pack(fill="x", padx=24, pady=8)

        # Mode
        ttk.Label(opts_frame, text="Mode:").grid(row=0, column=0, sticky="w")
        self.mode_var = tk.StringVar(value="video")
        mode_combo = ttk.Combobox(opts_frame, textvariable=self.mode_var, state="readonly",
                                  values=["video", "audio"], width=10)
        mode_combo.grid(row=0, column=1, padx=(4, 20))
        mode_combo.bind("<<ComboboxSelected>>", self._on_mode_change)

        # Resolution
        ttk.Label(opts_frame, text="Resolution:").grid(row=0, column=2, sticky="w")
        self.res_var = tk.StringVar(value="best")
        self.res_combo = ttk.Combobox(opts_frame, textvariable=self.res_var, state="readonly",
                                      values=["best"] + RESOLUTIONS, width=10)
        self.res_combo.grid(row=0, column=3, padx=(4, 20))

        # Audio format
        ttk.Label(opts_frame, text="Audio fmt:").grid(row=0, column=4, sticky="w")
        self.afmt_var = tk.StringVar(value="mp3")
        self.afmt_combo = ttk.Combobox(opts_frame, textvariable=self.afmt_var, state="readonly",
                                       values=SUPPORTED_AUDIO_FORMATS, width=8)
        self.afmt_combo.grid(row=0, column=5, padx=(4, 0))

        # Output directory
        dir_frame = ttk.Frame(self.root)
        dir_frame.pack(fill="x", padx=24, pady=4)

        ttk.Label(dir_frame, text="📂 Save to:").pack(side="left")
        self.dir_label = ttk.Label(dir_frame, text=self.download_dir, style="Status.TLabel")
        self.dir_label.pack(side="left", padx=8, fill="x", expand=True)
        ttk.Button(dir_frame, text="Browse", command=self._browse_dir).pack(side="right")

        # ── Buttons ──
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=24, pady=8)

        self.download_btn = tk.Button(btn_frame, text="⬇  DOWNLOAD", font=("Segoe UI", 12, "bold"),
                                      bg="#e94560", fg="white", relief="flat", bd=0,
                                      activebackground="#c0392b", activeforeground="white",
                                      cursor="hand2", command=self._start_download)
        self.download_btn.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 6))

        self.cancel_btn = tk.Button(btn_frame, text="✕  CANCEL", font=("Segoe UI", 12, "bold"),
                                    bg="#636e72", fg="white", relief="flat", bd=0,
                                    activebackground="#2d3436", activeforeground="white",
                                    cursor="hand2", state="disabled", command=self._cancel_download)
        self.cancel_btn.pack(side="right", ipady=6, padx=(6, 0))

        # ── Info Fetch Button ──
        info_frame = ttk.Frame(self.root)
        info_frame.pack(fill="x", padx=24, pady=2)
        ttk.Button(info_frame, text="ℹ  Fetch Video Info", command=self._fetch_info).pack(side="left")

        # ── Progress ──
        prog_frame = ttk.Frame(self.root)
        prog_frame.pack(fill="x", padx=24, pady=8)

        self.progress_bar = ttk.Progressbar(prog_frame, length=400, mode="determinate")
        self.progress_bar.pack(fill="x")

        info_row = ttk.Frame(prog_frame)
        info_row.pack(fill="x", pady=4)

        self.percent_label = ttk.Label(info_row, text="0%", style="Status.TLabel")
        self.percent_label.pack(side="left")

        self.speed_label = ttk.Label(info_row, text="", style="Status.TLabel")
        self.speed_label.pack(side="left", padx=20)

        self.eta_label = ttk.Label(info_row, text="", style="Status.TLabel")
        self.eta_label.pack(side="right")

        # ── Status Log ──
        ttk.Label(self.root, text="Log:").pack(anchor="w", padx=24)
        log_frame = ttk.Frame(self.root)
        log_frame.pack(fill="both", expand=True, padx=24, pady=(2, 16))

        self.log_text = tk.Text(log_frame, height=8, bg="#16213e", fg="#a0d2db",
                                font=("Consolas", 9), relief="flat", bd=6,
                                wrap="word", state="disabled")
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.log_text.pack(fill="both", expand=True)

    # ── Helpers ──────────────────────────────────────────────────────────

    def _log(self, msg):
        self.log_text.configure(state="normal")
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{ts}] {msg}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _browse_dir(self):
        d = filedialog.askdirectory(initialdir=self.download_dir)
        if d:
            self.download_dir = d
            self.dir_label.config(text=d)

    def _on_mode_change(self, event=None):
        if self.mode_var.get() == "audio":
            self.res_combo.configure(state="disabled")
            self.afmt_combo.configure(state="readonly")
        else:
            self.res_combo.configure(state="readonly")
            self.afmt_combo.configure(state="disabled")

    def _format_bytes(self, n):
        for unit in ["B", "KB", "MB", "GB"]:
            if n < 1024:
                return f"{n:.1f} {unit}"
            n /= 1024
        return f"{n:.1f} TB"

    def _format_speed(self, bps):
        if not bps:
            return "..."
        return f"{self._format_bytes(bps)}/s"

    def _format_eta(self, seconds):
        if not seconds:
            return ""
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        if h:
            return f"{h}h {m}m {s}s"
        return f"{m}m {s}s"

    # ── Fetch Info ───────────────────────────────────────────────────────

    def _fetch_info(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("No URL", "Please enter a video URL first.")
            return

        def _worker():
            try:
                self._log(f"Fetching info for: {url[:80]}...")
                engine = DownloadEngine(output_dir=self.download_dir)
                info = engine.fetch_info(url)
                if info:
                    self.root.after(0, lambda: self._show_info(info))
                else:
                    self._log("Could not fetch video info.")
            except Exception as e:
                self._log(f"Error: {e}")

        threading.Thread(target=_worker, daemon=True).start()

    def _show_info(self, info):
        title = info.get("title", "Unknown")
        uploader = info.get("uploader", "Unknown")
        duration = info.get("duration", 0)
        views = info.get("view_count", 0)
        site = info.get("extractor", "Unknown")
        formats = info.get("formats", [])

        dur_str = f"{duration // 60}:{duration % 60:02d}" if duration else "N/A"
        views_str = f"{views:,}" if views else "N/A"

        heights = sorted(set(
            f["height"] for f in formats
            if f.get("height") and f.get("vcodec") != "none"
        ), reverse=True)
        res_str = ", ".join(f"{h}p" for h in heights[:6]) if heights else "N/A"

        lines = [
            f"Title:      {title}",
            f"Uploader:   {uploader}",
            f"Site:       {site}",
            f"Duration:   {dur_str}",
            f"Views:      {views_str}",
            f"Resolutions: {res_str}",
            f"Formats:    {len(formats)} available",
        ]
        self._log("─" * 50)
        for line in lines:
            self._log(line)
        self._log("─" * 50)

        # Auto-select best resolution
        if heights:
            best = str(heights[0])
            if best in RESOLUTIONS:
                self.res_var.set(best)

    # ── Download ─────────────────────────────────────────────────────────

    def _start_download(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("No URL", "Please enter a video URL.")
            return

        if self.downloading:
            return

        self.downloading = True
        self.download_btn.configure(state="disabled", bg="#636e72")
        self.cancel_btn.configure(state="normal")
        self.progress_bar["value"] = 0

        mode = self.mode_var.get()
        res = self.res_var.get()
        afmt = self.afmt_var.get()
        audio_only = mode == "audio"
        resolution = None if res == "best" else int(res)

        self._log(f"Starting {'audio' if audio_only else 'video'} download...")
        self._log(f"URL: {url[:80]}")
        if resolution:
            self._log(f"Resolution: {resolution}p")
        if audio_only:
            self._log(f"Audio format: {afmt}")

        def on_progress(pct, downloaded, total, speed, eta):
            self.root.after(0, lambda: self._update_progress(pct, downloaded, total, speed, eta))

        def on_complete(filename, title):
            self.root.after(0, lambda: self._download_done(filename, title))

        def on_error(err):
            self.root.after(0, lambda: self._download_error(err))

        def _worker():
            try:
                engine = DownloadEngine(
                    output_dir=self.download_dir,
                    on_progress=on_progress,
                    on_complete=on_complete,
                    on_error=on_error,
                )
                self.engine = engine
                engine.download(
                    url,
                    resolution=resolution,
                    audio_only=audio_only,
                    audio_format=afmt,
                )
            except Exception:
                pass  # Already handled via on_error

        threading.Thread(target=_worker, daemon=True).start()

    def _update_progress(self, pct, downloaded, total, speed, eta):
        self.progress_bar["value"] = pct
        self.percent_label.config(text=f"{pct:.1f}%")
        if total:
            self.speed_label.config(text=f"{self._format_bytes(downloaded)} / {self._format_bytes(total)}  ({self._format_speed(speed)})")
        else:
            self.speed_label.config(text=f"{self._format_bytes(downloaded)}  ({self._format_speed(speed)})")
        self.eta_label.config(text=f"ETA: {self._format_eta(eta)}" if eta else "")

    def _download_done(self, filename, title):
        self.downloading = False
        self.download_btn.configure(state="normal", bg="#e94560")
        self.cancel_btn.configure(state="disabled")
        self.progress_bar["value"] = 100
        self.percent_label.config(text="100%")
        self.speed_label.config(text="")
        self.eta_label.config(text="")
        self._log(f"✅ Download complete: {title}")
        self._log(f"   Saved to: {filename}")
        messagebox.showinfo("Download Complete", f"✅ {title}\n\nSaved to:\n{filename}")

    def _download_error(self, err):
        self.downloading = False
        self.download_btn.configure(state="normal", bg="#e94560")
        self.cancel_btn.configure(state="disabled")
        self._log(f"❌ Error: {err}")
        messagebox.showerror("Download Error", f"Download failed:\n\n{err}")

    def _cancel_download(self):
        if self.engine:
            self.engine.cancel()
            self._log("⛔ Download cancelled by user.")
            self.downloading = False
            self.download_btn.configure(state="normal", bg="#e94560")
            self.cancel_btn.configure(state="disabled")


# ─── CLI Mode ────────────────────────────────────────────────────────────────

def cli_download(url, resolution=None, audio_only=False, audio_format="mp3", output_dir=None):
    """Download without GUI — for quick one-liner usage."""
    download_dir = output_dir or DEFAULT_DOWNLOAD_DIR

    def on_progress(pct, downloaded, total, speed, eta):
        bar_len = 40
        filled = int(bar_len * pct / 100)
        bar = "█" * filled + "░" * (bar_len - filled)
        speed_str = f"{speed / 1024 / 1024:.1f} MB/s" if speed else "..."
        sys.stdout.write(f"\r  {bar} {pct:.1f}%  {speed_str}   ")
        sys.stdout.flush()

    def on_complete(filename, title):
        print(f"\n✅ Done: {title}")
        print(f"   Saved to: {filename}")

    def on_error(err):
        print(f"\n❌ Error: {err}")

    engine = DownloadEngine(
        output_dir=download_dir,
        on_progress=on_progress,
        on_complete=on_complete,
        on_error=on_error,
    )

    engine.download(
        url,
        resolution=resolution,
        audio_only=audio_only,
        audio_format=audio_format,
    )


# ─── Entry Point ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Youtube Video Downloader — Download video/audio from 1000+ sites",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python app.py                              # Launch GUI
  python app.py "https://youtube.com/..."    # Quick download (best quality)
  python app.py "URL" --audio                # Extract audio as MP3
  python app.py "URL" --res 720              # Download at 720p
  python app.py "URL" --res 1080 --dir ~/Vids  # Custom output folder
  python app.py "URL" --audio --audio-format wav  # Audio as WAV
        """,
    )
    parser.add_argument("url", nargs="?", help="Video URL to download")
    parser.add_argument("--audio", action="store_true", help="Extract audio only")
    parser.add_argument("--res", choices=RESOLUTIONS, help="Video resolution (e.g., 720, 1080)")
    parser.add_argument("--audio-format", choices=SUPPORTED_AUDIO_FORMATS, default="mp3",
                        help="Audio format (default: mp3)")
    parser.add_argument("--dir", help="Output directory")

    args = parser.parse_args()

    if args.url:
        # CLI mode — direct download
        cli_download(
            url=args.url,
            resolution=args.res,
            audio_only=args.audio,
            audio_format=args.audio_format,
            output_dir=args.dir,
        )
    else:
        # GUI mode
        root = tk.Tk()
        DownloaderApp(root)
        root.mainloop()


if __name__ == "__main__":
    main()
