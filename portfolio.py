import os
from flask import Flask, render_template
import feedparser
    
app = Flask(__name__)

############################## ENGLISH ##############################
@app.route('/')
def home():
    return render_template('eng/index.html')

@app.route('/about')
def about():
    return render_template('eng/about.html')

@app.route('/blog')
def blog():
    feed_url = 'https://medium.com/@andrevargas22/feed'
    feed = feedparser.parse(feed_url)
    articles = []

    for entry in feed.entries:
        article = {
            'title': entry.title,
            'link': entry.link,
            'published': entry.published,
            'summary': entry.summary
        }
        articles.append(article)

    return render_template('eng/blog.html',articles=articles)

@app.route('/map')
def world():
    return render_template('eng/map.html')

@app.route('/games')
def games():
    return render_template('eng/game.html')

@app.route('/mnist_api')
def mnist():
    mnist_endpoint = os.getenv('MNIST_ENDPOINT')
    return render_template('eng/mnist.html', mnist_endpoint=mnist_endpoint)

@app.route('/mlops')
def mlops():
    return render_template('eng/mlops.html')

############################## PT-BR ##############################
@app.route('/br')
def home_pt():
    return render_template('pt/index.html')

@app.route('/br/about')
def about_pt():
    return render_template('pt/about.html')

@app.route('/br/blog')
def blog_pt():
    feed_url = 'https://medium.com/@andrevargas22/feed'
    feed = feedparser.parse(feed_url)
    articles = []

    for entry in feed.entries:
        article = {
            'title': entry.title,
            'link': entry.link,
            'published': entry.published,
            'summary': entry.summary
        }
        articles.append(article)

    return render_template('pt/blog.html',articles=articles)

@app.route('/br/map')
def world_pt():
    return render_template('pt/map.html')

@app.route('/br/games')
def games_pt():
    return render_template('pt/game.html')

@app.route('/br/mnist_api')
def mnist_pt():
    mnist_endpoint = os.getenv('MNIST_ENDPOINT')
    return render_template('pt/mnist.html', mnist_endpoint=mnist_endpoint)

############################## COMMON ##############################

@app.route('/render_map')
def render_map():
    return render_template('common/folium.html')

if __name__ == '__main__':

    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)