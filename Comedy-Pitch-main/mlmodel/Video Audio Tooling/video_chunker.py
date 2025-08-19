import argparse
import ffmpeg
import os

def split_media(media_path, timestamps, output_dir):
    """
    Splits a video or audio file into chunks based on a list of timestamps using ffmpeg.

    :param media_path: Path to the input video or audio file.
    :param timestamps: A list of tuples, where each tuple contains the start and end time in seconds for a chunk.
    :param output_dir: The directory where the media chunks will be saved.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    base_name = os.path.splitext(os.path.basename(media_path))[0]
    file_ext = os.path.splitext(media_path)[1]

    for i, (start_time, end_time) in enumerate(timestamps):
        output_filename = os.path.join(output_dir, f"{base_name}_chunk_{i+1}{file_ext}")
        print(f"Creating chunk: {output_filename} from {start_time}s to {end_time}s")
        
        try:
            (
                ffmpeg
                .input(media_path, ss=start_time, to=end_time)
                .output(output_filename, acodec='copy', vcodec='copy')
                .run(overwrite_output=True, quiet=True)
            )
        except ffmpeg.Error as e:
            print(f"Error creating chunk {output_filename}: {e.stderr.decode()}")
            # Fallback for streams that can't be bitstream copied
            try:
                print("Falling back to re-encoding...")
                (
                    ffmpeg
                    .input(media_path, ss=start_time, to=end_time)
                    .output(output_filename)
                    .run(overwrite_output=True, quiet=True)
                )
            except ffmpeg.Error as e_fallback:
                 print(f"Fallback failed for chunk {output_filename}: {e_fallback.stderr.decode()}")


def main():
    parser = argparse.ArgumentParser(description="Split a video or audio file into chunks based on specified timestamps.")
    parser.add_argument("media_path", type=str, help="Path to the media file to be split.")
    parser.add_argument("timestamps", type=str, help="Comma-separated timestamps for splitting. E.g., '0,10,20,30' for 0-10s, 10-20s, 20-30s chunks.")
    parser.add_argument("--output-dir", type=str, default=".", help="Directory to save the media chunks. Defaults to the current directory.")
    
    args = parser.parse_args()

    try:
        # Handle timestamps in format 'M:SS' or seconds
        time_parts = args.timestamps.split(',')
        times = []
        for t in time_parts:
            if ':' in t:
                minutes, seconds = map(int, t.split(':'))
                times.append(minutes * 60 + seconds)
            else:
                times.append(float(t))

        if len(times) < 2:
            raise ValueError("At least two timestamps are required to create a chunk.")
        
        timestamps = [(times[i], times[i+1]) for i in range(len(times) - 1)]
    except ValueError as e:
        print(f"Error parsing timestamps: {e}")
        return

    split_media(args.media_path, timestamps, args.output_dir)

if __name__ == "__main__":
    main() 