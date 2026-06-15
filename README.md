🎙️ Transcriber
Desktop app to transcribe YouTube, TikTok, and Instagram Reels locally — no APIs, no limits, no cost.
Paste a URL, hit transcribe, get text. Supports batch (multiple URLs at once) and auto-detects language per video.
![Python](https://img.shields.io/badge/Python-3.8+-blue) ![License](https://img.shields.io/badge/license-MIT-green) ![Offline](https://img.shields.io/badge/runs-100%25%20local-black)
---
Features
Paste one or multiple URLs (one per line) and batch process them
Auto-detects language per video — Spanish, English, and 90+ more
Runs 100% locally — nothing leaves your machine
Supports YouTube, TikTok, Instagram Reels, and anything yt-dlp can download
Fast: uses faster-whisper with `int8` CPU inference + VAD silence skipping
Clean dark UI, real-time output, copy-to-clipboard
---
Install
1. Python dependencies
```bash
pip install yt-dlp faster-whisper
```
2. ffmpeg
Download from ffmpeg.org and add it to your system PATH.
On Windows: download the zip, extract it, and add the `bin/` folder to PATH via System Environment Variables.
---
Usage
```bash
python transcriber.py
```
Or create a desktop shortcut (Windows):
```
pythonw "C:\path\to\transcriber.py"
```
Double-click → paste URLs → Ctrl+Enter or click Transcribir.
---
Config
Two lines at the top of `transcriber.py`:
```python
MODEL = "tiny"   # tiny · base · small · medium · large-v3
LANG  = None     # None = autodetect · "es" · "en" · etc.
```
Model	Speed (CPU)	Accuracy
tiny	⚡⚡⚡ fastest	good enough for clear speech
base	⚡⚡ fast	better
small	⚡ moderate	solid
medium / large	🐢 slow	highest
`tiny` with `faster-whisper` on CPU handles a 20-minute video in ~2-3 minutes. That's the sweet spot for most use cases.
---
Notes
First run downloads the model and caches it (`~/.cache/huggingface/`)
No GPU required — `int8` CPU inference is fast enough
Instagram Reels require the profile to be public
`vad_filter=True` skips silent parts automatically, speeding things up further
---
License
MIT
