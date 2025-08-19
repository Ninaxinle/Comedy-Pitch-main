# -*- coding: utf-8 -*-
import os
from evaluation.evaluate_predictions import validate_laughter_detection

BASE = os.path.join("evaluation", "data-to-evaluate")
LABEL_DIR = os.path.join(BASE, "label")
PRED_DIR = os.path.join(BASE, "inference-results")

# Find Adele files by substring to avoid quoting issues
label_csv = None
pred_json = None

for name in os.listdir(LABEL_DIR):
    if "Adele Givens - Full Special" in name and name.endswith(".csv"):
        label_csv = os.path.join(LABEL_DIR, name)
        break

for name in os.listdir(PRED_DIR):
    if "Adele Givens - Full Special" in name and name.endswith(".json"):
        pred_json = os.path.join(PRED_DIR, name)
        break

if not label_csv or not pred_json:
    raise SystemExit(f"Could not locate files. label_csv={label_csv}, pred_json={pred_json}")

results = validate_laughter_detection(
    manual_labels_path=label_csv,
    model_predictions_path=pred_json,
    iou_threshold=0.1,
    tolerance_seconds=0.5,
    min_overlap_seconds=0.0,
    max_start_gap_seconds=0.0,
    predictions_override=None,
)

print("Files:")
print(f"  Labels: {label_csv}")
print(f"  Predictions: {pred_json}")
print("\nSummary:")
print(f"TP: {results['TP']}  FP: {results['FP']}  FN: {results['FN']}")
print(f"Precision: {results['precision']:.3f}  Recall: {results['recall']:.3f}  Accuracy: {results['accuracy']:.3f}  F1: {results['f1']:.3f}")