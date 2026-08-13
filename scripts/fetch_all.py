import urllib.request
import concurrent.futures
import re
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(ROOT, 'README.md'), 'r') as f:
    readme_content = f.read()

# Find all Google testing blog links
urls = re.findall(r'(https://testing.googleblog.com/[^\)]+)', readme_content)

def fetch_url(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            # Extract basic text from HTML (very roughly, just <p> tags)
            paragraphs = re.findall(r'<p>(.*?)</p>', html, re.DOTALL)
            text = " ".join(paragraphs)
            # Clean up HTML tags
            text = re.sub(r'<[^>]+>', '', text)
            return url, text[:2000] # Return just the first 2000 chars of the article text to avoid bloat
    except Exception as e:
        return url, f"Error: {e}"

print(f"Found {len(urls)} URLs to fetch.")

results = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(fetch_url, url) for url in urls]
    for future in concurrent.futures.as_completed(futures):
        url, text = future.result()
        results[url] = text

with open(os.path.join(ROOT, 'scripts/fetched_google_articles.json'), 'w') as f:
    json.dump(results, f, indent=2)

print("Done fetching.")
