import json
import urllib.parse
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(ROOT, "scripts/fetched_google_articles.json"), "r") as f:
    articles = json.load(f)

with open(os.path.join(ROOT, "BEST_PRACTICES.md"), "a") as out_f:
    out_f.write("\n\n---\n\n")
    out_f.write("# Part 5: Complete Google 'Testing on the Toilet' Reference Library\n\n")
    out_f.write("This section contains the core content extracted from all Google Testing on the Toilet blog posts referenced in the repository, ensuring no detail is lost.\n\n")
    
    for url, content in articles.items():
        # Clean up the URL to make a readable title
        path = urllib.parse.urlparse(url).path
        title = path.split('/')[-1].replace('.html', '').replace('-', ' ').title()
        
        out_f.write(f"## {title}\n")
        out_f.write(f"**Source:** {url}\n\n")
        
        # Write the content
        if content.startswith("Error:"):
            out_f.write("*Failed to fetch content.*\n\n")
        else:
            out_f.write(content.strip() + "...\n\n")
            
print("Appended Google articles to BEST_PRACTICES.md")
