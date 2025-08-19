# 🎭 Word-Level Laughter Labeling Pipeline

This repository contains scripts to analyze stand-up comedy audio by labeling each word in the transcript based on whether it occurs inside or outside of audience laughter.

# Word-Level Laughter Labeling

This project processes MP3 audio files to detect laughter and label each word based on whether it's spoken during audience laughter.

## Features

- Transcribe audio using WhisperX
- Detect laughter segments with a pretrained model
- Label each word as:
  - `S`: Start of laughter
  - `L`: Laughter continues
  - `E`: End of laughter
  - `N`: Not during laughter
- If no words overlap with laughter, a `__LAUGHTER__` row is added

Run Steps:

- transcript_text.py — transcribe audio to word timestamps

- laugh_segment.py — detect laughter and save segments

- label_words_laughter.py — generate labeled word tables







