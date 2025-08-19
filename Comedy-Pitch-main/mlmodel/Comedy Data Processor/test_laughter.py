import os
import sys
import subprocess

def process_audio(input_file, output_dir):
    """
    Process an audio file to detect laughter segments.
    
    Args:
        input_file (str): Path to the input audio file
        output_dir (str): Directory to save the output segments
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    script_path = 'segment_laughter.py'
    command = [
        sys.executable, script_path,
        '--input_audio_file', input_file,
        '--output_dir', output_dir,
        '--save_to_textgrid', 'True',
        '--save_to_audio_files', 'True',
        '--min_length', '0.2',
        '--threshold', '0.5',
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