import os
import sys
import argparse
import subprocess
from pathlib import Path
import logging
import shutil
import time

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.StreamHandler(),
                        logging.FileHandler('batch_process_hybrid.log')
                    ])
logger = logging.getLogger(__name__)

def process_dataset(input_dir, output_dir, funny_threshold=0.4, unfunny_threshold=0.5):
    """Process all clips in the dataset with different thresholds for funny/unfunny clips.
    
    Args:
        input_dir: Path to the input dataset directory
        output_dir: Path to the output directory
        funny_threshold: Threshold for laughter detection in funny clips
        unfunny_threshold: Threshold for laughter detection in unfunny clips
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Process funny clips
    funny_audio_dir = os.path.join(input_dir, "funny_audio_mp3")
    funny_text_dir = os.path.join(input_dir, "funny_text")
    
    # Process unfunny clips
    unfunny_audio_dir = os.path.join(input_dir, "unfunny_audio_mp3")
    unfunny_text_dir = os.path.join(input_dir, "unfunny_text")
    
    # Verify directories exist
    for dir_path in [funny_audio_dir, funny_text_dir, unfunny_audio_dir, unfunny_text_dir]:
        if not os.path.exists(dir_path):
            logger.error(f"Directory not found: {dir_path}")
            return False
    
    # Process funny clips
    logger.info(f"Processing funny clips with threshold: {funny_threshold}")
    process_directory(funny_audio_dir, funny_text_dir, output_dir, "funny", funny_threshold)
    
    # Process unfunny clips
    logger.info(f"Processing unfunny clips with threshold: {unfunny_threshold}")
    process_directory(unfunny_audio_dir, unfunny_text_dir, output_dir, "unfunny", unfunny_threshold)
    
    logger.info("All clips processed!")
    return True

def process_directory(audio_dir, text_dir, output_dir, category, threshold):
    """Process all clips in a directory.
    
    Args:
        audio_dir: Path to audio files directory
        text_dir: Path to text files directory
        output_dir: Path to output directory
        category: "funny" or "unfunny"
        threshold: Laughter detection threshold
    """
    # Convert all MP3s to WAVs first to check for any conversion issues
    temp_dir = os.path.join("temp", category)
    os.makedirs(temp_dir, exist_ok=True)
    
    # Get all MP3 files
    mp3_files = [f for f in os.listdir(audio_dir) if f.endswith(".mp3")]
    logger.info(f"Found {len(mp3_files)} {category} MP3 files")
    
    success_count = 0
    error_count = 0
    
    for mp3_file in mp3_files:
        clip_id = mp3_file.replace(".mp3", "")
        full_clip_id = f"{category}_{clip_id}"
        
        # Define paths
        mp3_path = os.path.join(audio_dir, mp3_file)
        wav_path = os.path.join(temp_dir, clip_id + ".wav")
        
        # Handle different naming patterns for funny and unfunny clips
        if category == "funny":
            # Funny clips have text files with "_text_" in the name instead of "_audio_"
            base_id = clip_id.replace("_audio_", "_text_")
            txt_path = os.path.join(text_dir, f"{base_id}.txt")
        else:
            # Unfunny clips have the same name for audio and text
            txt_path = os.path.join(text_dir, clip_id + ".txt")
        
        # Check if text file exists
        if not os.path.exists(txt_path):
            logger.warning(f"Text file not found for {clip_id}, skipping")
            continue
            
        # Read transcript
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                transcript = f.read().strip()
        except Exception as e:
            logger.error(f"Error reading transcript for {clip_id}: {e}")
            error_count += 1
            continue
            
        # Skip if output already exists
        output_clip_dir = os.path.join(output_dir, f"clip_{full_clip_id}")
        if os.path.exists(output_clip_dir) and os.path.exists(os.path.join(output_clip_dir, "score.npy")):
            logger.info(f"Output already exists for {full_clip_id}, skipping")
            success_count += 1
            continue
            
        # Convert MP3 to WAV
        try:
            logger.info(f"Converting {mp3_path} to WAV")
            convert_mp3_to_wav(mp3_path, wav_path)
        except Exception as e:
            logger.error(f"Error converting {clip_id} to WAV: {e}")
            error_count += 1
            continue
            
        # Process clip
        try:
            logger.info(f"Processing {full_clip_id} with threshold {threshold}")
            cmd = [
                sys.executable,
                "process_clip.py",
                "--audio", wav_path,
                "--transcript", transcript,
                "--id", full_clip_id,
                "--output_dir", output_dir,
                "--threshold", str(threshold)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Error processing {full_clip_id}: {result.stderr}")
                error_count += 1
            else:
                logger.info(f"Successfully processed {full_clip_id}")
                success_count += 1
        except Exception as e:
            logger.error(f"Error processing {full_clip_id}: {e}")
            error_count += 1
    
    logger.info(f"Processed {success_count} {category} clips successfully, {error_count} errors")

def convert_mp3_to_wav(mp3_path, wav_path):
    """Convert MP3 to WAV using ffmpeg"""
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
    except subprocess.CalledProcessError as e:
        logger.error(f"Error during conversion: {e}")
        logger.error(f"ffmpeg stderr: {e.stderr.decode()}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description='Process comedy dataset with hybrid thresholds')
    parser.add_argument('--input_dir', type=str, default='AI_open_mic_dataset', 
                       help='Input dataset directory')
    parser.add_argument('--output_dir', type=str, default='hybrid_output', 
                       help='Output directory for processed clips')
    parser.add_argument('--funny_threshold', type=float, default=0.4,
                       help='Threshold for laughter detection in funny clips (default: 0.4)')
    parser.add_argument('--unfunny_threshold', type=float, default=0.5,
                       help='Threshold for laughter detection in unfunny clips (default: 0.5)')
    
    args = parser.parse_args()
    
    # Record start time
    start_time = time.time()
    
    # Process the dataset
    process_dataset(
        args.input_dir, 
        args.output_dir,
        args.funny_threshold,
        args.unfunny_threshold
    )
    
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    logger.info(f"Processing complete! Total time: {elapsed_time/60:.2f} minutes")

if __name__ == "__main__":
    main() 