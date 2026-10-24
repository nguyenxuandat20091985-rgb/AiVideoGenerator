"""
Download Facebook video using yt-dlp.
"""

import os
import tempfile
from pathlib import Path

import yt_dlp


def download_facebook_video(url: str, output_dir: str | None = None) -> str:
    """
    Download a public Facebook video and return the local file path.

    Args:
        url: Facebook video / watch / reel URL
        output_dir: Directory to save the file (default: system temp)

    Returns:
        Absolute path to the downloaded mp4 file
    """
    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="fb_dl_")

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Unique filename template
    outtmpl = os.path.join(output_dir, "%(id)s.%(ext)s")

    ydl_opts = {
        "outtmpl": outtmpl,
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "merge_output_format": "mp4",
        "quiet": False,
        "no_warnings": False,
        "retries": 3,
        "fragment_retries": 3,
        # Uncomment if you need cookies for private videos:
        # "cookiesfrombrowser": ("firefox",),
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if info is None:
            raise RuntimeError("yt-dlp không lấy được thông tin video.")

        # Resolve final filename
        filename = ydl.prepare_filename(info)
        # After merge the extension becomes .mp4
        if not filename.endswith(".mp4"):
            base, _ = os.path.splitext(filename)
            filename = base + ".mp4"

        if not os.path.isfile(filename):
            # Fallback: search the directory
            for f in Path(output_dir).glob("*"):
                if f.suffix.lower() in {".mp4", ".mkv", ".webm"}:
                    filename = str(f)
                    break
            else:
                raise FileNotFoundError(f"Không tìm thấy file sau khi download: {output_dir}")

    print(f"[Downloader] Đã tải xong → {filename}")
    return os.path.abspath(filename)
