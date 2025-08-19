# Video and Audio Tooling

This repository contains two Python scripts for basic video and audio manipulation.

## Setup

Before running the scripts, you need to install the required Python packages. It is recommended to use a virtual environment.

```bash
# Create and activate a virtual environment (optional but recommended)
python -m venv venv
# On Windows
venv\\Scripts\\activate
# On macOS/Linux
source venv/bin/activate

# Install the required packages
pip install -r requirements.txt
```

## `video_chunker.py`

This script splits a video or audio file into smaller chunks based on specified timestamps.

### Usage

```bash
python video_chunker.py <media_path> <timestamps> [--output-dir <output_directory>]
```

-   `<media_path>`: Path to the video or audio file you want to split.
-   `<timestamps>`: A comma-separated string of timestamps in seconds. For example, `'0,60,120,180'` will create three chunks: 0-60s, 60-120s, and 120-180s.
-   `--output-dir`: (Optional) The directory where the output media chunks will be saved. Defaults to the current directory.

### Example

```bash
python video_chunker.py my_video.mp4 "0,10,25,40" --output-dir video_chunks
```

This command will create three files in the `video_chunks` directory:
-   `my_video_chunk_1.mp4` (from 0s to 10s)
-   `my_video_chunk_2.mp4` (from 10s to 25s)
-   `my_video_chunk_3.mp4` (from 25s to 40s)

## `audio_combiner.py`

This script combines multiple audio files from a directory into a single audio file. The script assumes the audio files are named with a common prefix and a sequential number at the end (e.g., `audio_1.mp3`, `audio_2.mp3`).

### Usage

```bash
python audio_combiner.py <input_dir> <output_dir>
```

-   `<input_dir>`: The directory containing the audio files to be combined.
-   `<output_dir>`: The directory where the combined output audio files will be saved.

### Example

Suppose you have a folder named `audio_parts` with the following files:
-   `showA_1.wav`
-   `showA_2.wav`
-   `showB_1.wav`

```bash
python audio_combiner.py audio_parts combined_shows
```

This command will create two files in the `combined_shows` directory:
- `showA_combined.mp3`
- `showB_combined.mp3` 