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
from datetime import datetime

# Load environment variables
load_dotenv()


class NewsSegment(BaseModel):
    """Represents a single news segment in the newscast."""
    title: str
    content: str
    summary: str
    audio: Optional[bytes] = None

class Newscastfy:
    def __init__(self):
        """Initialize the Newscastfy generator with API clients."""
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
                    {"role": "system", "content": """You are a professional news anchor. Create an engaging news segment (around 250 words) that:
1. Starts with an engaging phrase like "Our next story", "next up", "the next item" or "Moving on"
2. Uses a conversational, engaging tone while maintaining journalistic integrity
3. Includes key details, context, and any relevant quotes or statistics
4. Ends with a natural transition or conclusion
5. Avoids technical jargon unless necessary
6. Focuses on the most important aspects of the story

Format the response as a complete news segment ready for broadcast."""},
                    {"role": "user", "content": first_chunk} 
                ],
                max_tokens=1000  # Increased for longer summaries
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

    def save_audio(self, audio_data: bytes) -> str:
        """Save the audio data to a file in the output directory.
        
        Args:
            audio_data: The audio data in bytes to save
            
        Returns:
            str: The path where the audio was saved
        """
        # Create output directory if it doesn't exist
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Save to output file
        output_filename = f"newscast_{int(time.time())}.mp3"
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, "wb") as f:
            f.write(audio_data)
        print(f"Final newscast saved to: {output_path}")
        return output_path

    def generate(self, urls: List[str], dry_run: bool = False) -> str:
        """Generate a complete newscast from a list of URLs.
        
        Args:
            urls: List of URLs to process
            dry_run: If True, only generates text output without audio
            
        Returns:
            str: Path to the output file (audio or text)
        """
        segments_data = []
        
        # Create welcome message with current date
        current_date = datetime.now().strftime("%B %d, %Y")
        welcome_message = f"Welcome to your daily news summary for {current_date}. Here are today's top stories."
        
        # Generate welcome audio if not in dry run mode
        welcome_audio = None
        if not dry_run:
            welcome_audio = self.text_to_speech(welcome_message)
            print("Generated welcome audio")
        
        # Create welcome segment
        welcome_segment = NewsSegment(
            title="Welcome",
            content=welcome_message,
            summary=welcome_message,
            audio=welcome_audio
        )
        segments_data.append(welcome_segment)
        
        for url in urls:
            try:
                print(f"Processing URL: {url}")
                # Extract content
                content = self.extract_content(url)
                print(f"Extracted content length: {len(content)}")
                
                # Generate summary (now uses chunking)
                summary = self.summarize(content)
                
                # Only generate audio if not in dry run mode
                audio = None
                if not dry_run:
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
                continue
        
        if not segments_data:
             raise Exception("No segments were successfully generated.")

        # Add goodbye message
        goodbye_message = "That's all for today's news. Thank you for listening, and we'll be back tomorrow with more stories."
        
        # Generate goodbye audio if not in dry run mode
        goodbye_audio = None
        if not dry_run:
            goodbye_audio = self.text_to_speech(goodbye_message)
            print("Generated goodbye audio")
        
        # Create goodbye segment
        goodbye_segment = NewsSegment(
            title="Goodbye",
            content=goodbye_message,
            summary=goodbye_message,
            audio=goodbye_audio
        )
        segments_data.append(goodbye_segment)

        if dry_run:
            # Create output directory if it doesn't exist
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            
            # Save text output
            output_filename = f"newscast_{int(time.time())}.txt"
            output_path = os.path.join(output_dir, output_filename)
            
            with open(output_path, "w") as f:
                for i, segment in enumerate(segments_data, 1):
                    f.write(f"{segment.summary}\n")
                    f.write("\n")
            
            print(f"Text newscast saved to: {output_path}")
            return output_path
        else:
            # Combine all segments
            print("Combining audio segments...")
            final_audio = self.combine_audio([seg.audio for seg in segments_data if seg.audio])
            print("Audio combination complete.")
            
            # Save the final audio
            return self.save_audio(final_audio) 