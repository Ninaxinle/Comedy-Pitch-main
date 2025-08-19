# 🎙️ AI-OpenMic Preprocessing Output Format

This document describes the expected **output files** of this project to train a humor rating model for the [AI-OpenMic](https://github.com/cfiltnlp/AI-OpenMic) project.

Each processed clip should produce **three aligned files**:

---

## 📁 Output Directory Structure (per clip)

```
/clip_0001/
  ├── audioembed.npy         # shape: (33, 8000)
  ├── BertBase.pkl           # shape: (512, 768)
  └── score.npy              # shape: (5,)
```

---

## ✅ File Descriptions

### 1. `audioembed.npy`

- **Format**: `.npy` (NumPy array)
- **Shape**: `(33, 8000)`
- **Content**: Audio features extracted from the **laughter-muted** audio clip.
  - Features may include MFCCs, RMS energy, and spectrogram filters.
- **Details**:
  - Use a tool like [`laughr`](https://github.com/jeffgreenca/laughr) or [`laughter-detection`](https://github.com/jrgillick/laughter-detection) to remove audience laughter.
  - Use `librosa` or similar to extract features.
  - Pad or truncate to exactly 8000 time frames.

---

### 2. `BertBase.pkl`

- **Format**: `.pkl` (Pickle file) or `.npy`
- **Shape**: `(512, 768)` *(for BERT-base)* or `(512, 1024)` *(for RoBERTa-large)*
- **Content**: Token-wise BERT embeddings for the clip's transcript.
- **Details**:
  - Tokenize the transcript (max 512 tokens).
  - Generate embeddings using a pretrained transformer model (e.g. BERT, RoBERTa).
  - **Sum the final 4 hidden layers** for each token to get a rich contextual embedding.

---

### 3. `score.npy`

- **Format**: `.npy` (NumPy array)
- **Shape**: `(5,)`
- **Content**: One-hot encoded humor score on a 5-point Likert scale (0 = not funny, 4 = very funny).
- **How to generate**:
  - Detect audience laughter in the original clip.
  - Compute total laughter duration.
  - Normalize: `laughter_duration / clip_duration`
  - Assign a score using thresholds based on dataset-wide mean (μ) and std (σ).
  - Convert score (0–4) to one-hot vector.

---

## 🧠 Summary Table

| File           | Format | Shape        | Description                            |
|----------------|--------|--------------|----------------------------------------|
| `audioembed.npy` | `.npy` | (33, 8000)   | Voice/audio features from muted clip   |
| `BertBase.pkl`   | `.pkl` | (512, 768)   | Transcript token embeddings from BERT  |
| `score.npy`      | `.npy` | (5,)         | One-hot humor score from laughter      |

---

## 🛠️ Tools Recommended

- **Text embeddings**: HuggingFace Transformers (e.g., `bert-base-uncased`)
- **Audio features**: `librosa`, `numpy`
- **Laughter detection**: [`laughr`](https://github.com/jeffgreenca/laughr), [`laughter-detection`](https://github.com/jrgillick/laughter-detection)
- **Embedding storage**: Python `pickle` or `np.save`

---

## 🔗 Reference

For more details, see the [AI-OpenMic GitHub project](https://github.com/cfiltnlp/AI-OpenMic) and the associated [EMNLP 2021 paper](https://aclanthology.org/2021.emnlp-main.492/).