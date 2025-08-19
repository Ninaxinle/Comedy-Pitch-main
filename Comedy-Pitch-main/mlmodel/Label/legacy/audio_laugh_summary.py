import pandas as pd

# === File paths ===
transcript_path = "/Users/molly/Desktop/DFWAI2025/Data/sampleTestLaugh/transcript/transcript_summary.csv"
laughter_path = "/Users/molly/Desktop/DFWAI2025/Data/sampleTestLaugh/segments/laugh_segments.csv"
output_path = "/Users/molly/Desktop/DFWAI2025/Data/sampleTestLaugh/label/audio_laugh_summary.csv"

# === Load transcript CSV ===
df_transcript = pd.read_csv(transcript_path)

# === Load laughter segments CSV ===
df_laughter = pd.read_csv(laughter_path)

# === Aggregate laughter statistics for each audio file ===
df_laughter_stats = df_laughter.groupby("AudioFileID").agg(
    LaughterCount=("LaughterID", "count"),
    TotalLaughterDuration=("Duration", "sum")
).reset_index()

# === Merge the transcript info with laughter statistics ===
df_summary = pd.merge(df_transcript, df_laughter_stats, on="AudioFileID", how="left")

# === Fill missing values for audio files with no laughter ===
df_summary["LaughterCount"] = df_summary["LaughterCount"].fillna(0).astype(int)
df_summary["TotalLaughterDuration"] = df_summary["TotalLaughterDuration"].fillna(0).round(2)

# === Save the combined summary to CSV ===
df_summary.to_csv(output_path, index=False)
print(f"✅ Summary saved to: {output_path}")
