# 🎬 MediaFlow

A modern, full-stack media downloader web application featuring a premium glassmorphism interface and a high-performance Python FastAPI backend.

## ⚠️ Legal Disclaimer

MediaFlow is intended only for downloading content that you own or have permission to download. Users are responsible for complying with applicable copyright laws and the terms of service of the platforms they use.

---

## ✨ Features

* 🔍 **Smart Media Analysis** — Extract title, thumbnail, duration, uploader, and available formats from a media URL.
* 📥 **High-Quality Downloads** — Download videos in multiple resolutions (144p–4K) or extract audio in MP3 format.
* ⚡ **Real-Time Progress Tracking** — Live download progress with speed, ETA, and status updates using Server-Sent Events (SSE).
* 📂 **Download History** — View, search, and manage previous downloads.
* ⚙️ **Custom Settings** — Configure download location, theme, language, and default quality.
* 🎨 **Premium Glassmorphism UI** — Modern responsive interface with Dark and Light themes.
* 🚀 **FastAPI Backend** — High-performance asynchronous API powered by FastAPI and Uvicorn.
* 🔒 **Secure URL Validation** — Validates supported URLs before processing.
* 📱 **Responsive Design** — Optimized for desktop, tablet, and mobile devices.

---

## 📸 Preview

After starting the application, open:

`http://localhost:5050`

---

# 🚀 Installation

## Prerequisites

* Python 3.10 or later
* FFmpeg *(Optional, recommended for audio extraction and video merging)*

## Setup

```bash
# Clone the repository
git clone <repository-url>

# Navigate into the project
cd MediaFlow

# Create a virtual environment
python -m venv venv

# Activate the environment

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the application
python app/app.py
```

The server will be available at:

```
http://localhost:5050
```

---

## 🎵 Installing FFmpeg (Optional)

### Windows

Download FFmpeg from the official website and add it to your system PATH.

### macOS

```bash
brew install ffmpeg
```

### Ubuntu / Debian

```bash
sudo apt install ffmpeg
```

---





