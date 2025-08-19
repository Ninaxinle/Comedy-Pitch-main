import argparse
import json
import sys
from pathlib import Path
from typing import Iterable, List, Tuple

import numpy as np
import pandas as pd


def find_segment_csvs(
    input_dir: Path,
    recursive: bool = False,
) -> List[Path]:
    """
    Find segment label CSVs inside input_dir.

    Supports both the correct pattern "*_segments_labeled.csv" and the common typo
    "*_segement_labeled.csv".
    """
    pattern_depth = "**/" if recursive else ""
    patterns = [
        f"{pattern_depth}*_segments_labeled.csv",
        f"{pattern_depth}*_segement_labeled.csv",
    ]
    matches: List[Path] = []
    for pat in patterns:
        matches.extend(sorted(input_dir.glob(pat)))
    # Remove duplicates (possible if patterns overlap)
    unique = []
    seen = set()
    for p in matches:
        if p.resolve() not in seen:
            unique.append(p)
            seen.add(p.resolve())
    return unique


def load_ratios_from_file(
    csv_path: Path,
    clip_01: bool = True,
    min_duration: float = 0.0,
) -> Tuple[pd.Series, pd.DataFrame]:
    """
    Load a segments_labeled CSV and compute laughter_ratio per row.

    Returns the ratio Series and the DataFrame with a new "laughter_ratio" column.
    Rows with invalid or nonpositive durations are dropped for ratio stats.
    """
    try:
        df = pd.read_csv(csv_path, encoding="utf-8")
    except UnicodeDecodeError:
        # Fallback for possible BOM or mixed encodings
        df = pd.read_csv(csv_path, encoding="utf-8-sig")

    required_cols = {"laughter_duration", "duration"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(
            f"Missing required columns {sorted(missing)} in {csv_path.name}"
        )

    # Compute ratio
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = df["laughter_duration"].astype(float) / df["duration"].astype(float)

    # Optionally clip to [0,1] to guard against minor labeling drift
    if clip_01:
        ratio = ratio.clip(lower=0.0, upper=1.0)

    df = df.copy()
    df["laughter_ratio"] = ratio

    # Filter rows considered for global stats
    valid_mask = (
        df["duration"].astype(float) > min_duration
    ) & df["laughter_ratio"].notna()

    return df.loc[valid_mask, "laughter_ratio"], df


def compute_global_stats(ratios: Iterable[float]) -> Tuple[float, float]:
    arr = np.asarray(list(ratios), dtype=float)
    if arr.size == 0:
        return float("nan"), float("nan")
    return float(np.mean(arr)), float(np.std(arr, ddof=1))


def write_scored_file(
    original_df: pd.DataFrame,
    output_path: Path,
    global_mean: float,
    global_std: float,
) -> None:
    """
    Write a scored CSV with added columns based on provided global stats:
    - laughter_ratio (already present from preprocessing)
    - laughter_zscore
    - laughter_rating_4pt (0-4 as per threshold table with ±0.75σ)
    - laughter_rating_5pt (0-5 scale, top bin uses μ + 1.0σ; zero-laughter remains 0)
    """
    df = original_df.copy()

    # Remove any legacy rating columns to avoid duplicates in output
    legacy_cols = [
        "laughter_rating_0to5",
        "laughter_rating_5pt",
    ]
    for col in legacy_cols:
        if col in df.columns:
            df = df.drop(columns=[col])

    # Z-score
    if np.isnan(global_std) or global_std == 0.0:
        df["laughter_zscore"] = np.nan
    else:
        df["laughter_zscore"] = (df["laughter_ratio"] - global_mean) / global_std

    # Ratings
    if np.isnan(global_mean) or np.isnan(global_std) or global_std == 0.0:
        df["laughter_rating_4pt"] = np.nan
        df["laughter_rating_5pt"] = np.nan
    else:
        lower = global_mean - 0.75 * global_std
        upper = global_mean + 0.75 * global_std
        ratio = df["laughter_ratio"].astype(float)

        conditions = [
            ratio.eq(0.0),
            (ratio > 0.0) & (ratio <= lower),
            (ratio > lower) & (ratio <= global_mean),
            (ratio > global_mean) & (ratio <= upper),
            (ratio > upper),
        ]
        choices = [0, 1, 2, 3, 4]
        rating_4 = np.select(conditions, choices, default=np.nan)
        df["laughter_rating_4pt"] = rating_4
        # 5-point (0..5) per requested bins:
        # 0: score == 0
        # 1: 0 < score ≤ μ − 1σ
        # 2: μ − 1σ < score ≤ μ − 0.5σ
        # 3: μ − 0.5σ < score ≤ μ
        # 4: μ < score ≤ μ + 0.75σ
        # 5: score > μ + 0.75σ
        lower_1 = global_mean - 1.0 * global_std
        lower_05 = global_mean - 0.5 * global_std
        upper_075 = global_mean + 0.75 * global_std
        conditions_5 = [
            ratio.eq(0.0),
            (ratio > 0.0) & (ratio <= lower_1),
            (ratio > lower_1) & (ratio <= lower_05),
            (ratio > lower_05) & (ratio <= global_mean),
            (ratio > global_mean) & (ratio <= upper_075),
            (ratio > upper_075),
        ]
        choices_5 = [0, 1, 2, 3, 4, 5]
        df["laughter_rating_5pt"] = np.select(conditions_5, choices_5, default=np.nan)

    # Persist global stats as columns for downstream reference
    df["global_mean"] = global_mean if not np.isnan(global_mean) else None
    df["global_std"] = global_std if not np.isnan(global_std) else None

    df.to_csv(output_path, index=False, encoding="utf-8")


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Compute global laughter stats across *_segments_labeled.csv files.\n"
            "For each row: laughter_ratio = laughter_duration / duration.\n"
            "Outputs global mean and standard deviation across all valid rows."
        )
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        required=True,
        help="Directory containing one or more *_segments_labeled.csv files.",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recurse into subdirectories to find CSVs.",
    )
    parser.add_argument(
        "--min-duration",
        type=float,
        default=0.0,
        help="Exclude rows with duration <= this threshold (default: 0.0).",
    )
    parser.add_argument(
        "--no-clip",
        action="store_true",
        help="Do not clip laughter_ratio to [0,1].",
    )
    parser.add_argument(
        "--write-scores",
        action="store_true",
        help=(
            "After computing global stats, write per-file scored CSVs with"
            " added columns: laughter_ratio and laughter_zscore."
        ),
    )
    parser.add_argument(
        "--inplace",
        action="store_true",
        help=(
            "If set with --write-scores, overwrite original files in place."
            " Otherwise writes alongside with suffix _scored.csv."
        ),
    )

    args = parser.parse_args(argv)

    input_dir: Path = args.input_dir
    if not input_dir.exists() or not input_dir.is_dir():
        print(
            json.dumps(
                {
                    "error": "input_dir_not_found",
                    "input_dir": str(input_dir),
                }
            ),
            file=sys.stdout,
        )
        print(f"[ERROR] Input directory not found: {input_dir}", file=sys.stderr)
        return 2

    csv_files = find_segment_csvs(input_dir, recursive=args.recursive)
    if not csv_files:
        print(
            json.dumps(
                {
                    "files_processed": 0,
                    "rows_considered": 0,
                    "global_mean": None,
                    "global_std": None,
                    "note": "No matching *_segments_labeled.csv files found",
                }
            ),
            file=sys.stdout,
        )
        print(
            f"[WARN] No CSVs found in {input_dir} (recursive={args.recursive})",
            file=sys.stderr,
        )
        return 0

    all_ratios: List[float] = []
    per_file_frames: List[Tuple[Path, pd.DataFrame]] = []

    clip_01 = not args.no_clip
    for csv_path in csv_files:
        try:
            ratios, df_with_ratio = load_ratios_from_file(
                csv_path, clip_01=clip_01, min_duration=args.min_duration
            )
        except Exception as exc:  # pylint: disable=broad-except
            print(f"[ERROR] Failed to load {csv_path}: {exc}", file=sys.stderr)
            continue

        all_ratios.extend(ratios.tolist())
        per_file_frames.append((csv_path, df_with_ratio))

    global_mean, global_std = compute_global_stats(all_ratios)

    result = {
        "files_processed": len(per_file_frames),
        "rows_considered": int(len(all_ratios)),
        "global_mean": None if np.isnan(global_mean) else global_mean,
        "global_std": None if np.isnan(global_std) else global_std,
    }

    # Print final metrics to stdout as JSON for easy downstream use
    print(json.dumps(result, ensure_ascii=False), file=sys.stdout)

    # Emit debug info to stderr
    print(
        f"[INFO] Processed {result['files_processed']} files,"
        f" {result['rows_considered']} rows → mean={result['global_mean']},"
        f" std={result['global_std']}",
        file=sys.stderr,
    )

    if args.write_scores and not np.isnan(global_mean) and not np.isnan(global_std):
        for csv_path, df in per_file_frames:
            if args.inplace:
                out_path = csv_path
            else:
                out_path = csv_path.with_name(csv_path.stem + "_scored.csv")
            try:
                write_scored_file(df, out_path, global_mean, global_std)
                print(
                    f"[INFO] Wrote scores → {out_path}",
                    file=sys.stderr,
                )
            except Exception as exc:  # pylint: disable=broad-except
                print(
                    f"[ERROR] Failed to write scores for {csv_path}: {exc}",
                    file=sys.stderr,
                )

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

