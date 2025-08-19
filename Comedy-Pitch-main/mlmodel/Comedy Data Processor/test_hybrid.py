import os
import sys
import subprocess
import argparse
from pathlib import Path
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test clips to process
FUNNY_CLIPS = ["TT_QLC_audio_01"]
UNFUNNY_CLIPS = ["TEDCC01", "TedCov01"]

def convert_mp3_to_wav(mp3_path, wav_path):
    """Convert MP3 to WAV using ffmpeg"""
    logger.info(f"Converting {mp3_path} to {wav_path}")
    
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
        logger.warning("ffmpeg not found in common locations. Assuming ffmpeg is in PATH.")
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
        return True
    except Exception as e:
        logger.error(f"Error during conversion: {str(e)}")
        return False

def process_clip(clip_id, category, threshold, input_dir, output_dir):
    """Process a single clip with the specified threshold."""
    logger.info(f"Processing {category} clip {clip_id} with threshold {threshold}")
    
    # Define paths
    audio_dir = os.path.join(input_dir, f"{category}_audio_mp3")
    text_dir = os.path.join(input_dir, f"{category}_text")
    mp3_path = os.path.join(audio_dir, f"{clip_id}.mp3")
    
    # Handle different naming patterns for funny and unfunny clips
    if category == "funny":
        # Funny clips have text files with "_text_" in the name instead of "_audio_"
        base_id = clip_id.replace("_audio_", "_text_")
        txt_path = os.path.join(text_dir, f"{base_id}.txt")
    else:
        # Unfunny clips have the same name for audio and text
        txt_path = os.path.join(text_dir, f"{clip_id}.txt")
    
    wav_path = os.path.join("temp", f"{clip_id}.wav")
    
    # Create temp directory
    os.makedirs("temp", exist_ok=True)
    
    # Verify files exist
    if not os.path.exists(mp3_path):
        logger.error(f"MP3 file not found: {mp3_path}")
        return False
        
    if not os.path.exists(txt_path):
        logger.error(f"Text file not found: {txt_path}")
        return False
    
    # Read transcript
    with open(txt_path, "r", encoding="utf-8") as f:
        transcript = f.read().strip()
    
    logger.info(f"Read transcript: {len(transcript)} chars")
    
    # Convert to WAV
    if not convert_mp3_to_wav(mp3_path, wav_path):
        logger.error(f"Failed to convert {clip_id} to WAV")
        return False
    
    # Process clip
    full_id = f"{category}_{clip_id}"
    cmd = [
        sys.executable,
        "process_clip.py",
        "--audio", wav_path,
        "--transcript", transcript,
        "--id", full_id,
        "--output_dir", output_dir,
        "--threshold", str(threshold)
    ]
    
    logger.info(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Error processing clip: {result.stderr}")
            return False
            
        # Check the score
        import numpy as np
        score_path = os.path.join(output_dir, f"clip_{full_id}", "score.npy")
        if os.path.exists(score_path):
            score = np.load(score_path)
            score_value = np.argmax(score)
            logger.info(f"Score for {full_id}: {score_value}/4 - One-hot: {score}")
        else:
            logger.error(f"Score file not found for {full_id}")
            
        return True
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Test hybrid threshold approach')
    parser.add_argument('--input_dir', type=str, default='AI_open_mic_dataset', 
                       help='Input dataset directory')
    parser.add_argument('--output_dir', type=str, default='hybrid_test_output', 
                       help='Output directory')
    parser.add_argument('--funny_threshold', type=float, default=0.3,
                       help='Threshold for funny clips')
    parser.add_argument('--unfunny_threshold', type=float, default=0.5,
                       help='Threshold for unfunny clips')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Process funny clips
    logger.info("=== Processing funny clips ===")
    funny_success = 0
    for clip_id in FUNNY_CLIPS:
        if process_clip(clip_id, "funny", args.funny_threshold, args.input_dir, args.output_dir):
            funny_success += 1
    
    # Process unfunny clips
    logger.info("=== Processing unfunny clips ===")
    unfunny_success = 0
    for clip_id in UNFUNNY_CLIPS:
        if process_clip(clip_id, "unfunny", args.unfunny_threshold, args.input_dir, args.output_dir):
            unfunny_success += 1
    
    # Summary
    logger.info(f"Successfully processed {funny_success}/{len(FUNNY_CLIPS)} funny clips")
    logger.info(f"Successfully processed {unfunny_success}/{len(UNFUNNY_CLIPS)} unfunny clips")

if __name__ == "__main__":
    main() 