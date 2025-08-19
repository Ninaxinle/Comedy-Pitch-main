import os
from pydub import AudioSegment
import subprocess

mp3_path = r"C:\Users\train\Source\Repos\AI Standup Comedy Judge\AI_open_mic_dataset\funny_audio_mp3\AA_RN_audio_01.mp3"
wav_path = r"C:\Users\train\Source\Repos\AI Standup Comedy Judge\AI_open_mic_dataset\funny_audio_mp3\AA_RN_audio_01.wav"

# Try to find ffmpeg in common locations
ffmpeg_paths = [
    r"C:\ffmpeg\bin\ffmpeg.exe",
    r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
    r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
    os.path.expanduser("~\\ffmpeg\\bin\\ffmpeg.exe")
]

ffmpeg_path = None
for path in ffmpeg_paths:
    if os.path.exists(path):
        ffmpeg_path = path
        break

if ffmpeg_path is None:
    print("ffmpeg not found in common locations. Please make sure ffmpeg is installed and in your PATH.")
    print("You can download ffmpeg from: https://ffmpeg.org/download.html")
    exit(1)

print(f"Using ffmpeg from: {ffmpeg_path}")
print(f"Converting {mp3_path} to {wav_path}...")

# Use subprocess to call ffmpeg directly
try:
    subprocess.run([
        ffmpeg_path,
        '-i', mp3_path,
        '-acodec', 'pcm_s16le',
        '-ar', '44100',
        '-ac', '2',
        wav_path
    ], check=True)
    print("Conversion complete!")
except subprocess.CalledProcessError as e:
    print(f"Error during conversion: {e}")
except Exception as e:
    print(f"Unexpected error: {e}") 