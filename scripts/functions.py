"""
Production-ready utility functions for my website.

Author: André Vargas
"""

import json
from pathlib import Path
import feedparser
import socket
import bleach


def fetch_articles():
    """
    Fetches articles from the user's Medium RSS feed and returns them as a list of dictionaries.
    
    Returns:
        list: A list of dictionaries containing the title, link, published date, and sanitized 
        summary for each article.
        tuple: Error message and status code if request fails or times out.
    """
    feed_url = 'https://medium.com/@andrevargas22/feed'
    
    # Set socket timeout for feedparser requests (10 seconds)
    original_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(10)
    
    try:
        feed = feedparser.parse(feed_url)
        articles = []

        if feed.bozo:
            return "Error fetching feed", 500

        for entry in feed.entries:
            # Security: Sanitize HTML content to prevent XSS attacks
            # Expanded tag list to support technical blog content while remaining secure
            safe_title = bleach.clean(entry.title, tags=[], strip=True)  # Plain text only
            safe_summary = bleach.clean(
                entry.summary, 
                tags=[
                    # Basic formatting
                    'p', 'br', 'strong', 'em', 'b', 'i', 'u',
                    # Headers for article structure
                    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                    # Lists
                    'ul', 'ol', 'li',
                    # Links (essential for references)
                    'a',
                    # Code blocks and inline code (essential for technical articles)
                    'pre', 'code',
                    # Images and figures (Medium articles often have illustrations)
                    'img', 'figure', 'figcaption',
                    # Blockquotes and structural elements
                    'blockquote', 'div', 'span'
                ],
                attributes={
                    'a': ['href', 'title'],  
                    'img': ['src', 'alt', 'title', 'width', 'height'],  
                    'figure': ['class'],  
                    'div': ['class'],  
                    'span': ['class'],  
                    'pre': ['class'],   
                    'code': ['class']  
                },
                strip=True  
            )
            
            article = {
                'title': safe_title,
                'link': entry.link, 
                'published': entry.published,
                'summary': safe_summary
            }
            articles.append(article)
        return articles
    
    except socket.timeout:
        return "Feed request timed out", 408
    except Exception as e:
        return f"Error fetching feed: {str(e)}", 500
    finally:
        # Restore original socket timeout
        socket.setdefaulttimeout(original_timeout)


def load_games():
    """
    Loads games data from JSON file. If file doesn't exist, returns empty list.
    """
    try:
        # Get the parent directory of this script, then navigate to static/json
        json_path = Path(__file__).parent.parent / 'static' / 'json' / 'games.json'
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)['games']
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading games.json: {e}")
        return []


def get_games_by_letter(letter):
    """
    Returns list of games that start with given letter.
    """
    games = load_games()
    return [g for g in games if g['title'].upper().startswith(letter)]