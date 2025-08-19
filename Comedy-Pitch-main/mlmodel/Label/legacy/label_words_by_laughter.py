import pandas as pd
import os

# Input paths
transcript_folderpath = "/Users/molly/Desktop/DFWAI2025/Data/sampleTestLaugh/transcript/word_time_stamp"
laughter_path = "/Users/molly/Desktop/DFWAI2025/Data/sampleTestLaugh/segments/laugh_segments.csv"
output_path = "/Users/molly/Desktop/DFWAI2025/Data/sampleTestLaugh/label/labeled_words"
os.makedirs(output_path, exist_ok=True)

# Load laughter data
laughter_df = pd.read_csv(laughter_path)

# Function to apply labeling
def label_words_by_laughter(word_df, laughter_segments, audio_id):
    word_df["LaughterLabel"] = "N"
    insert_rows = []

    for _, row in laughter_segments.iterrows():
        start, end = row["StartTime"], row["EndTime"]
        overlap = word_df[(word_df["end"] > start) & (word_df["start"] < end)]

        if overlap.empty:
            # Insert virtual laugh label if no word overlaps
            insert_rows.append({
                "word": "__LAUGHTER__",
                "start": (start + end) / 2 - 0.001,
                "end": (start + end) / 2 + 0.001,
                "AudioFileID": audio_id,
                "LaughterLabel": "L"
            })
        else:
            overlap_sorted = overlap.sort_values("start")
            indices = overlap_sorted.index.tolist()
            for i, idx in enumerate(indices):
                if i == 0:
                    word_df.loc[idx, "LaughterLabel"] = "S"
                elif i == len(indices) - 1:
                    word_df.loc[idx, "LaughterLabel"] = "E"
                else:
                    word_df.loc[idx, "LaughterLabel"] = "L"

    # Append virtual rows if needed
    if insert_rows:
        virtual_df = pd.DataFrame(insert_rows)
        word_df = pd.concat([word_df, virtual_df], ignore_index=True)

    return word_df.sort_values("start")

# Process each file
for file in os.listdir(transcript_folderpath):
    if file.endswith("_words.csv"):
        audio_id = file.replace("_words.csv", "")
        word_df = pd.read_csv(os.path.join(transcript_folderpath, file))
        if "AudioFileID" not in word_df.columns:
            word_df["AudioFileID"] = audio_id

        segments = laughter_df[laughter_df["AudioFileID"] == audio_id]
        labeled_df = label_words_by_laughter(word_df, segments, audio_id)

        output_file = os.path.join(output_path, f"{audio_id}_words_labeled.csv")
        labeled_df.to_csv(output_file, index=False)
        print(f"✅ Labeled file saved: {output_file}")
