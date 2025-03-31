from newscastfy import Newscastfy

def main():
    # Initialize the newscast generator
    newscastfy = Newscastfy()
    
    # Example Wikipedia URLs (generally easier to scrape)
    urls = [
        "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "https://en.wikipedia.org/wiki/Mars"
    ]
    
    try:
        # Generate the newscast
        audio_file = newscastfy.generate(urls=urls)
        print(f"Newscastfy generated successfully! Audio saved to: {audio_file}")
    except Exception as e:
        print(f"Error generating newscast: {str(e)}")

if __name__ == "__main__":
    main() 