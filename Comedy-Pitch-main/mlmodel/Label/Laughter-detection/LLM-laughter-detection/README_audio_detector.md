# Audio Laughter Detector

A Python library for detecting laughter in audio files using OpenAI's audio analysis capabilities. This tool chunks audio in memory and sends it to OpenAI for precise laughter detection with transcript correlation.

## Features

- **In-memory audio chunking**: No temporary files created
- **In-memory transcript chunking**: Automatically extracts relevant transcript segments based on time range
- **Transcript correlation**: Uses full transcript timestamps to improve accuracy
- **Flexible transcript formats**: Supports Whisper-like segments, word-level timestamps, and custom formats
- **Batch processing**: Process entire audio files in configurable chunks
- **Robust error handling**: Retry logic and comprehensive error reporting
- **Multiple audio formats**: Supports MP3, WAV, M4A, AAC, OGG

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements_audio_detector.txt
```

2. Set up your configuration:
   - Copy `config.py` to `config_local.py`
   - Edit `config_local.py` and replace `"sk-your-actual-openai-api-key-here"` with your actual OpenAI API key
   - Optionally, update the default file paths for your audio and transcript files

```bash
cp config.py config_local.py
# Then edit config_local.py with your API key
```

## Quick Start

```python
from audio_laughter_detector import AudioLaughterDetector

# Initialize the detector
detector = AudioLaughterDetector()

# Load your transcript (example format)
transcript = {
    "segments": [
        {"start": 10.0, "end": 12.5, "text": "So I was walking down the street"},
        {"start": 12.5, "end": 15.0, "text": "and this guy comes up to me"},
        {"start": 15.0, "end": 18.0, "text": "and says the funniest thing"}
    ]
}

# Detect laughter in a specific chunk
result = detector.detect_laughter_in_chunk(
    audio_path="path/to/your/audio.mp3",
    transcript_json=transcript,
    start_time=10.0,
    end_time=30.0
)

print(result)
```

## API Reference

### AudioLaughterDetector Class

#### Constructor
```python
AudioLaughterDetector(api_key=None, model=None)
```

- `api_key`: OpenAI API key (optional, will use config file if not provided)
- `model`: OpenAI model to use for analysis (optional, will use config default if not provided)

#### Methods

##### `detect_laughter_in_chunk(audio_path, transcript_json, start_time, end_time, max_retries=3)`

Analyze a specific chunk of audio for laughter detection.

**Parameters:**
- `audio_path`: Path to the full audio file
- `transcript_json`: Full transcript with timestamps
- `start_time`: Start time of the chunk in seconds
- `end_time`: End time of the chunk in seconds
- `max_retries`: Maximum number of retry attempts (default: 3)

**Returns:**
```json
{
    "success": true,
    "chunk_info": {
        "start_time": 10.0,
        "end_time": 30.0,
        "duration": 20.0,
        "file_size_mb": 2.5
    },
    "analysis": {
        "laughter_instances": [
            {
                "start_time": 12.5,
                "end_time": 14.2,
                "type": "giggle",
                "intensity": "light",
                "notes": "Brief giggle after joke"
            }
        ],
        "analysis_notes": "Detected light laughter following the punchline"
    }
}
```

##### `batch_detect_laughter(audio_path, transcript_json, chunk_duration=30.0, overlap=5.0)`

Process an entire audio file in chunks for laughter detection.

**Parameters:**
- `audio_path`: Path to the audio file
- `transcript_json`: Full transcript with timestamps
- `chunk_duration`: Duration of each chunk in seconds (default: 30.0)
- `overlap`: Overlap between chunks in seconds (default: 5.0)

**Returns:** List of results for each chunk

## Transcript Formats

The system supports multiple transcript formats:

### Whisper-like Format
```json
{
    "segments": [
        {"start": 10.0, "end": 12.5, "text": "So I was walking down the street"},
        {"start": 12.5, "end": 15.0, "text": "and this guy comes up to me"}
    ]
}
```

### Word-level Format
```json
{
    "words": [
        {"start": 10.0, "end": 10.5, "word": "So"},
        {"start": 10.5, "end": 11.0, "word": "I"},
        {"start": 11.0, "end": 11.5, "word": "was"}
    ]
}
```

### Simple Format
```json
[
    {"start": 10.0, "end": 12.5, "text": "So I was walking down the street"},
    {"start": 12.5, "end": 15.0, "text": "and this guy comes up to me"}
]
```

### Sentence-level Format (with start_time/end_time)
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

## Transcript Chunking

The system automatically chunks both audio and transcript in memory:

1. **Audio chunking**: Extracts the specified time range from the full audio file
2. **Transcript chunking**: Filters transcript segments to only include those that overlap with the time range
3. **Memory efficient**: No temporary files created, everything processed in memory
4. **Flexible formats**: Supports multiple transcript formats with different timestamp field names

## Improved Prompt

The system uses an enhanced prompt that:

1. **Provides context**: Explains that the audio is a chunk of a longer recording
2. **Shows relevant transcript**: Only includes transcript segments within the chunk timeframe
3. **Clear instructions**: Specific guidance on what to look for and how to respond
4. **Structured output**: Requests JSON format for easy parsing
5. **Correlation guidance**: Encourages using transcript timestamps to correlate laughter with speech

## Example Usage

See `example_laughter_detection.py` for a complete working example.

## Error Handling

The system includes comprehensive error handling:

- **File validation**: Checks for file existence and supported formats
- **Size limits**: Validates against OpenAI's 25MB limit
- **API retries**: Automatic retry logic for failed API calls
- **JSON parsing**: Graceful handling of malformed responses
- **Memory management**: Efficient in-memory processing

## Performance Considerations

- **Chunk size**: Keep chunks under 5 minutes for optimal performance
- **Overlap**: Use 5-10 second overlap to avoid missing laughter at chunk boundaries
- **Batch processing**: Use `batch_detect_laughter()` for processing entire files
- **Memory usage**: Audio is processed in memory, so large files may require more RAM

## Limitations

- Requires OpenAI API key and credits
- Audio files must be under 25MB per chunk
- Processing time depends on audio length and API response time
- Accuracy depends on audio quality and OpenAI model performance

## Troubleshooting

### Common Issues

1. **"Audio file not found"**: Check the file path and ensure the file exists
2. **"Unsupported audio format"**: Convert to supported format (MP3, WAV, M4A, AAC, OGG)
3. **"Audio chunk too large"**: Reduce chunk duration or use lower quality audio
4. **"OpenAI API key is required"**: Set your API key in `config_local.py`

### Getting Help

- Check the example script for usage patterns
- Verify your transcript format matches one of the supported formats
- Ensure your audio file is in a supported format and under size limits 