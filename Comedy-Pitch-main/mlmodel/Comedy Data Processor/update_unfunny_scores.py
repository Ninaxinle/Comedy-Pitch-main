#!/usr/bin/env python3
import pandas as pd

def update_unfunny_scores():
    # Read the scores CSV file
    print("Reading all_scores.csv...")
    df = pd.read_csv('all_scores.csv')
    
    # Count how many unfunny videos exist
    unfunny_count = len(df[df['category'] == 'Unfunny'])
    print(f"Found {unfunny_count} unfunny videos")
    
    # Count how many unfunny videos already have score 0
    already_zero = len(df[(df['category'] == 'Unfunny') & (df['score'] == 0)])
    print(f"Of these, {already_zero} already have a score of 0")
    
    # Count how many need to be updated
    to_update = unfunny_count - already_zero
    print(f"Need to update {to_update} unfunny videos to score 0")
    
    # Update all unfunny videos to have score 0
    df.loc[df['category'] == 'Unfunny', 'score'] = 0
    
    # Also update the score_label to "Not funny" for consistency
    df.loc[df['category'] == 'Unfunny', 'score_label'] = 'Not funny'
    
    # Save the updated CSV file
    print("Saving updated scores to all_scores.csv...")
    df.to_csv('all_scores.csv', index=False)
    print("Done!")

if __name__ == "__main__":
    update_unfunny_scores() 