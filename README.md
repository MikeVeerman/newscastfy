# Newscast

A Python library that transforms multiple news articles into an engaging audio newscast. Newscast takes multiple URLs, extracts the content, and creates a professional-sounding news broadcast with summaries of each article.

## Features

- Extract content from multiple news URLs
- Generate concise summaries using AI
- Convert summaries into natural-sounding speech
- Combine multiple segments into a cohesive newscast
- Support for various news sources and formats

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/newscast.git
cd newscast
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables:
```bash
cp .env.example .env
```
Then edit `.env` with your API keys for OpenAI and ElevenLabs.

## Usage

```python
from newscast import Newscast

# Initialize the newscast generator
newscast = Newscast()

# Generate a newscast from multiple URLs
urls = [
    "https://example.com/news1",
    "https://example.com/news2",
    "https://example.com/news3"
]

# Generate the newscast
audio_file = newscast.generate(urls=urls)
```

## API Reference

### Newscast Class

The main class for generating newscasts.

#### Methods

- `generate(urls: List[str]) -> str`: Generates a newscast from a list of URLs
- `extract_content(url: str) -> str`: Extracts content from a URL
- `summarize(content: str) -> str`: Generates a summary of the content
- `text_to_speech(text: str) -> bytes`: Converts text to speech
- `combine_audio(segments: List[bytes]) -> bytes`: Combines multiple audio segments

## License

MIT License 