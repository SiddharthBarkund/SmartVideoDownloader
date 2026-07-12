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

# 📖 Usage

1. Launch the application.
2. Paste a supported video URL.
3. Click **Analyze**.
4. Select your preferred quality and format.
5. Click **Download**.
6. Track the download progress in real time.
7. Access previous downloads from the **History** page.

---

# 📁 Project Structure

```
MediaFlow/
│
├── app/
│   ├── __init__.py
│   ├── app.py
│   ├── config.py
│   │
│   ├── routes/
│   │   ├── api.py
│   │   ├── history.py
│   │   └── settings.py
│   │
│   ├── services/
│   │   ├── video_service.py
│   │   └── history_service.py
│   │
│   ├── utils/
│   │   ├── validators.py
│   │   ├── formatters.py
│   │   └── logger.py
│   │
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   │
│   └── templates/
│       └── index.html
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

# 🛠️ Tech Stack

| Layer             | Technology                    |
| ----------------- | ----------------------------- |
| Frontend          | HTML5, CSS3, JavaScript (ES6) |
| Backend           | FastAPI + Uvicorn             |
| Media Engine      | yt-dlp                        |
| Database          | SQLite + aiosqlite            |
| Real-Time Updates | Server-Sent Events (SSE)      |
| Styling           | Glassmorphism UI              |

---

# 📌 Future Roadmap

* User authentication
* Download queue management
* Playlist downloading
* Subtitle downloads
* Batch downloads
* Browser extension
* Docker support
* Multi-language interface
* Download scheduler
* Cloud storage integration

---

# 📄 License

Licensed under the **MIT License**.

This project is intended for educational, research, and personal use only.
