"""
This module defines the Flask web application for André Vargas's personal website. The application serves different 
routes to render templates for various sections of the website.

The deployed application is hosted on Google Cloud Run and can be accessed at the following URL: andrevargas.com.br

Author: André Vargas
"""

import os
import time
import json
import logging
import re
import hmac
import base64
from hashlib import sha256
from flask import Flask, render_template, request
import feedparser
from pathlib import Path
import requests
import xml.etree.ElementTree as ET
import jwt

# Configurar logging para Cloud Run
logging.basicConfig(level=logging.INFO)
    
app = Flask(__name__)
    
############################## PAGE ROUTES ##############################
@app.route('/')
def home():
    """
    Renders the homepage.

    Returns:
        Template: The index.html template for the homepage.
    """
    return render_template('pages/index.html')

@app.route('/about')
def about():
    """
    Renders the 'About' page.

    Returns:
        Template: The about.html template for the About section.
    """
    return render_template('pages/about.html')

@app.route('/blog')
def blog():
    """
    Renders the blog page with articles fetched from the Medium feed.

    Returns:
        Template: The blog.html template populated with Medium articles.
    """
    articles = fetch_articles()
    return render_template('pages/blog.html', articles=articles)

@app.route('/map')
def world():
    """
    Renders the map page.

    Returns:
        Template: The map.html template for the Map section.
    """
    mapbox_token = os.getenv('MAPBOX_ACCESS_TOKEN')
    return render_template('pages/map.html', mapbox_token=mapbox_token)

@app.route('/games')
def games():
    """
    Renders the finished games page.
    """
    return render_template('pages/game.html', 
                         get_games_by_letter=get_games_by_letter)

@app.route('/mnist_api')
def mnist():
    """
    Renders the MNIST page and passes the MNIST API endpoint.

    Returns:
        Template: The mnist.html template with the MNIST API endpoint.
    """
    mnist_endpoint = os.getenv('MNIST_ENDPOINT')
    return render_template('pages/mnist.html', mnist_endpoint=mnist_endpoint)

@app.route('/game_of_life')
def game_of_life():
    """
    Renders the Game of Life page.

    Returns:
        Template: The game_of_life.html template for the section.
    """
    return render_template('pages/game_of_life.html')


############################## FUNCTIONS USED BY PAGES ##############################
def fetch_articles():
    """
    Fetches articles from the user's Medium RSS feed and returns them as a list of dictionaries.

    Returns:
        list: A list of dictionaries containing the title, link, published date, and summary for each article.
    """
    feed_url = 'https://medium.com/@andrevargas22/feed'
    feed = feedparser.parse(feed_url)
    articles = []

    if feed.bozo:
        return "Error fetching feed", 500

    for entry in feed.entries:
        article = {
            'title': entry.title,
            'link': entry.link,
            'published': entry.published,
            'summary': entry.summary
        }
        articles.append(article)
    return articles

def load_games():
    """
    Loads games data from JSON file. If file doesn't exist, returns empty list.
    """
    try:
        json_path = Path(__file__).parent / 'static' / 'json' / 'games.json'
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)['games']
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading games.json: {e}")  # Add debug logging
        return []

def get_games_by_letter(letter):
    """
    Returns list of games that start with given letter.
    """
    games = load_games()
    return [g for g in games if g['title'].upper().startswith(letter)]

############################## TESTING FEATURES ##############################
#### WebSub Callback:
@app.route('/websub/callback', methods=['GET', 'POST'])
def websub_callback():
    """
    Endpoint to receive YouTube WebSub notifications.
    
    GET: Hub Challenge verification
    POST: Receives notifications of new videos
    """
    if request.method == 'GET':
        challenge = request.args.get('hub.challenge')
        mode = request.args.get('hub.mode')
        
        logging.info("[WebSub] GET request received")
        
        if challenge:
            if re.match(r'^[a-zA-Z0-9_-]{1,128}$', challenge):
                logging.info("[WebSub] Valid Challenge")
                return challenge
            else:
                logging.error("[WebSub] Invalid Challenge")
                return "Invalid challenge", 400

        logging.info("[WebSub] No challenge - Returning OK")
        return "OK"
    
    elif request.method == 'POST':
        logging.info("[WebSub] POST notification received")
        data = request.get_data(as_text=True)
        
        hub_signature = request.headers.get('X-Hub-Signature')
        if hub_signature:
            try:
                algorithm, signature = hub_signature.split('=', 1)
                if algorithm != 'sha1':
                    logging.error("[WebSub] Unsupported algorithm")
                    return "Unsupported algorithm", 400

                logging.info("[WebSub] Notification with signature received")
            except ValueError:
                logging.error("[WebSub] Invalid signature format")
                return "Invalid signature format", 400
        else:
            logging.info("[WebSub] No signature notification received")

        video_data = parse_youtube_notification(data)
        if video_data:
            logging.info("########### [VIDEO PARSED] ###########")
            logging.info(f"Link: {video_data['url']}")
            logging.info(f"Channel: {video_data['channel']}")
            logging.info(f"Title: {video_data['title']}")
            logging.info(f"Published at: {video_data['published']}")
            logging.info("######################################")
            
            trigger_video_processing_workflow(video_data)
        
        return "OK"

def parse_youtube_notification(xml_data):
    """
    Parses the XML notification from YouTube WebSub.
    """
    try:
        # Parse the XML
        root = ET.fromstring(xml_data)
        
        # Namespaces YouTube/Atom
        namespaces = {
            'atom': 'http://www.w3.org/2005/Atom',
            'yt': 'http://www.youtube.com/xml/schemas/2015'
        }
        
        # Get video entry
        entry = root.find('atom:entry', namespaces)
        if entry is None:
            logging.error("[Parse] No entry found in XML")
            return None

        # Extract video information
        video_id = entry.find('yt:videoId', namespaces)
        title = entry.find('atom:title', namespaces)
        link = entry.find('atom:link[@rel="alternate"]', namespaces)
        author = entry.find('atom:author/atom:name', namespaces)
        published = entry.find('atom:published', namespaces)

        # Build video data
        video_data = {
            'video_id': video_id.text.strip() if video_id is not None and video_id.text else 'Unknown',
            'title': title.text.strip() if title is not None and title.text else 'No title',
            'url': link.get('href') if link is not None else f'https://www.youtube.com/watch?v={video_id.text}',
            'channel': author.text.strip() if author is not None and author.text else 'Unknown',
            'published': published.text.strip() if published is not None and published.text else 'Unknown'
        }
        
        logging.info(f"Video Data: {video_data}")
        
        return video_data
        
    except ET.ParseError as e:
        logging.error(f"[Parse] XML Parse Error: {e}")
        return None
    except Exception as e:
        logging.error(f"[Parse] Unexpected Error: {e}")
        return None

def _load_private_key():
    """
    Get the GitHub App private key from environment variables.
    """
    
    key = os.getenv("GITHUB_APP_PRIVATE_KEY")
    if not key:
        return None
    if "\\n" in key:
        key = key.replace("\\n", "\n")
    return key


def _generate_github_app_jwt(app_id: str, private_key: str) -> str:
    """
    Generate a short-lived JWT for GitHub App authentication.
    """
    
    now = int(time.time())
    payload = {
        "iat": now - 60,  
        "exp": now + 540,  
        "iss": app_id
    }
    token = jwt.encode(payload, private_key, algorithm="RS256")
    return token


def _get_installation_token(app_jwt: str, installation_id: str) -> str | None:
    """
    Get an installation access token for a GitHub App.
    """
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github.v3+json"
    }
    try:
        r = requests.post(url, headers=headers, timeout=10)
        if r.status_code == 201:
            data = r.json()
            return data.get("token")
        logging.error(f"[GitHub] Failed to get installation token: {r.status_code} {r.text}")
    except Exception as e:
        logging.error(f"[GitHub] Error requesting installation token: {e}")
    return None


def _get_dispatch_token():
    """
    Return an installation access token using GitHub App authentication.
    """
    
    app_id = os.getenv("GITHUB_APP_ID")
    inst_id = os.getenv("GITHUB_APP_INSTALLATION_ID")
    private_key = _load_private_key()

    if not all([app_id, inst_id, private_key]):
        logging.error("[GitHub] GitHub App configuration incomplete (missing App ID, Installation ID, or private key)")
        return None

    try:
        app_jwt = _generate_github_app_jwt(app_id, private_key)
        install_token = _get_installation_token(app_jwt, inst_id)
        if install_token:
            return install_token
        logging.error("[GitHub] Failed to obtain installation access token")
        return None
    except Exception as e:
        logging.error(f"[GitHub] GitHub App authentication failed: {e}")
        return None


def _valid_video_id(video_id: str) -> bool:
    """
    Validate YouTube video ID format.
    """
    return bool(re.fullmatch(r"[A-Za-z0-9_-]{6,20}", video_id or ""))


def trigger_video_processing_workflow(video_data):
    """
    Dispatch a workflow event in the target repository using a GitHub App token.
    """
    
    if not video_data or video_data.get("video_id") in (None, "Unknown"):
        logging.error("[GitHub] Missing or invalid video data")
        return

    if not _valid_video_id(video_data.get("video_id", "")):
        logging.error("[GitHub] Video ID pattern invalid - aborting dispatch")
        return

    repo_owner = "andrevargas22"
    repo_name = "grenalbot"
    token = _get_dispatch_token()
    if not token:
        return

    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/dispatches"
    payload = {
        "event_type": "video_published",
        "client_payload": {
            "video_id": video_data["video_id"],
            "video_url": video_data["url"],
            "title": video_data["title"],
            "channel": video_data["channel"],
            "published_at": video_data["published"]
        }
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=10)
        if r.status_code == 204:
            logging.info(f"[GitHub] Workflow dispatch sent for video_id={video_data['video_id']}")
        else:
            logging.error(f"[GitHub] Dispatch failed {r.status_code}: {r.text}")
    except Exception as e:
        logging.error(f"[GitHub] Dispatch error: {e}")

############################## MAIN EXECUTION ##############################
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)