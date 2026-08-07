import logging
import os
from pathlib import Path
from typing import Optional

import yt_dlp
from pydub import AudioSegment

logging.basicConfig(level=logging.INFO)

DOWNLOAD_DIRECTORY = Path("downloads")
DOWNLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)


def resolve_cookie_file(base_dir: Optional[Path] = None) -> Optional[str]:
    """Resolve a usable yt-dlp cookie file for local and server environments."""
    search_paths = []

    env_cookie = os.getenv("YTDLP_COOKIE_FILE")
    if env_cookie:
        search_paths.append(Path(env_cookie))

    if base_dir is None:
        base_dir = Path(__file__).resolve().parents[1]

    search_paths.extend(
        [
            base_dir / "cookies.txt",
            Path.cwd() / "cookies.txt",
            Path(__file__).resolve().parent.parent / "cookies.txt",
        ]
    )

    for candidate in search_paths:
        if not candidate:
            continue

        try:
            resolved = candidate if candidate.is_absolute() else (base_dir / candidate).resolve()
        except Exception:
            resolved = candidate

        if resolved.exists():
            return str(resolved)

    return None


def build_auth_attempts(base_dir: Optional[Path] = None) -> list[tuple[str, dict]]:
    """Build a list of yt-dlp auth strategies to try in order."""
    attempts: list[tuple[str, dict]] = []

    cookie_file = resolve_cookie_file(base_dir)
    if cookie_file:
        attempts.append(("cookiefile", {"cookiefile": cookie_file}))

    configured_browser = os.getenv("YTDLP_COOKIES_FROM_BROWSER")
    if configured_browser:
        attempts.append(("cookiesfrombrowser", {"cookiesfrombrowser": (configured_browser,)}))
    elif os.name == "nt":
        for browser in ("chrome", "edge", "brave", "firefox"):
            attempts.append(("cookiesfrombrowser", {"cookiesfrombrowser": (browser,)}))

    if not attempts:
        logging.info("No cookie-based authentication methods are available.")

    return attempts


# ---------------------------
# Download YouTube Audio
# ---------------------------

def download_youtube_audio(url: str) -> str:
    logging.info("Downloading YouTube audio...")

    output_template = str(DOWNLOAD_DIRECTORY / "%(title)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best[ext=m4a]/bestaudio/best",
        "outtmpl": output_template,
        "noplaylist": True,
        "quiet": False,
        "no_warnings": False,
        "retries": 20,
        "fragment_retries": 20,
        "extractor_retries": 20,
        "socket_timeout": 180,
        "geo_bypass": True,
        "concurrent_fragment_downloads": 2,
        "hls_prefer_native": True,
        "extract_flat": False,
        "skip_unavailable_fragments": True,
        "extractor_args": {
            "youtube": {
                "player_client": [
                    "android",
                    "web",
                ],
                "player_skip": [
                    "configs",
                    "web_player",
                ],
            }
        },
        "http_headers": {
            "User-Agent":
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/138.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "writethumbnail": False,
    }

    attempts = build_auth_attempts()
    if not attempts:
        logging.info("No auth methods configured; attempting download without cookies.")
        attempts = [("default", {})]

    cookie_file = resolve_cookie_file()
    logging.info("Resolved YouTube cookie file: %s", cookie_file or "<none>")
    logging.info("YTDLP_COOKIE_FILE env var: %s", os.getenv("YTDLP_COOKIE_FILE") or "<not set>")

    last_error: Optional[Exception] = None
    last_error_text = ""
    for attempt_name, auth_opts in attempts:
        attempt_opts = dict(ydl_opts)
        attempt_opts.update(auth_opts)

        if attempt_name == "cookiefile":
            logging.info("Trying YouTube download with cookie file auth.")
        elif attempt_name == "cookiesfrombrowser":
            logging.info("Trying YouTube download with browser-cookie auth.")
        else:
            logging.info("Trying YouTube download with default auth.")

        try:
            with yt_dlp.YoutubeDL(attempt_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded = ydl.prepare_filename(info)
                wav_path = os.path.splitext(downloaded)[0] + ".wav"

                if not os.path.exists(wav_path):
                    raise FileNotFoundError(f"WAV file not found: {wav_path}")

                logging.info("Download successful.")
                return wav_path

        except Exception as exc:
            last_error = exc
            last_error_text = str(exc)
            logging.warning("yt-dlp auth attempt %s failed: %s", attempt_name, exc)
            continue

    logging.exception("yt-dlp failed")

    if "Sign in to confirm you're not a bot" in last_error_text or "cookies" in last_error_text.lower():
        raise RuntimeError(
            "Unable to download YouTube audio because YouTube is blocking the request. "
            "The hosted environment may not have usable YouTube cookies. "
            "Please try another video or use a machine with a valid browser session."
        )

    raise RuntimeError(
        "Unable to download YouTube audio.\n\n"
        f"{last_error_text if last_error_text else 'Unknown error'}"
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