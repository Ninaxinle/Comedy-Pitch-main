import os
import sys
import subprocess
import librosa
import soundfile as sf

def get_audio_duration(audio_path):
    """Get the duration of an audio file in seconds."""
    try:
        y, sr = librosa.load(audio_path, sr=None)
        duration = librosa.get_duration(y=y, sr=sr)
        return duration
    except Exception as e:
        print(f"[ERROR] Failed to get audio duration: {e}")
        return None

def inspect_audio(input_file):
    """Print detailed info about the audio file."""
    try:
        print(f"[INFO] Analyzing audio file: {input_file}")
        duration = get_audio_duration(input_file)
        print(f"[INFO] Audio duration: {duration:.2f} seconds")
        
        # Load file with librosa to check basic properties
        y, sr = librosa.load(input_file, sr=None)
        print(f"[INFO] Sample rate: {sr} Hz")
        print(f"[INFO] Number of channels: {1 if len(y.shape) == 1 else y.shape[1]}")
        print(f"[INFO] Number of samples: {len(y)}")
        
        # Check if audio has content or is silent
        max_amplitude = abs(y).max()
        print(f"[INFO] Maximum amplitude: {max_amplitude:.6f}")
        
        # Check first minute and last minute for activity
        first_minute = y[:min(len(y), int(sr*60))]
        last_minute = y[-min(len(y), int(sr*60)):]
        
        print(f"[INFO] First minute max amplitude: {abs(first_minute).max():.6f}")
        print(f"[INFO] Last minute max amplitude: {abs(last_minute).max():.6f}")
        
    except Exception as e:
        print(f"[ERROR] Error analyzing audio file: {e}")

def process_audio(input_file, output_dir):
    """
    Process an audio file to detect laughter segments.
    
    Args:
        input_file (str): Path to the input audio file
        output_dir (str): Directory to save the output segments
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # First, get audio info
    inspect_audio(input_file)
    
    script_path = 'segment_laughter.py'
    command = [
        sys.executable, script_path,
        '--input_audio_file', input_file,
        '--output_dir', output_dir,
        '--save_to_textgrid', 'True',
        '--save_to_audio_files', 'True',
        '--min_length', '0.2',
        '--threshold', '0.3',
        '--num_workers', '0'
    ]
    
    print(f"[DEBUG] Running command in directory: {os.path.join('libs', 'laughter-detection')}")
    print(f"[DEBUG] Command: {' '.join(command)}")
    
    try:
        proc = subprocess.Popen(
            command,
            cwd=os.path.join('libs', 'laughter-detection'),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        print("[DEBUG] Process started")
        for line in proc.stdout:
            print(line, end='')
        
        proc.wait()
        print(f"[DEBUG] Process exited with code: {proc.returncode}")
        
        # Check output files
        print("[DEBUG] Checking output files:")
        if os.path.exists(output_dir):
            files = os.listdir(output_dir)
            print(f"[DEBUG] Files in output directory: {files}")
            
            # Check TextGrid file if it exists
            textgrid_files = [f for f in files if f.endswith('.TextGrid')]
            for tg_file in textgrid_files:
                tg_path = os.path.join(output_dir, tg_file)
                print(f"[DEBUG] Reading TextGrid file: {tg_path}")
                with open(tg_path, 'r') as f:
                    content = f.read()
                    print(f"[DEBUG] TextGrid content:\n{content}")
        else:
            print(f"[DEBUG] Output directory {output_dir} does not exist")
            
    except Exception as e:
        print(f"[ERROR] Exception occurred: {str(e)}")

if __name__ == "__main__":
    # Use the specific file we want to analyze
    input_file = os.path.abspath("AI_open_mic_dataset/funny_audio_mp3/AW_BC_audio_05.mp3")
    
    # Check if the file exists
    if not os.path.exists(input_file):
        print(f"[ERROR] Input file does not exist: {input_file}")
        sys.exit(1)
    
    output_dir = "laughter_test_output"
    print(f"[DEBUG] Processing file: {input_file}")
    process_audio(input_file, output_dir) 