from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os
from .newscastfy import Newscastfy

app = FastAPI(
    title="Newscastfy API",
    description="API for generating newscasts from multiple URLs",
    version="0.1.0"
)

class NewscastfyRequest(BaseModel):
    urls: List[str]

class NewscastfyResponse(BaseModel):
    audio_file: str
    summaries: List[str]

@app.post("/generate", response_model=NewscastfyResponse)
async def generate_newscastfy(request: NewscastfyRequest):
    """Generate a newscast from a list of URLs."""
    try:
        newscastfy = Newscastfy()
        segments = []
        summaries = []
        
        # Process each URL
        for url in request.urls:
            content = newscastfy.extract_content(url)
            summary = newscastfy.summarize(content)
            audio = newscastfy.text_to_speech(summary)
            summaries.append(summary)
            segments.append(audio)
        
        # Combine audio segments
        final_audio = newscastfy.combine_audio(segments)
        
        # Save to file
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "newscast.mp3")
        
        with open(output_file, "wb") as f:
            f.write(final_audio)
        
        return NewscastfyResponse(
            audio_file=output_file,
            summaries=summaries
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 