import os
import sys
import json
import importlib.util
import unicodedata
import argparse
# Torch is optional; used only to detect CUDA availability. Fall back to CPU if missing.
try:  # pragma: no cover
    import torch  # type: ignore
except Exception:  # pragma: no cover
    torch = None  # type: ignore
import pandas as pd
import numpy as np

try:
    import soundfile as sf  # preferred for robust read/write
except Exception:  # pragma: no cover
    sf = None


def load_module_from_path(module_name: str, file_path: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module {module_name} from {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_laughter_detection(script_dir: str, audio_path: str, output_root: str) -> None:
    ld_dir = os.path.join(script_dir, "Laughter-detection")
    model_path = os.path.join(ld_dir, "Models", "model.safetensors")
    output_dir = os.path.join(output_root, "4-laughter-detected")
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    laughter_json_path = os.path.join(output_dir, base_name + ".json")

    # Skip if laughter output already exists
    if os.path.exists(laughter_json_path) and os.path.getsize(laughter_json_path) > 0:
        print(f"⏭️  Laughter already exists, skipping: {laughter_json_path}")
        return

    # Load and run Laughter-detection/inference.py programmatically
    inference_path = os.path.join(ld_dir, "inference.py")
    print(f"🎯 Running laughter detection → {os.path.basename(audio_path)}")
    # Ensure local imports in inference.py (e.g., numpy_patch) resolve
    if ld_dir not in sys.path:
        sys.path.insert(0, ld_dir)
    inference = load_module_from_path("laughter_inference", inference_path)
    # inference.main(audio_path, output_dir, model_path)
    try:
        inference.main(audio_path, output_dir, model_path)
        print(f"✅ Laughter JSON saved in: {output_dir}")
    except Exception as e:
        print(f"⚠️  Laughter detection failed for {os.path.basename(audio_path)}: {e}")


def main(data_root: str | None = None):
    # Set up paths for data-to-label pipeline
    script_dir = os.path.dirname(__file__)
    base_root = data_root if data_root else os.path.join(script_dir, "data-to-label")
    input_folder = os.path.join(base_root, "1-input-audio")
    transcript_folder = os.path.join(base_root, "2-transcript")
    output_folder = os.path.join(base_root, "3-word-timestamp")

    # Create output directory if not exists
    os.makedirs(output_folder, exist_ok=True)

    # Choose device and compute type
    if torch is not None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        device = "cpu"
    compute_type = "int8" if device == "cpu" else "float16"

    # Defer loading WhisperX alignment model until needed
    print(f"🔍 Device selected: {device}")
    model_a = None
    metadata = None

    # Loop through each audio file
    for filename in os.listdir(input_folder):
        if filename.endswith((".wav", ".mp3", ".m4a", ".flac")):
            audio_path = os.path.join(input_folder, filename)
            base_name = os.path.splitext(filename)[0]
            segments_path = os.path.join(transcript_folder, f"{base_name}_segments.json")
            sentences_path = os.path.join(transcript_folder, f"{base_name}_sentences.json")

            # Decide alignment source
            # Default: sentences (faster here and robust with coalescing)
            force_align_with = os.environ.get("FORCE_ALIGN_WITH", "").strip().lower()
            input_json_path = None
            input_type = None
            # Load presence flags
            has_segments = os.path.exists(segments_path)
            has_sentences = os.path.exists(sentences_path)
            if force_align_with in ("segments", "segment", "seg") and has_segments:
                input_json_path = segments_path
                input_type = "segments"
            elif force_align_with in ("sentences", "sentence", "sent") and has_sentences:
                input_json_path = sentences_path
                input_type = "sentences"
            else:
                # Default behavior: prefer sentences if available
                if has_sentences:
                    input_json_path = sentences_path
                    input_type = "sentences"
                elif has_segments:
                    input_json_path = segments_path
                    input_type = "segments"
                else:
                    print(f"⚠️  No transcript JSON found for {filename} (looked for *_sentences.json and *_segments.json), skipping...")
                    continue

            print(f"🔍 Processing: {filename}")

            # Step 1: Load existing transcript JSON (sentences preferred)
            with open(input_json_path, "r", encoding="utf-8") as f:
                segments_data = json.load(f)

            # Convert to WhisperX format
            # Handle both segment-level and sentence-level schemas with keys start_time/end_time/text
            def normalize_text(s: str) -> str:
                # Normalize Unicode, replace smart quotes/dashes with ASCII equivalents
                s = unicodedata.normalize("NFKC", s)
                replacements = {
                    "“": '"', "”": '"', "‘": "'", "’": "'",
                    "–": "-", "—": "-", "…": "..."
                }
                for k, v in replacements.items():
                    s = s.replace(k, v)
                return " ".join(s.split())

            raw_segments = []
            for seg in segments_data:
                start = seg.get("start_time") or seg.get("start")
                end = seg.get("end_time") or seg.get("end")
                text = seg.get("text", "")
                if start is None or end is None:
                    continue
                raw_segments.append({
                    "start": float(start),
                    "end": float(end),
                    "text": normalize_text(str(text))
                })

            # If using sentence-level, merge very short sentences into windows for more robust alignment
            def coalesce_short(sent_list, min_window_sec: float = 2.0, min_chars: int = 20):
                if input_type != "sentences":
                    return sent_list
                coalesced = []
                cur = None
                for seg in sent_list:
                    duration = float(seg["end"]) - float(seg["start"])
                    if cur is None:
                        cur = dict(seg)
                        continue
                    window_dur = float(cur["end"]) - float(cur["start"])
                    window_chars = len(cur["text"])
                    if window_dur < min_window_sec or window_chars < min_chars or duration < 0.6:
                        # merge into current window
                        cur["end"] = max(cur["end"], seg["end"])
                        cur["text"] = (cur["text"] + " " + seg["text"]).strip()
                    else:
                        coalesced.append(cur)
                        cur = dict(seg)
                if cur is not None:
                    coalesced.append(cur)
                return coalesced

            segments = coalesce_short(raw_segments)

            # Add small padding around each segment for better acoustic context
            # Default padding 0.3s (can override via ALIGN_PADDING_SEC)
            pad_sec = float(os.environ.get("ALIGN_PADDING_SEC", "0.3"))
            if pad_sec > 0:
                # Get audio duration lazily via torchaudio.info to avoid heavy decode
                try:
                    import torchaudio
                    info = torchaudio.info(audio_path)
                    audio_dur = float(info.num_frames) / float(info.sample_rate)
                except Exception:
                    audio_dur = None
                padded = []
                for s in segments:
                    start = max(0.0, float(s["start"]) - pad_sec)
                    end_val = float(s["end"]) + pad_sec
                    if audio_dur is not None:
                        end_val = min(end_val, audio_dur)
                    padded.append({"start": start, "end": end_val, "text": s["text"]})
                segments = padded

            # Save path for word timestamps
            output_path = os.path.join(output_folder, f"{base_name}_words.csv")

            # Step 2: Perform alignment for word-level timestamps (skip if exists)
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                print(f"⏭️  Words already exist, skipping: {output_path}")
            else:
                # Lazy-import whisperx only if alignment is actually required
                try:
                    import whisperx  # type: ignore
                except Exception as e:  # pragma: no cover
                    raise RuntimeError(
                        "whisperx is required for alignment but is not installed. Install with: pip install -U whisperx"
                    ) from e

                if model_a is None or metadata is None:
                    model_a, metadata = whisperx.load_align_model(language_code="en", device=device)

                print(f"🔄 Aligning {len(segments)} {input_type}...")
                result_aligned = whisperx.align(segments, model_a, metadata, audio_path, device)

                # Step 3: Export word data to CSV
                word_data = []
                for seg in result_aligned["word_segments"]:
                    word_data.append({
                        "word": seg["word"],
                        "start": seg["start"],
                        "end": seg["end"]
                    })

                df = pd.DataFrame(word_data)
                df.to_csv(output_path, index=False)
                print(f"✅ Saved to: {output_path} ({len(word_data)} words)")

            # Step 4: Run laughter detection and save JSON
            data_root_dir = base_root
            run_laughter_detection(script_dir, audio_path, data_root_dir)

            # Step 5: Generate labels (segment-level and word-level)
            labels_dir = os.path.join(base_root, "5-label")
            os.makedirs(labels_dir, exist_ok=True)

            # Load laughter events JSON
            laughter_json_path = os.path.join(data_root, "4-laughter-detected", f"{base_name}.json")
            laughter_events = {}
            if os.path.exists(laughter_json_path):
                try:
                    with open(laughter_json_path, "r", encoding="utf-8") as lf:
                        laughter_events = json.load(lf)
                except Exception:
                    laughter_events = {}

            # Helper: compute overlap duration between [a1,a2] and [b1,b2]
            def overlap_seconds(a1, a2, b1, b2):
                lo = max(a1, b1)
                hi = min(a2, b2)
                return max(0.0, hi - lo)

            # 5.1 Segment-level labels: copy segments.json + laughter_duration column
            seg_out_csv = os.path.join(labels_dir, f"{base_name}_segments_labeled.csv")
            if os.path.exists(segments_path) and not (os.path.exists(seg_out_csv) and os.path.getsize(seg_out_csv) > 0):
                with open(segments_path, "r", encoding="utf-8") as f:
                    seg_list = json.load(f)
                # Flatten to DataFrame preserving all original keys
                seg_df = pd.DataFrame(seg_list)
                # Compute laughter duration per segment
                durations = []
                # Prepare events list
                events = []
                for ev in (laughter_events or {}).values():
                    try:
                        events.append((float(ev["start_sec"]), float(ev["end_sec"])))
                    except Exception:
                        continue
                for _, seg in seg_df.iterrows():
                    s = float(seg.get("start_time", seg.get("start", 0.0)))
                    e = float(seg.get("end_time", seg.get("end", 0.0)))
                    total = 0.0
                    for (ls, le) in events:
                        total += overlap_seconds(s, e, ls, le)
                    durations.append(round(total, 3))
                seg_df["laughter_duration"] = durations
                seg_df.to_csv(seg_out_csv, index=False)
                print(f"✅ Segment labels: {seg_out_csv}")
            else:
                if os.path.exists(seg_out_csv):
                    print(f"⏭️  Segment labels exist, skipping: {seg_out_csv}")

            # 5.2 Word-level labels: words CSV + SourceFile + SegmentID + LaughterLabel
            words_out_csv = os.path.join(labels_dir, f"{base_name}_words_labeled.csv")
            if not (os.path.exists(words_out_csv) and os.path.getsize(words_out_csv) > 0):
                if os.path.exists(output_path):
                    words_df = pd.read_csv(output_path)
                    # Add SourceFile
                    words_df["SourceFile"] = filename
                    # Map words to segments to assign SegmentID
                    seg_list_for_map = []
                    if os.path.exists(segments_path):
                        with open(segments_path, "r", encoding="utf-8") as f:
                            seg_list_for_map = json.load(f)
                    # Build list of (start,end,segment_id)
                    seg_intervals = []
                    for seg in seg_list_for_map:
                        try:
                            s = float(seg.get("start_time", seg.get("start", 0.0)))
                            e = float(seg.get("end_time", seg.get("end", 0.0)))
                            sid = seg.get("segment_id")
                            seg_intervals.append((s, e, sid))
                        except Exception:
                            continue
                    def lookup_segment_id(mid):
                        for (s, e, sid) in seg_intervals:
                            if s <= mid <= e:
                                return sid
                        return None
                    # Assign SegmentID per word mid-point
                    mids = (words_df["start"].astype(float) + words_df["end"].astype(float)) / 2.0
                    words_df["SegmentID"] = [lookup_segment_id(m) for m in mids]

                    # LaughterLabel per laughter events
                    words_df["LaughterLabel"] = "N"
                    # Prepare sorted indices by start for efficient overlap search
                    words_df = words_df.sort_values("start").reset_index(drop=True)
                    # Build events sorted
                    events_sorted = []
                    for ev in (laughter_events or {}).values():
                        try:
                            events_sorted.append((float(ev["start_sec"]), float(ev["end_sec"])))
                        except Exception:
                            continue
                    events_sorted.sort(key=lambda x: x[0])

                    insert_rows = []
                    for (ls, le) in events_sorted:
                        overlap_mask = (words_df["end"] > ls) & (words_df["start"] < le)
                        overlap_idx = words_df.index[overlap_mask].tolist()
                        if not overlap_idx:
                            # insert virtual laugh marker if no word overlaps
                            mid = (ls + le) / 2.0
                            # Determine segment id for virtual row
                            v_sid = lookup_segment_id(mid)
                            insert_rows.append({
                                "word": "__LAUGHTER__",
                                "start": mid - 0.001,
                                "end": mid + 0.001,
                                "SourceFile": filename,
                                "SegmentID": v_sid,
                                "LaughterLabel": "L",
                            })
                            continue
                        # Label first/middle/last
                        # Ensure chronological order
                        overlap_idx.sort(key=lambda i: float(words_df.loc[i, "start"]))
                        for pos, idxw in enumerate(overlap_idx):
                            if pos == 0:
                                words_df.at[idxw, "LaughterLabel"] = "S"
                            elif pos == len(overlap_idx) - 1:
                                words_df.at[idxw, "LaughterLabel"] = "E"
                            else:
                                words_df.at[idxw, "LaughterLabel"] = "L"

                    if insert_rows:
                        words_df = pd.concat([words_df, pd.DataFrame(insert_rows)], ignore_index=True)
                        words_df = words_df.sort_values("start").reset_index(drop=True)

                    words_df.to_csv(words_out_csv, index=False)
                    print(f"✅ Word labels: {words_out_csv}")
                else:
                    print(f"⚠️  Words CSV not found, skipping word labels: {output_path}")
            else:
                print(f"⏭️  Word labels exist, skipping: {words_out_csv}")

            # Step 6: Produce laughter-muted audio with identical duration
            muted_dir = os.path.join(base_root, "6-laughter-muted-audio")
            os.makedirs(muted_dir, exist_ok=True)

            # Build list of [start, end] intervals from laughter_events
            intervals = []
            if isinstance(laughter_events, dict):
                ev_iter = laughter_events.values()
            elif isinstance(laughter_events, list):
                ev_iter = laughter_events
            else:
                ev_iter = []

            for ev in ev_iter:
                try:
                    s = float(ev.get("start_sec", ev.get("start", ev.get("startTime", 0.0))))
                    e = float(ev.get("end_sec", ev.get("end", ev.get("endTime", 0.0))))
                    if e > s:
                        intervals.append((s, e))
                except Exception:
                    continue

            # If there are no intervals, still emit a passthrough copy as *_muted.wav
            muted_out_path = os.path.join(muted_dir, f"{base_name}_muted.wav")

            def _write_audio_wav(data_array: np.ndarray, sr: int, path: str) -> None:
                # Expect shape (num_frames, num_channels)
                if sf is not None:
                    sf.write(path, data_array, sr)
                else:  # fallback via librosa + soundfile late import if available
                    try:
                        import soundfile as _sf  # type: ignore
                        _sf.write(path, data_array, sr)
                    except Exception as _:
                        raise RuntimeError("soundfile is required to write audio; please install with pip install soundfile")

            def _read_audio_any(path: str) -> tuple[np.ndarray, int]:
                # Returns (num_frames, num_channels), sample_rate
                if sf is not None:
                    data, sr = sf.read(path, always_2d=True)
                    # shape (frames, channels)
                    return data.astype(np.float32, copy=False), int(sr)
                # Fallback to librosa
                try:
                    import librosa  # type: ignore
                    y, sr = librosa.load(path, sr=None, mono=False)
                    if y.ndim == 1:
                        y = y[:, None]  # (frames, 1)
                    else:
                        y = y.T  # (frames, channels)
                    return y.astype(np.float32, copy=False), int(sr)
                except Exception as _:
                    raise RuntimeError("Neither soundfile nor librosa available to read audio")

            try:
                audio_data, sr = _read_audio_any(audio_path)
                num_frames = audio_data.shape[0]

                # Zero samples inside laughter intervals with padding
                mute_pad = float(os.environ.get("MUTE_PADDING_SEC", "0.1"))
                for (ls, le) in intervals:
                    start_idx = max(0, int(round((ls - mute_pad) * sr)))
                    end_idx = min(num_frames, int(round((le + mute_pad) * sr)))
                    if end_idx > start_idx:
                        audio_data[start_idx:end_idx, :] = 0.0

                _write_audio_wav(audio_data, sr, muted_out_path)
                print(f"✅ Laughter-muted audio: {muted_out_path}")
            except Exception as e:
                print(f"⚠️  Failed to create laughter-muted audio for {filename}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", dest="data_root", type=str, default=None, help="Base folder that contains 1-input-audio, 2-transcript, ... If not set, defaults to <repo>/mlmodel/Label/data-to-label")
    args = parser.parse_args()
    main(args.data_root)

