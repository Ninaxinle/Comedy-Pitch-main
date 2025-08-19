import os
import numpy as np
import pickle
import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd

def analyze_current_progress():
    # Set the path to the output directory
    output_dir = Path("dataset_output")
    
    # Check if the directory exists
    if not output_dir.exists():
        print(f"Output directory {output_dir} does not exist")
        return
    
    # Get all clip directories
    clip_dirs = [d for d in output_dir.iterdir() if d.is_dir()]
    print(f"Found {len(clip_dirs)} processed clips")
    
    # Initialize data structures
    funny_scores = []
    unfunny_scores = []
    clips_with_data = []
    clips_without_score = []
    clips_without_embedding = []
    
    # Analyze each clip directory
    for clip_dir in clip_dirs:
        clip_id = clip_dir.name
        score_file = clip_dir / "score.npy"
        bert_file = clip_dir / "BertBase.pkl"
        audio_embed_file = clip_dir / "audioembed.npy"
        
        # Check if this is a funny or unfunny clip
        is_funny = "funny" in clip_id.lower()
        category = "funny" if is_funny else "unfunny"
        
        # Track data availability
        has_score = score_file.exists()
        has_bert = bert_file.exists()
        has_audio = audio_embed_file.exists()
        
        # Process score if available
        if has_score:
            try:
                score = np.load(score_file)
                mean_score = float(np.mean(score))
                
                # Add to appropriate list
                if is_funny:
                    funny_scores.append(mean_score)
                else:
                    unfunny_scores.append(mean_score)
                
                # Add to clip data
                clips_with_data.append({
                    'clip_id': clip_id,
                    'category': category,
                    'score': mean_score,
                    'has_bert': has_bert,
                    'has_audio': has_audio
                })
            except Exception as e:
                print(f"Error processing score for {clip_id}: {e}")
                clips_without_score.append(clip_id)
        else:
            clips_without_score.append(clip_id)
        
        # Check for missing embeddings
        if not has_bert or not has_audio:
            clips_without_embedding.append(clip_id)
    
    # Print summary statistics
    print("\n===== SUMMARY STATISTICS =====")
    print(f"Total clips processed: {len(clip_dirs)}")
    print(f"Clips with score data: {len(clips_with_data)}")
    print(f"Clips without score data: {len(clips_without_score)}")
    print(f"Clips missing embeddings: {len(clips_without_embedding)}")
    
    if funny_scores:
        print(f"\nFunny clips analyzed: {len(funny_scores)}")
        print(f"Average funny score: {np.mean(funny_scores):.4f}")
        print(f"Min funny score: {np.min(funny_scores):.4f}")
        print(f"Max funny score: {np.max(funny_scores):.4f}")
    
    if unfunny_scores:
        print(f"\nUnfunny clips analyzed: {len(unfunny_scores)}")
        print(f"Average unfunny score: {np.mean(unfunny_scores):.4f}")
        print(f"Min unfunny score: {np.min(unfunny_scores):.4f}")
        print(f"Max unfunny score: {np.max(unfunny_scores):.4f}")
    
    # Create visualization if we have enough data
    if funny_scores or unfunny_scores:
        # Create output image
        plt.figure(figsize=(10, 6))
        
        # Plot histograms
        if funny_scores:
            plt.hist(funny_scores, alpha=0.7, label='Funny Clips', bins=20, color='green')
        if unfunny_scores:
            plt.hist(unfunny_scores, alpha=0.7, label='Unfunny Clips', bins=20, color='red')
        
        plt.title('Distribution of Humor Scores')
        plt.xlabel('Humor Score')
        plt.ylabel('Number of Clips')
        plt.legend()
        plt.grid(alpha=0.3)
        
        # Save figure
        output_file = 'current_progress_scores.png'
        plt.savefig(output_file)
        print(f"\nVisualization saved to {output_file}")
        
        # Create sorted dataframe of all clips with scores
        if clips_with_data:
            df = pd.DataFrame(clips_with_data)
            df_sorted = df.sort_values(by='score', ascending=False)
            
            # Save top scores to CSV
            csv_file = 'current_scores.csv'
            df_sorted.to_csv(csv_file, index=False)
            print(f"Top scores saved to {csv_file}")
            
            # Print top 10 funny clips
            funny_df = df_sorted[df_sorted['category'] == 'funny']
            print("\n===== TOP 10 FUNNY CLIPS =====")
            for i, row in funny_df.head(10).iterrows():
                print(f"{row['clip_id']}: {row['score']:.4f}")
            
            # Print top 10 unfunny clips (should be lower scores)
            unfunny_df = df_sorted[df_sorted['category'] == 'unfunny']
            print("\n===== TOP 10 UNFUNNY CLIPS =====")
            for i, row in unfunny_df.head(10).iterrows():
                print(f"{row['clip_id']}: {row['score']:.4f}")

if __name__ == "__main__":
    analyze_current_progress() 