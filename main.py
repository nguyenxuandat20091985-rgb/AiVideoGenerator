#!/usr/bin/env python3
"""
AiVideoGenerator – Facebook Video Auto Processor & Poster

Usage:
    python main.py "https://www.facebook.com/watch/?v=XXXX"
    python main.py "URL" --reels
    python main.py          # interactive mode
"""

import argparse
import os
import shutil
import sys
import tempfile
from pathlib import Path

from dotenv import load_dotenv

from modules.downloader import download_facebook_video
from modules.processor import process_video_ffmpeg
from modules.uploader import upload_to_facebook_page

load_dotenv()

WATERMARK_TEXT = os.getenv("WATERMARK_TEXT", "YourBrand")


def cleanup(*paths: str):
    """Remove temporary files / directories safely."""
    for p in paths:
        if not p:
            continue
        try:
            if os.path.isfile(p):
                os.remove(p)
                print(f"[Cleanup] Đã xóa file: {p}")
            elif os.path.isdir(p):
                shutil.rmtree(p, ignore_errors=True)
                print(f"[Cleanup] Đã xóa thư mục: {p}")
        except Exception as e:
            print(f"[Cleanup] Không xóa được {p}: {e}")


def run_pipeline(facebook_url: str, as_reel: bool = False, keep_files: bool = False):
    """
    Full pipeline:
    1. Download
    2. Process (FFmpeg)
    3. Upload to Facebook Page
    4. Cleanup
    """
    temp_root = tempfile.mkdtemp(prefix="fb_pipeline_")
    dl_dir = os.path.join(temp_root, "download")
    proc_dir = os.path.join(temp_root, "processed")

    downloaded = None
    processed = None

    try:
        print("=" * 50)
        print("Bước 1/3 – Download video từ Facebook")
        print("=" * 50)
        downloaded = download_facebook_video(facebook_url, output_dir=dl_dir)

        print("\n" + "=" * 50)
        print("Bước 2/3 – Xử lý FFmpeg (cắt + flip + speed + watermark)")
        print("=" * 50)
        processed = process_video_ffmpeg(
            downloaded,
            output_dir=proc_dir,
            cut_start=2.0,
            cut_end=2.0,
            speed=1.03,
            watermark_text=WATERMARK_TEXT,
        )

        print("\n" + "=" * 50)
        print("Bước 3/3 – Upload lên Facebook Page")
        print("=" * 50)
        result = upload_to_facebook_page(
            processed,
            title="Auto Video",
            description="Processed & auto-posted",
            as_reel=as_reel,
        )

        print("\n" + "=" * 50)
        print("✅ HOÀN TẤT")
        print("=" * 50)
        print(result)
        return result

    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        raise

    finally:
        if not keep_files:
            cleanup(temp_root)
        else:
            print(f"[Keep] File tạm được giữ tại: {temp_root}")


def main():
    parser = argparse.ArgumentParser(
        description="Download Facebook video → process → post to your Page"
    )
    parser.add_argument(
        "url",
        nargs="?",
        help="Facebook video / watch / reel URL",
    )
    parser.add_argument(
        "--reels",
        action="store_true",
        help="Upload as Facebook Reel instead of regular video",
    )
    parser.add_argument(
        "--keep",
        action="store_true",
        help="Keep temporary files after processing",
    )
    args = parser.parse_args()

    url = args.url
    if not url:
        url = input("Dán link video Facebook: ").strip()

    if not url:
        print("Không có URL. Thoát.")
        sys.exit(1)

    if "facebook.com" not in url and "fb.watch" not in url:
        print("Cảnh báo: URL có vẻ không phải Facebook. Vẫn tiếp tục...")

    run_pipeline(url, as_reel=args.reels, keep_files=args.keep)


if __name__ == "__main__":
    main()
