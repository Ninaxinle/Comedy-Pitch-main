import os
import torch
import whisperx
import pandas as pd
import librosa

# Set input/output paths
audio_folder = "/Users/molly/Desktop/DFWAI2025/Data/sampleTestLaugh/testMp3"
output_folder = "/Users/molly/Desktop/DFWAI2025/Data/sampleTestLaugh/transcript"
os.makedirs(output_folder, exist_ok=True)

# Path for final summary CSV
csv_output_path = os.path.join(output_folder, "transcript_summary.csv")

# Load main WhisperX model
device = "cuda" if torch.cuda.is_available() else "cpu"
model = whisperx.load_model("large-v3", device, compute_type="int8")

# Initialize transcript summary
summary = []

# Loop through all MP3 files
for file_name in os.listdir(audio_folder):
    if file_name.endswith(".mp3"):
        audio_path = os.path.join(audio_folder, file_name)
        audio_id = os.path.splitext(file_name)[0]
        print(f"🔍 Transcribing: {audio_id}")

        # Step 1: Transcribe audio
        result = model.transcribe(audio_path, batch_size=16)

        # Step 2: Load alignment model
        model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)

        # Step 3: Get word-level timestamps
        result_aligned = whisperx.align(result["segments"], model_a, metadata, audio_path, device)

        # Step 4: Save full transcript to .txt
        full_text = " ".join([seg["text"].strip() for seg in result["segments"]])
        txt_path = os.path.join(output_folder, f"{audio_id}.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(full_text)

        # Step 5: Get audio duration in seconds
        duration_sec = round(librosa.get_duration(path=audio_path), 2)

        # Step 6: Append info to summary
        summary.append({
            "AudioFileID": audio_id,
            "TranscriptText": full_text,
            "AudioDuration": duration_sec
        })

# Step 7: Save transcript summary CSV
df = pd.DataFrame(summary)
df.to_csv(csv_output_path, index=False)
print(f"\n✅ All done! Transcript summary saved to: {csv_output_path}")
