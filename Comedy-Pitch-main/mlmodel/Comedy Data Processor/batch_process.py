import os
import argparse
import logging
import csv
import sys
from pathlib import Path
import librosa
import soundfile as sf
import traceback
from process_clip import ClipProcessor

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def convert_mp3_to_wav(mp3_path: str, wav_path: str) -> None:
    """Convert MP3 file to WAV format."""
    logger.info(f"Converting {mp3_path} to WAV format...")
    y, sr = librosa.load(mp3_path, sr=None)
    sf.write(wav_path, y, sr)
    logger.info(f"Conversion complete: {wav_path}")

def process_clip(processor, audio_path, transcript, clip_id, output_dir):
    """Process a single clip and handle errors."""
    try:
        wav_path = audio_path
        
        # Clean clip_id (remove spaces and special characters)
        clean_clip_id = clip_id.strip().replace(' ', '_')
        
        # Convert to WAV if it's an MP3 file
        if audio_path.lower().endswith('.mp3'):
            wav_dir = Path(output_dir) / f"clip_{clean_clip_id}"
            wav_dir.mkdir(parents=True, exist_ok=True)
            wav_path = wav_dir / "original_audio.wav"
            convert_mp3_to_wav(audio_path, str(wav_path))
        
        # Process the clip using the cleaned clip_id
        success = processor.process_clip(
            audio_path=str(wav_path),
            transcript=transcript,
            clip_id=clean_clip_id
        )
        
        return success
    except Exception as e:
        logger.error(f"Error processing clip {clip_id}: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Batch process comedy clips')
    parser.add_argument('--input_csv', type=str, required=True, 
                       help='CSV file with columns: audio_path,transcript,clip_id')
    parser.add_argument('--output_dir', type=str, default='output',
                       help='Output directory for processed clips')
    
    args = parser.parse_args()
    
    # Initialize processor
    processor = ClipProcessor(args.output_dir)
    
    # Check if input CSV exists
    if not os.path.exists(args.input_csv):
        logger.error(f"Input CSV file not found: {args.input_csv}")
        return 1
    
    # Process clips from CSV
    successful_clips = 0
    failed_clips = 0
    
    try:
        with open(args.input_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Count total clips
            f.seek(0)
            total_clips = sum(1 for row in reader) - 1  # Subtract 1 for header
            
            # Reset file pointer
            f.seek(0)
            next(reader)  # Skip header
            
            for i, row in enumerate(reader):
                try:
                    audio_path = row.get('audio_path')
                    transcript = row.get('transcript')
                    clip_id = row.get('clip_id')
                    
                    if not all([audio_path, clip_id]):
                        logger.error(f"Missing required fields in row {i+1}")
                        failed_clips += 1
                        continue
                    
                    logger.info(f"Processing clip {i+1}/{total_clips}: {clip_id}")
                    
                    # Set default transcript if none provided
                    if not transcript:
                        transcript = f"Transcript for clip {clip_id}"
                        logger.warning(f"No transcript provided for clip {clip_id}. Using placeholder.")
                    
                    # Process the clip
                    success = process_clip(
                        processor=processor,
                        audio_path=audio_path,
                        transcript=transcript,
                        clip_id=clip_id,
                        output_dir=args.output_dir
                    )
                    
                    if success:
                        successful_clips += 1
                        logger.info(f"Successfully processed clip {clip_id}")
                    else:
                        failed_clips += 1
                        logger.error(f"Failed to process clip {clip_id}")
                    
                except Exception as e:
                    failed_clips += 1
                    logger.error(f"Error in row {i+1}: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing CSV file: {str(e)}")
        logger.error(traceback.format_exc())
        return 1
    
    # Summary
    logger.info(f"Batch processing complete. Successful: {successful_clips}, Failed: {failed_clips}")
    return 0 if failed_clips == 0 else 1

if __name__ == "__main__":
    sys.exit(main()) 