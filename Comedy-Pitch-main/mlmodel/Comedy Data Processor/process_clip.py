import os
import numpy as np
import librosa
import torch
from transformers import BertTokenizer, BertModel
import pickle
from pathlib import Path
import sys
import logging
import soundfile as sf
import subprocess
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClipProcessor:
    def __init__(self, output_dir: str, laughter_threshold: float = 0.5):
        """Initialize the clip processor.
        
        Args:
            output_dir: Base directory for output files
            laughter_threshold: Threshold for laughter detection (default: 0.5)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.laughter_threshold = laughter_threshold
        
        logger.info(f"Using laughter detection threshold: {self.laughter_threshold}")
        
        # Initialize BERT
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.bert_model = BertModel.from_pretrained('bert-base-uncased')
        self.bert_model.eval()  # Set to evaluation mode
        
    def process_clip(self, 
                    audio_path: str, 
                    transcript: str,
                    clip_id: str) -> bool:
        """Process a single clip and generate all required outputs.
        
        Args:
            audio_path: Path to the audio file
            transcript: Text transcript of the clip
            clip_id: Unique identifier for the clip
            
        Returns:
            bool: True if processing was successful
        """
        try:
            # Create clip directory
            clip_dir = self.output_dir / f"clip_{clip_id}"
            clip_dir.mkdir(exist_ok=True)
            
            # 1. Run laughter detection subprocess
            segments = self._run_laughter_detection(audio_path, clip_dir)
            
            # 2. Create laughter-muted audio
            muted_audio_path = clip_dir / "muted_audio.wav"
            self._create_laughter_muted_audio(audio_path, str(muted_audio_path), segments)
            
            # 3. Process audio and generate audioembed.npy
            audio_features = self._extract_audio_features(str(muted_audio_path))
            np.save(clip_dir / "audioembed.npy", audio_features)
            
            # 4. Generate BERT embeddings
            bert_embeddings = self._generate_bert_embeddings(transcript)
            with open(clip_dir / "BertBase.pkl", 'wb') as f:
                pickle.dump(bert_embeddings, f)
            
            # 5. Generate humor score
            score = self._generate_humor_score(segments, audio_path)
            np.save(clip_dir / "score.npy", score)
            
            # Keep the muted audio file for inspection
            # muted_audio_path.unlink()
            logger.info(f"Laughter-muted audio saved at: {muted_audio_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing clip {clip_id}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def _run_laughter_detection(self, audio_path: str, output_dir: Path):
        """Run the laughter detection subprocess and parse TextGrid for segments."""
        # Prepare output dir for detection
        output_dir.mkdir(parents=True, exist_ok=True)
        script_path = 'segment_laughter.py'
        
        # Convert paths to absolute paths
        abs_audio_path = os.path.abspath(audio_path)
        abs_output_dir = os.path.abspath(str(output_dir))
        
        # Add laughter-detection directory to PYTHONPATH
        env = os.environ.copy()
        env['PYTHONPATH'] = os.path.join(os.getcwd(), 'libs', 'laughter-detection') + os.pathsep + env.get('PYTHONPATH', '')
        command = [
            sys.executable, script_path,
            '--input_audio_file', abs_audio_path,
            '--output_dir', abs_output_dir,
            '--save_to_textgrid', 'True',
            '--save_to_audio_files', 'False',
            '--min_length', '0.2',
            '--threshold', str(self.laughter_threshold),
            '--num_workers', '0'
        ]
        logger.info(f"Running laughter detection: {' '.join(command)}")
        proc = subprocess.run(command, cwd=os.path.join('libs', 'laughter-detection'), capture_output=True, text=True, env=env)
        
        # Check if laughter detection failed
        if proc.returncode != 0:
            logger.error(f"Laughter detection failed: {proc.stderr}")
            raise RuntimeError("Laughter detection subprocess failed")
            
        # Check if "found 0 laughs" in the output
        if "found 0 laughs" in proc.stdout:
            logger.info("No laughter detected in the audio clip")
            return []
        
        # Find the TextGrid file
        textgrid_file = None
        for f in os.listdir(output_dir):
            if f.endswith('_laughter.TextGrid'):
                textgrid_file = os.path.join(str(output_dir), f)
                break
                
        # If no TextGrid file is found, it means no laughter was detected
        if not textgrid_file:
            logger.info("No TextGrid file found - no laughter detected")
            return []
            
        return self._parse_textgrid(textgrid_file)

    def _parse_textgrid(self, textgrid_path: str):
        """Parse a Praat TextGrid file for laughter intervals."""
        segments = []
        with open(textgrid_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Debug: Print parts of the TextGrid content
        logger.info(f"TextGrid file: {textgrid_path}")
        content_preview = content[:300] + "..." if len(content) > 300 else content
        logger.info(f"TextGrid content (preview): {content_preview}")
            
        # Try a simpler pattern that looks for any line with 'laugh' and the lines before it for times
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if '"laugh"' in line and i >= 2:  # Make sure we have at least 2 previous lines
                try:
                    # Go back 2 lines to find xmin
                    xmin_line = lines[i-2]
                    # Go back 1 line to find xmax
                    xmax_line = lines[i-1]
                    
                    # Extract the values
                    xmin_match = re.search(r'(\d+\.\d+)', xmin_line)
                    xmax_match = re.search(r'(\d+\.\d+)', xmax_line)
                    
                    if xmin_match and xmax_match:
                        start = float(xmin_match.group(1))
                        end = float(xmax_match.group(1))
                        segments.append((start, end))
                        logger.info(f"Found laughter segment: {start} - {end}")
                except Exception as e:
                    logger.warning(f"Error parsing TextGrid line {i}: {e}")
        
        logger.info(f"Found {len(segments)} laughter segments.")
        return segments

    def _create_laughter_muted_audio(self, input_path: str, output_path: str, laughter_segments):
        """Create a version of the audio with laughter segments muted.
        
        Args:
            input_path: Path to input audio file
            output_path: Path to save muted audio file
            laughter_segments: List of laughter segments
        """
        # Load audio
        y, sr = librosa.load(input_path, sr=None)
        
        # Create a copy of the audio
        muted_y = y.copy()
        
        # Mute laughter segments by setting them to zero
        for start, end in laughter_segments:
            start_sample = int(start * sr)
            end_sample = int(end * sr)
            muted_y[start_sample:end_sample] = 0
        
        # Save muted audio
        sf.write(output_path, muted_y, sr)
        
        # Log whether any muting occurred
        if len(laughter_segments) > 0:
            logger.info(f"Muted {len(laughter_segments)} laughter segments in audio")
        else:
            logger.info("No laughter segments to mute - saved original audio")
        
    def _extract_audio_features(self, audio_path: str) -> np.ndarray:
        """Extract audio features from the laughter-muted clip.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            np.ndarray: Audio features with shape (33, 8000)
        """
        # Load audio
        y, sr = librosa.load(audio_path, sr=None)
        
        # Extract features
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
        spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
        zero_crossing_rate = librosa.feature.zero_crossing_rate(y)
        
        # Stack features
        features = np.vstack([
            mfccs,
            spectral_centroid,
            spectral_rolloff,
            spectral_contrast,
            zero_crossing_rate
        ])
        
        # Pad or truncate to 8000 frames
        if features.shape[1] < 8000:
            features = np.pad(features, ((0, 0), (0, 8000 - features.shape[1])))
        else:
            features = features[:, :8000]
            
        return features
    
    def _generate_bert_embeddings(self, text: str) -> np.ndarray:
        """Generate BERT embeddings for the transcript.
        
        Args:
            text: Input text transcript
            
        Returns:
            np.ndarray: BERT embeddings with shape (512, 768)
        """
        # Tokenize
        tokens = self.tokenizer(text, 
                              max_length=512,
                              padding='max_length',
                              truncation=True,
                              return_tensors='pt')
        
        # Generate embeddings
        with torch.no_grad():
            outputs = self.bert_model(**tokens, output_hidden_states=True)
            # Sum last 4 hidden layers
            embeddings = sum(outputs.hidden_states[-4:])[0].numpy()
            
        return embeddings
    
    def _generate_humor_score(self, laughter_segments, audio_path: str) -> np.ndarray:
        """Generate one-hot encoded humor score based on laughter.
        
        Args:
            laughter_segments: List of laughter segments
            audio_path: Path to the audio file
            
        Returns:
            np.ndarray: One-hot encoded score with shape (5,)
        """
        # Add debugging info
        logger.info(f"Number of laughter segments: {len(laughter_segments)}")
        
        # Calculate total laughter duration
        total_laughter_duration = 0
        for i, (start, end) in enumerate(laughter_segments):
            duration = end - start
            total_laughter_duration += duration
            logger.info(f"Segment {i+1}: {start:.2f}s - {end:.2f}s (duration: {duration:.2f}s)")
        
        # Get clip duration
        y, sr = librosa.load(audio_path, sr=None)
        clip_duration = len(y) / sr
        
        logger.info(f"Total laughter duration: {total_laughter_duration:.2f} seconds")
        logger.info(f"Clip duration: {clip_duration:.2f} seconds")
        
        # Calculate laughter ratio
        laughter_ratio = total_laughter_duration / clip_duration
        logger.info(f"Laughter ratio: {laughter_ratio:.4f} ({laughter_ratio*100:.2f}%)")
        
        # Assign score based on laughter ratio
        # Define thresholds based on dataset-wide mean and std (for example)
        # These should be configured based on your dataset statistics
        if laughter_ratio < 0.05:  # Less than 5% of clip is laughter
            score = 0
            logger.info("Score assigned: 0 (laughter ratio < 5%)")
        elif laughter_ratio < 0.10:  # 5-10%
            score = 1
            logger.info("Score assigned: 1 (laughter ratio 5-10%)")
        elif laughter_ratio < 0.15:  # 10-15%
            score = 2
            logger.info("Score assigned: 2 (laughter ratio 10-15%)")
        elif laughter_ratio < 0.20:  # 15-20%
            score = 3
            logger.info("Score assigned: 3 (laughter ratio 15-20%)")
        else:  # > 20%
            score = 4
            logger.info("Score assigned: 4 (laughter ratio > 20%)")
        
        # Convert to one-hot encoding
        one_hot = np.zeros(5)
        one_hot[score] = 1
        
        return one_hot

def main():
    # Command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Process a comedy clip to extract features')
    parser.add_argument('--audio', type=str, required=True, help='Path to audio file')
    parser.add_argument('--transcript', type=str, required=True, help='Transcript text')
    parser.add_argument('--id', type=str, required=True, help='Clip ID')
    parser.add_argument('--output_dir', type=str, default='output', help='Output directory')
    parser.add_argument('--threshold', type=float, default=0.5, help='Laughter detection threshold (default: 0.5)')
    
    args = parser.parse_args()
    
    # Process the clip
    processor = ClipProcessor(args.output_dir, args.threshold)
    success = processor.process_clip(
        audio_path=args.audio,
        transcript=args.transcript,
        clip_id=args.id
    )
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 