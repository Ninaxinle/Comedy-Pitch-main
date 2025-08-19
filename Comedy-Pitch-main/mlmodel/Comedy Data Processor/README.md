# Comedy Data Processor

A Python-based project for processing comedy audio clips to extract features for humor rating models.

## 🎯 Purpose

This tool processes comedy audio clips to create standardized outputs required by the [AI-OpenMic](https://github.com/cfiltnlp/AI-OpenMic) project. For each clip, it:

1. Detects and segments audience laughter
2. Creates laughter-muted audio versions
3. Extracts audio features (MFCCs, spectral features, etc.)
4. Generates BERT embeddings from transcripts
5. Assigns humor scores based on laughter intensity

## 🛠️ Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/yourusername/comedy-data-processor.git
cd comedy-data-processor
pip install -r requirements.txt
```

This project depends on the `laughter-detection` library, which is included as a submodule.

## 📋 Usage

### Processing the Entire Dataset

The main entry point for processing the AI-OpenMic dataset is `process_dataset.py`:

```bash
python process_dataset.py --dataset_dir "AI_open_mic_dataset" --output_dir "dataset_output" --csv_output "processed_clips.csv"
```

Additional options:
- `--funny_limit NUMBER`: Limit the number of funny clips to process
- `--unfunny_limit NUMBER`: Limit the number of unfunny clips to process  
- `--only_funny`: Process only funny clips
- `--only_unfunny`: Process only unfunny clips

### Hybrid Threshold Processing

For better classification results, use the hybrid threshold approach that applies different laughter detection thresholds to funny and unfunny clips:

```bash
python batch_process_hybrid.py --input_dir "AI_open_mic_dataset" --output_dir "hybrid_output" --funny_threshold 0.4 --unfunny_threshold 0.5
```

This approach helps eliminate false positives in unfunny clips while maintaining detection sensitivity for funny clips.

### Processing a Single Clip

For processing individual audio clips:

```bash
python process_clip.py --audio "/path/to/comedy_clip.wav" --transcript "Comedy clip transcript here" --id "unique_id" --output_dir "output"
```

### Processing Multiple Clips

To process multiple clips from a CSV file:

```bash
python batch_process.py --input_csv sample_clips.csv --output_dir output
```

Format of the CSV file (sample_clips.csv):
```
audio_path,transcript,clip_id
/path/to/audio1.mp3,"Transcript for clip 1",0001
/path/to/audio2.mp3,"Transcript for clip 2",0002
```

### Preparing Clips for Model Inference

To prepare new audio clips for inference with a trained model:

```bash
python prepare_clip_embeddings.py --audio "/path/to/new_recording.mp3" --transcript "/path/to/transcript.txt" --output_dir "inference_output" --id "custom_id" --threshold 0.5
```

This will:
1. Convert the audio to WAV format if needed
2. Detect and mute laughter segments using the specified threshold
3. Generate audio embeddings from the muted audio
4. Generate text embeddings from the transcript
5. Save all files in the format expected by the model
6. Delete the score.npy file (not needed for inference)
7. Return the embeddings ready for model prediction

This script uses the same `ClipProcessor` class as the training pipeline for consistency.

### Testing the Pipeline

To test the pipeline with an example audio file:

```bash
python test_laughter.py
```

For verbose testing output:

```bash
python test_laughter_verbose.py
```

## 📊 Reading Scores and Outputs

### Reading Scores

To read and display the humor scores for processed clips:

```bash
python read_scores.py --dir output
```

This will display the numerical score (0-4), the one-hot encoded vector, and an interpretation of the score.

### Reading All Outputs

To read and display detailed information about all outputs (scores, audio features, BERT embeddings):

```bash
python read_all_outputs.py --dir output
```

For a summary view:

```bash
python read_all_outputs.py --dir output --summary
```

To analyze a specific clip:

```bash
python read_all_outputs.py --dir output --clip_id 0001
```

### Visualizing Scores

To visualize humor scores across multiple clips:

```bash
python visualize_scores.py --dir output --output humor_scores.png
```

For analyzing score distribution:

```bash
python analyze_score_distribution.py --input all_scores.csv --output score_distribution.png
```

## 📁 Output Format

Each processed clip produces three aligned files in the output directory:

```
/clip_0001/
  ├── audioembed.npy         # shape: (33, 8000)
  ├── BertBase.pkl           # shape: (512, 768)
  └── score.npy              # shape: (5,)
```

See [README_OpenMic_Format.md](README_OpenMic_Format.md) for detailed specifications.

## 📊 Humor Score Calculation

Humor scores are calculated based on laughter ratio (total laughter duration / clip duration):

- Score 0: < 5% laughter
- Score 1: 5-10% laughter
- Score 2: 10-15% laughter
- Score 3: 15-20% laughter
- Score 4: > 20% laughter

Scores are one-hot encoded in a vector of shape (5,).

## 🔧 Customization

- Adjust laughter detection parameters in `_run_laughter_detection` method
- Modify score thresholds in `_generate_humor_score` method
- Change audio feature extraction in `_extract_audio_features` method 