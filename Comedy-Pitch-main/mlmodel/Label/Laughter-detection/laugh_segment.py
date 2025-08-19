import os
import subprocess
import json
import pandas as pd

# Set paths
audio_folder = "/Users/molly/Desktop/DFWAI2025/Data/sampleTestLaugh/testMp3"
output_dir = "/Users/molly/Desktop/DFWAI2025/Data/sampleTestLaugh/results"
excel_path = os.path.join(output_dir, "laugh_segments.csv")

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

summary = []

# Loop through all MP3 files
for file_name in os.listdir(audio_folder):
    if file_name.endswith(".mp3"):
        audio_path = os.path.join(audio_folder, file_name)
        print(f"Processing {file_name}...")

        # Run inference.py via subprocess
        subprocess.run([
            "python", "inference.py",
            "--audio_path", audio_path,
            "--output_dir", output_dir
        ])

        # Read generated JSON file
        base_name = os.path.splitext(file_name)[0]
        result_path = os.path.join(output_dir, base_name + ".json")

        if os.path.exists(result_path):
            with open(result_path, "r") as f:
                data = json.load(f)

                for laugh_id, segment in data.items():
                    start = segment.get("start_sec")
                    end = segment.get("end_sec")
                    duration = round(end - start, 2) if start is not None and end is not None else None

                    summary.append({
                        "AudioFileID": base_name,
                        "LaughterID": laugh_id,
                        "StartTime": round(start, 2),
                        "EndTime": round(end, 2),
                        "Duration": duration
                    })

# Write to Excel
df = pd.DataFrame(summary)
df.to_csv(excel_path, index=False)

print(f"✅ All done! Results saved to: {excel_path}")
