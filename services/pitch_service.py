"""Utility helpers for pitch shifting generated audio outputs.

This module relies on ffmpeg-compatible binaries being available on the host
system and uses pydub for audio manipulation.
"""

from __future__ import annotations

import os

import subprocess

from pydub import AudioSegment
from pydub.utils import which


def _configure_ffmpeg_paths() -> str | None:
    """Ensure pydub points to ffmpeg/ffprobe if they are available."""
    ffmpeg_path = os.getenv("FFMPEG_BINARY") or which("ffmpeg")
    ffprobe_path = os.getenv("FFPROBE_BINARY") or which("ffprobe")

    if ffmpeg_path:
        AudioSegment.converter = ffmpeg_path
        AudioSegment.ffmpeg = ffmpeg_path

    if ffprobe_path:
        AudioSegment.ffprobe = ffprobe_path

    return ffmpeg_path


# Configure once on import using whatever paths are currently available.
_configure_ffmpeg_paths()


def apply_pitch(audio_file_path: str, pitch_change: int) -> str:
    """Apply a semitone-based pitch shift to an audio file.

    Args:
        audio_file_path: Path to the audio file that should be pitch shifted.
        pitch_change: Semitone difference to apply (-8 to +8 expected).

    Returns:
        Path to the newly exported, pitch-adjusted audio file. If the requested
        pitch change is zero, the original path is returned unchanged.
    """
    ffmpeg_path = _configure_ffmpeg_paths()
    if not ffmpeg_path:
        raise RuntimeError(
            "FFmpeg binary not found. Set the FFMPEG_BINARY environment variable to the full path of ffmpeg.exe."
        )

    if not isinstance(pitch_change, int):
        raise ValueError("pitch_change must be an integer value representing semitones.")

    if pitch_change == 0:
        return audio_file_path

    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

    # Determine output path within the same directory, preserving extension.
    base_dir = os.path.dirname(audio_file_path)
    base_name, extension = os.path.splitext(os.path.basename(audio_file_path))
    extension = extension or ".mp3"
    output_name = f"{base_name}_pitch_{pitch_change}{extension}"
    output_path = os.path.join(base_dir, output_name)

    pitch_ratio = 2 ** (pitch_change / 12.0)
    cmd = [
        ffmpeg_path,
        "-y",
        "-i",
        audio_file_path,
        "-af",
        f"rubberband=pitch={pitch_ratio:.8f}",
        output_path,
    ]

    subprocess.run(cmd, check=True)

    return output_path


