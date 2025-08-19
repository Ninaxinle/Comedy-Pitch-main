#!/usr/bin/env python3
import os
import numpy as np
from glob import glob

def update_unfunny_training_files():
    # Directory containing processed clips
    output_dir = 'hybrid_output_0.4_0.5'
    
    # Find all unfunny clip directories
    unfunny_dirs = glob(os.path.join(output_dir, 'clip_unfunny_*'))
    print(f"Found {len(unfunny_dirs)} unfunny clip directories")
    
    # Keep track of updated and skipped files
    updated = 0
    already_zeros = 0
    
    # Process each unfunny directory
    for clip_dir in unfunny_dirs:
        score_file = os.path.join(clip_dir, 'score.npy')
        
        # Check if score file exists
        if os.path.exists(score_file):
            # Load the current score
            current_score = np.load(score_file)
            
            # Check if any element is non-zero
            if np.any(current_score > 0):
                # Create a new score array with all zeros (same shape as original)
                new_score = np.zeros_like(current_score)
                
                # Save the updated score
                np.save(score_file, new_score)
                updated += 1
                print(f"Updated {score_file}: {current_score} -> {new_score}")
            else:
                already_zeros += 1
                print(f"Skipped {score_file} (already all zeros)")
    
    print(f"\nSummary:")
    print(f"- {len(unfunny_dirs)} unfunny clip directories found")
    print(f"- {updated} score files updated to zeros")
    print(f"- {already_zeros} score files already had all zeros")
    print(f"- {len(unfunny_dirs) - updated - already_zeros} clip directories had no score.npy file")

if __name__ == "__main__":
    update_unfunny_training_files() 