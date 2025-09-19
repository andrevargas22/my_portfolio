"""
This module defines the Flask web application for André Vargas's personal website. The application serves different 
routes to render templates for various sections of the website.

The deployed application is hosted on Google Cloud Run and can be accessed at the following URL: andrevargas.com.br

Author: André Vargas
"""

# Imports
import os
import logging
from flask import Flask, render_template, request, g
import secrets

# Production functions
from scripts.functions import fetch_articles, get_games_by_letter

# Testing functions
from scripts.testing import handle_websub_callback

# Configure logging
logging.basicConfig(level=logging.INFO)
    
app = Flask(__name__)

# Security: Limit request body size
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  

# Handle request entity too large errors
@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle requests that exceed the maximum content length."""
    app.logger.warning(f"Request entity too large from {request.remote_addr}")
    return "Request entity too large. Maximum allowed size is 1MB.", 413

# Security headers
@app.before_request
def generate_csp_nonce():
    """Generate a per-request nonce for CSP (used for inline scripts that we intentionally allow)."""
    g.csp_nonce = secrets.token_urlsafe(16)

@app.after_request
def add_security_headers(response):
    """
    Add security headers to responses.
    """
    # Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # Prevent clickjacking attacks
    response.headers['X-Frame-Options'] = 'DENY'
    
    # XSS protection
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Content Security Policy
    nonce = getattr(g, 'csp_nonce', '')
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        f"script-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://maxcdn.bootstrapcdn.com https://api.mapbox.com 'nonce-{nonce}' blob:; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://api.mapbox.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://maxcdn.bootstrapcdn.com; "
        "img-src 'self' data: https://api.mapbox.com https://miro.medium.com https://cdn-images-1.medium.com https://i.gifer.com; "
        "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com data:; "
        "connect-src 'self' https://api.mapbox.com https://mnist-api-622916111375.us-central1.run.app; "
        "worker-src 'self' blob:; "
        "object-src 'none'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests"
    )
    
    # Referrer Policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Force HTTPS in production
    if request.is_secure:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    return response
    
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
    
    Implements graceful handling for timeout and network errors.

    Returns:
        Template: The blog.html template populated with Medium articles.
                 If feed fails to load, shows error message with fallback.
    """
    articles = fetch_articles()
    
    # Handle timeout and error cases
    if isinstance(articles, tuple):
        error_message, status_code = articles
        app.logger.warning(f"Blog feed error: {error_message} (Status: {status_code})")
        
        # Return template with error message instead of failing completely
        return render_template('pages/blog.html', 
                             articles=[], 
                             feed_error=error_message,
                             status_code=status_code)
    
    return render_template('pages/blog.html', articles=articles)

@app.route('/map')
def map_page():
    """
    Renders the travel map page with Mapbox integration.
    
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


############################## TESTING FEATURES ##############################
#### WebSub Callback:
@app.route('/websub/callback', methods=['GET', 'POST'])
def websub_callback():
    """
    Endpoint to receive YouTube WebSub notifications.
    
    GET: Hub Challenge verification
    POST: Receives notifications of new videos
    """
    result = handle_websub_callback(
        request_method=request.method,
        request_args=request.args,
        request_data=request.get_data(as_text=True),
        request_headers=request.headers
    )
    
    if isinstance(result, tuple):
        return result
    
    return result


############################## MAIN EXECUTION ##############################
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)