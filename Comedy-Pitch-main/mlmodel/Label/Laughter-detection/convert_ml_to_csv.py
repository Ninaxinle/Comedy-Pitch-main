import json
import csv
import sys
from pathlib import Path

def convert_ml_json_to_csv(json_file_path, csv_output_path, source_filename):
    """
    Convert ML inference JSON output to CSV format matching LLM laughter detection.
    
    Args:
        json_file_path: Path to the ML inference JSON file
        csv_output_path: Path to output CSV file
        source_filename: Original audio filename for SourceFile column
    """
    
    # Read the JSON file
    with open(json_file_path, 'r', encoding='utf-8') as f:
        ml_data = json.load(f)
    
    # Prepare CSV data
    csv_rows = []
    
    for instance_id, laughter_data in ml_data.items():
        start_time = laughter_data.get('start_sec', 0)
        end_time = laughter_data.get('end_sec', 0)
        duration = end_time - start_time
        
        # Create row matching LLM format
        row = {
            'SourceFile': source_filename,  # Keep the quotes as they are
            'SegmentID': instance_id,
            'StartTime': start_time,
            'EndTime': end_time,
            'Duration': duration,
            'Type': 'ml_detection',  # Distinguish from LLM detection
            'Intensity': 'unknown',  # ML doesn't provide intensity
            'Notes': f'ML detection #{instance_id}'
        }
        csv_rows.append(row)
    
    # Sort by start time
    csv_rows.sort(key=lambda x: x['StartTime'])
    
    # Write CSV file
    with open(csv_output_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['SourceFile', 'SegmentID', 'StartTime', 'EndTime', 'Duration', 'Type', 'Intensity', 'Notes']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)
    
    print(f"Converted {len(csv_rows)} ML detections to CSV format")
    print(f"Output saved to: {csv_output_path}")

if __name__ == "__main__":
    # Convert the Adele Givens ML results
    json_file = "optimized_output/adele_givens.json"
    csv_file = "optimized_output/adele_givens_ml_detections.csv"
    source_file = '"A Sex Sandwich＂- Adele Givens - Full Special.wav"'
    
    if Path(json_file).exists():
        convert_ml_json_to_csv(json_file, csv_file, source_file)
    else:
        print(f"Error: {json_file} not found")
        sys.exit(1) 