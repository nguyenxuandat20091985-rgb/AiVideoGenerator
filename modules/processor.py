"""
Process video with FFmpeg:
- Cut 2 seconds from start and end
- Horizontal flip (hflip)
- Speed 1.03x
- Add text watermark
"""

import os
import subprocess
import tempfile
from pathlib import Path


def get_video_duration(input_path: str) -> float:
    """Return duration in seconds using ffprobe."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        input_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(result.stdout.strip())


def process_video_ffmpeg(
    input_path: str,
    output_dir: str | None = None,
    cut_start: float = 2.0,
    cut_end: float = 2.0,
    speed: float = 1.03,
    watermark_text: str = "YourBrand",
) -> str:
    """
    Process the video and return path to the new file.

    Pipeline:
    1. Trim first `cut_start` and last `cut_end` seconds
    2. Horizontal flip
    3. Change speed to `speed`
    4. Overlay watermark text (bottom-right)
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input video không tồn tại: {input_path}")

    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="fb_proc_")
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    duration = get_video_duration(input_path)
    if duration <= (cut_start + cut_end + 1):
        raise ValueError(
            f"Video quá ngắn ({duration:.1f}s). Cần dài hơn {cut_start + cut_end + 1} giây."
        )

    # Effective duration after cutting start/end
    trim_duration = duration - cut_start - cut_end

    # Output filename
    base = Path(input_path).stem
    output_path = os.path.join(output_dir, f"{base}_processed.mp4")

    # setpts for video speed, atempo for audio (atempo range 0.5–2.0)
    # For 1.03 we can use a single atempo
    video_filter = (
        f"trim=start={cut_start}:duration={trim_duration},"
        f"setpts=PTS-STARTPTS,"
        f"hflip,"
        f"setpts={1/speed}*PTS,"
        f"drawtext=text='{watermark_text}':"
        f"fontsize=24:fontcolor=white@0.7:"
        f"x=w-tw-20:y=h-th-20:"
        f"box=1:boxcolor=black@0.4:boxborderw=6"
    )

    audio_filter = f"atrim=start={cut_start}:duration={trim_duration},asetpts=PTS-STARTPTS,atempo={speed}"

    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-vf", video_filter,
        "-af", audio_filter,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
        output_path,
    ]

    print("[Processor] Đang xử lý FFmpeg...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError(f"FFmpeg thất bại (code {result.returncode})")

    if not os.path.isfile(output_path):
        raise FileNotFoundError("FFmpeg chạy xong nhưng không tạo được file output.")

    print(f"[Processor] Xử lý xong → {output_path}")
    return os.path.abspath(output_path)
