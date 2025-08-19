import os
import torch
import whisperx
import pandas as pd

# Set up paths
input_folder = "/Users/molly/Desktop/DFWAI2025/Data/sampleTestLaugh/testMp3"
output_folder = "/Users/molly/Desktop/DFWAI2025/Data/sampleTestLaugh/transcript/word_time_stamp"

# Create output directory if not exists
os.makedirs(output_folder, exist_ok=True)

# Choose device and compute type
device = "cuda" if torch.cuda.is_available() else "cpu"
compute_type = "int8" if device == "cpu" else "float16"

# Load base WhisperX model
model = whisperx.load_model("large-v3", device, compute_type=compute_type)

# Loop through each MP3 file
for filename in os.listdir(input_folder):
    if filename.endswith(".mp3"):
        audio_path = os.path.join(input_folder, filename)
        print(f"🔍 Processing: {filename}")

        # Step 1: Transcribe audio
        result = model.transcribe(audio_path, batch_size=16)

        # Step 2: Load alignment model
        model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)

        # Step 3: Perform alignment for word-level timestamps
        result_aligned = whisperx.align(result["segments"], model_a, metadata, audio_path, device)

        # Step 4: Export word data to CSV
        word_data = []
        for seg in result_aligned["word_segments"]:
            word_data.append({
                "word": seg["word"],
                "start": seg["start"],
                "end": seg["end"]
            })

        df = pd.DataFrame(word_data)

        # Save to individual CSV file
        base_name = os.path.splitext(filename)[0]
        output_path = os.path.join(output_folder, f"{base_name}_words.csv")
        df.to_csv(output_path, index=False)
        print(f"✅ Saved to: {output_path}")
