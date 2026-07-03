# Smart Video Downloader

A modern, full-stack video downloader web application with a premium glassmorphism UI and Python Flask backend.

## ⚠️ Legal Disclaimer

This application should only be used to download content that you are authorized to download. Please comply with applicable laws and the terms of service of video platforms.

## Features

- 🔍 **Video Analysis** — Paste a URL to extract metadata (title, thumbnail, duration, formats)
- 📥 **Multi-Quality Downloads** — Choose from 144p to 4K, MP4/WEBM/MP3
- 📊 **Real-Time Progress** — Live progress bar, speed, and ETA via Server-Sent Events
- 📜 **Download History** — Searchable history with file location access
- ⚙️ **Settings** — Default folder, theme toggle, language selector
- 🎨 **Premium UI** — Dark/Light glassmorphism theme with smooth animations

## Screenshots

After running the app, visit `http://localhost:5050` to see the UI.

## Installation

### Prerequisites

- **Python 3.9+**
- **FFmpeg** (optional, required for MP3 audio extraction and some format merging)

### Steps

```bash
# 1. Clone or navigate to the project
cd SmartVideoDownloader

# 2. Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate     # Windows
# source venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python app/app.py
```

The app will start on **http://localhost:5050**.

### Installing FFmpeg (Optional)

- **Windows**: Download from https://ffmpeg.org/download.html and add to PATH
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`

## Usage

1. Open `http://localhost:5050` in your browser
2. Paste a video URL into the input field
3. Click **Analyze** to fetch video information
4. Select your desired quality and format
5. Click **Download** to start downloading
6. Monitor progress in real-time
7. View your download history in the **History** tab

## Project Structure

```
SmartVideoDownloader/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── app.py               # Entry point
│   ├── config.py            # Configuration
│   ├── routes/
│   │   ├── api.py           # Video analysis & download endpoints
│   │   ├── history.py       # Download history CRUD
│   │   └── settings.py      # App settings
│   ├── services/
│   │   ├── video_service.py # yt-dlp wrapper
│   │   └── history_service.py # SQLite history
│   ├── utils/
│   │   ├── validators.py    # URL validation
│   │   ├── formatters.py    # Size/duration formatting
│   │   └── logger.py        # Centralized logging
│   ├── static/
│   │   ├── css/             # Stylesheets
│   │   ├── js/              # JavaScript modules
│   │   └── img/             # Assets
│   └── templates/
│       └── index.html       # SPA shell
├── requirements.txt
├── README.md
└── .gitignore
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Backend | Python FastAPI + Uvicorn |
| Video Engine | yt-dlp |
| Database | SQLite (aiosqlite) |
| Real-Time | Server-Sent Events (SSE) |

## License

MIT License — for educational and personal use.
