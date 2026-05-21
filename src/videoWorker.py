import os
import traceback
from utils.logger import setup_logger
from utils.timecode import parse_timecode
from email_monitor import fetch_clip_requests
from drive_uploader import upload_to_drive
from notifier import send_notification
from cookie_extractor import get_cookies_file
import yt_dlp
import subprocess

logger = setup_logger("videoWorker")

# ---------------------------------------------------------
#  HIGH QUALITY DOWNLOADER (yt-dlp modern 2026 version)
# ---------------------------------------------------------

def download_high_quality(video_url: str, output_dir: str) -> str:
    """
    Download highest-quality video (AV1/VP9 preferred, H.264 fallback).
    Returns the downloaded file path.
    """

    os.makedirs(output_dir, exist_ok=True)
    cookies_file = get_cookies_file()

    ydl_opts = {
        "format": (
            "bestvideo[ext=webm][vcodec^=av01]+bestaudio[ext=webm]/"
            "bestvideo[ext=webm][vcodec^=vp9]+bestaudio[ext=webm]/"
            "bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/"
            "best"
        ),
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        "youtube_client": "android",
        "concurrent_fragment_downloads": 5,
        "retries": 10,
        "fragment_retries": 10,
        "throttled_rate": 1024 * 1024,
        "quiet": False,
        "no_warnings": False,
    }

    if cookies_file:
        ydl_opts["cookiefile"] = cookies_file
        logger.info(f"Using cookies file: {cookies_file}")

    logger.info(f"Starting high-quality download: {video_url}")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        filepath = ydl.prepare_filename(info)

    logger.info(f"Download complete: {filepath}")
    return filepath


# ---------------------------------------------------------
#  EMBEDDED CLIPPER (FFmpeg)
# ---------------------------------------------------------

def clip_video(input_path: str, start_time: str, end_time: str, label: str, output_dir: str) -> str:
    """
    Use ffmpeg to trim a clip from input_path between start_time and end_time.
    Returns the output file path.
    """

    os.makedirs(output_dir, exist_ok=True)

    start_sec = parse_timecode(start_time)
    end_sec = parse_timecode(end_time)
    duration = end_sec - start_sec

    if duration <= 0:
        raise ValueError("End time must be greater than start time")

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    safe_label = "".join(c for c in label if c.isalnum() or c in ("-", "_")).strip() or "clip"
    output_name = f"{base_name}_{safe_label}.mp4"
    output_path = os.path.join(output_dir, output_name)

    cmd = [
        "ffmpeg",
        "-y",
        "-ss", str(start_sec),
        "-i", input_path,
        "-t", str(duration),
        "-c", "copy",
        output_path,
    ]

    logger.info(f"Clipping video: {input_path}")
    logger.info(f"Command: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg failed: {e.stderr.decode(errors='ignore')}")
        raise

    logger.info(f"Clip created: {output_path}")
    return output_path


# ---------------------------------------------------------
#  MAIN PIPELINE
# ---------------------------------------------------------

DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "downloads")
CLIP_DIR = os.getenv("CLIP_DIR", "clips")

def process_requests():
    logger.info("Checking for new clip requests...")
    requests = fetch_clip_requests()

    if not requests:
        logger.info("No new requests.")
        return

    for req in requests:
        try:
            video_url = req["video_url"]
            start_time = req["start_time"]
            end_time = req["end_time"]
            label = req["label"]

            logger.info(f"Processing request: {video_url} [{start_time} - {end_time}] ({label})")

            # 1. Download
            downloaded_path = download_high_quality(video_url, DOWNLOAD_DIR)

            # 2. Clip
            clip_path = clip_video(downloaded_path, start_time, end_time, label, CLIP_DIR)

            # 3. Upload
            drive_url = upload_to_drive(clip_path)

            logger.info(f"Completed clip. Drive URL: {drive_url}")

            # 4. Notify (optional)
            # send_notification("user@example.com", "Your clip is ready", drive_url)

        except Exception as e:
            logger.error("Error processing request:")
            logger.error(traceback.format_exc())


if __name__ == "__main__":
    process_requests()
