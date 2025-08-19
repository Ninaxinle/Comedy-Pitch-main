import os
import sys
import argparse
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Analyze the hybrid processed dataset')
    parser.add_argument('--dir', type=str, required=True, 
                      help='Directory containing processed clips (e.g., "hybrid_output_0.4_0.5")')
    
    args = parser.parse_args()
    
    # Run analyze_score_distribution.py on the hybrid output
    logger.info(f"Analyzing score distribution for {args.dir}")
    
    import subprocess
    cmd = [
        sys.executable,
        "analyze_score_distribution.py",
        "--dir", args.dir
    ]
    
    try:
        logger.info(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Error analyzing scores: {result.stderr}")
            return 1
            
        logger.info(result.stdout)
        logger.info(f"Analysis complete. Check all_scores.csv for the results.")
        
        # Print the number of funny and unfunny clips
        import pandas as pd
        df = pd.read_csv("all_scores.csv")
        
        funny_clips = df[df["category"] == "Funny"]
        unfunny_clips = df[df["category"] == "Unfunny"]
        
        print("\nSUMMARY:")
        print(f"Total clips: {len(df)}")
        print(f"Funny clips: {len(funny_clips)}")
        print(f"Unfunny clips: {len(unfunny_clips)}")
        
        print("\nFUNNY SCORE DISTRIBUTION:")
        print(funny_clips["score"].value_counts().sort_index())
        
        print("\nUNFUNNY SCORE DISTRIBUTION:")
        print(unfunny_clips["score"].value_counts().sort_index())
        
        return 0
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 