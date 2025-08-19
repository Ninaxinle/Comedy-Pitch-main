#!/usr/bin/env python3
"""
Video/Audio Segmentation Pipeline for Stand-Up Comedy

This script processes stand-up comedy videos and audio files to create segmentation JSON files.
It extracts audio, transcribes with Whisper, and uses LLM for semantic segmentation.
"""

import os
import sys
import json
import yaml
import argparse
import logging
import warnings
from pathlib import Path
from typing import List, Dict, Any, Optional
import subprocess
import whisperx
import openai
from datetime import datetime

# Fix Windows symlink issues with Hugging Face cache
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN"] = "1"

# Fix cuDNN compatibility issues  
os.environ["CUDA_LAUNCH_BLOCKING"] = "1"
os.environ["TORCH_CUDNN_V8_API_DISABLED"] = "1"

# GPU detection for Whisper
import torch
import warnings

# Configure PyTorch backends for better cuDNN compatibility
try:
    torch.backends.cudnn.benchmark = True
    torch.backends.cudnn.deterministic = False
    torch.backends.cudnn.allow_tf32 = True
    # Make cuDNN more lenient with version mismatches
    torch.backends.cudnn.enabled = True
except Exception as e:
    pass  # Continue if cuDNN configuration fails

# Suppress Triton warnings (fall back to slower but stable implementations)
warnings.filterwarnings("ignore", message="Failed to launch Triton kernels")
warnings.filterwarnings("ignore", message="falling back to a slower.*implementation")

GPU_AVAILABLE = torch.cuda.is_available()

# Configure logging with UTF-8 encoding for Windows compatibility
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),
        logging.FileHandler('video_segmentation.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


class VideoSegmentationPipeline:
    """Main pipeline for video segmentation processing."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the pipeline with configuration."""
        self.config = self.load_config(config_path)
        self.setup_directories()
        self.setup_openai()
        self.load_whisper_model()
        self.load_llm_prompt()
    
    def _safe_filename_for_logging(self, filename: str) -> str:
        """Convert filename to ASCII-safe version for logging on Windows."""
        # Replace common problematic Unicode characters with ASCII equivalents
        replacements = {
            '\u29f8': '/',  # BIG SOLIDUS → regular slash
            '\uff1f': '?',  # FULLWIDTH QUESTION MARK → regular question mark
            '\uff1a': ':',  # FULLWIDTH COLON → regular colon
            '\uff0d': '-',  # FULLWIDTH HYPHEN-MINUS → regular hyphen
            '\u2013': '-',  # EN DASH → regular hyphen
            '\u2014': '-',  # EM DASH → regular hyphen
            '\u201c': '"',  # LEFT DOUBLE QUOTATION MARK → regular quotes
            '\u201d': '"',  # RIGHT DOUBLE QUOTATION MARK → regular quotes
            '\u2018': "'",  # LEFT SINGLE QUOTATION MARK → regular apostrophe
            '\u2019': "'",  # RIGHT SINGLE QUOTATION MARK → regular apostrophe
        }
        
        safe_filename = filename
        for unicode_char, ascii_char in replacements.items():
            safe_filename = safe_filename.replace(unicode_char, ascii_char)
        
        return safe_filename
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file {config_path} not found")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing configuration file: {e}")
            raise
    
    def setup_directories(self):
        """Create necessary directories if they don't exist."""
        dirs = self.config['directories']
        
        # Ensure 'summaries' directory is defined (backward compatibility)
        if 'summaries' not in dirs:
            dirs['summaries'] = 'output_summaries'
            logger.info("Added missing 'summaries' directory to config: output_summaries")
        
        for dir_name, dir_path in dirs.items():
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            logger.debug(f"Directory ensured: {dir_path}")
    
    def setup_openai(self):
        """Setup OpenAI client."""
        api_key = self.config['llm']['api_key']
        if api_key == "your-openai-api-key":
            # Try to get from environment variable
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                logger.error("OpenAI API key not set. Please set OPENAI_API_KEY environment variable or update config.yaml")
                raise ValueError("OpenAI API key not configured")
        
        openai.api_key = api_key
        self.openai_client = openai.OpenAI(
            api_key=api_key,
            max_retries=0  # Disable OpenAI client's built-in retries - we handle retries ourselves
        )
        logger.info("OpenAI client initialized (with custom retry logic)")
    
    def load_whisper_model(self):
        """Load the WhisperX model for transcription."""
        try:
            model_name = self.config['whisper']['model']
            
            # Check if CPU is forced in config
            force_cpu = self.config['whisper'].get('force_cpu', False)
            device = "cpu" if force_cpu else ("cuda" if GPU_AVAILABLE else "cpu")
            
            logger.info(f"Loading WhisperX model: {model_name} on {device}")
            if force_cpu:
                logger.info("CPU mode forced in config to avoid cuDNN issues")
            elif GPU_AVAILABLE:
                logger.info("GPU detected - using CUDA for faster transcription")
            
            # Load WhisperX model with compute type optimizations
            compute_type = "float16" if (GPU_AVAILABLE and not force_cpu) else "int8"
            self.whisper_model = whisperx.load_model(model_name, device, compute_type=compute_type)
            
            # Load alignment model for better word timestamps
            self.alignment_model, self.alignment_metadata = whisperx.load_align_model(
                language_code="en", device=device
            )
            
            logger.info("WhisperX model and alignment model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading WhisperX model: {e}")
            raise
    
    def load_llm_prompt(self):
        """Load LLM prompts from files."""
        try:
            # Load chunker LLM prompts
            with open('prompt-chunker-system-prompt.txt', 'r', encoding='utf-8') as f:
                self.chunker_system_prompt = f.read().strip()
            with open('prompt-chunker-user-prompt-instruction.txt', 'r', encoding='utf-8') as f:
                self.chunker_user_instruction_prompt = f.read().strip()
            logger.info ("Chunker LLM prompts loaded successfully")

            # Load initial segmentation prompts
            with open('prompt-system-prompt.txt', 'r', encoding='utf-8') as f:
                self.system_prompt = f.read().strip()
            with open('prompt-user-prompt-instruction.txt', 'r', encoding='utf-8') as f:
                self.user_instruction_prompt = f.read().strip()
            logger.info("Initial LLM prompts loaded successfully")
            
            # Load editor LLM prompts
            with open('prompt-editor-system-prompt.txt', 'r', encoding='utf-8') as f:
                self.editor_system_prompt = f.read().strip()
            with open('prompt-editor-user-prompt-instruction.txt', 'r', encoding='utf-8') as f:
                self.editor_user_instruction_prompt = f.read().strip()
            logger.info("Editor LLM prompts loaded successfully")
            
            # Load summarizer LLM prompts
            with open('prompt-summarizer-system-prompt.txt', 'r', encoding='utf-8') as f:
                self.summarizer_system_prompt = f.read().strip()
            with open('prompt-summarizer-user-prompt-instruction.txt', 'r', encoding='utf-8') as f:
                self.summarizer_user_instruction_prompt = f.read().strip()
            logger.info("Summarizer LLM prompts loaded successfully")

            # Load summary merger LLM prompts
            with open('prompt-summay-merger-system-prompt.txt', 'r', encoding='utf-8') as f:
                self.summary_merger_system_prompt = f.read().strip()
            with open('prompt-summary-merger-user-prompt-instruction.txt', 'r', encoding='utf-8') as f:
                self.summary_merger_user_prompt = f.read().strip()
            logger.info("Summary merger LLM prompts loaded successfully")
            
        except FileNotFoundError as e:
            logger.error(f"LLM prompt file not found: {e}")
            raise
    
    def extract_audio(self, input_path: str, output_path: str, start_time: float = None, end_time: float = None) -> bool:
        """Extract audio from video or audio file using FFmpeg, optionally with time range."""
        try:
            ffmpeg_config = self.config['ffmpeg']
            cmd = ['ffmpeg', '-y']  # Start with base command and overwrite flag
            
            # Add input file
            cmd.extend(['-i', input_path])
            
            # Add time range if specified (for chunk extraction)
            if start_time is not None and end_time is not None:
                duration = end_time - start_time
                cmd.extend(['-ss', str(start_time), '-t', str(duration)])
                cmd.extend(['-c', 'copy'])  # Copy codec for faster chunk extraction
                logger.info(f"Extracting audio chunk: {input_path} ({start_time:.1f}s - {end_time:.1f}s) -> {output_path}")
            else:
                # Full extraction for video files
                cmd.extend([
                    '-vn',  # No video
                    '-acodec', ffmpeg_config['audio_codec'],
                    '-ar', str(ffmpeg_config['sample_rate']),
                    '-ac', str(ffmpeg_config['channels'])
                ])
                logger.info(f"Extracting full audio: {input_path} -> {output_path}")
            
            # Add output path
            cmd.append(output_path)
            
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            
            if result.returncode == 0:
                if start_time is not None:
                    chunk_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
                    logger.info(f"Audio chunk extraction successful: {output_path} ({chunk_size/1024/1024:.1f}MB)")
                else:
                    logger.info(f"Audio extraction successful: {output_path}")
                return True
            else:
                logger.error(f"FFmpeg error: {result.stderr}")
                return False
                
        except FileNotFoundError:
            logger.error("FFmpeg not found. Please install FFmpeg and add it to PATH")
            return False
        except Exception as e:
            logger.error(f"Error extracting audio: {e}")
            return False
    
    def transcribe_audio(self, audio_path: str) -> Optional[Dict[str, Any]]:
        """Transcribe audio using WhisperX with advanced word-level timestamps."""
        try:
            logger.info(f"🎵 TRANSCRIBE_AUDIO FUNCTION CALLED: {audio_path}")
            logger.info(f"🔧 CONFIG CHECK - whisper section: {self.config.get('whisper', 'MISSING!')}")
            
            # User requested to switch back to Python API due to CLI timeouts.
            logger.info("Using WhisperX Python API (no VAD) as requested.")
            result = self._transcribe_with_python_api(audio_path)
            
            if not result:
                return None
                
            logger.info(f"WhisperX transcription completed. Found {len(result.get('segments', []))} segments")
            return result
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return None
    
    def _transcribe_with_cli_vad(self, audio_path: str, vad_method: str, vad_onset: float, vad_offset: float) -> Optional[Dict[str, Any]]:
        """Transcribe using WhisperX CLI with VAD settings."""
        try:
            import tempfile
            import os
            
            # Create temporary output directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Build WhisperX CLI command
                model_name = self.config['whisper']['model']
                language = self.config['whisper'].get('language', 'en')
                force_cpu = self.config['whisper'].get('force_cpu', False)
                device = "cpu" if force_cpu else ("cuda" if GPU_AVAILABLE else "cpu")
                compute_type = "int8" if force_cpu else "float16"
                
                cmd = [
                    "py310\\Scripts\\whisperx", 
                    audio_path,
                    "--model", model_name,
                    "--batch_size", "16",
                    "--compute_type", compute_type,
                    "--device", device,
                    "--output_format", "json",
                    "--output_dir", temp_dir
                ]
                
                # Add language setting
                if language != 'auto':
                    cmd.extend(["--language", language])
                
                # Add VAD settings
                if vad_method:
                    cmd.extend(["--vad_method", vad_method])
                if vad_onset is not None:
                    cmd.extend(["--vad_onset", str(vad_onset)])
                if vad_offset is not None:
                    cmd.extend(["--vad_offset", str(vad_offset)])
                
                logger.info(f"Running WhisperX CLI: {' '.join(cmd)}")
                
                # Run WhisperX CLI (increased timeout for long audio files)
                # For full specials: ~1 minute processing per 5 minutes of audio with VAD
                timeout_seconds = self.config.get('whisper', {}).get('cli_timeout', 3600)  # Default 1 hour
                logger.info(f"WhisperX CLI timeout set to {timeout_seconds} seconds ({timeout_seconds//60} minutes)")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_seconds)
                
                if result.returncode == 0:
                    # Load results from JSON file
                    audio_name = Path(audio_path).stem
                    json_file = os.path.join(temp_dir, f"{audio_name}.json")
                    
                    if os.path.exists(json_file):
                        with open(json_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        logger.info("WhisperX CLI transcription completed successfully")
                        return data
                    else:
                        logger.error(f"WhisperX CLI output file not found: {json_file}")
                        return None
                else:
                    logger.error(f"WhisperX CLI failed: {result.stderr}")
                    return None
                    
        except subprocess.TimeoutExpired:
            logger.error("WhisperX CLI timed out")
            return None
        except Exception as e:
            logger.error(f"Error running WhisperX CLI: {e}")
            return None

  
  
    
    def _transcribe_with_python_api(self, audio_path: str) -> Optional[Dict[str, Any]]:
        """Transcribe using WhisperX Python API (original approach)."""
        try:
            # Load audio
            audio = whisperx.load_audio(audio_path)
            
            # Step 1: Transcribe with WhisperX (much faster and more accurate)
            # Pass language from config to avoid 30-second language detection on each file
            language = self.config['whisper'].get('language', 'en')
            transcribe_options = {'batch_size': 16}
            if language != 'auto':
                transcribe_options['language'] = language
                logger.info(f"LANGUAGE SETTING: Using specified language: {language} (skipping detection)")
            else:
                logger.info("LANGUAGE SETTING: Language set to 'auto' - will detect from first 30 seconds")
            
            logger.info(f"TRANSCRIBE OPTIONS: {transcribe_options}")
            
            result = self.whisper_model.transcribe(audio, **transcribe_options)
            logger.info(f"Initial transcription completed. Found {len(result['segments'])} segments")
            
            # Step 2: Align for precise word-level timestamps (if not disabled)
            no_align = self.config['whisper'].get('no_align', False)
            if no_align:
                logger.info("⚠️  FORCED ALIGNMENT DISABLED - Using raw Whisper timestamps (may fix timing offset issues)")
            else:
                logger.info("Aligning transcription for precise word timestamps...")
                force_cpu = self.config['whisper'].get('force_cpu', False)
                align_device = "cpu" if force_cpu else ("cuda" if GPU_AVAILABLE else "cpu")
                result = whisperx.align(
                    result['segments'], 
                    self.alignment_model, 
                    self.alignment_metadata, 
                    audio, 
                    device=align_device,
                    return_char_alignments=False
                )
            
            logger.info(f"WhisperX transcription {'(raw timestamps)' if no_align else 'and alignment'} completed")
            return result
            
        except Exception as e:
            logger.error(f"Error transcribing with Python API: {e}")
            return None
    
    def align_chunk_audio(self, chunk_sentences: List[Dict], chunk_audio_path: str, start_offset: float = 0.0) -> Optional[Dict[str, Any]]:
        """Align existing sentences to chunk audio (skip transcription entirely for major speedup)."""
        try:
            logger.info(f"Aligning existing sentences to chunk audio: {chunk_audio_path}")
            logger.info(f"Using {len(chunk_sentences)} sentences from original transcript (alignment-only, no transcription)")
            
            # Load chunk audio
            audio = whisperx.load_audio(chunk_audio_path)
            
            # Convert our sentence format to WhisperX segments format (text-only, no timestamps)
            segments = []
            for sentence in chunk_sentences:
                # Send only text - let WhisperX determine timing on chunk audio from scratch
                segment = {
                    "text": sentence["text"]
                    # No timestamps! WhisperX will align text to chunk audio (starting at 0:00)
                }
                segments.append(segment)
            
            logger.debug(f"Converted {len(segments)} sentences to WhisperX segments format")
            
            # ONLY do alignment (skip transcription entirely!)
            logger.info("Performing alignment-only (skipping transcription for 4-8x speedup)...")
            force_cpu = self.config['whisper'].get('force_cpu', False)
            align_device = "cpu" if force_cpu else ("cuda" if GPU_AVAILABLE else "cpu")
            
            aligned_result = whisperx.align(
                segments,                    # ← Use existing sentences, not transcription!
                self.alignment_model, 
                self.alignment_metadata, 
                audio, 
                device=align_device,
                return_char_alignments=False
            )
            
            logger.info(f"Alignment-only completed successfully. Aligned {len(aligned_result.get('segments', []))} segments")
            return aligned_result
            
        except Exception as e:
            logger.error(f"Error in alignment-only processing: {e}")
            return None
    
    def extract_sentences_for_chunk(self, original_sentences: List[Dict], start_time: float, end_time: float) -> List[Dict]:
        """Extract sentences from original transcript that fall within the chunk time range."""
        chunk_sentences = []
        
        for sentence in original_sentences:
            sentence_start = sentence['start_time']
            sentence_end = sentence['end_time']
            
            # Include sentence if it overlaps with chunk time range
            if (sentence_start < end_time and sentence_end > start_time):
                chunk_sentences.append(sentence)
        
        logger.debug(f"Extracted {len(chunk_sentences)} sentences for chunk ({start_time:.1f}s - {end_time:.1f}s)")
        return chunk_sentences
    
    def _get_audio_duration(self, audio_path: str) -> Optional[float]:
        """Get audio duration using ffprobe."""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                '-of', 'csv=p=0', audio_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            
            if result.returncode == 0:
                duration = float(result.stdout.strip())
                logger.debug(f"Audio duration: {duration:.2f}s")
                return duration
            else:
                logger.error(f"ffprobe error: {result.stderr}")
                return None
                
        except (FileNotFoundError, ValueError) as e:
            logger.error(f"Error getting audio duration: {e}")
            return None
    
    def correct_sentence_timestamps(self, segments: List[Dict[str, Any]], audio_path: str) -> List[Dict[str, Any]]:
        """Correct sentence timestamps using word-level data and extend end times to include gaps with laughter."""
        corrected_sentences = []
        buffer = self.config['processing']['timestamp_buffer']
        
        # Get audio duration for calculating the final gap
        audio_duration = self._get_audio_duration(audio_path)
        
        for i, segment in enumerate(segments):
            sentence = {
                'index': i,
                'text': segment['text'].strip(),
                'start_time': segment['start'],
                'end_time': segment['end'],
                'gap_to_next': 0.0  # Initialize gap field
            }
            
            # If word-level timestamps are available, use them to correct sentence timing
            if 'words' in segment and segment['words']:
                words = segment['words']
                
                # Find words that fall within the segment timeframe
                segment_words = [
                    word for word in words
                    if word.get('start', 0) >= segment['start'] - buffer
                    and word.get('end', 0) <= segment['end'] + buffer
                ]
                
                if segment_words:
                    # Correct start time to remove leading silence
                    sentence['start_time'] = segment_words[0].get('start', segment['start'])
                    logger.debug(f"Corrected sentence {i} start: {segment['start']:.2f} -> {sentence['start_time']:.2f}")
            
            # CRITICAL: Calculate and store gap to next sentence for LLM segmentation cues
            if i < len(segments) - 1:
                next_segment = segments[i + 1]
                gap_to_next = next_segment['start'] - sentence['end_time']
                sentence['gap_to_next'] = round(gap_to_next, 2)
                
                # If there's a reasonable gap, extend end time to include it
                # This captures laughter/applause that occurs after the sentence
                if gap_to_next > 0.1:  # Small buffer to avoid overlaps
                    sentence['end_time'] = next_segment['start']
                    logger.debug(f"Extended sentence {i} end time by {gap_to_next:.2f}s to include gap (likely laughter)")
            else:
                # Last sentence: calculate gap to end of audio file
                if audio_duration:
                    gap_to_end = audio_duration - sentence['end_time']
                    sentence['gap_to_next'] = round(gap_to_end, 2)
                    
                    # Extend end time to end of audio if there's a reasonable gap
                    if gap_to_end > 0.1:
                        sentence['end_time'] = audio_duration
                        logger.info(f"Extended last sentence {i} end time by {gap_to_end:.2f}s to end of audio (captures final audience reaction)")
                else:
                    # Fallback: no gap for last sentence if duration unavailable
                    sentence['gap_to_next'] = 0.0
                    logger.warning("Could not determine audio duration - last sentence gap_to_next set to 0.0")
            
            corrected_sentences.append(sentence)
        
        # Log gap statistics for debugging
        gaps = [s['gap_to_next'] for s in corrected_sentences if s['gap_to_next'] > 0]
        large_gaps = [g for g in gaps if g > 1.0]
        if gaps:
            avg_gap = sum(gaps) / len(gaps)
            logger.info(f"Processed {len(corrected_sentences)} sentences with gap-inclusive timestamp correction")
            logger.info(f"Gap statistics: avg={avg_gap:.2f}s, large_gaps(>1s)={len(large_gaps)}, max_gap={max(gaps):.2f}s")
        
        return corrected_sentences
    
    def segment_with_llm(self, sentences: List[Dict[str, Any]], full_transcript: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Use LLM to segment sentences into joke segments, then review with editor LLM."""
        try:
            # Check if this is a mock/test scenario (fake API key)
            if self.config['llm']['api_key'] == "test-key":
                return self._generate_mock_segments(sentences)
            
            # STEP 1: Initial segmentation with first LLM
            logger.info("Step 1: Sending transcript to LLM for initial segmentation")
            
            # Prepare JSON data for user message
            sentences_json = json.dumps(sentences, indent=2)
            
            # Call OpenAI API for initial segmentation with retry logic
            api_params = {
                'model': self.config['llm']['model'],
                'messages': [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": self.user_instruction_prompt},
                    {"role": "user", "content": sentences_json}
                ],
                'temperature': self.config['llm']['temperature']
            }
            
            # Only add max_tokens if specified in config (allows unlimited output)
            if 'max_tokens' in self.config['llm']:
                api_params['max_tokens'] = self.config['llm']['max_tokens']
            
            response = self._call_llm_with_retry(api_params, "Initial segmentation")
            
            # Parse the initial segmentation response
            initial_output = response.choices[0].message.content.strip()
            
            # Clean up JSON if wrapped in code blocks
            if initial_output.startswith('```json'):
                initial_output = initial_output[7:]  # Remove ```json
            if initial_output.startswith('```'):
                initial_output = initial_output[3:]   # Remove ```
            if initial_output.endswith('```'):
                initial_output = initial_output[:-3]  # Remove trailing ```
            initial_output = initial_output.strip()
            
            # Try to parse initial segmentation as JSON
            try:
                initial_segments = json.loads(initial_output)
                logger.info(f"Initial LLM segmentation completed. Found {len(initial_segments)} joke segments")
            except json.JSONDecodeError:
                logger.error(f"Initial LLM output is not valid JSON: {initial_output}")
                return []
            
            # STEP 2: Review and refine with editor LLM
            logger.info("Step 2: Sending initial segmentation to editor LLM for review")
            
            # Call OpenAI API for segmentation review/editing with retry logic
            editor_api_params = {
                'model': self.config['llm']['model'],
                'messages': [
                    {"role": "system", "content": self.editor_system_prompt},
                    {"role": "user", "content": self.editor_user_instruction_prompt},
                    {"role": "user", "content": f"Original transcript:\n{sentences_json}"},  # Include original transcript
                    {"role": "user", "content": f"Initial segmentation to review:\n{initial_output}"}  # Send the first LLM's output
                ],
                'temperature': self.config['llm']['temperature']
            }
            
            # Only add max_tokens if specified in config
            if 'max_tokens' in self.config['llm']:
                editor_api_params['max_tokens'] = self.config['llm']['max_tokens']
            
            editor_response = self._call_llm_with_retry(editor_api_params, "Editor review")
            
            # Parse the editor response
            final_output = editor_response.choices[0].message.content.strip()
            
            # Clean up JSON if wrapped in code blocks
            if final_output.startswith('```json'):
                final_output = final_output[7:]  # Remove ```json
            if final_output.startswith('```'):
                final_output = final_output[3:]   # Remove ```
            if final_output.endswith('```'):
                final_output = final_output[:-3]  # Remove trailing ```
            final_output = final_output.strip()
            
            # Try to parse final segmentation as JSON
            try:
                final_segments = json.loads(final_output)
                logger.info(f"Editor LLM review completed. Final result: {len(final_segments)} refined joke segments")
                
                # Post-process: Add start and end times programmatically based on sentence indexes
                # Use full transcript if available (for chunking), otherwise use chunk sentences
                timing_sentences = full_transcript if full_transcript is not None else sentences
                enriched_segments = self._add_timing_to_segments(final_segments, timing_sentences)
                return enriched_segments
            except json.JSONDecodeError:
                logger.error(f"Editor LLM output is not valid JSON: {final_output}")
                logger.info("Falling back to initial segmentation")
                # Also add timing to fallback segmentation
                timing_sentences = full_transcript if full_transcript is not None else sentences
                enriched_initial_segments = self._add_timing_to_segments(initial_segments, timing_sentences)
                return enriched_initial_segments  # Fall back to initial segmentation if editor fails
                
        except Exception as e:
            error_msg = str(e).lower()
            # Check for token limit errors and re-raise them for chunking logic
            token_limit_indicators = [
                'token', 'too long', 'maximum context length',
                'request too large', 'tokens per min', 'rate_limit_exceeded',
                'must be reduced', 'input or output tokens must be reduced'
            ]
            
            is_token_limit_error = any(indicator in error_msg for indicator in token_limit_indicators)
            
            if is_token_limit_error:
                # Re-raise token limit errors so chunking logic can catch them
                logger.warning(f"Token limit error in LLM segmentation - will trigger chunking: {e}")
                raise e
            else:
                # For other errors, log and return empty list
                logger.error(f"Error in LLM segmentation: {e}")
                return []

    def _add_timing_to_segments(self, segments: List[Dict[str, Any]], sentences: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add start_time, end_time, duration, text, and total_gap to segments based on sentence indexes."""
        enriched_segments = []
        
        for segment in segments:
            if 'sentence_indexes' not in segment:
                logger.warning(f"Segment missing sentence_indexes: {segment}")
                continue
                
            sentence_indexes = segment['sentence_indexes']
            if not sentence_indexes:
                logger.warning(f"Empty sentence_indexes in segment: {segment}")
                continue
            
            try:
                # Get start time from first sentence
                first_sentence_idx = min(sentence_indexes)
                start_time = sentences[first_sentence_idx]['start_time']
                
                # Get end time from last sentence  
                last_sentence_idx = max(sentence_indexes)
                end_time = sentences[last_sentence_idx]['end_time']
                
                # Concatenate text from all sentences in the segment
                segment_texts = []
                total_gap = 0.0
                
                for idx in sorted(sentence_indexes):
                    if idx < len(sentences):
                        sentence = sentences[idx]
                        segment_texts.append(sentence['text'].strip())
                        
                        # Sum up gap_to_next values (if the field exists)
                        if 'gap_to_next' in sentence:
                            total_gap += sentence['gap_to_next']
                    else:
                        logger.warning(f"Invalid sentence index {idx} in segment")
                
                segment_text = " ".join(segment_texts)
                
                # Create enriched segment with timing, text, and gap information
                enriched_segment = {
                    **segment,  # Copy all existing fields
                    'start_time': round(start_time, 2),
                    'end_time': round(end_time, 2),
                    'duration': round(end_time - start_time, 2),
                    'text': segment_text,
                    'total_gap': round(total_gap, 2)
                }
                
                enriched_segments.append(enriched_segment)
                logger.debug(f"Added timing and text to segment {segment.get('segment_id', '?')}: {start_time:.2f}s - {end_time:.2f}s ({len(segment_texts)} sentences, {total_gap:.2f}s total gap)")
                
            except (IndexError, KeyError, TypeError) as e:
                logger.error(f"Error adding timing to segment {segment}: {e}")
                # Include segment without timing rather than dropping it
                enriched_segments.append(segment)
        
        logger.info(f"Added timing, text, and gap information to {len(enriched_segments)} segments")
        return enriched_segments
    
    def _call_llm_with_retry(self, api_params: Dict[str, Any], operation_name: str = "LLM call") -> Any:
        """Call LLM with intelligent retry that distinguishes between request-too-large vs rate-limit-hit."""
        import time
        import re
        
        max_retries = 5
        
        for attempt in range(max_retries + 1):
            try:
                response = self.openai_client.chat.completions.create(**api_params)
                
                # Log actual token usage and rate limits
                if hasattr(response, 'usage') and response.usage:
                    usage = response.usage
                    logger.info(f"{operation_name} tokens used: {usage.total_tokens:,} "
                               f"(prompt: {usage.prompt_tokens:,}, completion: {usage.completion_tokens:,})")
                
                if attempt > 0:
                    logger.info(f"{operation_name} succeeded after {attempt} retries")
                
                return response
                
            except Exception as e:
                error_msg = str(e)
                error_msg_lower = error_msg.lower()
                
                # Check what type of error this is
                rate_limit_indicators = [
                    'rate_limit_exceeded', 'too many requests', 'tokens per min',
                    'requests per min', 'rate limit', 'quota exceeded', 'request too large'
                ]
                
                # Retryable errors (network issues, server errors)
                retryable_indicators = [
                    'connection', 'timeout', 'network', 'server error', 'internal error',
                    'service unavailable', 'bad gateway', 'gateway timeout', 'temporarily unavailable'
                ]
                
                # Non-retryable errors (auth, bad request, etc.)
                non_retryable_indicators = [
                    'authentication', 'unauthorized', 'forbidden', 'invalid request',
                    'bad request', 'not found', 'method not allowed'
                ]
                
                is_rate_limit = any(indicator in error_msg_lower for indicator in rate_limit_indicators)
                is_retryable = any(indicator in error_msg_lower for indicator in retryable_indicators)
                is_non_retryable = any(indicator in error_msg_lower for indicator in non_retryable_indicators)
                
                if is_rate_limit:
                    # Parse the error to see if it's "request too large" vs "rate limit hit"
                    requested_too_large = self._is_request_too_large(error_msg)
                    
                    if requested_too_large:
                        # Request will NEVER succeed - don't retry, let chunking handle it
                        logger.warning(f"{operation_name} request too large for model limits - chunking required")
                        raise e  # Re-raise immediately for chunking logic to catch
                    
                    # It's a rate limit issue (quota exhausted), retry with delay
                    if attempt < max_retries:
                        delay = self._extract_retry_delay_from_error(error_msg)
                        if delay is None:
                            delay = min(5 * (2 ** attempt), 120)
                        
                        logger.warning(f"{operation_name} hit rate limit quota (attempt {attempt + 1}/{max_retries + 1}). "
                                     f"Waiting {delay}s before retry...")
                        time.sleep(delay)
                        continue
                    else:
                        logger.error(f"{operation_name} failed after {max_retries} rate limit retries")
                        raise e
                
                elif is_non_retryable:
                    # Authentication, bad request, etc. - don't retry
                    logger.error(f"{operation_name} failed with non-retryable error: {e}")
                    raise e
                
                elif is_retryable or attempt < max_retries:
                    # Network/server errors OR unknown errors (err on side of retrying)
                    if attempt < max_retries:
                        delay = min(2 * (2 ** attempt), 60)  # Shorter delays for network issues
                        error_type = "retryable" if is_retryable else "unknown"
                        logger.warning(f"{operation_name} failed with {error_type} error (attempt {attempt + 1}/{max_retries + 1}). "
                                     f"Waiting {delay}s before retry: {e}")
                        time.sleep(delay)
                        continue
                    else:
                        logger.error(f"{operation_name} failed after {max_retries} retries: {e}")
                        raise e
                else:
                    # Should not reach here, but just in case
                    raise e
        
        # Should never reach here
        raise Exception(f"{operation_name} failed after all retries")
    
    def _is_request_too_large(self, error_msg: str) -> bool:
        """Check if the error indicates the request is too large (vs rate limit hit)."""
        import re
        
        # Look for patterns like "Limit 30000, Requested 31255"
        limit_pattern = r'limit[:\s]+(\d+).*?requested[:\s]+(\d+)'
        match = re.search(limit_pattern, error_msg, re.IGNORECASE)
        
        if match:
            limit = int(match.group(1))
            requested = int(match.group(2))
            
            logger.info(f"Parsed token limits: requested={requested:,}, limit={limit:,}")
            
            if requested > limit:
                logger.info(f"Request ({requested:,}) exceeds limit ({limit:,}) - chunking needed")
                return True
            else:
                logger.info(f"Request ({requested:,}) within limit ({limit:,}) - rate limit quota issue")
                return False
        
        # Look for explicit "request too large" messages
        too_large_indicators = [
            'request too large', 'input or output tokens must be reduced',
            'exceeds.*limit', 'must be reduced in order to run'
        ]
        
        for indicator in too_large_indicators:
            if re.search(indicator, error_msg, re.IGNORECASE):
                logger.info("Error message indicates request is too large for model")
                return True
        
        # Default to treating as rate limit quota issue
        logger.info("Treating as rate limit quota issue (not request too large)")
        return False
    
    def _extract_retry_delay_from_error(self, error_msg: str) -> Optional[int]:
        """Extract suggested retry delay from OpenAI error message."""
        import re
        
        # Look for patterns like "Please retry after 60 seconds"
        retry_patterns = [
            r'retry after (\d+) seconds?',
            r'try again in (\d+) seconds?',
            r'wait (\d+) seconds?'
        ]
        
        for pattern in retry_patterns:
            match = re.search(pattern, error_msg, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return None
    



    

    
    def _find_chunk_boundary(self, sentences: List[Dict[str, Any]], target_time: float) -> int:
        """Find optimal chunk boundary using LLM to identify topic/unit endings."""
        try:
            chunking_config = self.config.get('chunking', {})
            search_window = chunking_config.get('boundary_search_window', 60)
            
            # Find sentences within the search window around target time
            window_start = target_time - search_window / 2
            window_end = target_time + search_window / 2
            
            candidate_sentences = []
            candidate_indices = []
            
            for i, sentence in enumerate(sentences):
                sentence_time = sentence.get('end_time', 0)
                if window_start <= sentence_time <= window_end:
                    candidate_sentences.append({
                        'index': i,
                        'end_time': sentence_time,
                        'text': sentence.get('text', '').strip()
                    })
                    candidate_indices.append(i)
            
            if not candidate_sentences:
                # Fallback: find closest sentence to target time
                closest_idx = 0
                closest_time_diff = float('inf')
                for i, sentence in enumerate(sentences):
                    time_diff = abs(sentence.get('end_time', 0) - target_time)
                    if time_diff < closest_time_diff:
                        closest_time_diff = time_diff
                        closest_idx = i
                logger.warning(f"No sentences found in boundary search window, using closest sentence at index {closest_idx}")
                return closest_idx
            
            # Use LLM to find the best topic/unit ending
            if self.config['llm']['api_key'] == "test-key":
                # Mock selection for testing
                logger.info("Using mock boundary selection for testing")
                return candidate_indices[len(candidate_indices) // 2]  # Pick middle candidate
            
            logger.info(f"Found {len(candidate_sentences)} candidate sentences for boundary detection")
            # Prepare boundary detection prompt using loaded chunk prompts
            boundary_prompt = json.dumps(candidate_sentences, indent=2)

            # Call LLM for boundary detection with retry logic, using loaded prompt variables
            api_params = {
                'model': self.config['llm']['model'],
                'messages': [
                    {"role": "system", "content": self.chunker_system_prompt},
                    {"role": "user", "content": self.chunker_user_instruction_prompt + "\n\n" + boundary_prompt}
                ],
                'temperature': 0.0,  # Deterministic for consistent selection
                'max_tokens': 5  # We only need a small number
            }
            
            response = self._call_llm_with_retry(api_params, "Boundary detection")
            boundary_response = response.choices[0].message.content.strip()
            
            # Try to extract a number from the response (more robust parsing)
            import re
            numbers = re.findall(r'\b\d+\b', boundary_response)
            
            selected_index = None
            if numbers:
                # Try each number found in the response
                for num_str in numbers:
                    try:
                        potential_index = int(num_str)
                        if potential_index in candidate_indices:
                            selected_index = potential_index
                            break
                    except ValueError:
                        continue
            
            if selected_index is not None:
                logger.info(f"LLM selected sentence index {selected_index} as optimal chunk boundary (extracted from: '{boundary_response}')")
                return selected_index
            else:
                logger.warning(f"LLM returned response without valid index: '{boundary_response}', using fallback")
                fallback_idx = candidate_indices[len(candidate_indices) // 2]
                logger.info(f"Using middle candidate as fallback: index {fallback_idx}")
                return fallback_idx
            
        except Exception as e:
            logger.error(f"Error finding chunk boundary: {e}")
            # Fallback: find sentence closest to target time
            closest_idx = 0
            closest_time_diff = float('inf')
            for i, sentence in enumerate(sentences):
                time_diff = abs(sentence.get('end_time', 0) - target_time)
                if time_diff < closest_time_diff:
                    closest_time_diff = time_diff
                    closest_idx = i
            return closest_idx
    

    
    
    def _process_with_chunking(self, sentences: List[Dict[str, Any]], audio_path: str, video_name: str, chunk_duration: float = None, audio_duration: float = None) -> bool:
        """Process large transcript using adaptive smart chunking approach."""
        try:
            chunking_config = self.config.get('chunking', {})
            
            # Get audio duration - either from parameter (transcript-only mode) or from audio file
            if audio_duration is None:
                if audio_path is None:
                    logger.error("No audio path or audio duration provided for chunking")
                    return False
                audio_duration = self._get_audio_duration(audio_path)
                if audio_duration is None:
                    logger.error("Could not determine audio duration")
                    return False
            else:
                logger.info(f"Using provided audio duration: {audio_duration:.1f}s (transcript-only mode)")
            
            # Start with HALF the total duration as initial chunk size (adaptive approach)
            if chunk_duration is None:
                chunk_duration = audio_duration / 2  # Smart: start with half total duration
                logger.info(f"Starting adaptive chunking with half duration: {chunk_duration/60:.1f} minutes")
            else:
                logger.info(f"Starting chunked processing with {chunk_duration/60:.1f}-minute chunks")
            
            min_duration = chunking_config.get('min_chunk_duration', 300)  # 5 minutes
            size_reduction_factor = chunking_config.get('size_reduction_factor', 0.2)  # 20% reduction
            
            # Process chunks dynamically (not creating all upfront)
            chunk_results = []
            current_start = 0.0
            chunk_num = 1
            
            while current_start < audio_duration:
                logger.info(f"Processing chunk {chunk_num} starting at {current_start/60:.1f} minutes")
                
                # Add delay between chunks to avoid rate limits (except for first chunk)
                if chunk_num > 1:
                    delay = chunking_config.get('delay_between_chunks', 10)
                    logger.info(f"Waiting {delay}s between chunks to avoid rate limits...")
                    import time
                    time.sleep(delay)
                
                # Try to process chunk with current size, reducing if it fails
                chunk_result, actual_end_time = self._process_adaptive_chunk(
                    sentences, audio_path, video_name, chunk_num, 
                    current_start, chunk_duration, audio_duration, min_duration, size_reduction_factor
                )
                
                if chunk_result:
                    chunk_results.append(chunk_result)
                    
                    # Move to next chunk starting from where this one ended
                    current_start = actual_end_time
                    chunk_num += 1
                    
                    # Calculate remaining duration for next chunk (from current position to end)
                    remaining_duration = audio_duration - current_start
                    if remaining_duration > 0:
                        # For next chunk, target the remaining duration (will be optimized by LLM)
                        chunk_duration = remaining_duration
                        logger.info(f"Chunk {chunk_num - 1} completed. Next chunk will target remaining {remaining_duration/60:.1f} minutes")
                    else:
                        logger.info(f"All audio processed. Total chunks: {chunk_num - 1}")
                else:
                    logger.error(f"Failed to process chunk {chunk_num} even with size reduction")
                    return False
            
            # Merge chunk results
            if not self._merge_chunk_results(chunk_results, video_name):
                logger.error("Failed to merge chunk results")
                return False
            
            # Create merged summary from all chunk summaries
            self._create_merged_summary(chunk_results, video_name)            
            logger.info(f"Successfully completed chunked processing for {video_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error in chunked processing: {e}")
            return False
    
    def _process_adaptive_chunk(self, sentences: List[Dict[str, Any]], audio_path: str, video_name: str, 
                               chunk_num: int, start_time: float, initial_duration: float, 
                               audio_duration: float, min_duration: float, size_reduction_factor: float) -> tuple:
        """Process a single chunk with adaptive size reduction if it fails due to token limits."""
        current_duration = initial_duration
        max_retries = self.config.get('chunking', {}).get('max_retries', 3)
        
        for attempt in range(max_retries + 1):
            # Calculate chunk end time
            target_end = start_time + current_duration
            if target_end > audio_duration:
                target_end = audio_duration
                actual_duration = target_end - start_time
            else:
                actual_duration = current_duration
            
            # Check if chunk would be too small
            if actual_duration < min_duration and target_end < audio_duration:
                logger.warning(f"Chunk {chunk_num} duration ({actual_duration/60:.1f} min) below minimum ({min_duration/60:.1f} min)")
                if attempt == 0:
                    # First attempt - use minimum duration
                    target_end = start_time + min_duration
                    if target_end > audio_duration:
                        target_end = audio_duration
                    actual_duration = target_end - start_time
                else:
                    # Already reduced - accept smaller chunk
                    pass
            
            # Find optimal boundary for this chunk size
            if target_end >= audio_duration:
                end_sentence_idx = len(sentences) - 1
                actual_end = audio_duration
            else:
                end_sentence_idx = self._find_chunk_boundary(sentences, target_end)
                actual_end = sentences[end_sentence_idx]['end_time']
            
            # Find start sentence index
            start_sentence_idx = 0
            for i, sentence in enumerate(sentences):
                if sentence['start_time'] >= start_time:
                    start_sentence_idx = i
                    break
            
            # Create chunk definition
            chunk = {
                'chunk_id': chunk_num,
                'start_time': start_time,
                'end_time': actual_end,
                'duration': actual_end - start_time,
                'start_sentence_idx': start_sentence_idx,
                'end_sentence_idx': end_sentence_idx,
                'sentences': sentences[start_sentence_idx:end_sentence_idx + 1]
            }
            
            logger.info(f"Attempt {attempt + 1}: Trying chunk {chunk_num} with {actual_end - start_time:.1f}s duration ({len(chunk['sentences'])} sentences)")
            
            try:
                chunk_result = self._process_single_chunk(chunk, audio_path, video_name, chunk_num, sentences)
                if chunk_result:
                    logger.info(f"Chunk {chunk_num} succeeded on attempt {attempt + 1}")
                    return chunk_result, actual_end
                else:
                    logger.warning(f"Chunk {chunk_num} failed processing on attempt {attempt + 1}")
                    
            except Exception as e:
                error_msg = str(e).lower()
                
                # Check if it's a token limit error
                token_limit_indicators = [
                    'token', 'too long', 'maximum context length',
                    'request too large', 'tokens per min', 'rate_limit_exceeded',
                    'must be reduced', 'input or output tokens must be reduced'
                ]
                
                is_token_limit_error = any(indicator in error_msg for indicator in token_limit_indicators)
                
                if is_token_limit_error and attempt < max_retries:
                    # Reduce chunk size and try again
                    current_duration = current_duration * (1 - size_reduction_factor)
                    logger.warning(f"Chunk {chunk_num} hit token limits on attempt {attempt + 1}. "
                                 f"Reducing size by {size_reduction_factor*100:.0f}% to {current_duration/60:.1f} minutes")
                    continue
                else:
                    # Non-token error or max retries exceeded
                    logger.error(f"Chunk {chunk_num} failed with error: {e}")
                    return None, None
        
        logger.error(f"Chunk {chunk_num} failed after {max_retries + 1} attempts with size reduction")
        return None, None
    
    def _process_single_chunk(self, chunk: Dict[str, Any], original_audio_path: str, video_name: str, chunk_num: int, original_sentences: List[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Process a single chunk by extracting sentences from full transcript and segmenting with LLM (no audio processing)."""
        try:
            # Step 1: Extract relevant sentences from original transcript for this chunk
            if not original_sentences:
                logger.error(f"No original sentences provided for chunk {chunk_num}")
                return None
                
            chunk_sentences = self.extract_sentences_for_chunk(
                original_sentences, 
                chunk['start_time'], 
                chunk['end_time']
            )
            
            if not chunk_sentences:
                logger.error(f"No sentences found for chunk {chunk_num} time range {chunk['start_time']:.1f}s - {chunk['end_time']:.1f}s")
                return None
            
            logger.info(f"Extracted {len(chunk_sentences)} sentences for chunk {chunk_num} (time range: {chunk['start_time']:.1f}s - {chunk['end_time']:.1f}s)")
            
            # Step 2: Segment with LLM using existing segment_with_llm function
            # Pass full transcript for timing lookup since segments have global sentence indexes
            chunk_segments = self.segment_with_llm(chunk_sentences, original_sentences)
            if not chunk_segments:
                logger.error(f"Failed to segment chunk {chunk_num}")
                return None
            
            # Step 3: Generate summary from chunk sentences (no intermediate files saved)
            chunk_transcript_text = self.extract_transcript_text(chunk_sentences)
            chunk_summary = self.generate_context_summary(chunk_transcript_text)
            if not chunk_summary:
                logger.warning(f"Failed to generate summary for chunk {chunk_num}")
                chunk_summary = ""
            
            logger.info(f"Successfully processed chunk {chunk_num} ({len(chunk_sentences)} sentences, {len(chunk_segments)} segments)")
            
            return {
                'chunk_id': chunk['chunk_id'],
                'chunk_num': chunk_num,
                'start_time': chunk['start_time'],
                'end_time': chunk['end_time'],
                'sentences': chunk_sentences,
                'segments': chunk_segments,
                'summary': chunk_summary
            }
            
        except Exception as e:
            logger.error(f"Error processing chunk {chunk_num}: {e}")
            return None
    

    

    def _merge_chunk_results(self, chunk_results: List[Dict[str, Any]], video_name: str) -> bool:
        """Merge chunk results into final output files (segments and summaries only - transcript remains untouched)."""
        try:
            dirs = self.config['directories']
            
            # NOTE: Transcript is NOT merged - it remains as originally created by WhisperX
            # Chunking only affects segments and summaries, not the transcript itself
            
            # Merge segments
            all_segments = []
            segment_id_offset = 0
            
            for chunk_result in chunk_results:
                chunk_segments = chunk_result['segments']
                # Adjust segment IDs to be unique across chunks
                for segment in chunk_segments:
                    if 'segment_id' in segment:
                        segment['segment_id'] += segment_id_offset
                    segment['source_chunk'] = chunk_result['chunk_num']  # Track which chunk this came from
                    all_segments.append(segment)
                
                # Update offset for next chunk
                if chunk_segments:
                    max_id = max(seg.get('segment_id', 0) for seg in chunk_segments)
                    segment_id_offset = max_id + 1
            
            # Save segments directly - they already have timing and text from LLM
            segments_path = os.path.join(dirs['segmentations'], f"{video_name}_segments.json")
            with open(segments_path, 'w', encoding='utf-8') as f:
                json.dump(all_segments, f, indent=2, ensure_ascii=False)
            logger.info(f"Merged segments saved: {segments_path} ({len(all_segments)} total segments)")
            
            return True
            
        except Exception as e:
            logger.error(f"Error merging chunk results: {e}")
            return False
    
    def _create_merged_summary(self, chunk_results: List[Dict[str, Any]], video_name: str) -> None:
        """Create a merged summary from all chunk summaries."""
        try:
            dirs = self.config['directories']
            
            # Collect all chunk summaries
            chunk_summaries = []
            for i, chunk_result in enumerate(chunk_results):
                if chunk_result['summary']:
                    chunk_summaries.append({
                        'chunk_num': chunk_result['chunk_num'],
                        'time_range': f"{chunk_result['start_time']/60:.1f}-{chunk_result['end_time']/60:.1f} minutes",
                        'summary': chunk_result['summary']
                    })
            
            if not chunk_summaries:
                logger.warning("No chunk summaries available for merging.")
                return

            # Check if this is a mock/test scenario
            if self.config['llm']['api_key'] == "test-key":
                logger.info("Creating mock merged summary for testing")
                merged_summary = f"Mock merged summary combining {len(chunk_summaries)} chunk summaries for {video_name}."
            else:
                logger.info(f"Creating merged summary from {len(chunk_summaries)} chunk summaries")
                
                summaries_text = "\n\n".join([
                    f"CHUNK {cs['chunk_num']} ({cs['time_range']}):\n{cs['summary']}" 
                    for cs in chunk_summaries
                ])
                
                api_params = {
                    'model': self.config['llm']['model'],
                    'messages': [
                        {"role": "system", "content": self.summary_merger_system_prompt},
                        {"role": "user", "content": self.summary_merger_user_prompt},
                        {"role": "user", "content": summaries_text}
                    ],
                    'temperature': self.config['llm']['temperature']
                }
                
                if 'max_tokens' in self.config['llm']:
                    api_params['max_tokens'] = self.config['llm']['max_tokens']
                
                response = self._call_llm_with_retry(api_params, "Merged summary generation")
                merged_summary = response.choices[0].message.content.strip()
            
            # Save merged summary
            summary_path = os.path.join(dirs['summaries'], f"{video_name}_summary.txt")
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(merged_summary)
            
            logger.info(f"Merged summary saved: {summary_path}")
            
        except Exception as e:
            logger.error(f"Error creating merged summary: {e}")

    def generate_context_summary(self, transcript_text: str) -> Optional[str]:
        """Generate a context summary using LLM for the entire transcript."""
        try:
            # Check if this is a mock/test scenario (fake API key)
            if self.config['llm']['api_key'] == "test-key":
                logger.info("Generating mock context summary for testing (using fake API key)")
                return "This is a mock context summary for testing purposes. The comedian discusses various topics including family, relationships, and observational humor throughout the performance."
            
            logger.info("Generating context summary with LLM")
            
            # Call OpenAI API for context summary generation with retry logic
            api_params = {
                'model': self.config['llm']['model'],
                'messages': [
                    {"role": "system", "content": self.summarizer_system_prompt},
                    {"role": "user", "content": self.summarizer_user_instruction_prompt},
                    {"role": "user", "content": transcript_text}
                ],
                'temperature': self.config['llm']['temperature']
            }
            
            # Only add max_tokens if specified in config (allows unlimited output)
            if 'max_tokens' in self.config['llm']:
                api_params['max_tokens'] = self.config['llm']['max_tokens']
            
            response = self._call_llm_with_retry(api_params, "Context summary generation")
            
            # Extract the summary from the response
            summary = response.choices[0].message.content.strip()
            
            logger.info(f"Context summary generated successfully ({len(summary)} characters)")
            return summary
                
        except Exception as e:
            logger.error(f"Error generating context summary: {e}")
            return None
    
    def extract_transcript_text(self, sentences: List[Dict[str, Any]]) -> str:
        """Extract plain text transcript without timestamps for summarizer input."""
        try:
            # Extract just the text from each sentence, preserving order
            text_parts = []
            for sentence in sentences:
                text = sentence.get('text', '').strip()
                if text:
                    text_parts.append(text)
            
            # Join with spaces to create a clean, readable transcript
            transcript_text = ' '.join(text_parts)
            
            logger.info(f"Extracted transcript text: {len(transcript_text)} characters from {len(sentences)} sentences")
            return transcript_text
                
        except Exception as e:
            logger.error(f"Error extracting transcript text: {e}")
            return ""
    
    def _generate_mock_segments(self, sentences: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate mock segments for testing purposes."""
        logger.info("Generating mock segments for testing (using fake API key)")
        
        # Create realistic mock segments by grouping sentences
        segments = []
        segment_id = 1
        
        # Group sentences into segments of 3-7 sentences each (typical joke length)
        import random
        random.seed(42)  # Deterministic for testing
        
        i = 0
        while i < len(sentences):
            # Random segment length between 3-7 sentences
            segment_length = min(random.randint(3, 7), len(sentences) - i)
            
            # Get sentence indexes for this segment
            sentence_indexes = list(range(i, i + segment_length))
            
            # Calculate segment timing
            start_time = sentences[i]['start_time']
            end_time = sentences[i + segment_length - 1]['end_time']
            
            # Concatenate text and calculate total gap from all sentences in the segment
            segment_texts = []
            total_gap = 0.0
            
            for idx in sentence_indexes:
                sentence = sentences[idx]
                segment_texts.append(sentence['text'].strip())
                
                # Sum up gap_to_next values (if the field exists)
                if 'gap_to_next' in sentence:
                    total_gap += sentence['gap_to_next']
            
            segment_text = " ".join(segment_texts)
            
            segment = {
                "segment_id": segment_id,
                "sentence_indexes": sentence_indexes,
                "start_time": round(start_time, 2),
                "end_time": round(end_time, 2),
                "duration": round(end_time - start_time, 2),
                "text": segment_text,
                "total_gap": round(total_gap, 2)
            }
            
            segments.append(segment)
            segment_id += 1
            i += segment_length
        
        logger.info(f"Generated {len(segments)} mock segments for testing")
        return segments
    
    def _get_output_status(self, video_path: str) -> Dict[str, Any]:
        """Get detailed status of output files for a given video."""
        video_name = Path(video_path).stem
        
        # Define all expected output paths
        dirs = self.config['directories']
        audio_path = os.path.join(dirs['output_audio'], f"{video_name}.wav")
        transcript_path = os.path.join(dirs['transcripts'], f"{video_name}_sentences.json")
        segments_path = os.path.join(dirs['segmentations'], f"{video_name}_segments.json")
        
        # Handle backward compatibility for summaries directory
        summaries_dir = dirs.get('summaries', 'output_summaries')
        summary_path = os.path.join(summaries_dir, f"{video_name}_summary.txt")
        
        # Check if each file exists
        status = {
            'audio': {
                'exists': os.path.exists(audio_path),
                'path': audio_path,
                'step': 'extract_audio'
            },
            'transcript': {
                'exists': os.path.exists(transcript_path),
                'path': transcript_path,
                'step': 'transcribe_audio'
            },
            'segmentation': {
                'exists': os.path.exists(segments_path),
                'path': segments_path,
                'step': 'segment_with_llm'
            },
            'summary': {
                'exists': os.path.exists(summary_path),
                'path': summary_path,
                'step': 'generate_summary'
            }
        }
        
        # Determine what's missing and the starting point
        all_exist = all(item['exists'] for item in status.values())
        
        # Find the first missing step (processing should start from here)
        step_order = ['audio', 'transcript', 'segmentation', 'summary']
        start_from_step = None
        missing_outputs = []
        
        for step in step_order:
            if not status[step]['exists']:
                missing_outputs.append(step)
                if start_from_step is None:
                    start_from_step = step
        
        status['_meta'] = {
            'all_exist': all_exist,
            'missing_outputs': missing_outputs,
            'start_from_step': start_from_step,
            'video_name': video_name
        }
        
        if all_exist:
            logger.info(f"All outputs exist for {self._safe_filename_for_logging(video_name)}: audio, transcript, segmentation, and summary")
        elif missing_outputs:
            logger.info(f"Missing outputs for {self._safe_filename_for_logging(video_name)}: {', '.join(missing_outputs)} (will start from: {start_from_step})")
        
        return status

    def process_video(self, video_path: str, overwrite: bool = False) -> bool:
        """Process a single video file through the pipeline, starting from the first missing output."""
        try:
            # Get the base filename without extension
            video_name = Path(video_path).stem
            safe_video_name = self._safe_filename_for_logging(video_name)
            logger.info(f"Processing video: {safe_video_name}")
            
            # Get output status to determine what needs to be processed
            status = self._get_output_status(video_path)
            meta = status['_meta']
            
            # Define output paths
            audio_path = status['audio']['path']
            transcript_path = status['transcript']['path']
            segments_path = status['segmentation']['path']
            summary_path = status['summary']['path']
            
            # Handle different processing scenarios
            if overwrite:
                logger.info(f"Overwrite mode: Processing entire pipeline for {safe_video_name}")
                start_from = 'audio'
            elif meta['all_exist']:
                logger.info(f"All outputs exist for {safe_video_name}. Use --overwrite to force reprocessing.")
                return True
            else:
                start_from = meta['start_from_step']
                logger.info(f"Starting incremental processing from: {start_from}")
            
            # Initialize variables for intermediate results
            sentences = None
            segments = None
            
            # Step 1: Extract audio (if needed)
            if start_from == 'audio':
                logger.info("Step 1: Extracting audio...")
                if not self.extract_audio(video_path, audio_path):
                    logger.error(f"Failed to extract audio from {video_path}")
                    return False
            else:
                logger.info("Step 1: Audio exists, skipping extraction")
            
            # Step 2: Transcribe audio (if needed)
            if start_from in ['audio', 'transcript']:
                logger.info("Step 2: Transcribing audio...")
                transcription_result = self.transcribe_audio(audio_path)
                if not transcription_result:
                    logger.error(f"Failed to transcribe audio from {audio_path}")
                    return False
                
                # Step 3: Correct sentence timestamps
                sentences = self.correct_sentence_timestamps(transcription_result['segments'], audio_path)
                
                # Save sentences to JSON
                with open(transcript_path, 'w', encoding='utf-8') as f:
                    json.dump(sentences, f, indent=2, ensure_ascii=False)
                logger.info(f"Sentences saved to: {transcript_path}")
            else:
                logger.info("Step 2: Transcript exists, loading from file")
                # Load existing transcript
                try:
                    with open(transcript_path, 'r', encoding='utf-8') as f:
                        sentences = json.load(f)
                    logger.info(f"Loaded {len(sentences)} sentences from existing transcript")
                except (FileNotFoundError, json.JSONDecodeError) as e:
                    logger.error(f"Failed to load existing transcript: {e}")
                    return False
            
            # Step 3: Segment with LLM (if needed)
            if start_from in ['audio', 'transcript', 'segmentation']:
                logger.info("Step 3: Segmenting with LLM...")
                
                # Try LLM segmentation first
                try:
                    segments = self.segment_with_llm(sentences)
                    logger.info("LLM segmentation completed successfully")
                except Exception as e:
                    error_msg = str(e).lower()
                    
                    # Check for token limit errors
                    token_limit_indicators = [
                        'token', 'too long', 'maximum context length',
                        'request too large', 'tokens per min', 'rate_limit_exceeded',
                        'must be reduced', 'input or output tokens must be reduced'
                    ]
                    
                    is_token_limit_error = any(indicator in error_msg for indicator in token_limit_indicators)
                    
                    if is_token_limit_error and self.config.get('chunking', {}).get('enabled', True):
                        logger.warning(f"LLM segmentation failed due to token limits: {e}")
                        logger.info("Switching to smart chunking approach")
                        
                        # Use chunking pipeline (this will handle everything including summaries)
                        if not self._process_with_chunking(sentences, audio_path, video_name):
                            logger.error(f"Failed to process with chunking")
                            return False
                        
                        # Chunking already creates summary, so we can return success
                        logger.info(f"Successfully processed video with chunking: {safe_video_name}")
                        return True
                    else:
                        # Not a token limit error or chunking disabled, re-raise
                        raise e
                
                if not segments:
                    logger.error(f"Failed to segment transcript with LLM")
                    return False
                
                # Save segments to JSON
                with open(segments_path, 'w', encoding='utf-8') as f:
                    json.dump(segments, f, indent=2, ensure_ascii=False)
                logger.info(f"Segments saved to: {segments_path}")
            else:
                logger.info("Step 3: Segmentation exists, skipping")
            
            # Step 4: Generate context summary (if needed)
            if start_from in ['audio', 'transcript', 'segmentation', 'summary']:
                logger.info("Step 4: Generating context summary...")
                transcript_text = self.extract_transcript_text(sentences)
                context_summary = self.generate_context_summary(transcript_text)
                if not context_summary:
                    logger.error(f"Failed to generate context summary")
                    return False
                
                # Save context summary to text file
                with open(summary_path, 'w', encoding='utf-8') as f:
                    f.write(context_summary)
                logger.info(f"Context summary saved to: {summary_path}")
            else:
                logger.info("Step 4: Summary exists, skipping")
            
            logger.info(f"Successfully processed video: {safe_video_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing video {video_path}: {e}")
            return False
    
    def process_folder(self, input_folder: str, overwrite: bool = False) -> None:
        """Process all video and audio files in the input folder."""
        media_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.mp3', '.wav', '.aac', '.flac', '.m4a', '.ogg']
        media_files = []
        
        # Find all video and audio files
        for ext in media_extensions:
            media_files.extend(Path(input_folder).glob(f"*{ext}"))
        
        if not media_files:
            logger.warning(f"No video or audio files found in {input_folder}")
            return
        
        logger.info(f"Found {len(media_files)} video/audio files to process")
        
        # Process each media file
        successful = 0
        for media_file in media_files:
            if self.process_video(str(media_file), overwrite):
                successful += 1
        
        logger.info(f"Media processing completed. {successful} files processed successfully")

    def process_transcript_only(self, transcript_path: str) -> bool:
        """Process a single transcript file for LLM segmentation and summarization only."""
        try:
            # Get the base filename without extension
            transcript_name = Path(transcript_path).stem
            if transcript_name.endswith('_sentences'):
                transcript_name = transcript_name[:-10]  # Remove '_sentences' suffix
            
            logger.info(f"Processing transcript: {transcript_name}")
            
            # Load existing transcript
            try:
                with open(transcript_path, 'r', encoding='utf-8') as f:
                    sentences = json.load(f)
                logger.info(f"Loaded {len(sentences)} sentences from {transcript_path}")
            except (FileNotFoundError, json.JSONDecodeError) as e:
                logger.error(f"Failed to load transcript from {transcript_path}: {e}")
                return False
            
            # Define output paths
            dirs = self.config['directories']
            segments_path = os.path.join(dirs['segmentations'], f"{transcript_name}_segments.json")
            
            # Handle backward compatibility for summaries directory
            summaries_dir = dirs.get('summaries', 'output_summaries')
            summary_path = os.path.join(summaries_dir, f"{transcript_name}_summary.txt")
            
            # Step 1: Try LLM segmentation first, with chunking fallback for large transcripts
            try:
                segments = self.segment_with_llm(sentences)
                logger.info("LLM segmentation completed successfully")
            except Exception as e:
                error_msg = str(e).lower()
                
                # Check for token limit errors
                token_limit_indicators = [
                    'token', 'too long', 'maximum context length',
                    'request too large', 'tokens per min', 'rate_limit_exceeded',
                    'must be reduced', 'input or output tokens must be reduced'
                ]
                
                is_token_limit_error = any(indicator in error_msg for indicator in token_limit_indicators)
                
                if is_token_limit_error and self.config.get('chunking', {}).get('enabled', True):
                    logger.warning(f"LLM segmentation failed due to token limits: {e}")
                    logger.info("Switching to smart chunking approach for transcript-only processing")
                    
                    # Calculate audio duration from sentence timestamps
                    if sentences:
                        audio_duration = max(sentence.get('end_time', 0) for sentence in sentences)
                        logger.info(f"Calculated audio duration from transcript: {audio_duration:.1f}s")
                        
                        # Use chunking pipeline with transcript-only mode
                        if not self._process_with_chunking(sentences, None, transcript_name, audio_duration=audio_duration):
                            logger.error(f"Failed to process transcript with chunking")
                            return False
                        
                        # Chunking already creates segments and summary, so we can return success
                        logger.info(f"Successfully processed transcript with chunking: {transcript_name}")
                        return True
                    else:
                        logger.error("No sentences found in transcript for duration calculation")
                        return False
                else:
                    # Not a token limit error or chunking disabled
                    logger.error(f"Failed to segment transcript with LLM: {e}")
                    return False
            
            if not segments:
                logger.error(f"Failed to segment transcript with LLM")
                return False
            
            # Save segments to JSON
            with open(segments_path, 'w', encoding='utf-8') as f:
                json.dump(segments, f, indent=2, ensure_ascii=False)
            logger.info(f"Segments saved to: {segments_path}")
            
            # Step 2: Generate context summary
            transcript_text = self.extract_transcript_text(sentences)
            context_summary = self.generate_context_summary(transcript_text)
            if not context_summary:
                logger.error(f"Failed to generate context summary")
                return False
            
            # Save context summary to text file
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(context_summary)
            logger.info(f"Context summary saved to: {summary_path}")
            
            logger.info(f"Successfully processed transcript: {transcript_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing transcript {transcript_path}: {e}")
            return False

    def process_video_transcript_only(self, video_path: str) -> bool:
        """Process transcript for a single video file for LLM segmentation only."""
        try:
            # Get the base filename without extension
            video_name = Path(video_path).stem
            transcript_path = os.path.join(self.config['directories']['transcripts'], f"{video_name}_sentences.json")
            
            logger.info(f"Looking for transcript: {transcript_path}")
            
            if not os.path.exists(transcript_path):
                logger.error(f"Transcript file not found: {transcript_path}")
                return False
            
            return self.process_transcript_only(transcript_path)
            
        except Exception as e:
            logger.error(f"Error processing video transcript {video_path}: {e}")
            return False

    def process_folder_transcripts_only(self, input_folder: str) -> None:
        """Process transcripts for all video and audio files in the input folder."""
        media_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.mp3', '.wav', '.aac', '.flac', '.m4a', '.ogg']
        media_files = []
        
        # Find all video and audio files
        for ext in media_extensions:
            media_files.extend(Path(input_folder).glob(f"*{ext}"))
        
        if not media_files:
            logger.warning(f"No video or audio files found in {input_folder}")
            return
        
        logger.info(f"Found {len(media_files)} video/audio files, looking for corresponding transcripts")
        
        # Process transcript for each media file
        successful = 0
        not_found = 0
        for media_file in media_files:
            media_name = media_file.stem
            transcript_path = os.path.join(self.config['directories']['transcripts'], f"{media_name}_sentences.json")
            
            if os.path.exists(transcript_path):
                if self.process_transcript_only(transcript_path):
                    successful += 1
            else:
                logger.warning(f"Transcript not found for media file: {media_name}")
                not_found += 1
        
        logger.info(f"Segmentation processing completed. {successful} transcripts processed, {not_found} transcripts not found")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Video/Audio Segmentation Pipeline for Stand-Up Comedy')
    parser.add_argument('input_path', help='Path to input video/audio file or folder')
    parser.add_argument('--config', default='config.yaml', help='Path to configuration file')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--segmentation-only', action='store_true', 
                       help='Skip video/audio processing and use existing transcript files for LLM segmentation only (does NOT regenerate transcripts)')
    parser.add_argument('--overwrite', action='store_true',
                       help='Force complete reprocessing of all media files, overwriting existing outputs')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # No argument validation needed anymore
    
    try:
        # Initialize pipeline
        pipeline = VideoSegmentationPipeline(args.config)
        
        # Check if input is a file or folder
        input_path = Path(args.input_path)
        
        if args.segmentation_only:
            # Process existing transcript files based on video names
            if input_path.is_file():
                # Single video file - find corresponding transcript
                pipeline.process_video_transcript_only(str(input_path))
            elif input_path.is_dir():
                # Process transcripts for all videos in folder
                pipeline.process_folder_transcripts_only(str(input_path))
            else:
                logger.error(f"Input path does not exist: {args.input_path}")
                sys.exit(1)
        else:
            # Normal video processing
            if input_path.is_file():
                # Process single video file
                pipeline.process_video(str(input_path), args.overwrite)
            elif input_path.is_dir():
                # Process folder of videos
                pipeline.process_folder(str(input_path), args.overwrite)
            else:
                logger.error(f"Input path does not exist: {args.input_path}")
                sys.exit(1)
            
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 