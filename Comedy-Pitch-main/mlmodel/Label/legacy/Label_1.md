# Label_1: Audio Laugh Analysis 

This project processes `.mp3` audio files to extract:

- Speech transcription using WhisperX
- Laughter segments using a pre-trained laughter segmentation model
- A final summary table with transcript, audio duration, number of laughs, and total laughter time

## Scripts

- `inference.py` – runs laughter detection and outputs `.json` files
- `laugh_segment.py` – converts laughter `.json` files into a CSV
- `transcript_text.py` – uses WhisperX to transcribe audio and save transcript + duration
- `audio_laugh_summary.py` – merges transcript and laughter info into a final summary

## Output

The final result is a CSV file like this:

| AudioFileID     | TranscriptText           | AudioDuration | LaughterCount | TotalLaughterDuration |
|------------------|--------------------------|----------------|----------------|------------------------|
| AJ_TP_audio_01  | Thank you, San Francisco. | 89.38          | 12             | 20.6                   |

## Requirements

- Python 3.8+
- whisperx
- torch
- pandas
- openpyxl

## Notes

- You need to download the WhisperX and laughter segmentation models in advance.
- WhisperX：https://github.com/m-bain/whisperX
- laughter segmentation model：https://github.com/omine-me/LaughterSegmentation
- All intermediate and final files are saved into ’SampleLabelData‘ folders.

