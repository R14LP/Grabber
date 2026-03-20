# YT Downloader

A fast, dark-themed video and audio downloader built with Python.

[Download Latest Version (.exe)](https://github.com/R14LP/YT-Downloader/releases/latest)

## Features

- **Turbo Mode:** Downloads from 10 simultaneous fragments to bypass server speed limits.
- **High Quality:** Auto-merges video and audio to deliver true 4K, 1080p, 720p, or 480p.
- **WMP Compatible:** Audio is re-encoded to AAC on merge — works with Windows Media Player out of the box.
- **MP3 Conversion:** Extract audio at 128, 192, or 320 kbps.
- **Per-Video Progress:** Each video/playlist item gets its own real-time progress bar.
- **Modern UI:** Responsive dark theme, scales with window size.

## Installation (For Developers)

1. Install Python 3.11
2. Clone: `git clone https://github.com/R14LP/YT-Downloader.git`
3. Install dependencies: `pip install flask yt-dlp pywebview`
4. Place `ffmpeg.exe` and `ffprobe.exe` next to `app.py`
5. Run: `python app.py`

## License

MIT License - feel free to use and modify!
```

```
What's New in v1.3.0

- Removed IDM dependency — app now handles all downloads natively with 10-thread turbo mode
- Fixed audio codec issue: merged MP4s now use AAC encoding, compatible with Windows Media Player
- Per-video progress tracking: each video in a playlist gets its own progress bar
- MP3 bitrate selector: choose 128, 192, or 320 kbps
- Added 480p quality option for video downloads
- Redesigned UI: fully responsive, scales with window size, new typography and layout

Download YT_Downloader_Setup_v1.3.0.exe below.