# Newscastfy

A Python library that transforms multiple news articles into an engaging audio newscast. Newscastfy takes multiple URLs, extracts the content, and creates a professional-sounding news broadcast with summaries of each article.

## Features

- Extract content from multiple news URLs
- Generate concise summaries using AI
- Convert summaries into natural-sounding speech
- Combine multiple segments into a cohesive newscast
- Support for various news sources and formats
- Dry run mode for testing text generation without audio

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
from newscastfy import Newscastfy

# Initialize the newscast generator
newscastfy = Newscastfy()

# Generate a newscast from multiple URLs
urls = [
    "https://example.com/news1",
    "https://example.com/news2",
    "https://example.com/news3"
]

# Generate the newscast with audio (default)
audio_file = newscastfy.generate(urls=urls)

# Or generate text-only output (dry run mode)
# This is useful for testing the text generation without using ElevenLabs credits
text_file = newscastfy.generate(urls=urls, dry_run=True)
```

## Running the Example

The repository includes an example script (`example.py`) that demonstrates how to use Newscastfy with real articles. To run it:

```bash
python example.py
```

This example will:
1. Process two sample articles (one from Google's blog and one from Notion)
2. Generate a newscast with both text and audio output
3. Save the output to a file and print its location

You can modify the URLs in `example.py` to process different articles of your choice.

## API Reference

### Newscastfy Class

The main class for generating newscasts.

#### Methods

- `generate(urls: List[str], dry_run: bool = False) -> str`: Generates a newscast from a list of URLs. When `dry_run` is True, only generates text output without audio, saving on ElevenLabs API credits.
- `extract_content(url: str) -> str`: Extracts content from a URL
- `summarize(content: str) -> str`: Generates a summary of the content
- `text_to_speech(text: str) -> bytes`: Converts text to speech
- `combine_audio(segments: List[bytes]) -> bytes`: Combines multiple audio segments

## License

MIT License 