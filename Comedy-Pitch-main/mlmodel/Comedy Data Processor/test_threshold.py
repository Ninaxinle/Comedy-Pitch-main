import os
import subprocess
import sys
import shutil
from pathlib import Path

# Define clip IDs to test
clip_ids = ["TEDCC01", "TedCov01"]

def convert_mp3_to_wav(mp3_path, wav_path):
    """Convert MP3 to WAV using ffmpeg"""
    print(f"Converting {mp3_path} to {wav_path}...")
    
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
        print("ffmpeg not found in common locations. Assuming ffmpeg is in PATH.")
        ffmpeg_path = "ffmpeg"
    
    try:
        subprocess.run([
            ffmpeg_path,
            '-i', mp3_path,
            '-acodec', 'pcm_s16le',
            '-ar', '44100',
            '-ac', '2',
            '-y',  # Overwrite existing file
            wav_path
        ], check=True, capture_output=True)
        print("Conversion complete!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")
        print(f"ffmpeg stderr: {e.stderr.decode()}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def process_clip(clip_id):
    """Process a clip using the adjusted threshold"""
    print(f"\nProcessing clip: {clip_id}")
    
    # Define paths
    mp3_path = os.path.join("AI_open_mic_dataset", "unfunny_audio_mp3", f"{clip_id}.mp3")
    wav_path = os.path.join("temp", f"{clip_id}.wav")
    text_path = os.path.join("AI_open_mic_dataset", "unfunny_text", f"{clip_id}.txt")
    output_dir = os.path.join("test_output_0.5")
    
    # Create output directory if it doesn't exist
    os.makedirs("temp", exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # Read transcript
    with open(text_path, "r", encoding="utf-8") as f:
        transcript = f.read().strip()
    
    print(f"Read transcript ({len(transcript)} chars)")
    
    # Convert MP3 to WAV
    if not convert_mp3_to_wav(mp3_path, wav_path):
        print(f"Failed to convert {clip_id}")
        return False
    
    # Call process_clip.py
    cmd = [
        sys.executable,
        "process_clip.py",
        "--audio", wav_path,
        "--transcript", transcript,
        "--id", f"unfunny_{clip_id}",
        "--output_dir", output_dir
    ]
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error processing clip: {result.stderr}")
            return False
        
        print(f"Stdout: {result.stdout}")
        
        # Read and display the score
        import numpy as np
        score_path = os.path.join(output_dir, f"clip_unfunny_{clip_id}", "score.npy")
        if os.path.exists(score_path):
            score = np.load(score_path)
            score_value = np.argmax(score)
            print(f"Score: {score_value}/4 - One-hot: {score}")
        else:
            print(f"Score file not found at {score_path}")
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Process all test clips"""
    successful = 0
    
    for clip_id in clip_ids:
        if process_clip(clip_id):
            successful += 1
    
    print(f"\nProcessed {successful}/{len(clip_ids)} clips successfully")

if __name__ == "__main__":
    main() 