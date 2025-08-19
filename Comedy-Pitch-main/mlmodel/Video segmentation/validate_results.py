#!/usr/bin/env python3
"""
Simple validation script to check pipeline results
"""

import json
import os
from pathlib import Path

def validate_pipeline_output():
    """Check the pipeline output files."""
    
    # Find transcript files
    transcript_files = list(Path("transcripts").glob("*_sentences.json"))
    
    if not transcript_files:
        print("❌ No transcript files found")
        return
    
    transcript_file = transcript_files[0]
    print(f"📄 Reading transcript: {transcript_file.name}")
    
    try:
        with open(transcript_file, 'r', encoding='utf-8') as f:
            sentences = json.load(f)
        
        print(f"✅ Found {len(sentences)} sentences")
        print(f"📊 Total duration: {sentences[-1]['end_time']:.1f} seconds")
        
        print("\n🎭 First few sentences:")
        for i, sentence in enumerate(sentences[:5]):
            print(f"  {i}: {sentence['text'][:70]}...")
            print(f"     ⏱️  {sentence['start_time']:.1f}s - {sentence['end_time']:.1f}s")
        
        print(f"\n📈 Sample timing data:")
        print(f"  Average sentence length: {sum(s['end_time'] - s['start_time'] for s in sentences) / len(sentences):.1f}s")
        print(f"  Shortest sentence: {min(s['end_time'] - s['start_time'] for s in sentences):.1f}s")
        print(f"  Longest sentence: {max(s['end_time'] - s['start_time'] for s in sentences):.1f}s")
        
    except Exception as e:
        print(f"❌ Error reading transcript: {e}")

if __name__ == "__main__":
    validate_pipeline_output() 