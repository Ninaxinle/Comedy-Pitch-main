# GPU Installation Guide

## 🚀 For GPU Acceleration (Recommended)

If you have an NVIDIA GPU, follow these steps for much faster processing:

### 1. Install CUDA-enabled PyTorch

```bash
# Remove CPU-only PyTorch first (if installed)
pip uninstall torch torchvision torchaudio -y

# Install CUDA-enabled versions
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 2. Install other dependencies

```bash
pip install openai-whisper openai moviepy PyYAML ffmpeg-python
```

### 3. Verify GPU is working

```bash
python -c "import torch; print('CUDA Available:', torch.cuda.is_available())"
```

Should output: `CUDA Available: True`

## 💻 For CPU-only Installation

If you don't have a GPU or prefer CPU-only:

```bash
pip install -r requirements.txt
```

## 🎯 Performance Comparison

- **CPU (base model)**: ~42 seconds for 7-minute video
- **GPU (large model)**: ~18 seconds for 7-minute video
- **GPU Benefits**: 2-3x faster + higher accuracy with larger models

## 🔧 Troubleshooting

**CUDA not detected:**
- Ensure you have NVIDIA GPU drivers installed
- Check CUDA toolkit compatibility (12.1+ recommended)
- Verify PyTorch CUDA installation: `torch.version.cuda`

**Memory issues:**
- Use smaller Whisper model in `config.yaml`: `model: "base"`
- Process videos one at a time instead of batch processing 