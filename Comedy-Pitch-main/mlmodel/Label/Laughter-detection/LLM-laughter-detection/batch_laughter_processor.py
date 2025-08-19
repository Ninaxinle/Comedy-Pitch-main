#!/usr/bin/env python3
"""
Batch laughter detection processor.

This script processes a folder containing audio files and their corresponding JSON files:
- Audio files (mp3, wav, etc.)
- _segments.json files containing segment information
- _sentences.json files containing full transcripts

For each audio file, it processes each segment and outputs laughter detection results to CSV.
"""

import os
import json
import csv
import glob
from pathlib import Path
from typing import Dict, List, Optional
import logging
from datetime import datetime
from audio_laughter_detector import AudioLaughterDetector

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BatchLaughterProcessor:
    """
    Processes a folder of audio files for laughter detection.
    """
    
    def __init__(self, input_folder: str, output_folder: str = None, api_key: str = None):
        """
        Initialize the batch processor.
        
        Args:
            input_folder: Path to folder containing audio files and JSON files
            output_folder: Path to save output CSV files (defaults to input_folder/results)
            api_key: OpenAI API key (optional, will use config if not provided)
        """
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder) if output_folder else self.input_folder / "results"
        self.output_folder.mkdir(exist_ok=True)
        
        # Initialize the laughter detector
        try:
            self.detector = AudioLaughterDetector(api_key=api_key)
            logger.info("AudioLaughterDetector initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AudioLaughterDetector: {e}")
            raise
        
        # Supported audio formats
        self.audio_extensions = {'.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac'}
        
        # Results storage
        self.all_results = []
    
    def find_audio_files(self) -> List[Path]:
        """
        Find all audio files in the input folder.
        
        Returns:
            List of audio file paths
        """
        audio_files = set()  # Use set to avoid duplicates
        for ext in self.audio_extensions:
            # Check for both lowercase and uppercase extensions
            audio_files.update(self.input_folder.glob(f"*{ext}"))
            audio_files.update(self.input_folder.glob(f"*{ext.upper()}"))
        
        # Convert to sorted list
        audio_files_list = sorted(list(audio_files))
        logger.info(f"Found {len(audio_files_list)} audio files in {self.input_folder}")
        return audio_files_list
    
    def find_json_files(self, audio_file: Path) -> tuple[Optional[Path], Optional[Path]]:
        """
        Find corresponding JSON files for an audio file.
        
        Args:
            audio_file: Path to the audio file
            
        Returns:
            Tuple of (segments_file, sentences_file) paths
        """
        base_name = audio_file.stem  # filename without extension
        
        # Look for _segments.json file
        segments_file = self.input_folder / f"{base_name}_segments.json"
        if not segments_file.exists():
            logger.warning(f"Segments file not found: {segments_file}")
            segments_file = None
        
        # Look for _sentences.json file
        sentences_file = self.input_folder / f"{base_name}_sentences.json"
        if not sentences_file.exists():
            logger.warning(f"Sentences file not found: {sentences_file}")
            sentences_file = None
        
        return segments_file, sentences_file
    
    def load_json_file(self, file_path: Path) -> Dict:
        """
        Load and parse a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Parsed JSON data
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Loaded JSON file: {file_path}")
            return data
        except Exception as e:
            logger.error(f"Failed to load JSON file {file_path}: {e}")
            raise
    
    def process_segment(self, audio_file: Path, segment: Dict, full_transcript: Dict) -> Dict:
        """
        Process a single segment for laughter detection.
        
        Args:
            audio_file: Path to the audio file
            segment: Segment information with start/end times
            full_transcript: Full transcript data
            
        Returns:
            Laughter detection result for this segment
        """
        # Extract segment timing
        start_time = segment.get('start_time', segment.get('start', 0))
        end_time = segment.get('end_time', segment.get('end', 0))
        segment_text = segment.get('text', '')
        segment_index = segment.get('index', -1)
        
        logger.info(f"Processing segment {segment_index}: {start_time:.2f}s - {end_time:.2f}s")
        
        try:
            # Detect laughter in this segment
            result = self.detector.detect_laughter_in_chunk(
                audio_path=str(audio_file),
                transcript_json=full_transcript,
                start_time=start_time,
                end_time=end_time
            )
            
            # Add segment metadata to result
            result['segment_info'] = {
                'index': segment_index,
                'start_time': start_time,
                'end_time': end_time,
                'text': segment_text,
                'duration': end_time - start_time
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to process segment {segment_index}: {e}")
            return {
                'success': False,
                'error': str(e),
                'segment_info': {
                    'index': segment_index,
                    'start_time': start_time,
                    'end_time': end_time,
                    'text': segment_text,
                    'duration': end_time - start_time
                }
            }
    
    def process_audio_file(self, audio_file: Path) -> List[Dict]:
        """
        Process a single audio file and all its segments.
        
        Args:
            audio_file: Path to the audio file
            
        Returns:
            List of laughter detection results for all segments
        """
        logger.info(f"Processing audio file: {audio_file.name}")
        
        # Find corresponding JSON files
        segments_file, sentences_file = self.find_json_files(audio_file)
        
        if not segments_file:
            logger.error(f"No segments file found for {audio_file.name}")
            return []
        
        if not sentences_file:
            logger.error(f"No sentences file found for {audio_file.name}")
            return []
        
        # Load JSON files
        try:
            segments_data = self.load_json_file(segments_file)
            full_transcript = self.load_json_file(sentences_file)
        except Exception as e:
            logger.error(f"Failed to load JSON files for {audio_file.name}: {e}")
            return []
        
        # Process each segment
        results = []
        segments = segments_data if isinstance(segments_data, list) else segments_data.get('segments', [])
        
        logger.info(f"Processing {len(segments)} segments for {audio_file.name}")
        
        for segment in segments:
            result = self.process_segment(audio_file, segment, full_transcript)
            result['audio_file'] = audio_file.name
            result['segments_file'] = segments_file.name
            result['sentences_file'] = sentences_file.name
            results.append(result)
        
        return results
    
    def save_results_to_csv(self, results: List[Dict], filename: str = None):
        """
        Save laughter detection results to CSV file.
        
        Args:
            results: List of laughter detection results
            filename: Output CSV filename (optional)
        """
        if not results:
            logger.warning("No results to save")
            return
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"laughter_detection_results_{timestamp}.csv"
        
        csv_path = self.output_folder / filename
        
        # Define CSV headers for flattened laughter instances
        headers = [
            'SourceFile', 'SegmentID', 'StartTime', 'EndTime', 'Duration', 
            'Type', 'Intensity', 'Notes'
        ]
        
        try:
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                
                for result in results:
                    # Extract segment info
                    segment_info = result.get('segment_info', {})
                    source_file = result.get('audio_file', '')
                    segment_id = segment_info.get('index', -1)
                    
                    # Extract laughter information if successful
                    if result.get('success') and 'analysis' in result:
                        analysis = result['analysis']
                        laughter_instances = analysis.get('laughter_instances', [])
                        
                        # Create a row for each laughter instance
                        for laughter in laughter_instances:
                            row = {
                                'SourceFile': source_file,
                                'SegmentID': segment_id,
                                'StartTime': laughter.get('start_time', ''),
                                'EndTime': laughter.get('end_time', ''),
                                'Duration': laughter.get('end_time', 0) - laughter.get('start_time', 0),
                                'Type': laughter.get('type', ''),
                                'Intensity': laughter.get('intensity', ''),
                                'Notes': laughter.get('notes', '')
                            }
                            writer.writerow(row)
                    else:
                        # If no laughter detected or error, still create a row to show the segment was processed
                        row = {
                            'SourceFile': source_file,
                            'SegmentID': segment_id,
                            'StartTime': segment_info.get('start_time', ''),
                            'EndTime': segment_info.get('end_time', ''),
                            'Duration': segment_info.get('duration', ''),
                            'Type': 'no_laughter' if result.get('success') else 'error',
                            'Intensity': '',
                            'Notes': result.get('error', 'No laughter detected') if not result.get('success') else 'No laughter detected in this segment'
                        }
                        writer.writerow(row)
            
            logger.info(f"Results saved to: {csv_path}")
            
        except Exception as e:
            logger.error(f"Failed to save CSV file: {e}")
            raise
    
    def process_all_files(self):
        """
        Process all audio files in the input folder.
        """
        logger.info(f"Starting batch processing of folder: {self.input_folder}")
        
        # Find all audio files
        audio_files = self.find_audio_files()
        
        if not audio_files:
            logger.warning("No audio files found in the input folder")
            return
        
        # Process each audio file
        all_results = []
        for i, audio_file in enumerate(audio_files, 1):
            logger.info(f"Processing file {i}/{len(audio_files)}: {audio_file.name}")
            
            try:
                results = self.process_audio_file(audio_file)
                all_results.extend(results)
                
                # Save intermediate results every 5 files
                if i % 5 == 0:
                    intermediate_filename = f"laughter_results_intermediate_{i}.csv"
                    self.save_results_to_csv(all_results, intermediate_filename)
                    logger.info(f"Saved intermediate results after {i} files")
                
            except Exception as e:
                logger.error(f"Failed to process {audio_file.name}: {e}")
                continue
        
        # Save final results
        self.save_results_to_csv(all_results, "laughter_detection_final_results.csv")
        
        # Print summary
        successful_results = [r for r in all_results if r.get('success')]
        total_laughter_instances = sum(
            len(r.get('analysis', {}).get('laughter_instances', [])) 
            for r in successful_results
        )
        
        logger.info(f"Batch processing completed!")
        logger.info(f"Total segments processed: {len(all_results)}")
        logger.info(f"Successful analyses: {len(successful_results)}")
        logger.info(f"Total laughter instances detected: {total_laughter_instances}")
        logger.info(f"Results saved to: {self.output_folder}")


def main():
    """
    Main function to run the batch processor.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Batch laughter detection processor')
    parser.add_argument('input_folder', help='Path to folder containing audio files and JSON files')
    parser.add_argument('--output-folder', help='Path to save output CSV files (defaults to input_folder/results)')
    parser.add_argument('--api-key', help='OpenAI API key (optional, will use config if not provided)')
    
    args = parser.parse_args()
    
    # Validate input folder
    if not os.path.exists(args.input_folder):
        print(f"Error: Input folder does not exist: {args.input_folder}")
        return
    
    # Initialize and run processor
    try:
        processor = BatchLaughterProcessor(
            input_folder=args.input_folder,
            output_folder=args.output_folder,
            api_key=args.api_key
        )
        processor.process_all_files()
        
    except Exception as e:
        logger.error(f"Batch processing failed: {e}")
        raise


if __name__ == "__main__":
    main() 