
import os
import shutil
import utility

def convert_to_wav(
    input_path,
    output_path,
    ffmpeg_binary="ffmpeg",
    sample_rate=16000,
    mono_channel=True
):
    """
    Convert an audio file to WAV format using ffmpeg.

    Args:
        input_path: Path to the input audio file
        output_path: Path where the converted WAV file should be saved
        ffmpeg_binary: Name or full path to the ffmpeg binary
        sample_rate: Sample rate to convert to (default: 16000)
        mono_channel: If True, convert to mono (1 channel). If False, preserve channels.
    """

    if not os.path.exists(input_path):
        return False, f"Input file does not exist: {input_path}"

    ffmpeg_path = shutil.which(ffmpeg_binary)
    if not ffmpeg_path:
        return False, "ffmpeg binary not found in PATH"

    ffmpeg_cmd = [
        ffmpeg_path,
        "-y",                      # Overwrite without asking
        "-i", input_path,          # Input file
        "-ar", f"{sample_rate}",   # Audio sample rate
    ]

    if mono_channel:
        ffmpeg_cmd.extend(["-ac", "1"])

    ffmpeg_cmd.append(output_path)

    status, output = utility.runProcessBlocking(ffmpeg_cmd)
    if not status:
        return False, output

    return True, output.strip()
