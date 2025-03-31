import os
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from elevenlabs.client import ElevenLabs
from elevenlabs import Voice, VoiceSettings
from dotenv import load_dotenv
import tempfile
from pydantic import BaseModel
from textwrap import wrap
import io
import time
from pydub import AudioSegment

# Load environment variables
load_dotenv()


class NewsSegment(BaseModel):
    """Represents a single news segment in the newscast."""
    title: str
    content: str
    summary: str
    audio: Optional[bytes] = None

class Newscast:
    def __init__(self):
        """Initialize the Newscast generator with API clients."""
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.elevenlabs_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
        
    def extract_content(self, url: str) -> str:
        """Extract content from a URL using BeautifulSoup."""
        try:
            # Add a User-Agent header to mimic a browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
                
            # Get text content
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            raise Exception(f"Failed to extract content from {url}: {str(e)}")

    def summarize(self, content: str, chunk_size: int = 10000) -> str:
        """Generate a concise summary using OpenAI's GPT model, handling long content by chunking."""
        
        first_chunk = content[:chunk_size]
        print(f"Summarizing first chunk ({len(first_chunk)} chars)...")

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    # Modified prompt to request a very short summary
                    {"role": "system", "content": "You are a news editor. Create an extremely concise, engaging summary (around 50 words) of the following text content in a style suitable for a news broadcast."},
                    {"role": "user", "content": first_chunk} 
                ],
                max_tokens=100 # Reduce max tokens as we expect a shorter output
            )
            summary = response.choices[0].message.content
            print(f"Chunk summarized (length: {len(summary)} chars).")
            return summary
        except Exception as e:
            raise Exception(f"Failed to generate summary for chunk: {str(e)}")

    def text_to_speech(self, text: str) -> bytes:
        """Convert text to speech using ElevenLabs."""
        try:
            # Use a specific Voice ID directly to avoid needing 'voices_read' permission
            rachel_voice_id = "21m00Tcm4TlvDq8ikWAM"
            
            # Generate audio using the client with the specific Voice ID
            audio_iterator = self.elevenlabs_client.generate(
                text=text,
                voice=rachel_voice_id, # Use the ID directly
                model="eleven_monolingual_v1"
            )
            # Consume the iterator to get the bytes
            audio_bytes = b"".join(audio_iterator)
            return audio_bytes
        except Exception as e:
            # Add more specific error logging if needed
            print(f"ElevenLabs Error Details: {e}") 
            raise Exception(f"Failed to convert text to speech: {str(e)}")

    def combine_audio(self, segments: List[bytes]) -> bytes:
        """Combine multiple audio segments into a single newscast."""
            
        try:
            # Convert each segment to AudioSegment
            audio_segments = []
            for segment in segments:
                # Ensure segment is not None or empty before processing
                if segment:
                    audio = AudioSegment.from_mp3(io.BytesIO(segment))
                    audio_segments.append(audio)
                else:
                    print("Warning: Skipping empty audio segment.")
            
            if not audio_segments:
                raise ValueError("No valid audio segments to combine.")
                
            # Add 1 second silence between segments
            silence = AudioSegment.silent(duration=1000)
            
            # Combine segments with silence
            final_audio = audio_segments[0]
            for segment in audio_segments[1:]:
                final_audio += silence + segment
                
            # Export to bytes
            buffer = io.BytesIO()
            final_audio.export(buffer, format="mp3")
            return buffer.getvalue()
            
        except Exception as e:
            # Catch potential pydub processing errors here
            raise Exception(f"Failed to combine audio segments using pydub (FFmpeg path: {AudioSegment.converter}): {str(e)}")

    def generate(self, urls: List[str]) -> str:
        """Generate a complete newscast from a list of URLs."""
        segments_data = []
        
        for url in urls:
            try:
                print(f"Processing URL: {url}")
                # Extract content
                content = self.extract_content(url)
                print(f"Extracted content length: {len(content)}")
                
                # Generate summary (now uses chunking)
                summary = self.summarize(content)
                # No need to print summary here, summarize method does it
                
                # Convert to speech
                audio = self.text_to_speech(summary)
                print(f"Generated audio length: {len(audio)} bytes")
                
                # Create segment data
                segment = NewsSegment(
                    title=url,  # You might want to extract a proper title
                    content=content, # Store full content if needed later
                    summary=summary,
                    audio=audio
                )
                segments_data.append(segment)
            except Exception as e:
                print(f"Error processing URL {url}: {e}")
                # Optionally skip this URL or handle the error differently
                continue
        
        if not segments_data:
             raise Exception("No segments were successfully generated.")

        # Combine all segments
        print("Combining audio segments...")
        final_audio = self.combine_audio([seg.audio for seg in segments_data if seg.audio])
        print("Audio combination complete.")
        
        # Create output directory if it doesn't exist
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Save to output file
        output_filename = f"newscast_{int(time.time())}.mp3"
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, "wb") as f:
            f.write(final_audio)
        print(f"Final newscast saved to: {output_path}")
        return output_path 