import numpy as np
import os
import argparse
from pathlib import Path

def read_score(score_file):
    """Read and interpret a score.npy file.
    
    Args:
        score_file: Path to the score.npy file
        
    Returns:
        Tuple of (score_value, one_hot_array)
    """
    # Load the one-hot encoded score
    one_hot = np.load(score_file)
    
    # Get the index of the "1" in the one-hot vector
    score_value = np.argmax(one_hot)
    
    return score_value, one_hot

def interpret_score(score_value):
    """Provide a text interpretation of the score value."""
    interpretations = {
        0: "Not funny (laughter ratio < 5%)",
        1: "Slightly funny (laughter ratio 5-10%)",
        2: "Moderately funny (laughter ratio 10-15%)",
        3: "Very funny (laughter ratio 15-20%)",
        4: "Extremely funny (laughter ratio > 20%)"
    }
    return interpretations.get(score_value, "Unknown score")

def main():
    parser = argparse.ArgumentParser(description='Read and display comedy clip scores')
    parser.add_argument('--dir', type=str, required=True, 
                       help='Directory containing processed clips (e.g., "output" or "batch_output")')
    
    args = parser.parse_args()
    
    base_dir = Path(args.dir)
    
    # Find all clip directories
    clip_dirs = [d for d in base_dir.iterdir() if d.is_dir() and d.name.startswith("clip_")]
    
    if not clip_dirs:
        print(f"No clip directories found in {base_dir}")
        return
    
    print(f"Found {len(clip_dirs)} processed clips:")
    print("-" * 60)
    
    for clip_dir in sorted(clip_dirs):
        clip_id = clip_dir.name.replace("clip_", "")
        score_file = clip_dir / "score.npy"
        
        if score_file.exists():
            score_value, one_hot = read_score(score_file)
            interpretation = interpret_score(score_value)
            
            print(f"Clip ID: {clip_id}")
            print(f"Score: {score_value}/4")
            print(f"Interpretation: {interpretation}")
            print(f"One-hot vector: {one_hot}")
            print("-" * 60)
        else:
            print(f"Clip ID: {clip_id} - No score file found")
            print("-" * 60)

if __name__ == "__main__":
    main() 