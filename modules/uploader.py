"""
Upload processed video to Facebook Page via Meta Graph API.
Supports both regular Page video and Reels.
"""

import os
import time
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()

FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
FB_API_VERSION = os.getenv("FB_API_VERSION", "v19.0")

GRAPH_BASE = f"https://graph.facebook.com/{FB_API_VERSION}"
RUPLOAD_BASE = f"https://rupload.facebook.com/video-upload/{FB_API_VERSION}"


def _check_credentials():
    if not FB_PAGE_ID or not FB_PAGE_ACCESS_TOKEN:
        raise EnvironmentError(
            "Thiếu FB_PAGE_ID hoặc FB_PAGE_ACCESS_TOKEN trong file .env"
        )


def upload_regular_video(
    video_path: str,
    title: str = "",
    description: str = "",
    published: bool = True,
) -> dict:
    """
    Upload video as a regular Page video (not Reel).
    Uses resumable upload under the hood via the /videos endpoint with file.
    """
    _check_credentials()

    url = f"{GRAPH_BASE}/{FB_PAGE_ID}/videos"

    with open(video_path, "rb") as f:
        files = {"source": f}
        data = {
            "access_token": FB_PAGE_ACCESS_TOKEN,
            "title": title or "Auto posted video",
            "description": description or "",
            "published": "true" if published else "false",
        }
        print("[Uploader] Đang upload video thường lên Page...")
        resp = requests.post(url, data=data, files=files, timeout=600)

    resp.raise_for_status()
    result = resp.json()
    print(f"[Uploader] Upload thành công → video_id = {result.get('id')}")
    return result


def upload_reel(
    video_path: str,
    description: str = "",
    title: str = "",
) -> dict:
    """
    Upload as Facebook Reel (3-phase flow).
    1. Initialize session → get video_id + upload_url
    2. Upload binary to rupload.facebook.com
    3. Finish & publish
    """
    _check_credentials()

    # Phase 1: start
    start_url = f"{GRAPH_BASE}/{FB_PAGE_ID}/video_reels"
    start_payload = {
        "upload_phase": "start",
        "access_token": FB_PAGE_ACCESS_TOKEN,
    }
    print("[Uploader] Reels – Phase 1: Initialize...")
    r1 = requests.post(start_url, data=start_payload, timeout=30)
    r1.raise_for_status()
    data1 = r1.json()
    video_id = data1["video_id"]
    upload_url = data1.get("upload_url") or f"{RUPLOAD_BASE}/{video_id}"

    # Phase 2: upload binary
    file_size = os.path.getsize(video_path)
    headers = {
        "Authorization": f"OAuth {FB_PAGE_ACCESS_TOKEN}",
        "offset": "0",
        "file_size": str(file_size),
    }
    print(f"[Uploader] Reels – Phase 2: Upload binary ({file_size / 1024 / 1024:.1f} MB)...")
    with open(video_path, "rb") as f:
        r2 = requests.post(upload_url, headers=headers, data=f, timeout=600)
    r2.raise_for_status()

    # Phase 3: finish & publish
    finish_payload = {
        "upload_phase": "finish",
        "video_id": video_id,
        "video_state": "PUBLISHED",
        "description": description or title or "",
        "access_token": FB_PAGE_ACCESS_TOKEN,
    }
    if title:
        finish_payload["title"] = title

    print("[Uploader] Reels – Phase 3: Publish...")
    r3 = requests.post(start_url, data=finish_payload, timeout=60)
    r3.raise_for_status()
    result = r3.json()
    print(f"[Uploader] Reel đăng thành công → {result}")
    return result


def upload_to_facebook_page(
    video_path: str,
    title: str = "",
    description: str = "",
    as_reel: bool = False,
) -> dict:
    """
    Main entry for uploading.
    """
    if as_reel:
        return upload_reel(video_path, description=description, title=title)
    return upload_regular_video(video_path, title=title, description=description)
