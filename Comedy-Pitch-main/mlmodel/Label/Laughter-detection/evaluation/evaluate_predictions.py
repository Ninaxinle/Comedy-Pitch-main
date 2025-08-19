# -*- coding: utf-8 -*-
import argparse
import os
import sys
import json
import pandas as pd
from typing import List, Tuple, Optional, Set


# ---------------- Core evaluation logic (inlined) ---------------- #

def calculate_iou(interval1: Tuple[float, float], interval2: Tuple[float, float]) -> float:
    start1, end1 = interval1
    start2, end2 = interval2
    intersection_start = max(start1, start2)
    intersection_end = min(end1, end2)
    intersection = max(0.0, intersection_end - intersection_start)
    area1 = end1 - start1
    area2 = end2 - start2
    union = area1 + area2 - intersection
    if union == 0:
        return 0.0
    return intersection / union


def _overlap_seconds(interval1: Tuple[float, float], interval2: Tuple[float, float]) -> float:
    start1, end1 = interval1
    start2, end2 = interval2
    return max(0.0, min(end1, end2) - max(start1, start2))


def _gap_before_seconds(pred: Tuple[float, float], label: Tuple[float, float]) -> float:
    pred_start, pred_end = pred
    label_start, _ = label
    if pred_end <= label_start:
        return max(0.0, label_start - pred_end)
    return 0.0


def evaluate_predictions_with_iou(
    predictions: List[Tuple[float, float]],
    labels: List[Tuple[float, float]],
    iou_threshold: float = 0.5,
    tolerance_seconds: float = 0.0,
    min_overlap_seconds: float = 0.0,
    max_start_gap_seconds: float = 0.0,
) -> Tuple[int, int, int, Set[Tuple[float, float]]]:
    """
    1:1 greedy matching with optional soft-match:
    Eligible if IoU >= iou_threshold OR (min_overlap_seconds > 0 and overlap >= min_overlap_seconds)
    OR (max_start_gap_seconds > 0 and end->start gap <= max_start_gap_seconds).
    """
    if len(predictions) == 0 or len(labels) == 0:
        return 0, len(predictions), len(labels), set(labels)

    padded_preds = [(p[0] - tolerance_seconds, p[1] + tolerance_seconds) for p in predictions]

    edges = []  # (score, pred_idx, label_idx, eligible)
    for pi, p in enumerate(padded_preds):
        for li, l in enumerate(labels):
            iou = calculate_iou(p, l)
            overlap = _overlap_seconds(p, l)
            gap_before = _gap_before_seconds(p, l)
            eligible = (
                iou >= iou_threshold or
                (min_overlap_seconds > 0.0 and overlap >= min_overlap_seconds) or
                (max_start_gap_seconds > 0.0 and gap_before <= max_start_gap_seconds)
            )
            score = max(iou, overlap)
            edges.append((score, pi, li, eligible))

    edges.sort(key=lambda x: x[0], reverse=True)

    assigned_preds = set()
    assigned_labels = set()

    for score, pi, li, eligible in edges:
        if not eligible:
            continue
        if pi in assigned_preds or li in assigned_labels:
            continue
        assigned_preds.add(pi)
        assigned_labels.add(li)

    TP = len(assigned_preds)
    FP = len(predictions) - TP
    FN = len(labels) - TP

    not_matched_labels: Set[Tuple[float, float]] = set()
    for li, l in enumerate(labels):
        if li not in assigned_labels:
            not_matched_labels.add(l)

    return TP, FP, FN, not_matched_labels


def calculate_metrics(TP: int, FP: int, FN: int) -> Tuple[float, float, float, float]:
    precision = TP / (TP + FP) if (TP + FP) > 0 else 0.0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0.0
    accuracy = TP / (TP + FP + FN) if (TP + FP + FN) > 0 else 0.0
    f1 = 2 * TP / (2 * TP + FP + FN) if (2 * TP + FP + FN) > 0 else 0.0
    return precision, recall, accuracy, f1


def load_manual_labels(csv_path: str) -> List[Tuple[float, float]]:
    df = pd.read_csv(csv_path)
    return list(zip(df['start_sec'].astype(float), df['end_sec'].astype(float)))


def load_model_predictions_json(json_path: str) -> List[Tuple[float, float]]:
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    predictions: List[Tuple[float, float]] = []
    for segment in data.values():
        predictions.append((float(segment['start_sec']), float(segment['end_sec'])))
    return predictions


def validate_laughter_detection(
    manual_labels_path: str,
    model_predictions_path: str,
    iou_threshold: float = 0.2,
    tolerance_seconds: float = 0.0,
    min_overlap_seconds: float = 0.0,
    max_start_gap_seconds: float = 0.0,
    predictions_override: Optional[List[Tuple[float, float]]] = None,
) -> dict:
    manual_labels = load_manual_labels(manual_labels_path)

    if predictions_override is not None:
        model_predictions = list(predictions_override)
    else:
        if not os.path.exists(model_predictions_path):
            raise FileNotFoundError(f"Model predictions file not found: {model_predictions_path}")
        # Decide by extension
        if model_predictions_path.lower().endswith('.json'):
            model_predictions = load_model_predictions_json(model_predictions_path)
        elif model_predictions_path.lower().endswith('.csv'):
            raise ValueError("CSV predictions not supported here; pass via predictions_override")
        else:
            raise ValueError("Unsupported predictions format; use JSON file or predictions_override")

    TP, FP, FN, not_matched_labels = evaluate_predictions_with_iou(
        model_predictions,
        manual_labels,
        iou_threshold=iou_threshold,
        tolerance_seconds=tolerance_seconds,
        min_overlap_seconds=min_overlap_seconds,
        max_start_gap_seconds=max_start_gap_seconds,
    )

    precision, recall, accuracy, f1 = calculate_metrics(TP, FP, FN)

    return {
        'TP': TP, 'FP': FP, 'FN': FN,
        'precision': precision, 'recall': recall, 'accuracy': accuracy, 'f1': f1,
        'num_predictions': len(model_predictions), 'num_labels': len(manual_labels),
        'not_matched_labels': sorted(list(not_matched_labels)),
    }


# ---------------- CLI for evaluating JSON or CSV predictions ---------------- #

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate laughter predictions (JSON or CSV) against ground-truth labels CSV."
    )
    parser.add_argument("labels_csv", type=str, help="Path to labels CSV file (columns: start_sec,end_sec)")
    parser.add_argument("predictions_path", type=str, help="Path to predictions file (.json or .csv)")
    parser.add_argument("--pred-format", choices=["auto", "json", "csv"], default="auto",
                        help="Format of predictions file (auto-detected by extension if 'auto')")
    parser.add_argument("--source", type=str, default=None,
                        help="For CSV predictions with multiple SourceFile values, filter to this exact SourceFile")
    parser.add_argument("--iou", type=float, default=0.2, help="IoU threshold (default: 0.2)")
    parser.add_argument("--tolerance", type=float, default=0.0,
                        help="Pad prediction intervals by ±tolerance seconds before IoU (default: 0.0)")
    parser.add_argument("--min-overlap", type=float, default=0.0,
                        help="Soft-match: minimum overlap (seconds) to count as match (default: 0.0 = disabled)")
    parser.add_argument("--max-start-gap", type=float, default=0.0,
                        help="Soft-match: max seconds allowed between pred end and label start (default: 0.0 = disabled)")
    return parser.parse_args()


def load_predictions_from_csv(csv_path: str, source_key: Optional[str]) -> List[Tuple[float, float]]:
    df = pd.read_csv(csv_path)
    if "StartTime" not in df.columns or "EndTime" not in df.columns:
        raise ValueError("CSV predictions must contain columns 'StartTime' and 'EndTime'")

    if "SourceFile" in df.columns:
        if source_key is not None:
            df = df[df["SourceFile"] == source_key].copy()
            if df.empty:
                uniques = pd.read_csv(csv_path)["SourceFile"].dropna().unique().tolist()
                raise ValueError(
                    f"No rows match SourceFile={source_key!r}. Available SourceFile values: {uniques}"
                )
        else:
            unique_sources = df["SourceFile"].dropna().unique().tolist()
            if len(unique_sources) > 1:
                raise ValueError(
                    "CSV contains multiple SourceFile values. Please pass --source to select one. "
                    f"Found: {unique_sources}"
                )
    return list(zip(df["StartTime"].astype(float).tolist(), df["EndTime"].astype(float).tolist()))


def main() -> None:
    args = parse_args()

    if not os.path.exists(args.labels_csv):
        print(f"❌ Labels CSV not found: {args.labels_csv}")
        sys.exit(1)
    if not os.path.exists(args.predictions_path):
        print(f"❌ Predictions file not found: {args.predictions_path}")
        sys.exit(1)

    pred_format = args.pred_format
    if pred_format == "auto":
        if args.predictions_path.lower().endswith(".json"):
            pred_format = "json"
        elif args.predictions_path.lower().endswith(".csv"):
            pred_format = "csv"
        else:
            print("❌ Could not auto-detect predictions format. Use --pred-format csv|json")
            sys.exit(1)

    if pred_format == "json":
        results = validate_laughter_detection(
            manual_labels_path=args.labels_csv,
            model_predictions_path=args.predictions_path,
            iou_threshold=args.iou,
            tolerance_seconds=args.tolerance,
            min_overlap_seconds=args.min_overlap,
            max_start_gap_seconds=args.max_start_gap,
            predictions_override=None,
        )
    else:
        predictions = load_predictions_from_csv(args.predictions_path, args.source)
        print(f"Loaded {len(predictions)} prediction intervals from CSV")
        results = validate_laughter_detection(
            manual_labels_path=args.labels_csv,
            model_predictions_path="",
            iou_threshold=args.iou,
            tolerance_seconds=args.tolerance,
            min_overlap_seconds=args.min_overlap,
            max_start_gap_seconds=args.max_start_gap,
            predictions_override=predictions,
        )

    if not results:
        sys.exit(2)

    print("\nSummary:")
    print(f"TP: {results['TP']}  FP: {results['FP']}  FN: {results['FN']}")
    print(f"Precision: {results['precision']:.3f}  Recall: {results['recall']:.3f}  Accuracy: {results['accuracy']:.3f}  F1: {results['f1']:.3f}")


if __name__ == "__main__":
    main()