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
        # YouTube envia um challenge que precisamos retornar para verificar o endpoint
        challenge = request.args.get('hub.challenge')
        mode = request.args.get('hub.mode')
        topic = request.args.get('hub.topic')
        
        print(f"[WebSub] GET request received")
        print(f"[WebSub] Mode: {mode}")
        print(f"[WebSub] Topic: {topic}")
        print(f"[WebSub] Challenge: {challenge}")
        
        if challenge:
            # Validação de segurança: challenge deve ser alfanumérico e ter tamanho razoável
            if re.match(r'^[a-zA-Z0-9_-]{1,128}$', challenge):
                print(f"[WebSub] Challenge VÁLIDO - retornando: {challenge}")
                return challenge
            else:
                print(f"[WebSub] Challenge INVÁLIDO - rejeitado: {challenge}")
                return "Invalid challenge", 400
        
        print(f"[WebSub] Sem challenge - retornando OK")
        return "OK"
    
    elif request.method == 'POST':
        # Aqui recebemos as notificações de novos vídeos
        data = request.get_data(as_text=True)
        
        # Validação HMAC para verificar autenticidade (YouTube envia X-Hub-Signature)
        hub_signature = request.headers.get('X-Hub-Signature')
        if hub_signature:
            # Extrair algoritmo e assinatura (formato: "sha1=abc123...")
            try:
                algorithm, signature = hub_signature.split('=', 1)
                if algorithm != 'sha1':
                    print(f"[WebSub] Algoritmo não suportado: {algorithm}")
                    return "Unsupported algorithm", 400
                
                # Para produção, use um secret real. Por agora, vamos apenas logar
                # secret = os.getenv('WEBSUB_SECRET', 'your-secret-here')
                # expected_signature = hmac.new(
                #     secret.encode('utf-8'),
                #     data.encode('utf-8'),
                #     hashlib.sha1
                # ).hexdigest()
                
                # if not hmac.compare_digest(signature, expected_signature):
                #     print(f"[WebSub] Assinatura inválida")
                #     return "Invalid signature", 403
                
                print(f"[WebSub] Notificação com assinatura recebida: {hub_signature}")
            except ValueError:
                print(f"[WebSub] Formato de assinatura inválido: {hub_signature}")
                return "Invalid signature format", 400
        else:
            print(f"[WebSub] Notificação sem assinatura recebida (pode ser de teste)")
        
        print(f"[WebSub] Headers: {dict(request.headers)}")
        print(f"[WebSub] Body: {data}")
        return "OK"
    
############################## MAIN EXECUTION ##############################
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)