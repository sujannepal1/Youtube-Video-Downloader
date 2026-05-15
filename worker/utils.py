import os

import yt_dlp

from app.config import settings


def extract_metadata(url: str) -> dict:
    """Fetch video metadata without downloading the file."""
    ydl_opts = {"quiet": True, "no_warnings": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            "title": info.get("title"),
            "artist": info.get("artist") or info.get("uploader"),
            "duration": info.get("duration"),
            "url": url,
        }


def download_audio(url: str) -> str:
    """Download the best-quality audio track and convert it to MP3.

    Returns the path to the resulting MP3 file.
    """
    os.makedirs(settings.DOWNLOAD_DIR, exist_ok=True)
    output_template = os.path.join(settings.DOWNLOAD_DIR, "%(id)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_id = info.get("id")
        if not video_id:
            raise ValueError(f"Could not determine video ID for URL: {url}")

    return os.path.join(settings.DOWNLOAD_DIR, f"{video_id}.mp3")
