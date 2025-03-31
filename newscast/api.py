from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os
from .newscast import Newscast

app = FastAPI(
    title="Newscast API",
    description="API for generating newscasts from multiple URLs",
    version="0.1.0"
)

class NewscastRequest(BaseModel):
    urls: List[str]

class NewscastResponse(BaseModel):
    audio_file: str
    summaries: List[str]

@app.post("/generate", response_model=NewscastResponse)
async def generate_newscast(request: NewscastRequest):
    """Generate a newscast from a list of URLs."""
    try:
        newscast = Newscast()
        segments = []
        summaries = []
        
        # Process each URL
        for url in request.urls:
            content = newscast.extract_content(url)
            summary = newscast.summarize(content)
            audio = newscast.text_to_speech(summary)
            summaries.append(summary)
            segments.append(audio)
        
        # Combine audio segments
        final_audio = newscast.combine_audio(segments)
        
        # Save to file
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "newscast.mp3")
        
        with open(output_file, "wb") as f:
            f.write(final_audio)
        
        return NewscastResponse(
            audio_file=output_file,
            summaries=summaries
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 