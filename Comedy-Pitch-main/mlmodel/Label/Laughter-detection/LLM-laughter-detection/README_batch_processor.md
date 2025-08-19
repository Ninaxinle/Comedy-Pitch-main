# Batch Laughter Detection Processor

A Python script that processes a folder of audio files with their corresponding JSON files for laughter detection and outputs results to CSV.

## Overview

This processor automatically:
1. **Scans a folder** for audio files and their corresponding JSON files
2. **Processes each segment** of each audio file for laughter detection
3. **Outputs results** to CSV files with detailed laughter analysis

## File Structure Requirements

Your input folder should contain files with this naming pattern:

```
your_folder/
├── audio_file_1.mp3
├── audio_file_1_segments.json
├── audio_file_1_sentences.json
├── audio_file_2.wav
├── audio_file_2_segments.json
├── audio_file_2_sentences.json
└── ...
```

### File Types

- **Audio files**: `.mp3`, `.wav`, `.m4a`, `.aac`, `.ogg`, `.flac`
- **Segments files**: `{audio_name}_segments.json` - contains segment information
- **Sentences files**: `{audio_name}_sentences.json` - contains full transcript

### JSON File Formats

#### Segments File (`_segments.json`)
```json
[
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
    }
]
```

#### Sentences File (`_sentences.json`)
```json
[
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
    }
]
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements_audio_detector.txt
```

2. Set up your API key in `config_local.py`:
```bash
cp config.py config_local.py
# Edit config_local.py and add your OpenAI API key
```

## Usage

### Command Line

```bash
# Basic usage
python batch_laughter_processor.py /path/to/your/folder

# With custom output folder
python batch_laughter_processor.py /path/to/your/folder --output-folder /path/to/results

# With API key (overrides config)
python batch_laughter_processor.py /path/to/your/folder --api-key "your-api-key-here"
```

### Python Script

```python
from batch_laughter_processor import BatchLaughterProcessor

# Initialize processor
processor = BatchLaughterProcessor(
    input_folder="/path/to/your/folder",
    output_folder="/path/to/results"  # optional
)

# Process all files
processor.process_all_files()
```

## Output

The processor creates CSV files with the following columns:

| Column | Description |
|--------|-------------|
| `audio_file` | Name of the audio file |
| `segment_index` | Index of the segment |
| `start_time` | Start time of the segment (seconds) |
| `end_time` | End time of the segment (seconds) |
| `duration` | Duration of the segment (seconds) |
| `segment_text` | Text content of the segment |
| `success` | Whether the analysis was successful |
| `laughter_count` | Number of laughter instances detected |
| `laughter_instances` | JSON string with detailed laughter information |
| `analysis_notes` | Notes from the AI analysis |
| `error_message` | Error message if analysis failed |
| `file_size_mb` | Size of the audio chunk in MB |

### Sample CSV Output

```csv
audio_file,segment_index,start_time,end_time,duration,segment_text,success,laughter_count,laughter_instances,analysis_notes,error_message,file_size_mb
sample_audio.mp3,0,33.38,39.70,6.32,"What is up, New York?",true,1,"[{'start_time': 35.2, 'end_time': 36.8, 'type': 'giggle', 'intensity': 'light', 'notes': 'Brief giggle after greeting'}]","Detected light laughter following the greeting",,2.1
sample_audio.mp3,1,39.72,42.29,2.57,"Y'all look good, and I am so happy to be here.",true,0,"[]","No laughter detected in this segment",,0.8
```

## Features

### Automatic File Discovery
- Automatically finds audio files and their corresponding JSON files
- Supports multiple audio formats
- Handles case-insensitive file extensions

### Robust Error Handling
- Continues processing even if individual files fail
- Detailed error logging
- Graceful handling of missing files

### Progress Tracking
- Saves intermediate results every 5 files
- Detailed logging of processing progress
- Summary statistics at completion

### Memory Efficient
- Processes files one at a time
- Uses in-memory chunking for audio and transcripts
- No temporary files created

## Example Workflow

1. **Prepare your data**:
   ```
   my_data/
   ├── comedy_show_1.mp3
   ├── comedy_show_1_segments.json
   ├── comedy_show_1_sentences.json
   ├── comedy_show_2.mp3
   ├── comedy_show_2_segments.json
   └── comedy_show_2_sentences.json
   ```

2. **Run the processor**:
   ```bash
   python batch_laughter_processor.py my_data
   ```

3. **Check results**:
   ```
   my_data/results/
   ├── laughter_detection_final_results.csv
   ├── laughter_results_intermediate_5.csv
   └── laughter_results_intermediate_10.csv
   ```

## Configuration

The processor uses the same configuration as the main laughter detector:

- **API settings**: From `config_local.py`
- **Chunk duration**: Default 30 seconds (configurable)
- **Overlap**: Default 5 seconds (configurable)
- **Retry attempts**: Default 3 (configurable)

## Troubleshooting

### Common Issues

1. **"No audio files found"**
   - Check that your audio files have supported extensions
   - Ensure files are in the correct folder

2. **"Segments file not found"**
   - Verify that `{audio_name}_segments.json` exists
   - Check file naming convention

3. **"Sentences file not found"**
   - Verify that `{audio_name}_sentences.json` exists
   - Check file naming convention

4. **"OpenAI API key is required"**
   - Set your API key in `config_local.py`
   - Or pass it via command line with `--api-key`

### Performance Tips

- **Large folders**: The processor saves intermediate results every 5 files
- **Memory usage**: Processes one file at a time to minimize memory usage
- **API limits**: Respects OpenAI rate limits with automatic retries

## Advanced Usage

### Custom Processing

```python
from batch_laughter_processor import BatchLaughterProcessor

# Initialize processor
processor = BatchLaughterProcessor("/path/to/folder")

# Process specific files manually
audio_files = processor.find_audio_files()
for audio_file in audio_files[:3]:  # Process first 3 files
    results = processor.process_audio_file(audio_file)
    processor.save_results_to_csv(results, "custom_results.csv")
```

### Batch Processing with Custom Settings

```python
# Custom output folder
processor = BatchLaughterProcessor(
    input_folder="/path/to/folder",
    output_folder="/custom/results/path"
)

# Process all files
processor.process_all_files()
```

## Logging

The processor provides detailed logging:

- **INFO**: Processing progress and file discovery
- **WARNING**: Missing files or non-critical issues
- **ERROR**: Processing failures and errors

Logs are output to console and can be redirected to a file:

```bash
python batch_laughter_processor.py /path/to/folder > processing.log 2>&1
``` 