# 🎬 YT Downloader

A highly intelligent, dark-themed video and audio downloader built with Python. 

[🚀 Download Latest Version (.exe)](https://github.com/R14LP/YT-Downloader/releases/latest)

## ✨ Smart Features & Architecture
- **IDM Integration:** Intelligently detects Internet Download Manager (IDM). If a clean, single-part MP4 link is found, it automatically forwards the download to IDM for maximum speed.
- **Concurrent Turbo Mode:** For streaming sites that use `.m3u8` or `.mpd` (where IDM fails), the app seamlessly switches to its native turbo mode, downloading from **10 simultaneous fragments** to bypass server speed limits.
- **High Quality:** Auto-merges video and audio to deliver true 4K, 1080p, or 720p without quality loss.
- **MP3 Conversion:** Extract high-quality audio from any video.
- **Modern UI:** Sleek, responsive, cyber-glass dark theme using PyWebview.
- **Portable:** Single standalone `.exe` file.

## 🛠️ Installation (For Developers)
1. Install Python 3.11.
2. Clone this repo: `git clone https://github.com/R14LP/YT-Downloader.git`
3. Install dependencies: `pip install flask yt-dlp pywebview`
4. Run: `python app.py`

## ⚖️ License
MIT License - feel free to use and modify!