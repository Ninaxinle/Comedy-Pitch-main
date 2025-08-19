#!/usr/bin/env python3
import subprocess
import os
import sys

# Path to audio file
audio_file = r"I:\Dropbox\Voice memos\2025-05-21_asian gene.m4a"

# First, convert the audio to WAV format (simpler for laughter detection)
try:
    import librosa
    import soundfile as sf
    print("Converting audio to WAV format...")
    y, sr = librosa.load(audio_file, sr=None)
    wav_path = "test_audio.wav"
    sf.write(wav_path, y, sr)
    print(f"Converted to {wav_path}")
except Exception as e:
    print(f"Error converting audio: {e}")
    sys.exit(1)

# Create output directory
out_dir = "laughter_test_output"
os.makedirs(out_dir, exist_ok=True)

# Get absolute paths for clarity
wav_path_abs = os.path.abspath(wav_path)
out_dir_abs = os.path.abspath(out_dir)
laugher_detection_dir = os.path.abspath(os.path.join('libs', 'laughter-detection'))

# Set up environment variables for subprocess
env = os.environ.copy()

# The key fix: Set PYTHONPATH correctly
# We only need the laughter-detection dir since we'll run from there
if 'PYTHONPATH' in env:
    env['PYTHONPATH'] = f"{laugher_detection_dir}{os.pathsep}{env['PYTHONPATH']}"
else:
    env['PYTHONPATH'] = laugher_detection_dir

# Run the laughter detection script directly, but specify just the script name
# since we'll change the working directory
cmd = [
    sys.executable,
    'segment_laughter.py',  # Just the script name, we'll set cwd
    '--input_audio_file', wav_path_abs,
    '--output_dir', out_dir_abs,
    '--save_to_textgrid', 'True', 
    '--save_to_audio_files', 'True',
    '--min_length', '0.2',
    '--threshold', '0.3',
    '--num_workers', '0'
]

print("\nRunning laughter detection from the laughter-detection directory:")
print(f"Command: {' '.join(cmd)}")
print(f"Working directory: {laugher_detection_dir}")
print(f"PYTHONPATH: {env.get('PYTHONPATH', '')}")

# Run the command from the laughter-detection directory
try:
    result = subprocess.run(
        cmd,
        cwd=laugher_detection_dir,  # Set working directory
        env=env,
        capture_output=True,
        text=True
    )
    
    print(f"\nExit code: {result.returncode}")
    
    print("\nSTDOUT:")
    print(result.stdout)
    
    print("\nSTDERR:")
    print(result.stderr)
    
except Exception as e:
    print(f"Error running laughter detection: {e}")
    sys.exit(1)

# Check if the output directory exists and list its contents
print(f"\nContents of {out_dir}:")
if os.path.exists(out_dir):
    files = os.listdir(out_dir)
    if files:
        for f in files:
            print(f"- {f}")
        
        # Check if any TextGrid files were created
        textgrid_files = [f for f in files if f.endswith('.TextGrid')]
        if textgrid_files:
            print(f"\nFound TextGrid file: {textgrid_files[0]}")
        else:
            print("\nNo TextGrid files found")
    else:
        print("Directory is empty")
else:
    print("Directory does not exist") 