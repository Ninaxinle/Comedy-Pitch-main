# 🎭 Video Segmentation Pipeline for Stand-Up Comedy

A production-ready application that processes stand-up comedy videos to create AI-powered segmentation JSON files. Features GPU-accelerated WhisperX transcription, intelligent incremental processing, context-aware summarization, two-stage LLM segmentation, and comprehensive comedy-optimized metadata.

## 🚀 What's New

- **⚡ Smart Incremental Processing**: Automatically resumes from missing steps, no manual flags needed
- **📝 Context Summarization**: AI generates global context summaries for better segmentation
- **🔄 Optimized Pipeline**: `audio → transcript → summary → segmentation` for context-aware boundaries
- **🛠️ Simplified API**: Removed `--skip-existing` (automatic), added `--overwrite` for force reprocessing
- **🔧 Backward Compatible**: Existing config files automatically upgraded, no breaking changes

## ✨ Key Features

- **🚀 GPU Acceleration**: 12x faster WhisperX processing with NVIDIA CUDA support
- **🎯 Ultra-High Accuracy**: WhisperX with forced alignment and Voice Activity Detection
- **🧠 Two-Stage AI Segmentation**: Initial segmentation + specialized editor review
- **📝 Context Summarization**: AI-generated global context for better segment understanding
- **⚡ Incremental Processing**: Smart resume from missing steps, auto-skip completed videos
- **⏱️ Gap Timing Analysis**: Captures audience laughter/applause between sentences
- **📊 Unlimited Processing**: No token limits - handles full-length comedy specials
- **🔒 Secure**: Git-safe configuration system protects API keys
- **🎬 Review UI**: Interactive web interface for validating segmentation results

## 🏆 Performance Benchmarks

| System | Video Length | Processing Time | Speedup |
|--------|-------------|-----------------|---------|
| **RTX 2080 (WhisperX)** | 7 minutes | ~8 seconds | **12x faster** |
| **CPU (WhisperX)** | 7 minutes | ~20 seconds | **3x faster** |
| OpenAI Whisper (GPU) | 7 minutes | ~60 seconds | baseline |

**Tested with**: Jason Cheny comedy video (117 sentences → 5 refined joke segments)

## 🎬 Segmentation Review UI

**Professional web-based interface for validating AI-generated comedy segmentations**

The project includes a beautiful, responsive web interface that makes it easy to review and validate your segmentation results with synchronized audio playback.

![Review UI Features](https://img.shields.io/badge/UI-Modern%20Web%20Interface-blue?style=for-the-badge)
![Audio Support](https://img.shields.io/badge/Audio-WAV%2FMP3%2FM4A-green?style=for-the-badge)
![Responsive](https://img.shields.io/badge/Design-Mobile%20Ready-purple?style=for-the-badge)

### ✨ Key Features

- **🎭 Comedy-Optimized**: Designed specifically for stand-up comedy validation
- **📂 Drag & Drop**: Simple file loading for segmentation JSON + audio files  
- **🎵 Precision Audio**: HTML5 player with frame-accurate timestamp control
- **🎯 Smart Navigation**: 
  - Jump to segment start/end instantly
  - Play individual segments with auto-stop
  - Real-time audio position tracking
- **📊 Rich Metadata Display**: All segment data beautifully formatted
- **⏱️ Timing Validation**: Visual gaps, duration, and sentence count
- **🎨 Professional UI**: Modern design with smooth animations
- **📱 Cross-Platform**: Works on desktop, tablet, and mobile

### 🚀 Quick Start

```bash
# 1. Open the review interface
start segmentation_review_ui.html  # Windows
open segmentation_review_ui.html   # macOS
firefox segmentation_review_ui.html # Linux

# 2. Load your files:
#    - Select JSON from output_segmentations/
#    - Select audio from output_audio/
#    - Click "Load Files"

# 3. Review each segment:
#    - Read the segment text
#    - Use playback controls to validate timing
#    - Check if gaps capture audience reactions
```

### 🎯 Perfect for Validation

**Comedy Timing Validation:**
- ✅ Verify punchlines align with segment endings
- ✅ Check setup-punchline grouping makes sense
- ✅ Ensure gaps capture audience laughter/applause
- ✅ Validate topic transitions between segments

**Technical Verification:**
- ✅ Confirm timestamp accuracy across all segments
- ✅ Check sentence indexing is correct
- ✅ Verify no audio/text sync issues
- ✅ Test segment boundary precision

### 📊 Supported Metadata

**Automatically displays all available fields:**
- **segment_id**: Segment identifier and sequence
- **start_time/end_time**: Precise timestamps (seconds)
- **duration**: Segment length for pacing analysis
- **sentence_indexes**: Reference to original transcript
- **text**: Complete segment text (setup + punchline)
- **total_gap**: Audience reaction timing (laughter/applause)
- **Custom fields**: Any additional metadata from your pipeline

### 🎨 Interface Overview

**Left Panel (Controls):**
- File selection and loading
- Audio player with scrub control
- Real-time timestamp display (MM:SS format)

**Right Panel (Segments):**
- Scrollable list of all segments
- Rich metadata cards with color coding
- Interactive playback buttons for each segment
- Responsive layout adapts to screen size

### 💡 Pro Tips

- **Quick Review**: Use "Play Segment" to rapidly validate each joke
- **Boundary Check**: Jump to start/end to verify timing precision  
- **Gap Analysis**: Look for segments with large total_gap values - these often contain the best audience reactions
- **Mobile Review**: Interface works great on tablets for portable validation

## 📁 Enhanced Output Structure

For each video file, the pipeline generates:

```
output_audio/
  ├── video1.wav                    # High-quality extracted audio (16kHz mono)
  
output_transcripts/  
  ├── video1_sentences.json         # Sentences with gap timing analysis
  
output_summaries/
  ├── video1_summary.txt            # AI-generated context summary for segment understanding

output_segmentations/
  ├── video1_segments.json          # AI-refined joke segments with complete metadata
```

### Enhanced Output Format

**Sentences JSON (with gap timing):**
```json
[
  {
    "index": 0, 
    "text": "I was on a plane.", 
    "start_time": 1.23, 
    "end_time": 4.15,
    "gap_to_next": 2.1
  },
  {
    "index": 1, 
    "text": "And the guy next to me...", 
    "start_time": 4.17, 
    "end_time": 6.02,
    "gap_to_next": 0.3
  }
]
```

**Segments JSON (complete metadata):**
```json
[
  {
    "segment_id": 1,
    "sentence_indexes": [0, 1, 2],
    "start_time": 1.23,
    "end_time": 8.45,
    "duration": 7.22,
    "text": "I was on a plane. And the guy next to me started snoring...",
    "total_gap": 4.8
  }
]
```

**New fields:**
- **`gap_to_next`**: Seconds of silence/laughter after each sentence
- **`total_gap`**: Total audience reaction time within segment  
- **`duration`**: Programmatically calculated segment length
- **`text`**: Complete concatenated transcript for segment

## 🛠️ Installation

### Prerequisites

1. **Python 3.8+**
2. **FFmpeg**: Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)  
3. **OpenAI API Key**: Get from [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
4. **GPU (Recommended)**: NVIDIA GPU with CUDA support for 12x faster processing

### Setup

1. **Clone and setup the environment:**
   ```bash
   cd "Video segmentation"
   python -m venv py310
   
   # Windows
   py310\Scripts\activate
   
   # Linux/Mac  
   source py310/bin/activate
   ```

2. **Install dependencies:**
   
   **For GPU acceleration (recommended):**
   ```bash
   pip install -r requirements.txt
   ```
   
   **For CPU-only:**
   ```bash
   pip install whisperx>=3.4.2 openai>=1.0.0 moviepy>=1.0.3 PyYAML>=6.0 ffmpeg-python>=0.2.0
   pip install torch torchvision torchaudio  # CPU versions
   ```

3. **Configure OpenAI API:**
   
   ```bash
   # Copy the example config and customize it
   cp config.example.yaml config.yaml
   ```
   
   Then edit `config.yaml` with your settings:
   
   **Option A:** Set API key in config file
   ```yaml
   llm:
     api_key: "your-actual-api-key-here"
   ```
   
   **Option B:** Use environment variable
   ```bash
   # Windows
   set OPENAI_API_KEY=your-api-key-here
   
   # Linux/Mac
   export OPENAI_API_KEY=your-api-key-here
   ```

## 🚀 Usage

### Basic Usage

**Process a single video (with smart resume):**
```bash
python video_segmentation.py "path/to/video.mp4"
```

**Process a folder of videos (automatic incremental processing):**
```bash
python video_segmentation.py "input_videos/"
```

**Force complete reprocessing (overwrite all outputs):**
```bash
python video_segmentation.py "input_videos/" --overwrite
```

**Test LLM segmentation + summary only (uses existing transcripts):**
```bash
python video_segmentation.py "input_videos/" --segmentation-only
```

**Process with debug info:**
```bash
python video_segmentation.py "input_videos/" --debug
```

### Advanced Pipeline Features

**🔄 Incremental Processing:**
- **Smart Resume**: Automatically detects existing outputs and starts from first missing step
- **Dependency Chain**: `audio → transcript → summary → segmentation`
- **Auto-Skip**: Videos with all outputs completed are automatically skipped
- **Efficiency**: No unnecessary reprocessing of expensive steps (audio extraction, transcription)

**📝 Context Summarization:**
- **Global Context**: AI generates comprehensive performance summaries
- **Better Segmentation**: Summary provides context for more informed joke boundary decisions
- **Themes & Characters**: Identifies recurring elements and ongoing narratives
- **Standalone Understanding**: Enables segment comprehension without full transcript

**🧠 Two-Stage LLM Segmentation:**
- **Stage 1**: Initial comedy-aware segmentation with context awareness
- **Stage 2**: Specialized editor review and refinement
- **Automatic fallback**: Uses initial segmentation if editor fails
- **Result**: Higher quality joke boundaries with global context

**⏱️ Gap Timing Analysis:**
- Captures audience laughter/applause between sentences
- Large gaps (>1s) indicate natural joke boundaries
- Helps LLM make better segmentation decisions
- Provides comedy performance analytics

### Configuration

The application uses `config.yaml` for all settings:

```yaml
llm:
  model: "gpt-4o-mini"          # Fast and cost-effective
  temperature: 0.3              # Consistency vs creativity
  # No max_tokens - unlimited processing

whisper:
  model: "large"               # Best accuracy with WhisperX
  language: "en"               # Or "auto" for detection
  
directories:
  output_transcripts: "output_transcripts"
  summaries: "output_summaries"
  output_segmentations: "output_segmentations"

processing:
  timestamp_buffer: 0.05       # Buffer for timestamp correction
  silence_gap_threshold: 1.5   # Joke boundary detection threshold
```

**All models supported:**
- **WhisperX**: tiny, base, small, medium, large
- **OpenAI**: gpt-4o, gpt-4o-mini, gpt-4, gpt-3.5-turbo

## 📋 Command Line Options

**Main Pipeline:**
```bash
python video_segmentation.py INPUT_PATH [options]

Options:
  --config CONFIG          Path to config file (default: config.yaml)
  --debug                  Enable debug logging
  --overwrite              Force complete reprocessing, overwriting all existing outputs
  --segmentation-only      Use existing transcripts for LLM segmentation + summary only
```

**Test Script:**
```bash
python test_pipeline.py [options]

Options:
  --video VIDEO     Specific video name to test (partial match)
  --mock-llm        Skip LLM API call for testing
  --debug          Enable debug logging
```

## 🎭 Technical Pipeline

### 🔄 Optimized Processing Order
```
Video → Audio → Transcript → Summary → Segmentation
```

**Why this order?**
- **Context First**: Summary provides global context before segmentation decisions
- **Better Boundaries**: LLM uses performance themes to identify natural joke breaks  
- **Efficiency**: Context generation needs only plain text (no timestamps)

### WhisperX Enhancement
- **12x faster** than OpenAI Whisper via batched inference
- **Voice Activity Detection (VAD)** for better pause detection
- **Forced phoneme alignment** for precise word timestamps
- **Less hallucination** and better long-form accuracy

### 📝 Context Summarization
1. **Plain Text Input**: Uses transcript without timestamps for cleaner LLM processing
2. **Global Analysis**: Identifies themes, recurring characters, ongoing narratives
3. **Segmentation Context**: Summary informs better joke boundary decisions
4. **Standalone Value**: Enables understanding of individual segments in isolation

### Comedy-Optimized Processing
1. **Gap Detection**: WhisperX trims timestamps to speech boundaries - laughter exists in gaps
2. **Timestamp Extension**: Sentence end times extended to capture audience reactions
3. **LLM Cues**: Gap timing helps AI identify natural joke boundaries
4. **Context-Aware Segmentation**: Uses global summary for informed boundary decisions
5. **Two-Stage Review**: Specialized editor LLM refines initial segmentation

### Output Enhancement
- **Programmatic timing**: Start/end times calculated from sentence indexes (not LLM)
- **Complete metadata**: Duration, text content, and gap analysis in every segment
- **Context summaries**: Global performance understanding for each video
- **Analytics ready**: Total audience reaction time per segment

## 🔧 Troubleshooting

### Common Issues

**GPU not detected:**
```bash
# Check CUDA installation
python -c "import torch; print('CUDA Available:', torch.cuda.is_available())"
```
- Install CUDA-enabled PyTorch from requirements.txt
- Verify NVIDIA drivers are installed

**FFmpeg not found:**
- Windows: Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
- Mac: `brew install ffmpeg`  
- Linux: `sudo apt install ffmpeg`

**WhisperX model issues:**
- ✅ **Auto-download**: Models download automatically on first use
- ✅ **Stable processing**: FP32 precision for reliability
- ✅ **Warning suppression**: Triton/cuDNN warnings handled

**API errors:**
- Verify OpenAI API key has sufficient credits
- gpt-4o-mini recommended for cost efficiency
- Two-stage LLM + summarizer uses 3 API calls per video

**Config file compatibility:**
- ✅ **Automatic upgrade**: Old config files automatically get `summaries` directory added
- ✅ **Backward compatible**: Existing setups continue working without manual updates
- ✅ **No breaking changes**: All previous functionality preserved

**VAD reliability issues:**
- ⚠️ **Scale-dependent behavior**: VAD settings that work on short clips may fail on full-length videos
- **Test evidence**: onset=0.1, offset=0.8 shows 10/10 success on 10-second clips but fails on full 60+ minute videos
- **Content-specific**: Works reliably on some full specials (Lewis Black) but not others (LGBTQ comedians)
- **Timestamp recovery**: When VAD fails and first sentence is mistimed, subsequent sentences self-correct after 1-2 sentences
- **Recommendation**: Test VAD settings on short clips first, expect different behavior on full videos
- **Fallback strategy**: Consider disabling VAD for problematic long videos if issues persist

### Performance Optimization

**For large batches:**
```bash
# Automatic incremental processing (default behavior)
python video_segmentation.py "input_videos/"
# Videos with all outputs are automatically skipped
# Processing resumes from first missing step for each video
```

**For prompt testing:**
```bash
# Test LLM changes without reprocessing video/audio
python video_segmentation.py "input_videos/" --segmentation-only
# Uses existing transcripts for segmentation + summary generation
```

## 🏗️ Project Structure

```
Video segmentation/
├── video_segmentation.py           # Main pipeline script
├── test_pipeline.py                # Test script
├── config.example.yaml             # Configuration template
├── config.yaml                     # Your actual config (git-ignored)
├── requirements.txt                # Python dependencies with CUDA
├── prompt-system-prompt.txt        # Initial LLM segmentation prompt
├── prompt-user-prompt-instruction.txt # Initial LLM instructions
├── prompt-editor-system-prompt.txt # Editor LLM prompt
├── prompt-summarizer-system-prompt.txt # Context summarizer LLM prompt
├── prompt-summarizer-user-prompt-instruction.txt # Summarizer instructions
├── input_videos/                   # Input video files
├── output_audio/                   # Extracted audio files
├── output_transcripts/              # Sentence-level transcripts with gaps
├── output_summaries/                # AI-generated context summaries
├── output_segmentations/            # AI-refined segments with metadata
└── test video data/                # Test videos
```

## 📊 Real-World Performance

**Processing Results:**

| Video | Length | Sentences | Initial → Refined Segments | Total Gaps | Processing Time |
|-------|--------|-----------|----------------------------|-------------|-----------------|
| Jason Cheny | 7 min | 117 | 9 → 5 segments | 12.7-35.2s per segment | **8 seconds** |
| Comedy Special* | 60 min | ~1000 | ~60 → ~40 segments | Variable | **2-3 minutes** |

*Estimated based on tested performance

**Gap Timing Insights:**
- Segments with 20+ seconds of gaps indicate highly successful jokes
- Large gaps (>1s) help AI identify natural boundaries
- Total gap analysis reveals audience engagement patterns

## 🎯 Use Cases

- **Comedy Analytics**: Measure audience reaction timing and engagement
- **Content Optimization**: Identify highest-performing joke segments
- **Batch Processing**: Efficient pipeline for large comedy collections
- **Research**: Study comedy timing, structure, and audience response
- **Video Editing**: Automated rough cuts with audience reaction context

## 🤝 Contributing

1. **Performance Testing**: Share WhisperX results with different GPUs
2. **LLM Prompt Engineering**: Improve two-stage segmentation accuracy  
3. **Gap Analysis**: Enhance audience reaction detection algorithms
4. **Integration**: Build analytics tools using enhanced JSON outputs

## 📝 License

Educational and research use. Commercial applications welcome with attribution. 