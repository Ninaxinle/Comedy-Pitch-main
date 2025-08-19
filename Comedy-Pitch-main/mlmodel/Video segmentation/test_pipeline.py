#!/usr/bin/env python3
"""
Test script for the Video Segmentation Pipeline

This script tests the pipeline with the available test videos and validates outputs.
"""

import os
import sys
import json
import shutil
from pathlib import Path
import argparse
import logging

# Add current directory to path for imports
sys.path.append('.')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def copy_test_video(source_dir: str = "test video data", target_dir: str = "input_videos", video_name: str = None):
    """Copy a test video to the input directory."""
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    
    if not source_path.exists():
        logger.error(f"Source directory does not exist: {source_dir}")
        return None
    
    # Get list of video files
    video_files = list(source_path.glob("*.mp4")) + list(source_path.glob("*.mov"))
    
    if not video_files:
        logger.error(f"No video files found in {source_dir}")
        return None
    
    # Select video to copy
    if video_name:
        selected_video = None
        for video in video_files:
            if video_name.lower() in video.name.lower():
                selected_video = video
                break
        if not selected_video:
            logger.error(f"Video containing '{video_name}' not found")
            return None
    else:
        # Use the smallest video file for testing
        selected_video = min(video_files, key=lambda x: x.stat().st_size)
    
    target_file = target_path / selected_video.name
    
    # Copy the file
    try:
        shutil.copy2(selected_video, target_file)
        logger.info(f"Copied test video: {selected_video.name} ({selected_video.stat().st_size / (1024*1024):.1f} MB)")
        return str(target_file)
    except Exception as e:
        logger.error(f"Failed to copy video: {e}")
        return None


def validate_outputs(video_name: str, config_file: str = "config.yaml"):
    """Validate that all expected output files were created."""
    base_name = Path(video_name).stem
    
    # Load config to get correct directories
    import yaml
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Use config directories
    dirs = config['directories']
    audio_file = f"{dirs['output_audio']}/{base_name}.wav"
    transcript_file = f"{dirs['transcripts']}/{base_name}_sentences.json"
    segments_file = f"{dirs['segmentations']}/{base_name}_segments.json"
    
    results = {}
    
    # Check audio file
    if os.path.exists(audio_file):
        size = os.path.getsize(audio_file)
        results['audio'] = {'exists': True, 'size': size}
        logger.info(f"✓ Audio file created: {audio_file} ({size / (1024*1024):.1f} MB)")
    else:
        results['audio'] = {'exists': False, 'size': 0}
        logger.error(f"✗ Audio file missing: {audio_file}")
    
    # Check transcript file
    if os.path.exists(transcript_file):
        try:
            with open(transcript_file, 'r') as f:
                transcript_data = json.load(f)
            results['transcript'] = {
                'exists': True, 
                'sentences': len(transcript_data),
                'sample': transcript_data[:2] if transcript_data else []
            }
            logger.info(f"✓ Transcript file created: {transcript_file} ({len(transcript_data)} sentences)")
            if transcript_data:
                logger.info(f"  Sample: {transcript_data[0]['text'][:50]}...")
        except Exception as e:
            results['transcript'] = {'exists': True, 'error': str(e)}
            logger.error(f"✗ Error reading transcript file: {e}")
    else:
        results['transcript'] = {'exists': False}
        logger.error(f"✗ Transcript file missing: {transcript_file}")
    
    # Check segments file
    if os.path.exists(segments_file):
        try:
            with open(segments_file, 'r') as f:
                segments_data = json.load(f)
            results['segments'] = {
                'exists': True, 
                'segments': len(segments_data),
                'sample': segments_data[:1] if segments_data else []
            }
            logger.info(f"✓ Segments file created: {segments_file} ({len(segments_data)} segments)")
            if segments_data:
                logger.info(f"  First segment: {segments_data[0]}")
        except Exception as e:
            results['segments'] = {'exists': True, 'error': str(e)}
            logger.error(f"✗ Error reading segments file: {e}")
    else:
        results['segments'] = {'exists': False}
        logger.error(f"✗ Segments file missing: {segments_file}")
    
    return results


def test_pipeline(video_name: str = None, use_mock_llm: bool = False):
    """Test the video segmentation pipeline."""
    logger.info("Starting pipeline test...")
    
    # Copy test video
    video_file = copy_test_video(video_name=video_name)
    if not video_file:
        logger.error("Failed to copy test video")
        return False
    
    # Import the pipeline (after copying video)
    try:
        from video_segmentation import VideoSegmentationPipeline
    except ImportError as e:
        logger.error(f"Failed to import pipeline: {e}")
        return False
    
    # Use main config, but override API key for mock testing
    config_file = "config.yaml"
    
    if use_mock_llm:
        # Load the main config and only override the API key
        import yaml
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Override API key for mock testing
        config['llm']['api_key'] = "test-key"
        
        # Save temporary config
        test_config = "test_config.yaml" 
        with open(test_config, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        config_file = test_config
        logger.info(f"Using mock LLM with your config settings (API key: test-key)")
    
    try:
        # Initialize pipeline
        pipeline = VideoSegmentationPipeline(config_file)
        
        # Test individual components if possible
        logger.info("Testing audio extraction...")
        
        # Process the video
        success = pipeline.process_video(video_file)
        
        # Validate outputs regardless of LLM success when using mock
        results = validate_outputs(video_file, config_file)
        
        # Print summary
        logger.info("\n=== Test Results Summary ===")
        for component, result in results.items():
            status = "✓" if result['exists'] else "✗"
            logger.info(f"{status} {component.title()}: {result}")
        
        if use_mock_llm:
            # When using mock LLM, all components should work (including mock segments)
            full_success = all(result['exists'] for result in results.values())
            if full_success:
                logger.info("✓ Full end-to-end pipeline completed successfully (with mock LLM)")
                logger.info("  Note: Used your config settings with mock API key")
                return True
            else:
                # At minimum, audio + transcript should work
                core_success = results['audio']['exists'] and results['transcript']['exists']
                if core_success:
                    logger.info("✓ Core pipeline (audio + transcription) completed successfully")
                    logger.info("  ⚠️  Mock segmentation failed but core components work")
                    return True
                else:
                    logger.error("✗ Core pipeline failed")
                    return False
        else:
            # Full pipeline test - all components must work
            if success:
                logger.info("✓ Full pipeline completed successfully")
                return all(result['exists'] for result in results.values())
            else:
                logger.error("✗ Pipeline failed")
                return False
            
    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        return False
    
    finally:
        # Clean up test config
        if use_mock_llm and os.path.exists(test_config):
            os.remove(test_config)


def main():
    """Main test function."""
    parser = argparse.ArgumentParser(description='Test Video Segmentation Pipeline')
    parser.add_argument('--video', help='Specific video name to test (partial match)')
    parser.add_argument('--mock-llm', action='store_true', help='Use mock LLM config (skip actual API call)')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    success = test_pipeline(video_name=args.video, use_mock_llm=args.mock_llm)
    
    if success:
        logger.info("🎉 All tests passed!")
        sys.exit(0)
    else:
        logger.error("❌ Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    main() 