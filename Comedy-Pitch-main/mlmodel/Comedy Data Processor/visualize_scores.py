import numpy as np
import os
import argparse
from pathlib import Path
import matplotlib.pyplot as plt

def read_score(score_file):
    """Read and interpret a score.npy file."""
    # Load the one-hot encoded score
    one_hot = np.load(score_file)
    
    # Get the index of the "1" in the one-hot vector
    score_value = np.argmax(one_hot)
    
    return score_value

def collect_scores(base_dir):
    """Collect scores from all clips in the directory."""
    base_dir = Path(base_dir)
    
    # Find all clip directories
    clip_dirs = [d for d in base_dir.iterdir() if d.is_dir() and d.name.startswith("clip_")]
    
    scores = []
    clip_ids = []
    
    for clip_dir in sorted(clip_dirs):
        clip_id = clip_dir.name.replace("clip_", "")
        score_file = clip_dir / "score.npy"
        
        if score_file.exists():
            score_value = read_score(score_file)
            scores.append(score_value)
            clip_ids.append(clip_id)
    
    return scores, clip_ids

def visualize_scores(scores, clip_ids, output_file=None):
    """Create visualizations for the collected scores."""
    # Bar plot of scores
    plt.figure(figsize=(10, 6))
    bars = plt.bar(clip_ids, scores, color='skyblue')
    
    # Add score labels on top of bars
    for bar, score in zip(bars, scores):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{score}/4',
                ha='center', va='bottom')
    
    plt.xlabel('Clip ID')
    plt.ylabel('Humor Score (0-4)')
    plt.title('Humor Scores by Clip')
    plt.ylim(0, 4.5)  # Set y-axis limit to accommodate labels
    
    # Add score interpretation guide
    plt.figtext(0.5, 0.01, 
               "Score guide: 0=Not funny (<5%), 1=Slightly funny (5-10%), 2=Moderately funny (10-15%), "
               "3=Very funny (15-20%), 4=Extremely funny (>20%)",
               ha="center", fontsize=9, bbox={"facecolor":"lightgrey", "alpha":0.5, "pad":5})
    
    plt.tight_layout(rect=[0, 0.05, 1, 1])  # Adjust for guide text
    
    if output_file:
        plt.savefig(output_file)
        print(f"Saved visualization to {output_file}")
    else:
        plt.show()

def main():
    parser = argparse.ArgumentParser(description='Visualize comedy clip scores')
    parser.add_argument('--dir', type=str, required=True, 
                       help='Directory containing processed clips (e.g., "output" or "batch_output")')
    parser.add_argument('--output', type=str, default=None,
                       help='Output file path for visualization (default: show interactive plot)')
    
    args = parser.parse_args()
    
    # Collect scores
    scores, clip_ids = collect_scores(args.dir)
    
    if not scores:
        print(f"No score files found in {args.dir}")
        return
    
    print(f"Found {len(scores)} clip scores:")
    for clip_id, score in zip(clip_ids, scores):
        print(f"Clip {clip_id}: {score}/4")
    
    # Visualize scores
    visualize_scores(scores, clip_ids, args.output)

if __name__ == "__main__":
    main() 