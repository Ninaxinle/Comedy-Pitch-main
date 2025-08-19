#!/usr/bin/env python3
"""
Convert batch processor CSV output to validator-compatible format.
"""

import csv
import json
import os
from pathlib import Path

def convert_csv_for_validator(input_csv_path, output_csv_path):
    """
    Convert the batch processor CSV to validator-compatible format.
    
    The validator expects:
    - SourceFile: audio file name
    - StartTime: laughter start time
    - EndTime: laughter end time
    
    Our CSV has:
    - audio_file: audio file name
    - laughter_instances: JSON array with start_time/end_time
    """
    
    # Read the input CSV
    rows = []
    with open(input_csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    
    # Convert to validator format
    validator_rows = []
    
    for row in rows:
        audio_file = row['audio_file']
        laughter_instances_str = row['laughter_instances']
        
        try:
            # Parse the laughter instances JSON
            laughter_instances = json.loads(laughter_instances_str)
            
            # Create a row for each laughter instance
            for instance in laughter_instances:
                validator_row = {
                    'SourceFile': audio_file,
                    'StartTime': str(instance.get('start_time', 0)),
                    'EndTime': str(instance.get('end_time', 0)),
                    'Type': instance.get('type', 'unknown'),
                    'Intensity': instance.get('intensity', 'unknown'),
                    'Notes': instance.get('notes', ''),
                    'SegmentStart': row.get('start_time', ''),
                    'SegmentEnd': row.get('end_time', ''),
                    'SegmentText': row.get('segment_text', '')
                }
                validator_rows.append(validator_row)
                
        except json.JSONDecodeError as e:
            print(f"Warning: Could not parse laughter instances for {audio_file}: {e}")
            continue
    
    # Write the validator-compatible CSV
    fieldnames = ['SourceFile', 'StartTime', 'EndTime', 'Type', 'Intensity', 'Notes', 'SegmentStart', 'SegmentEnd', 'SegmentText']
    
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(validator_rows)
    
    print(f"Converted {len(validator_rows)} laughter instances to validator format")
    print(f"Output saved to: {output_csv_path}")
    
    return output_csv_path

def main():
    """Main function to convert the CSV."""
    
    # Find the input CSV file
    input_csv = "llm-test-data/results/laughter_detection_final_results.csv"
    
    if not os.path.exists(input_csv):
        print(f"Error: Input CSV file not found: {input_csv}")
        return
    
    # Create output filename
    output_csv = "llm-test-data/results/laughter_detection_validator_format.csv"
    
    # Convert the CSV
    convert_csv_for_validator(input_csv, output_csv)
    
    # Show a sample of the converted data
    print("\nSample of converted data:")
    with open(output_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i < 5:  # Show first 5 rows
                print(f"  {row['SourceFile']}: {row['StartTime']}s - {row['EndTime']}s ({row['Type']}, {row['Intensity']})")
            else:
                break

if __name__ == "__main__":
    main() 