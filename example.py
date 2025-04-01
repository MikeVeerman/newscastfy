from newscastfy import Newscastfy

def main():
    newscastfy = Newscastfy()
    
    # Two articles to put in the newscast. While we scrape publicly available websites,
    # you could use your own contentt such as slack summaries, emails and reports.
    urls = [
        "https://blog.google/technology/google-deepmind/gemini-model-thinking-updates-march-2025/",
        "https://www.notion.com/blog/how-an-author-wrote-his-first-book-using-notion"
    ]
    
    try:
        output_file = newscastfy.generate(urls=urls, dry_run=False)
        print(f"Newscastfy generated successfully! Text output saved to: {output_file}")
    except Exception as e:
        print(f"Error generating newscast: {str(e)}")

if __name__ == "__main__":
    main() 