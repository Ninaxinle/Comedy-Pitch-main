import argparse
from pydub import AudioSegment
import os
import re
from collections import defaultdict

def combine_audio_files(input_dir, output_dir):
    """
    Combines chunked audio files in a directory into their respective full-length files.
    Files are grouped by a common prefix and sorted numerically before combining.

    :param input_dir: Directory containing the chunked audio files.
    :param output_dir: Directory where the combined audio files will be saved.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    # Group files by their base name (prefix)
    audio_groups = defaultdict(list)
    
    # Regex to extract base name and sequence number (e.g., "name_1.mp3")
    # This will capture prefixes like 'AA_RN_audio' from 'AA_RN_audio_01.mp3'
    pattern = re.compile(r'^(.*?)_(\d+)\.(mp3|wav)$', re.IGNORECASE)

    for filename in os.listdir(input_dir):
        match = pattern.match(filename)
        if match:
            prefix = match.group(1)
            number = int(match.group(2))
            audio_groups[prefix].append((number, filename))
        else:
            print(f"Skipping file with unrecognized format: {filename}")

    if not audio_groups:
        print("No audio files found in the directory that match the expected format 'prefix_number.ext'.")
        return

    # Process each group of audio files
    for prefix, files in audio_groups.items():
        # Sort files by their sequence number
        files.sort()
        
        # Start with an empty audio segment
        combined_audio = AudioSegment.empty()
        
        print(f"\nCombining files for prefix: {prefix}")
        for _, filename in files:
            file_path = os.path.join(input_dir, filename)
            print(f"  - Adding file: {filename}")
            
            file_extension = os.path.splitext(filename)[1].lower()
            try:
                if file_extension == '.mp3':
                    audio_segment = AudioSegment.from_mp3(file_path)
                elif file_extension == '.wav':
                    audio_segment = AudioSegment.from_wav(file_path)
                else:
                    # Should not happen with the current regex, but good practice
                    print(f"Unsupported file format: {file_extension}. Skipping {filename}.")
                    continue
                combined_audio += audio_segment
            except Exception as e:
                print(f"    Error processing file {filename}: {e}")
                continue

        # Determine output format and save the file
        if combined_audio.duration_seconds > 0:
            output_filename = f"{prefix}_combined.mp3"
            output_path = os.path.join(output_dir, output_filename)
            
            print(f"  -> Exporting combined audio to {output_path}")
            combined_audio.export(output_path, format="mp3")
        else:
            print(f"  -> No audio segments were combined for prefix {prefix}. Skipping output.")

    print("\nAudio combination process complete.")

def main():
    parser = argparse.ArgumentParser(description="Combine chunked audio files from a directory based on their prefixes.")
    parser.add_argument("input_dir", type=str, help="Directory containing the audio files to be combined.")
    parser.add_argument("output_dir", type=str, help="Directory to save the combined output audio files.")
    
    args = parser.parse_args()

    combine_audio_files(args.input_dir, args.output_dir)

if __name__ == "__main__":
    main() 