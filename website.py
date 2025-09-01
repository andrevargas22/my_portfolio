"""
This module defines the Flask web application for André Vargas's personal website. The application serves different 
routes to render templates for various sections of the website.

The deployed application is hosted on Google Cloud Run and can be accessed at the following URL: andrevargas.com.br

Author: André Vargas
"""

import os
from flask import Flask, render_template, request
import feedparser
import json
from pathlib import Path
import re
import hmac
import hashlib
import logging
import requests
import xml.etree.ElementTree as ET

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

@app.route('/render_map')
def render_map():
    """
    Renders the map page using Folium.

    Returns:
        Template: The folium.html template for displaying the map.
    """
    return render_template('base/folium.html')

############################## TESTING FEATURES ##############################
#### WebSub Callback:
@app.route('/websub/callback', methods=['GET', 'POST'])
def websub_callback():
    """
    Endpoint para receber notificações do YouTube via WebSub.
    
    GET: Verificação de hub challenge (obrigatório pelo WebSub)
    POST: Recebe notificações de novos vídeos
    """
    if request.method == 'GET':
        challenge = request.args.get('hub.challenge')
        mode = request.args.get('hub.mode')
        
        logging.info("[WebSub] GET request received")
        
        if challenge:
            # Validação de segurança
            if re.match(r'^[a-zA-Z0-9_-]{1,128}$', challenge):
                logging.info("[WebSub] Challenge válido")
                return challenge
            else:
                logging.error("[WebSub] Challenge inválido")
                return "Invalid challenge", 400
        
        logging.info("[WebSub] Sem challenge - retornando OK")
        return "OK"
    
    elif request.method == 'POST':
        logging.info("[WebSub] POST notification received")
        data = request.get_data(as_text=True)
        
        # Validação HMAC para verificar autenticidade (YouTube envia X-Hub-Signature)
        hub_signature = request.headers.get('X-Hub-Signature')
        if hub_signature:
            try:
                algorithm, signature = hub_signature.split('=', 1)
                if algorithm != 'sha1':
                    logging.error("[WebSub] Algoritmo não suportado")
                    return "Unsupported algorithm", 400
                
                logging.info("[WebSub] Notificação com assinatura recebida")
            except ValueError:
                logging.error("[WebSub] Formato de assinatura inválido")
                return "Invalid signature format", 400
        else:
            logging.info("[WebSub] Notificação sem assinatura recebida")
        
        # Parse XML e trigger do workflow
        video_data = parse_youtube_notification(data)
        if video_data:
            logging.info("########### [VIDEO PARSED] ###########")
            logging.info(f"Link: {video_data['url']}")
            logging.info(f"Canal: {video_data['channel']}")
            logging.info(f"Título: {video_data['title']}")
            logging.info(f"Postado em: {video_data['published']}")
            logging.info("######################################")
            
            # trigger_video_processing_workflow(video_data)
        
        return "OK"

def parse_youtube_notification(xml_data):
    """
    Parse do XML recebido do YouTube WebSub para extrair informações do vídeo
    """
    try:
        # Parse do XML
        logging.info(f"[Parse] XML recebido: {xml_data[:500]}...")  # Primeiros 500 chars
        root = ET.fromstring(xml_data)
        
        # Namespaces do YouTube/Atom
        namespaces = {
            'atom': 'http://www.w3.org/2005/Atom',
            'yt': 'http://www.youtube.com/xml/schemas/2015'
        }
        
        # Encontrar a entry do vídeo
        entry = root.find('atom:entry', namespaces)
        if entry is None:
            logging.error("[Parse] Nenhuma entry encontrada no XML")
            logging.info(f"[Parse] Root tag: {root.tag}, namespaces: {root.nsmap if hasattr(root, 'nsmap') else 'N/A'}")
            return None
        
        # Extrair informações com debug individual
        video_id = entry.find('yt:videoId', namespaces)
        logging.info(f"[Parse] video_id found: {video_id is not None}")
        
        title = entry.find('atom:title', namespaces)
        logging.info(f"[Parse] title found: {title is not None}")
        
        link = entry.find('atom:link[@rel="alternate"]', namespaces)
        logging.info(f"[Parse] link found: {link is not None}")
        
        author = entry.find('atom:author/atom:name', namespaces)
        logging.info(f"[Parse] author found: {author is not None}")
        
        published = entry.find('atom:published', namespaces)
        logging.info(f"[Parse] published found: {published is not None}")
        
        if not all([video_id, title, link, author, published]):
            logging.error("[Parse] Dados incompletos no XML")
            return None
        
        video_data = {
            'video_id': video_id.text,
            'title': title.text,
            'url': link.get('href'),
            'channel': author.text,
            'published': published.text
        }
        
        return video_data
        
    except ET.ParseError as e:
        logging.error(f"[Parse] Erro ao fazer parse do XML: {e}")
        return None
    except Exception as e:
        logging.error(f"[Parse] Erro inesperado: {e}")
        return None

def trigger_video_processing_workflow(video_data):
    """
    Dispara workflow no repositório de processamento de vídeo
    """
    github_token = os.getenv('GITHUB_TOKEN')  # Personal Access Token
    repo_owner = "andrevargas22"  # seu usuário
    repo_name = "video-processor"  # nome do outro repo
    
    if not github_token:
        logging.error("[GitHub] Token não configurado")
        return
    
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/dispatches"
    
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    
    payload = {
        "event_type": "video_published",  # nome do evento
        "client_payload": {  # AQUI VOCÊ PASSA OS DADOS!
            "video_id": video_data["video_id"],
            "video_url": video_data["url"],
            "title": video_data["title"],
            "channel": video_data["channel"],
            "published_at": video_data["published"]
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 204:
            logging.info(f"[GitHub] Workflow triggered para vídeo: {video_data['title']}")
        else:
            logging.error(f"[GitHub] Falha ao disparar workflow: {response.status_code}")
    except Exception as e:
        logging.error(f"[GitHub] Erro ao disparar workflow: {e}")
    
############################## MAIN EXECUTION ##############################
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)