"""
Awesome List Aggregator Script
Purpose: Automatically discover, summarize, and curate new Delta Lake and Iceberg content
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
import feedparser
import requests
from bs4 import BeautifulSoup


# Configuration file for trusted sources
SOURCES_CONFIG_FILE = "scripts/config/trusted_sources.json"
PROCESSED_URLS_FILE = "community/processed_urls.json"
AWESOME_LIST_FILE = "docs/awesome-list.md"
NEW_RESOURCES_FILE = "/tmp/new_resources.json"

# Keywords to search for
KEYWORDS = [
    "delta lake",
    "apache iceberg",
    "data lakehouse",
    "table format",
    "acid transactions",
]


def load_trusted_sources():
    """
    Load trusted sources configuration.
    
    Returns:
        dict: Configuration with RSS feeds and websites
    """
    sources_path = Path(SOURCES_CONFIG_FILE)
    
    if not sources_path.exists():
        # Default sources if config doesn't exist
        default_sources = {
            "rss_feeds": [
                "https://delta.io/blog/feed.xml",
                "https://iceberg.apache.org/feed.xml",
                "https://www.databricks.com/blog/category/engineering/delta/feed",
            ],
            "websites": [
                "https://delta.io/blog/",
                "https://iceberg.apache.org/blogs/",
            ],
        }
        
        # Create config file
        sources_path.parent.mkdir(parents=True, exist_ok=True)
        with open(sources_path, "w") as f:
            json.dump(default_sources, f, indent=2)
        
        return default_sources
    
    with open(sources_path, "r") as f:
        return json.load(f)


def load_processed_urls():
    """
    Load the list of already processed URLs.
    
    Returns:
        set: Set of processed URL hashes
    """
    processed_path = Path(PROCESSED_URLS_FILE)
    
    if not processed_path.exists():
        processed_path.parent.mkdir(parents=True, exist_ok=True)
        with open(processed_path, "w") as f:
            json.dump([], f)
        return set()
    
    with open(processed_path, "r") as f:
        urls = json.load(f)
        return set(urls)


def save_processed_urls(urls):
    """
    Save the list of processed URLs.
    
    Args:
        urls: Set of processed URL hashes
    """
    with open(PROCESSED_URLS_FILE, "w") as f:
        json.dump(list(urls), f, indent=2)


def hash_url(url):
    """
    Generate a hash for a URL.
    
    Args:
        url: URL string
        
    Returns:
        str: MD5 hash of the URL
    """
    return hashlib.md5(url.encode()).hexdigest()


def fetch_rss_feed(feed_url):
    """
    Fetch and parse an RSS feed.
    
    Args:
        feed_url: URL of the RSS feed
        
    Returns:
        list: List of feed entries
    """
    try:
        print(f"  Fetching RSS feed: {feed_url}")
        feed = feedparser.parse(feed_url)
        
        if feed.bozo:
            print(f"  ⚠️  Feed parsing warning: {feed_url}")
            return []
        
        print(f"  ✅ Found {len(feed.entries)} entries")
        return feed.entries
    except Exception as e:
        print(f"  ❌ Error fetching feed {feed_url}: {e}")
        return []


def fetch_website_links(website_url):
    """
    Scrape a website for blog post links.
    
    Args:
        website_url: URL of the website
        
    Returns:
        list: List of dictionaries with link and title
    """
    try:
        print(f"  Fetching website: {website_url}")
        response = requests.get(website_url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Find all links (this is a simplified approach)
        links = []
        for link in soup.find_all("a", href=True):
            href = link.get("href")
            title = link.get_text(strip=True)
            
            # Basic filtering
            if href and title and len(title) > 10:
                # Make absolute URL
                if not href.startswith("http"):
                    from urllib.parse import urljoin
                    href = urljoin(website_url, href)
                
                links.append({"url": href, "title": title})
        
        print(f"  ✅ Found {len(links)} links")
        return links
    except Exception as e:
        print(f"  ❌ Error fetching website {website_url}: {e}")
        return []


def is_relevant(title, content):
    """
    Check if content is relevant based on keywords.
    
    Args:
        title: Title of the article
        content: Content snippet
        
    Returns:
        bool: True if relevant
    """
    text = (title + " " + content).lower()
    
    for keyword in KEYWORDS:
        if keyword.lower() in text:
            return True
    
    return False


def generate_summary_simple(title, content):
    """
    Generate a simple summary without AI (fallback).
    
    Args:
        title: Article title
        content: Article content
        
    Returns:
        str: Simple summary
    """
    # Extract first sentence or first 150 characters
    if content:
        sentences = content.split(".")
        if sentences:
            summary = sentences[0].strip()
            if len(summary) > 150:
                summary = summary[:150] + "..."
            return summary
    
    return "New article about Delta Lake and Apache Iceberg."


def generate_summary_ai(title, content, url):
    """
    Generate an AI-powered summary (placeholder for LLM integration).
    
    Args:
        title: Article title
        content: Article content
        url: Article URL
        
    Returns:
        str: AI-generated summary
    """
    # This is a placeholder for AI integration
    # In production, you would call an LLM API here:
    # - OpenAI GPT
    # - Google Gemini
    # - Anthropic Claude
    # - Local LLM
    
    # Check for API keys
    openai_key = os.environ.get("OPENAI_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    
    if not openai_key and not gemini_key:
        # Fall back to simple summary
        return generate_summary_simple(title, content)
    
    # For now, return simple summary
    # TODO: Implement actual LLM API call
    print(f"  ℹ️  AI summary generation not yet implemented, using simple summary")
    return generate_summary_simple(title, content)


def discover_new_resources():
    """
    Discover new resources from trusted sources.
    
    Returns:
        list: List of new resource dictionaries
    """
    print("\n🔍 Discovering new resources...")
    
    sources = load_trusted_sources()
    processed_urls = load_processed_urls()
    new_resources = []
    
    # Process RSS feeds
    print("\n📰 Processing RSS feeds...")
    for feed_url in sources.get("rss_feeds", []):
        entries = fetch_rss_feed(feed_url)
        
        for entry in entries:
            url = entry.get("link", "")
            title = entry.get("title", "")
            content = entry.get("summary", "")
            published = entry.get("published", "")
            
            if not url or not title:
                continue
            
            url_hash = hash_url(url)
            
            # Skip if already processed
            if url_hash in processed_urls:
                continue
            
            # Check relevance
            if not is_relevant(title, content):
                continue
            
            # Generate summary
            summary = generate_summary_ai(title, content, url)
            
            new_resources.append({
                "url": url,
                "title": title,
                "summary": summary,
                "source": feed_url,
                "published": published,
                "discovered": datetime.now().isoformat(),
            })
            
            processed_urls.add(url_hash)
            print(f"  ✅ New: {title}")
    
    # Process websites
    print("\n🌐 Processing websites...")
    for website_url in sources.get("websites", []):
        links = fetch_website_links(website_url)
        
        for link in links[:10]:  # Limit to 10 links per website
            url = link["url"]
            title = link["title"]
            
            url_hash = hash_url(url)
            
            # Skip if already processed
            if url_hash in processed_urls:
                continue
            
            # Check relevance
            if not is_relevant(title, ""):
                continue
            
            # Generate summary
            summary = generate_summary_simple(title, "")
            
            new_resources.append({
                "url": url,
                "title": title,
                "summary": summary,
                "source": website_url,
                "published": "",
                "discovered": datetime.now().isoformat(),
            })
            
            processed_urls.add(url_hash)
            print(f"  ✅ New: {title}")
    
    # Save processed URLs
    save_processed_urls(processed_urls)
    
    return new_resources


def update_awesome_list(new_resources):
    """
    Update the awesome list with new resources.
    
    Args:
        new_resources: List of new resource dictionaries
    """
    awesome_path = Path(AWESOME_LIST_FILE)
    
    # Ensure directory exists
    awesome_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create or read existing file
    if not awesome_path.exists():
        content = "# Awesome Delta Lake & Apache Iceberg Resources\n\n"
        content += "A curated list of articles, blog posts, and resources about Delta Lake and Apache Iceberg.\n\n"
        content += "## Recent Articles\n\n"
    else:
        with open(awesome_path, "r") as f:
            content = f.read()
        
        # Find where to insert new resources
        if "## Recent Articles" not in content:
            content += "\n## Recent Articles\n\n"
    
    # Generate markdown for new resources
    new_content = ""
    for resource in new_resources:
        title = resource["title"]
        url = resource["url"]
        summary = resource["summary"]
        discovered = datetime.fromisoformat(resource["discovered"]).strftime("%Y-%m-%d")
        
        new_content += f"### [{title}]({url})\n\n"
        new_content += f"*Discovered: {discovered}*\n\n"
        new_content += f"{summary}\n\n"
        new_content += "---\n\n"
    
    # Insert new content after "## Recent Articles"
    marker = "## Recent Articles\n\n"
    if marker in content:
        parts = content.split(marker, 1)
        content = parts[0] + marker + new_content + parts[1]
    else:
        content += new_content
    
    # Write updated content
    with open(awesome_path, "w") as f:
        f.write(content)
    
    print(f"✅ Updated {AWESOME_LIST_FILE} with {len(new_resources)} new resources")


def main():
    """
    Main function to discover and aggregate new resources.
    """
    print("=" * 60)
    print("🤖 Awesome List Aggregator")
    print("=" * 60)
    
    # Discover new resources
    new_resources = discover_new_resources()
    
    if not new_resources:
        print("\n✅ No new resources found")
        return
    
    print(f"\n📊 Summary: Found {len(new_resources)} new resource(s)")
    
    # Save new resources for PR body
    with open(NEW_RESOURCES_FILE, "w") as f:
        json.dump(new_resources, f, indent=2)
    
    # Update awesome list
    print("\n📝 Updating awesome list...")
    update_awesome_list(new_resources)
    
    print("\n✅ Resource aggregation completed successfully!")


if __name__ == "__main__":
    main()
