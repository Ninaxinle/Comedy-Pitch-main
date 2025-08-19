#!/usr/bin/env python3
"""
Example script demonstrating how to use the BatchLaughterProcessor.

This script shows how to process a folder of audio files with their corresponding JSON files.
"""

import os
import json
from pathlib import Path
from batch_laughter_processor import BatchLaughterProcessor

def create_sample_data():
    """
    Create sample data for testing the batch processor.
    """
    # Create a sample folder structure
    sample_folder = Path("sample_data")
    sample_folder.mkdir(exist_ok=True)
    
    # Sample audio file (you would replace this with actual audio)
    audio_file = sample_folder / "sample_audio.mp3"
    if not audio_file.exists():
        # Create a dummy file for demonstration
        audio_file.write_text("This is a dummy audio file for testing")
    
    # Sample segments data
    segments_data = [
        {
            "index": 0,
            "text": "What is up, New York?",
            "start_time": 33.376,
            "end_time": 39.704,
            "gap_to_next": 0.02
        },
        {
            "index": 1,
            "text": "Y'all look good, and I am so happy to be here.",
            "start_time": 39.724,
            "end_time": 42.288,
            "gap_to_next": 0.04
        },
        {
            "index": 2,
            "text": "So glad to be here.",
            "start_time": 42.328,
            "end_time": 43.269,
            "gap_to_next": 0.04
        }
    ]
    
    # Sample sentences data (full transcript)
    sentences_data = [
        {
            "index": 0,
            "text": "What is up, New York?",
            "start_time": 33.376,
            "end_time": 39.704,
            "gap_to_next": 0.02
        },
        {
            "index": 1,
            "text": "Y'all look good, and I am so happy to be here.",
            "start_time": 39.724,
            "end_time": 42.288,
            "gap_to_next": 0.04
        },
        {
            "index": 2,
            "text": "So glad to be here.",
            "start_time": 42.328,
            "end_time": 43.269,
            "gap_to_next": 0.04
        },
        {
            "index": 3,
            "text": "I'm so excited to be performing for you tonight.",
            "start_time": 43.309,
            "end_time": 46.892,
            "gap_to_next": 0.03
        },
        {
            "index": 4,
            "text": "This is going to be a great show!",
            "start_time": 46.922,
            "end_time": 49.156,
            "gap_to_next": 0.05
        }
    ]
    
    # Save JSON files
    segments_file = sample_folder / "sample_audio_segments.json"
    with open(segments_file, 'w', encoding='utf-8') as f:
        json.dump(segments_data, f, indent=2)
    
    sentences_file = sample_folder / "sample_audio_sentences.json"
    with open(sentences_file, 'w', encoding='utf-8') as f:
        json.dump(sentences_data, f, indent=2)
    
    print(f"Sample data created in: {sample_folder}")
    print(f"Files created:")
    print(f"  - {audio_file}")
    print(f"  - {segments_file}")
    print(f"  - {sentences_file}")
    
    return sample_folder

def example_usage():
    """
    Example of how to use the BatchLaughterProcessor.
    """
    print("=== Batch Laughter Detection Example ===\n")
    
    # Check if OpenAI API key is set
    try:
        from config_local import OPENAI_API_KEY
        if not OPENAI_API_KEY or OPENAI_API_KEY == "sk-your-actual-openai-api-key-here":
            print("Error: Please set your OpenAI API key in config_local.py")
            print("Open config_local.py and replace 'sk-your-actual-openai-api-key-here' with your actual API key")
            return
    except ImportError:
        print("Error: Please create config_local.py with your OpenAI API key")
        print("Copy config.py to config_local.py and add your API key")
        return
    
    # Create sample data
    sample_folder = create_sample_data()
    
    # Example 1: Process a folder with default settings
    print("\n--- Example 1: Basic Batch Processing ---")
    print(f"Processing folder: {sample_folder}")
    
    try:
        processor = BatchLaughterProcessor(input_folder=str(sample_folder))
        processor.process_all_files()
        print("✓ Batch processing completed successfully!")
        
    except Exception as e:
        print(f"✗ Batch processing failed: {e}")
        print("Note: This is expected if you don't have actual audio files or API credits")
    
    # Example 2: Process with custom output folder
    print("\n--- Example 2: Custom Output Folder ---")
    custom_output = Path("custom_results")
    
    try:
        processor = BatchLaughterProcessor(
            input_folder=str(sample_folder),
            output_folder=str(custom_output)
        )
        processor.process_all_files()
        print(f"✓ Results saved to: {custom_output}")
        
    except Exception as e:
        print(f"✗ Custom output processing failed: {e}")
    
    # Example 3: Process specific files manually
    print("\n--- Example 3: Manual File Processing ---")
    
    try:
        processor = BatchLaughterProcessor(input_folder=str(sample_folder))
        
        # Find audio files
        audio_files = processor.find_audio_files()
        print(f"Found {len(audio_files)} audio files")
        
        for audio_file in audio_files:
            print(f"\nProcessing: {audio_file.name}")
            
            # Find corresponding JSON files
            segments_file, sentences_file = processor.find_json_files(audio_file)
            print(f"  Segments file: {segments_file}")
            print(f"  Sentences file: {sentences_file}")
            
            if segments_file and sentences_file:
                # Load JSON files
                segments_data = processor.load_json_file(segments_file)
                full_transcript = processor.load_json_file(sentences_file)
                
                print(f"  Loaded {len(segments_data)} segments")
                print(f"  Loaded {len(full_transcript)} sentences")
                
                # Process each segment
                for segment in segments_data:
                    start_time = segment.get('start_time', 0)
                    end_time = segment.get('end_time', 0)
                    text = segment.get('text', '')[:50] + "..." if len(segment.get('text', '')) > 50 else segment.get('text', '')
                    print(f"    Segment {segment.get('index', '?')}: {start_time:.2f}s - {end_time:.2f}s | {text}")
        
        print("\n✓ Manual processing demonstration completed!")
        
    except Exception as e:
        print(f"✗ Manual processing failed: {e}")

def main():
    """
    Main function to run the example.
    """
    print("Batch Laughter Detection Processor - Example Usage")
    print("=" * 50)
    
    example_usage()
    
    print("\n" + "=" * 50)
    print("Example completed!")
    print("\nTo use with your own data:")
    print("1. Place your audio files in a folder")
    print("2. Ensure each audio file has corresponding _segments.json and _sentences.json files")
    print("3. Run: python batch_laughter_processor.py /path/to/your/folder")
    print("4. Check the results folder for CSV output files")

if __name__ == "__main__":
    main() 