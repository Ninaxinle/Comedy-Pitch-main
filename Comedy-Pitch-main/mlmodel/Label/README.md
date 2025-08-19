# 🎭 Labeling Pipeline (Alignment → Laughter → Labels → Review UI)

This folder contains a full pipeline to:
- Generate word-level timestamps by aligning provided transcripts to audio (WhisperX align)
- Detect laughter events
- Produce segment-level and word-level labels
- Review results in a local web UI

## 🚀 Features

- **Neural Network Detection**: Uses a fine-tuned wav2vec2 model for accurate laughter detection
- **Audio Processing**: Advanced audio preprocessing with silence detection and amplification
- **Interactive Labeling**: HTML tool for manual laughter annotation
- **Validation Pipeline**: Comprehensive evaluation system with IoU-based metrics
- **Batch Processing**: Efficient processing of multiple audio files
- **Export Options**: Multiple output formats (JSON, CSV) for different use cases

## 📋 Requirements

- Python 3.8+
- PyTorch 1.9+
- CUDA (optional, for GPU acceleration)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd Label
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv laughter_env
```

### 3. Activate Virtual Environment
**Windows:**
```bash
laughter_env\Scripts\activate
```

**Linux/Mac:**
```bash
source laughter_env/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Download the Pre-trained Model

**⚠️ IMPORTANT**: You need to download the pre-trained laughter detection model:

1. **Download from Hugging Face**: [omine-me/LaughterSegmentation](https://huggingface.co/omine-me/LaughterSegmentation/tree/main)
2. **File to download**: `model.safetensors` (1.26 GB)
3. **Place it in**: `models/model.safetensors`

```bash
# Create models directory
mkdir models

# Download the model file and place it in models/model.safetensors
# The model file is 1.26 GB and contains the trained laughter detection weights
```

## 📁 Required Folder Structure (Data Root)

Your base folder (called “data root”) must contain these subfolders:

```
<DATA_ROOT>/
  ├── 1-input-audio/                 # audio files (.wav/.mp3/.m4a/.flac)
  ├── 2-transcript/
  │     ├── {name}_sentences.json    # sentence-level transcript
  │     └── {name}_segments.json     # segment metadata (includes sentence_indexes)
  ├── 3-word-timestamp/              # output: {name}_words.csv
  ├── 4-laughter-detected/           # output: {name}.json (laughter events)
  └── 5-label/                       # output: labeled CSVs
```

Notes:
- If `{name}_words.csv` already exists, alignment is skipped.
- `{name}_words_labeled.csv` files will be written under `5-label/`.

## 🚀 Run the Pipeline

Script: `label-audio.py`

```
# Windows PowerShell
laughter_env/Scripts/python.exe label-audio.py --data-root "D:\\Downloads\\Segment data\\Batch 1 (shrot)"
```

What it does per audio file:
1. Aligns using `{name}_sentences.json` with 0.3s padding (defaults built-in) → writes `3-word-timestamp/{name}_words.csv`
2. Runs laughter detection → writes `4-laughter-detected/{name}.json`
3. Produces labels in `5-label/`:
   - `{name}_segments_labeled.csv`: all segment fields + `laughter_duration`
   - `{name}_words_labeled.csv`: word,start,end + `SourceFile`,`SegmentID`,`LaughterLabel` (S/E/L; N is omitted visually)

Idempotent behavior:
- Skips steps if outputs already exist and are non-empty.
- You can delete any output to regenerate only that step.

### 3. Validation and Evaluation

```bash
python standalone_validation.py
```

This compares model predictions with manual labels and provides:
- F1 Score, Precision, Recall
- Detailed analysis of missed/false detections
- IoU-based evaluation metrics

## 🖥️ Review UI

File: `label_review_ui.html`

How to use:
1. Open the HTML file in your browser
2. Click “Choose folder” and select your data root (e.g., `D:\\Downloads\\Segment data\\Batch 1 (shrot)`)
3. Select an audio file on the left

What you’ll see:
- Segments with total laughter duration (from `5-label/{name}_segments_labeled.csv`)
- Sentences within each segment (from `2-transcript/{name}_sentences.json`)
  - Click “Play sentence” to audition
  - Laughter overlaps within the sentence shown as chips; click to audition that region
- Words with S/E/L labels (from `5-label/{name}_words_labeled.csv`)
  - Color-coded chips (S=green, L=yellow, E=red); click to jump to word timing

## 🔧 Notes and Defaults

- Alignment defaults: sentences + 0.3s padding (internally configurable via env `FORCE_ALIGN_WITH` and `ALIGN_PADDING_SEC` if needed; not required for normal use)
- Laughter model: wav2vec2-based detector (see `Laughter-detection/inference.py`)
- GPU: Auto-detected; CUDA 12.1 builds recommended for speed

## 📊 Performance

The model performance depends on:
- **Audio quality** and preprocessing
- **Laughter characteristics** (duration, intensity, type)
- **Background noise** levels
- **Threshold settings** in inference

## 🎛️ Configuration

### Audio Processing Parameters
- **Sample Rate**: 16kHz
- **Segment Length**: 7 seconds
- **Overlap**: 2 seconds
- **Threshold**: 0.5 (adjustable in inference.py)

### Model Parameters
- **Batch Size**: 10
- **Device**: Auto-detects CUDA/CPU
- **Precision**: Float32

## 🔍 Troubleshooting

### Common Issues

1. **Model not found error**:
   ```
   FileNotFoundError: Model file not found: ./models/model.safetensors
   ```
   **Solution**: Download the model from [Hugging Face](https://huggingface.co/omine-me/LaughterSegmentation/tree/main)

2. **CUDA out of memory**:
   **Solution**: Reduce batch size in `inference.py`

3. **Poor detection accuracy**:
   **Solutions**:
   - Adjust threshold in `inference.py` (line 147)
   - Improve audio quality
   - Use manual labeling tool to create better training data

### Performance Tips

- **Use GPU** for faster inference
- **Preprocess audio** to reduce noise
- **Adjust threshold** based on your use case
- **Validate results** with manual labels

## 📈 Validation Results

The validation system provides:
- **IoU-based evaluation** with configurable thresholds
- **Detailed segment analysis**
- **Performance metrics** (F1, Precision, Recall)
- **Missed/false detection reports**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with validation
5. Submit a pull request

## 📄 License

[Add your license information here]

## 🙏 Acknowledgments

- **Model**: Based on [omine-me/LaughterSegmentation](https://huggingface.co/omine-me/LaughterSegmentation/tree/main)
- **Base Architecture**: wav2vec2 from Hugging Face Transformers
- **Audio Processing**: librosa and pydub libraries

---

**Note**: This system is designed for research and development purposes. For production use, additional testing and validation is recommended. 

## 📊 Scoring Labeled Segments (Global Stats + Ratings)

Script: `mlmodel/Label/score_segments.py`

What it does:
- Scans for `*_segments_labeled.csv` files (and common typo `*_segement_labeled.csv`)
- Computes `laughter_ratio = laughter_duration / duration` per row (clipped to [0,1])
- Aggregates all rows to compute global mean (μ) and std (σ)
- Writes per-file scored CSVs with added columns

Minimal usage (Windows PowerShell):

```powershell
& ".\mlmodel\Label\laughter_env\Scripts\python.exe" \
  ".\mlmodel\Label\score_segments.py" \
  --input-dir "D:\\Downloads\\Segment data" \
  --recursive \
  --write-scores \
  --inplace
```

Flags you’ll typically use:
- `--input-dir`: Root folder containing your batch folders (it will find `5-label/` files under it)
- `--recursive`: Search subfolders recursively for matching CSVs
- `--write-scores`: Write scored CSVs with new columns
- `--inplace`: Overwrite originals (omit to write `*_scored.csv` next to originals)

Output columns added to each CSV:
- `laughter_ratio`: normalized laughter percentage per segment
- `laughter_zscore`: standard score relative to global μ, σ
- `laughter_rating_4pt`: 0–4 rating using ±0.75σ thresholds and a zero-only bin
- `laughter_rating_5pt`: 0–5 rating with bins:
  - 0: score = 0
  - 1: 0 < score ≤ μ − 1σ
  - 2: μ − 1σ < score ≤ μ − 0.5σ
  - 3: μ − 0.5σ < score ≤ μ
  - 4: μ < score ≤ μ + 0.75σ
  - 5: score > μ + 0.75σ
- `global_mean`: μ used for scoring
- `global_std`: σ used for scoring

Stdout JSON example:
```json
{"files_processed": 123, "rows_considered": 4567, "global_mean": 0.1432, "global_std": 0.0821}
```

Notes:
- If you prefer not to overwrite originals, omit `--inplace` to create `*_scored.csv` files.
- Only exact zero ratios map to rating 0; all positive ratios are binned per thresholds above.