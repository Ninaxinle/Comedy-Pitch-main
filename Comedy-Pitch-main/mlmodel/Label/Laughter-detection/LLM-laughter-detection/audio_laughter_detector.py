import os
import json
import base64
import tempfile
from typing import Dict, List, Tuple, Optional
import openai
from pydub import AudioSegment
import io
import logging

# Try to import local config, fall back to default config
try:
    from config_local import *
except ImportError:
    from config import *

# Configure logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL))
logger = logging.getLogger(__name__)

class AudioLaughterDetector:
    """
    A class to detect laughter in audio chunks using OpenAI's audio analysis capabilities.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = None):
        """
        Initialize the detector with OpenAI API key and model.
        
        Args:
            api_key: OpenAI API key. If None, will try to get from config or environment variable
            model: OpenAI model to use for audio analysis. If None, will use config default
        """
        # Get API key from parameter, config, or environment variable
        self.api_key = api_key or OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
        if not self.api_key or self.api_key == "your-openai-api-key-here" or self.api_key == "sk-your-actual-openai-api-key-here":
            raise ValueError("OpenAI API key is required. Please set it in config_local.py or pass api_key parameter.")
        
        # Get model from parameter or config
        self.model = model or OPENAI_MODEL
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # Supported audio formats from config
        self.supported_formats = SUPPORTED_AUDIO_FORMATS
    
    def _validate_audio_file(self, audio_path: str) -> str:
        """
        Validate audio file and return its format.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Audio format (extension without dot)
            
        Raises:
            ValueError: If file doesn't exist or format is not supported
        """
        if not os.path.exists(audio_path):
            raise ValueError(f"Audio file not found: {audio_path}")
        
        file_ext = os.path.splitext(audio_path)[1].lower().lstrip('.')
        if file_ext not in self.supported_formats:
            raise ValueError(f"Unsupported audio format: {file_ext}. Supported formats: {', '.join(self.supported_formats)}")
        
        return file_ext
    
    def _chunk_audio_in_memory(self, audio_path: str, start_time: float, end_time: float) -> Tuple[bytes, str]:
        """
        Extract a chunk of audio from the full audio file in memory.
        
        Args:
            audio_path: Path to the full audio file
            start_time: Start time in seconds
            end_time: End time in seconds
            
        Returns:
            Tuple of (audio_bytes, format)
        """
        try:
            # Load the audio file
            audio = AudioSegment.from_file(audio_path)
            
            # Convert times to milliseconds
            start_ms = int(start_time * 1000)
            end_ms = int(end_time * 1000)
            
            # Extract the chunk
            chunk = audio[start_ms:end_ms]
            
            # Export to bytes buffer
            buffer = io.BytesIO()
            chunk.export(buffer, format="wav")
            audio_bytes = buffer.getvalue()
            buffer.close()
            
            logger.info(f"Extracted audio chunk from {start_time}s to {end_time}s ({len(audio_bytes)} bytes)")
            return audio_bytes, "wav"
            
        except Exception as e:
            logger.error(f"Error chunking audio: {e}")
            raise
    
    def _encode_audio_to_base64(self, audio_bytes: bytes) -> str:
        """
        Encode audio bytes to base64 string.
        
        Args:
            audio_bytes: Raw audio bytes
            
        Returns:
            Base64 encoded string
        """
        return base64.b64encode(audio_bytes).decode('utf-8')
    
    def _chunk_transcript_in_memory(self, transcript_json: Dict, start_time: float, end_time: float) -> Dict:
        """
        Extract transcript segments that fall within the specified time range in memory.
        
        Args:
            transcript_json: Full transcript with timestamps
            start_time: Start time of the chunk in seconds
            end_time: End time of the chunk in seconds
            
        Returns:
            Chunked transcript containing only segments within the time range
        """
        chunked_transcript = []
        
        # Handle different transcript formats
        if isinstance(transcript_json, list):
            # Direct list format (like your example)
            for segment in transcript_json:
                if isinstance(segment, dict):
                    seg_start = segment.get('start_time', segment.get('start', 0))
                    seg_end = segment.get('end_time', segment.get('end', 0))
                    
                    # Check if segment overlaps with the chunk time range
                    if seg_start <= end_time and seg_end >= start_time:
                        # Create a copy of the segment to avoid modifying the original
                        chunked_segment = segment.copy()
                        chunked_transcript.append(chunked_segment)
        
        elif isinstance(transcript_json, dict):
            if 'segments' in transcript_json:
                # Whisper-like format
                chunked_segments = []
                for segment in transcript_json['segments']:
                    seg_start = segment.get('start', 0)
                    seg_end = segment.get('end', 0)
                    if seg_start <= end_time and seg_end >= start_time:
                        chunked_segments.append(segment.copy())
                
                chunked_transcript = {'segments': chunked_segments}
                
            elif 'words' in transcript_json:
                # Word-level format
                chunked_words = []
                for word in transcript_json['words']:
                    word_start = word.get('start', 0)
                    word_end = word.get('end', 0)
                    if word_start <= end_time and word_end >= start_time:
                        chunked_words.append(word.copy())
                
                chunked_transcript = {'words': chunked_words}
            
            else:
                # Assume it's a simple format with start/end/text
                for item in transcript_json:
                    if isinstance(item, dict) and ('start' in item or 'start_time' in item):
                        item_start = item.get('start_time', item.get('start', 0))
                        item_end = item.get('end_time', item.get('end', 0))
                        if item_start <= end_time and item_end >= start_time:
                            chunked_transcript.append(item.copy())
        
        # Sort by start time if it's a list
        if isinstance(chunked_transcript, list):
            chunked_transcript.sort(key=lambda x: x.get('start_time', x.get('start', 0)))
        
        logger.info(f"Extracted {len(chunked_transcript) if isinstance(chunked_transcript, list) else 'multiple'} transcript segments for time range {start_time:.2f}s - {end_time:.2f}s")
        return chunked_transcript
    
    def _create_analysis_prompt(self, chunked_transcript: Dict, start_time: float, end_time: float) -> str:
        """
        Create an improved prompt for laughter detection analysis using chunked transcript.
        
        Args:
            chunked_transcript: Chunked transcript containing only relevant segments
            start_time: Start time of the audio chunk
            end_time: End time of the audio chunk
            
        Returns:
            Formatted prompt string
        """
        # Extract text from chunked transcript
        transcript_text = ""
        
        if isinstance(chunked_transcript, list):
            # Direct list format
            for segment in chunked_transcript:
                seg_start = segment.get('start_time', segment.get('start', 0))
                seg_end = segment.get('end_time', segment.get('end', 0))
                text = segment.get('text', '')
                transcript_text += f"[{seg_start:.2f}s - {seg_end:.2f}s] {text}\n"
        
        elif isinstance(chunked_transcript, dict):
            if 'segments' in chunked_transcript:
                # Whisper-like format
                for segment in chunked_transcript['segments']:
                    seg_start = segment.get('start', 0)
                    seg_end = segment.get('end', 0)
                    text = segment.get('text', '').strip()
                    transcript_text += f"[{seg_start:.2f}s - {seg_end:.2f}s] {text}\n"
            
            elif 'words' in chunked_transcript:
                # Word-level format
                for word in chunked_transcript['words']:
                    word_start = word.get('start', 0)
                    word_end = word.get('end', 0)
                    text = word.get('word', '').strip()
                    transcript_text += f"[{word_start:.2f}s - {word_end:.2f}s] {text}\n"
        
        if not transcript_text.strip():
            transcript_text = "No transcript segments found for this time period.\n"
        
        # Create the prompt
        prompt = f"""You are an expert audio analyst specializing in laughter detection.

I'm providing you with:
1. An audio chunk (from {start_time:.2f}s to {end_time:.2f}s of a longer recording)
2. The relevant transcript segments for this time period

TRANSCRIPT SEGMENTS FOR THIS TIME PERIOD:
{transcript_text}

CRITICAL INSTRUCTION: You MUST respond ONLY with a JSON object. Do NOT include any other text, explanations, or conversational filler outside of the JSON.

TASK: Analyze the audio chunk and identify ONLY genuine laughter sounds.

CRITICAL LAUGHTER DETECTION RULES:
1. **ONLY DETECT AUDIENCE LAUGHTER**: Focus on audience reactions to jokes, ignore speaker laughter
2. **TIMING ACCURACY**: Laughter typically occurs AFTER punchlines, not during speech
3. **CORRECT TIMING**: If laughter happens after a sentence ends, the laughter start_time should be AFTER the sentence's end_time
4. **IGNORE SPEAKER LAUGHTER**: Do not detect when the speaker laughs at their own jokes
5. **AUDIENCE REACTIONS**: Look for collective audience laughter, not individual speaker sounds

LAUGHTER TYPES TO DETECT (AUDIENCE ONLY):
- Audience laughter (collective audience reaction)
- Audience chuckles
- Audience giggles
- Sustained audience laughter
- Belly laughs from audience

SOUNDS TO IGNORE:
- Clapping/applause (rhythmic hand sounds)
- Cheering (shouting, whooping)
- Coughing/sneezing
- Background noise
- Music
- Speaker laughter (when the comedian laughs)
- Individual speaker sounds
- Any non-audience laughter sounds

CLAPPING DETECTION:
- Clapping sounds are rhythmic, repetitive hand sounds (like "clap-clap-clap")
- They often occur at the end of jokes or performances
- They are NOT laughter - they are applause
- If you hear rhythmic hand sounds, this is clapping - IGNORE IT
- Only detect genuine laughter sounds, not applause
- Clapping is usually louder and more percussive than laughter
- Laughter has a more organic, varied sound pattern
- If you're unsure, it's probably clapping - do not detect it

TIMING GUIDELINES:
- Laughter usually starts 0.5-2 seconds AFTER a punchline
- Use transcript timestamps to identify when sentences end
- Place laughter start_time AFTER the sentence that caused it
- Laughter duration is typically 1-5 seconds

CRITICAL TIMING RULES:
- Laughter can start DURING a sentence if something funny is said mid-sentence
- Laughter can start AFTER a sentence ends if the punchline is at the end
- Use your ears to determine the EXACT moment laughter begins
- Do NOT place laughter at the start of sentences unless you actually hear laughter there
- If you hear laughter during speech, determine if it's audience or speaker laughter
- Only detect AUDIENCE laughter, ignore speaker laughter

TIMING VALIDATION:
- Listen carefully to the audio to find the exact moment laughter starts
- Use transcript timestamps to understand context but trust your ears for timing
- If the note says "laughter after this joke" but timing seems wrong, re-listen and adjust
- Laughter timing should match what you actually hear, not what you think should happen
- Be precise about when laughter actually begins in the audio

JSON OUTPUT FORMAT:
{{
    "laughter_instances": [
        {{
            "start_time": 12.5,
            "end_time": 14.2,
            "type": "audience laughter",
            "intensity": "moderate",
            "notes": "Audience laughter after punchline about texting"
        }}
    ],
    "analysis_notes": "Brief description of what you heard"
}}

IMPORTANT: Use "audience laughter" as the type for all detected laughter instances.

If NO laughter is detected:
{{
    "laughter_instances": [],
    "analysis_notes": "No laughter detected in this audio segment"
}}

ANALYSIS PROCESS:
1. Listen to the audio chunk carefully multiple times
2. Identify when laughter actually begins in the audio (not when you think it should)
3. Look for AUDIENCE laughter sounds that can occur during or after sentences
4. Distinguish between audience laughter and speaker laughter during speech
5. IGNORE clapping, applause, cheering, or any rhythmic sounds
6. Provide precise timing for genuine audience laughter only
7. Use transcript timestamps for context but trust your ears for exact timing
8. Focus on collective audience reactions, not individual speaker sounds
9. If you hear laughter during speech, determine if it's audience or speaker laughter
10. Be accurate about when laughter actually starts, not when it "should" start"""
        
        return prompt
    
    def detect_laughter_in_chunk(
        self, 
        audio_path: str, 
        transcript_json: Dict, 
        start_time: float, 
        end_time: float,
        max_retries: int = None
    ) -> Dict:
        """
        Detect laughter in an audio chunk using OpenAI's audio analysis.
        
        Args:
            audio_path: Path to the full audio file
            transcript_json: Full transcript with timestamps
            start_time: Start time of the chunk in seconds
            end_time: End time of the chunk in seconds
            max_retries: Maximum number of retry attempts
            
        Returns:
            Dictionary containing laughter detection results
            
        Raises:
            ValueError: If parameters are invalid
            Exception: If API call fails
        """
        # Validate inputs
        if start_time >= end_time:
            raise ValueError("start_time must be less than end_time")
        
        if end_time - start_time > MAX_CHUNK_DURATION:
            logger.warning(f"Audio chunk is longer than {MAX_CHUNK_DURATION} seconds. This may exceed API limits.")
        
        # Use config default for max_retries if not provided
        max_retries = max_retries or MAX_RETRIES
        
        # Validate audio file
        audio_format = self._validate_audio_file(audio_path)
        
        # Extract audio chunk in memory
        audio_bytes, chunk_format = self._chunk_audio_in_memory(audio_path, start_time, end_time)
        
        # Check file size (OpenAI has 25MB limit)
        file_size_mb = len(audio_bytes) / (1024 * 1024)
        if file_size_mb > MAX_FILE_SIZE_MB:
            raise ValueError(f"Audio chunk too large: {file_size_mb:.2f}MB (max {MAX_FILE_SIZE_MB}MB)")
        
        # Encode to base64
        base64_audio = self._encode_audio_to_base64(audio_bytes)
        
        # Chunk transcript in memory based on time range
        chunked_transcript = self._chunk_transcript_in_memory(transcript_json, start_time, end_time)
        
        # Create analysis prompt using chunked transcript
        prompt = self._create_analysis_prompt(chunked_transcript, start_time, end_time)
        
        # Prepare messages for OpenAI
        messages = [
            {
                "role": "system",
                "content": "You are an expert audio analyst specializing in laughter detection. Provide precise, accurate analysis of laughter in audio segments."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_audio",
                        "input_audio": {
                            "data": base64_audio,
                            "format": chunk_format
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
        
        # Make API call with retries
        for attempt in range(max_retries):
            try:
                logger.info(f"Making OpenAI API call (attempt {attempt + 1}/{max_retries})")
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=MAX_TOKENS,
                    temperature=TEMPERATURE  # Low temperature for more consistent analysis
                )
                
                result_text = response.choices[0].message.content
                logger.info("OpenAI API call successful")
                
                # Try to parse JSON response
                try:
                    result = json.loads(result_text)
                    logger.info(f"Successful JSON response: {result_text}")
                    return {
                        "success": True,
                        "chunk_info": {
                            "start_time": start_time,
                            "end_time": end_time,
                            "duration": end_time - start_time,
                            "file_size_mb": file_size_mb
                        },
                        "analysis": result
                    }
                except json.JSONDecodeError:
                    # If response isn't valid JSON, return the raw text
                    logger.warning("OpenAI response is not valid JSON, returning raw text")
                    logger.info(f"Raw AI response: {result_text}")
                    return {
                        "success": True,
                        "chunk_info": {
                            "start_time": start_time,
                            "end_time": end_time,
                            "duration": end_time - start_time,
                            "file_size_mb": file_size_mb
                        },
                        "analysis": {
                            "raw_response": result_text,
                            "laughter_instances": [],
                            "analysis_notes": "Response could not be parsed as JSON"
                        }
                    }
                
            except Exception as e:
                logger.error(f"API call failed (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    raise Exception(f"Failed to analyze audio after {max_retries} attempts: {e}")
                continue
    
    def batch_detect_laughter(
        self, 
        audio_path: str, 
        transcript_json: Dict, 
        chunk_duration: float = None,
        overlap: float = None
    ) -> List[Dict]:
        """
        Detect laughter in multiple chunks of an audio file.
        
        Args:
            audio_path: Path to the audio file
            transcript_json: Full transcript with timestamps
            chunk_duration: Duration of each chunk in seconds
            overlap: Overlap between chunks in seconds
            
        Returns:
            List of laughter detection results for each chunk
        """
        # Use config defaults if not provided
        chunk_duration = chunk_duration or DEFAULT_CHUNK_DURATION
        overlap = overlap or DEFAULT_OVERLAP
        
        # Get audio duration
        audio = AudioSegment.from_file(audio_path)
        total_duration = len(audio) / 1000.0  # Convert to seconds
        
        results = []
        current_start = 0.0
        
        while current_start < total_duration:
            current_end = min(current_start + chunk_duration, total_duration)
            
            logger.info(f"Processing chunk {current_start:.2f}s - {current_end:.2f}s")
            
            try:
                result = self.detect_laughter_in_chunk(
                    audio_path, transcript_json, current_start, current_end
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing chunk {current_start:.2f}s - {current_end:.2f}s: {e}")
                results.append({
                    "success": False,
                    "error": str(e),
                    "chunk_info": {
                        "start_time": current_start,
                        "end_time": current_end,
                        "duration": current_end - current_start
                    }
                })
            
            current_start = current_end - overlap
        
        return results


# Example usage function
def example_usage():
    """
    Example of how to use the AudioLaughterDetector class.
    """
    # Initialize detector
    detector = AudioLaughterDetector()
    
    # Example transcript (you would load this from your actual transcript file)
    transcript_example = {
        "segments": [
            {"start": 10.0, "end": 12.5, "text": "So I was walking down the street"},
            {"start": 12.5, "end": 15.0, "text": "and this guy comes up to me"},
            {"start": 15.0, "end": 18.0, "text": "and says the funniest thing"}
        ]
    }
    
    # Detect laughter in a specific chunk
    result = detector.detect_laughter_in_chunk(
        audio_path="path/to/your/audio.mp3",
        transcript_json=transcript_example,
        start_time=10.0,
        end_time=20.0
    )
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    example_usage() 