import logging
import os
from pathlib import Path

import yt_dlp
from pydub import AudioSegment

logging.basicConfig(level=logging.INFO)

DOWNLOAD_DIRECTORY = Path("downloads")
DOWNLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)

COOKIE_FILE = os.getenv("YTDLP_COOKIE_FILE")

# ---------------------------
# Download YouTube Audio
# ---------------------------

def download_youtube_audio(url: str) -> str:
    logging.info("Downloading YouTube audio...")

    output_template = str(DOWNLOAD_DIRECTORY / "%(title)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "noplaylist": True,
        "quiet": False,
        "no_warnings": False,
        "retries": 10,
        "fragment_retries": 10,
        "socket_timeout": 60,
        "geo_bypass": True,
        "concurrent_fragment_downloads": 4,
        "extractor_retries": 5,

        # Better extraction strategy
        "extractor_args": {
            "youtube": {
                "player_client": [
                    "android",
                    "web",
                    "tv"
                ]
            }
        },

        "http_headers": {
            "User-Agent":
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/138.0.0.0 Safari/537.36"
        },

        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
    }

    # Optional cookie support
    if COOKIE_FILE and os.path.exists(COOKIE_FILE):
        logging.info("Using cookie file: %s", COOKIE_FILE)
        ydl_opts["cookiefile"] = COOKIE_FILE
    else:
        logging.info("No cookie file configured.")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            downloaded = ydl.prepare_filename(info)
            wav_path = os.path.splitext(downloaded)[0] + ".wav"

            if not os.path.exists(wav_path):
                raise FileNotFoundError(
                    f"WAV file not found after download: {wav_path}"
                )

            logging.info("Downloaded successfully.")

            return wav_path

    except Exception as e:
        logging.exception("YouTube download failed")
        raise RuntimeError(
            f"Unable to download YouTube video.\n\n{e}"
        )


# ---------------------------
# Convert local file to WAV
# ---------------------------

def convert_to_wav(input_path: str) -> str:
    logging.info("Converting local media to WAV...")

    output_path = os.path.splitext(input_path)[0] + "_converted.wav"

    audio = AudioSegment.from_file(input_path)

    audio = (
        audio
        .set_channels(1)
        .set_frame_rate(16000)
    )

    audio.export(output_path, format="wav")

    return output_path


# ---------------------------
# Chunk Audio
# ---------------------------

def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list[str]:
    logging.info("Chunking audio...")

    audio = AudioSegment.from_wav(wav_path)

    chunk_ms = chunk_minutes * 60 * 1000

    chunks = []

    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start:start + chunk_ms]

        chunk_path = (
            f"{os.path.splitext(wav_path)[0]}"
            f"_chunk_{i}.wav"
        )

        chunk.export(chunk_path, format="wav")

        chunks.append(chunk_path)

    logging.info("Created %d chunks.", len(chunks))

    return chunks


# ---------------------------
# Main entry point
# ---------------------------

def process_input(source: str) -> list[str]:
    """
    Accepts either:
      - Local video/audio path
      - YouTube URL
    Returns:
      List of WAV chunk paths
    """

    logging.info("Processing input: %s", source)

    if source.startswith(("http://", "https://")):
        wav_path = download_youtube_audio(source)
    else:
        wav_path = convert_to_wav(source)

    chunks = chunk_audio(wav_path)

    logging.info("Processing complete.")

    return chunks