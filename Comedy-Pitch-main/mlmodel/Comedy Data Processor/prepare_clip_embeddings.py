#!/usr/bin/env python3
"""
Clip preprocessing script for comedy audio analysis.

This script prepares audio and transcript for model inference:
1. Converts the audio to WAV format if needed
2. Detects and mutes laughter segments
3. Extracts audio features from the muted audio
4. Generates BERT embeddings from the transcript
5. Verifies files are in the correct format for AI-OpenMic

This uses the same ClipProcessor as the training pipeline for consistency.
"""

import os
import sys
import argparse
import logging
import pickle
import numpy as np
from pathlib import Path
import shutil

# Import the ClipProcessor used for training
from process_clip import ClipProcessor

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_for_inference(audio_path, transcript_path, output_dir, clip_id=None, laughter_threshold=0.5):
    """
    Process a comedy audio clip and prepare embeddings for inference.
    
    Args:
        audio_path: Path to the audio file
        transcript_path: Path to the transcript file
        output_dir: Output directory
        clip_id: Optional custom ID
        laughter_threshold: Threshold for laughter detection
        
    Returns:
        str: Path to the processed clip directory
    """
    # Read the transcript from file
    with open(transcript_path, 'r', encoding='utf-8') as f:
        transcript = f.read().strip()
    
    logger.info(f"Processing audio: {audio_path}")
    logger.info(f"Transcript: {transcript[:100]}..." if len(transcript) > 100 else f"Transcript: {transcript}")
    
    # Generate clip ID if not provided
    if not clip_id:
        clip_id = Path(audio_path).stem
    
    # Initialize processor
    processor = ClipProcessor(output_dir, laughter_threshold)
    
    # Process the audio to generate embeddings
    success = processor.process_clip(
        audio_path=audio_path,
        transcript=transcript,
        clip_id=clip_id
    )
    
    if not success:
        logger.error("Failed to process audio")
        return None
    
    # Get the clip directory
    clip_dir = Path(output_dir) / f"clip_{clip_id}"
    
    # Delete score.npy file since it's not needed for inference
    score_path = clip_dir / "score.npy"
    if score_path.exists():
        score_path.unlink()
        logger.info(f"Removed score file: {score_path}")
    
    # Validate the output files
    validate_files(clip_dir)
    
    return str(clip_dir)

def validate_files(clip_dir):
    """
    Validate that all required files for AI-OpenMic are present.
    
    Args:
        clip_dir: Path to the clip directory
    """
    # Check audio embedding
    audio_embed_path = clip_dir / "audioembed.npy"
    if audio_embed_path.exists():
        audio_embedding = np.load(audio_embed_path)
        logger.info(f"Validated audio embedding with shape: {audio_embedding.shape}")
    else:
        logger.warning(f"Missing audio embedding file: {audio_embed_path}")
    
    # Check BERT embedding
    bert_embed_path = clip_dir / "BertBase.pkl"
    if bert_embed_path.exists():
        with open(bert_embed_path, 'rb') as f:
            text_embedding = pickle.load(f)
        logger.info(f"Validated text embedding with shape: {text_embedding.shape}")
    else:
        logger.warning(f"Missing text embedding file: {bert_embed_path}")
    
    # Check muted audio
    muted_audio_path = clip_dir / "muted_audio.wav"
    if muted_audio_path.exists():
        logger.info(f"Validated muted audio file: {muted_audio_path}")
    else:
        logger.warning(f"Missing muted audio file: {muted_audio_path}")

def main():
    parser = argparse.ArgumentParser(description='Process and prepare clip files for AI-OpenMic')
    parser.add_argument('--audio', type=str, required=True,
                       help='Path to the audio file')
    parser.add_argument('--transcript', type=str, required=True,
                       help='Path to the transcript file')
    parser.add_argument('--output_dir', type=str, default='inference_output',
                       help='Output directory for processed files')
    parser.add_argument('--id', type=str, default=None,
                       help='Custom ID for the clip (defaults to filename)')
    parser.add_argument('--threshold', type=float, default=0.5,
                       help='Threshold for laughter detection (default: 0.5)')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Process audio and get clip directory
    clip_dir = process_for_inference(
        audio_path=args.audio,
        transcript_path=args.transcript,
        output_dir=args.output_dir,
        clip_id=args.id,
        laughter_threshold=args.threshold
    )
    
    if clip_dir:
        logger.info(f"Successfully processed clip in: {clip_dir}")
        logger.info(f"Files are ready for AI-OpenMic in the format:")
        logger.info(f"  - audioembed.npy")
        logger.info(f"  - BertBase.pkl")
        logger.info(f"  - muted_audio.wav")
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main()) 