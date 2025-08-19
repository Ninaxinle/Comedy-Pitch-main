import numpy as np
import os
import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

def read_score(score_file):
    """Read and interpret a score.npy file."""
    # Load the one-hot encoded score
    one_hot = np.load(score_file)
    
    # Get the index of the "1" in the one-hot vector
    score_value = np.argmax(one_hot)
    
    return score_value, one_hot

def get_score_label(score_value):
    """Get text label for score value."""
    labels = {
        0: "Not funny",
        1: "Slightly funny",
        2: "Moderately funny",
        3: "Very funny",
        4: "Extremely funny"
    }
    return labels.get(score_value, "Unknown")

def analyze_scores(directory):
    """Analyze all scores in the given directory."""
    base_dir = Path(directory)
    
    # Find all clip directories
    clip_dirs = [d for d in base_dir.iterdir() if d.is_dir() and d.name.startswith("clip_")]
    
    if not clip_dirs:
        print(f"No clip directories found in {base_dir}")
        return
    
    print(f"Found {len(clip_dirs)} processed clips")
    
    # Initialize counters and data structures
    score_counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
    funny_scores = []
    unfunny_scores = []
    all_data = []
    
    # Process each clip
    for clip_dir in clip_dirs:
        clip_id = clip_dir.name
        score_file = clip_dir / "score.npy"
        
        if score_file.exists():
            try:
                score_value, one_hot = read_score(score_file)
                
                # Determine if it's a funny or unfunny clip based on name
                is_funny = clip_id.startswith("clip_funny_") 
                category = "Funny" if is_funny else "Unfunny"
                
                # Use the original score for all clips
                score_counts[score_value] += 1
                
                # Add to appropriate list
                if is_funny:
                    funny_scores.append(score_value)
                else:
                    unfunny_scores.append(score_value)
                
                # Add to dataset
                all_data.append({
                    'clip_id': clip_id,
                    'score': score_value,
                    'score_label': get_score_label(score_value),
                    'category': category
                })
                
            except Exception as e:
                print(f"Error processing {clip_id}: {e}")
    
    # Calculate statistics
    total_clips = sum(score_counts.values())
    
    # Print summary
    print("\n===== SCORE DISTRIBUTION =====")
    for score, count in score_counts.items():
        percentage = (count / total_clips * 100) if total_clips > 0 else 0
        print(f"{get_score_label(score)} (Score {score}): {count} clips ({percentage:.1f}%)")
    
    # Print category stats
    print(f"\nFunny clips: {len(funny_scores)}")
    print(f"Unfunny clips: {len(unfunny_scores)}")
    
    if funny_scores:
        avg_funny = sum(funny_scores) / len(funny_scores)
        print(f"Average funny score: {avg_funny:.2f}/4")
    
    if unfunny_scores:
        avg_unfunny = sum(unfunny_scores) / len(unfunny_scores)
        print(f"Average unfunny score: {avg_unfunny:.2f}/4")
    
    # Create visualizations
    if all_data:
        df = pd.DataFrame(all_data)
        
        # Create histogram of all scores
        plt.figure(figsize=(12, 6))
        plt.subplot(1, 2, 1)
        
        # Plot scores by category
        bars = plt.bar(
            list(score_counts.keys()),
            list(score_counts.values()),
            color='skyblue'
        )
        
        # Annotate bars with count
        for i, bar in enumerate(bars):
            plt.text(
                bar.get_x() + bar.get_width()/2,
                bar.get_height() + 1,
                str(score_counts[i]),
                ha='center'
            )
        
        plt.title('Humor Score Distribution')
        plt.xlabel('Score')
        plt.ylabel('Number of Clips')
        plt.xticks(list(score_counts.keys()), [get_score_label(i) for i in score_counts.keys()], rotation=45, ha='right')
        plt.tight_layout()
        
        # Create subplot for category comparison if we have both funny and unfunny
        if funny_scores and unfunny_scores:
            plt.subplot(1, 2, 2)
            
            # Count scores by category
            funny_counts = [0, 0, 0, 0, 0]
            unfunny_counts = [0, 0, 0, 0, 0]
            
            for score in funny_scores:
                funny_counts[score] += 1
                
            for score in unfunny_scores:
                unfunny_counts[score] += 1
            
            # Plot grouped bar chart
            x = np.arange(5)  # 5 score categories
            width = 0.35
            
            plt.bar(x - width/2, funny_counts, width, label='Funny', color='green', alpha=0.7)
            plt.bar(x + width/2, unfunny_counts, width, label='Unfunny', color='red', alpha=0.7)
            
            plt.title('Scores by Category')
            plt.xlabel('Score')
            plt.ylabel('Number of Clips')
            plt.xticks(x, [get_score_label(i) for i in range(5)], rotation=45, ha='right')
            plt.legend()
            plt.tight_layout()
        
        plt.savefig('score_distribution.png')
        print("\nSaved visualization to score_distribution.png")
        
        # Create a sorted CSV file
        df_sorted = df.sort_values(by=['category', 'score'], ascending=[True, False])
        df_sorted.to_csv('all_scores.csv', index=False)
        print("Saved all scores to all_scores.csv")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze humor score distribution')
    parser.add_argument('--dir', type=str, default='dataset_output', 
                       help='Directory containing processed clips')
    
    args = parser.parse_args()
    analyze_scores(args.dir) 