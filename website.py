"""
This module defines the Flask web application for André Vargas's personal website. The application serves different 
routes to render templates for various sections of the website.

The deployed application is hosted on Google Cloud Run and can be accessed at the following URL: andrevargas.com.br

Author: André Vargas
"""

import os
from flask import Flask, render_template
import feedparser
    
app = Flask(__name__)

############################## PAGE ROUTES ##############################
@app.route('/')
def home():
    """
    Renders the English homepage.

    Returns:
        Template: The index.html template for the English homepage.
    """
    return render_template('eng/index.html')

@app.route('/about')
def about():
    """
    Renders the English 'About' page.

    Returns:
        Template: The about.html template for the English section.
    """
    return render_template('eng/about.html')

@app.route('/blog')
def blog():
    """
    Renders the English blog page with articles fetched from the Medium feed.

    Returns:
        Template: The blog.html template populated with Medium articles.
    """
    articles = fetch_articles()
    return render_template('eng/blog.html', articles=articles)

@app.route('/map')
def world():
    """
    Renders the English map page.

    Returns:
        Template: The map.html template for the English section.
    """
    return render_template('eng/map.html')

@app.route('/games')
def games():
    """
    Renders the English games page.

    Returns:
        Template: The game.html template for the English section.
    """
    return render_template('eng/game.html')

@app.route('/mnist_api')
def mnist():
    """
    Renders the MNIST page and passes the MNIST API endpoint.

    Returns:
        Template: The mnist.html template with the MNIST API endpoint.
    """
    mnist_endpoint = os.getenv('MNIST_ENDPOINT')
    return render_template('eng/mnist.html', mnist_endpoint=mnist_endpoint)

@app.route('/mlops')
def mlops():
    """
    Renders the English MLOps Builder page.

    Returns:
        Template: The mlops.html template for the English section.
    """
    return render_template('eng/mlops.html')

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

@app.route('/render_map')
def render_map():
    """
    Renders the common map page using Folium.

    Returns:
        Template: The folium.html template for displaying the map.
    """
    return render_template('common/folium.html')
    
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
