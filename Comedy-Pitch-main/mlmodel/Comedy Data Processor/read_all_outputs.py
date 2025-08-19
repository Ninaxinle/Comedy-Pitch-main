import numpy as np
import os
import argparse
import pickle
from pathlib import Path

def read_score(score_file):
    """Read and interpret a score.npy file."""
    # Load the one-hot encoded score
    one_hot = np.load(score_file)
    
    # Get the index of the "1" in the one-hot vector
    score_value = np.argmax(one_hot)
    
    interpretations = {
        0: "Not funny (laughter ratio < 5%)",
        1: "Slightly funny (laughter ratio 5-10%)",
        2: "Moderately funny (laughter ratio 10-15%)",
        3: "Very funny (laughter ratio 15-20%)",
        4: "Extremely funny (laughter ratio > 20%)"
    }
    interpretation = interpretations.get(score_value, "Unknown score")
    
    return {
        "score_value": score_value,
        "one_hot": one_hot,
        "interpretation": interpretation
    }

def read_audio_features(audio_file):
    """Read audio features from audioembed.npy file."""
    features = np.load(audio_file)
    return {
        "shape": features.shape,
        "mean": np.mean(features),
        "std": np.std(features),
        "min": np.min(features),
        "max": np.max(features)
    }

def read_bert_embeddings(bert_file):
    """Read BERT embeddings from BertBase.pkl file."""
    with open(bert_file, 'rb') as f:
        embeddings = pickle.load(f)
    
    return {
        "shape": embeddings.shape,
        "mean": np.mean(embeddings),
        "std": np.std(embeddings),
        "min": np.min(embeddings),
        "max": np.max(embeddings)
    }

def main():
    parser = argparse.ArgumentParser(description='Read and display all processed clip outputs')
    parser.add_argument('--dir', type=str, required=True, 
                       help='Directory containing processed clips (e.g., "output" or "batch_output")')
    parser.add_argument('--clip_id', type=str, default=None,
                       help='Specific clip ID to analyze (optional)')
    parser.add_argument('--summary', action='store_true',
                       help='Show only a summary of all clips')
    
    args = parser.parse_args()
    
    base_dir = Path(args.dir)
    
    # Find all clip directories or a specific one
    if args.clip_id:
        clip_dirs = [base_dir / f"clip_{args.clip_id}"]
        if not clip_dirs[0].exists():
            print(f"Clip directory not found: {clip_dirs[0]}")
            return
    else:
        clip_dirs = [d for d in base_dir.iterdir() if d.is_dir() and d.name.startswith("clip_")]
    
    if not clip_dirs:
        print(f"No clip directories found in {base_dir}")
        return
    
    # Summary mode
    if args.summary:
        print(f"Summary of {len(clip_dirs)} processed clips:")
        print("-" * 60)
        
        for clip_dir in sorted(clip_dirs):
            clip_id = clip_dir.name.replace("clip_", "")
            score_file = clip_dir / "score.npy"
            
            if score_file.exists():
                score_info = read_score(score_file)
                print(f"Clip ID: {clip_id} - Score: {score_info['score_value']}/4 - {score_info['interpretation']}")
            else:
                print(f"Clip ID: {clip_id} - No score file found")
        
        return
    
    # Detailed mode
    print(f"Found {len(clip_dirs)} processed clips:")
    
    for clip_dir in sorted(clip_dirs):
        clip_id = clip_dir.name.replace("clip_", "")
        print("\n" + "=" * 60)
        print(f"CLIP: {clip_id}")
        print("=" * 60)
        
        # Read score
        score_file = clip_dir / "score.npy"
        if score_file.exists():
            try:
                score_info = read_score(score_file)
                print("\nSCORE:")
                print(f"Value: {score_info['score_value']}/4")
                print(f"Interpretation: {score_info['interpretation']}")
                print(f"One-hot vector: {score_info['one_hot']}")
            except Exception as e:
                print(f"Error reading score file: {e}")
        else:
            print("\nSCORE: Not found")
        
        # Read audio features
        audio_file = clip_dir / "audioembed.npy"
        if audio_file.exists():
            try:
                audio_info = read_audio_features(audio_file)
                print("\nAUDIO FEATURES:")
                print(f"Shape: {audio_info['shape']} (Expected: (33, 8000))")
                print(f"Mean: {audio_info['mean']:.4f}")
                print(f"Std: {audio_info['std']:.4f}")
                print(f"Range: [{audio_info['min']:.4f}, {audio_info['max']:.4f}]")
            except Exception as e:
                print(f"Error reading audio features file: {e}")
        else:
            print("\nAUDIO FEATURES: Not found")
        
        # Read BERT embeddings
        bert_file = clip_dir / "BertBase.pkl"
        if bert_file.exists():
            try:
                bert_info = read_bert_embeddings(bert_file)
                print("\nBERT EMBEDDINGS:")
                print(f"Shape: {bert_info['shape']} (Expected: (512, 768))")
                print(f"Mean: {bert_info['mean']:.4f}")
                print(f"Std: {bert_info['std']:.4f}")
                print(f"Range: [{bert_info['min']:.4f}, {bert_info['max']:.4f}]")
            except Exception as e:
                print(f"Error reading BERT embeddings file: {e}")
        else:
            print("\nBERT EMBEDDINGS: Not found")

if __name__ == "__main__":
    main() 