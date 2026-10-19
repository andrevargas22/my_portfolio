"""
This module defines the Flask web application for André Vargas's personal website. The application serves different
routes to render templates for various sections of the website.

The deployed application is hosted on Google Cloud Run and can be accessed at the following URL: andrevargas.com.br

Author: André Vargas
"""

# Imports
import os
import logging
from datetime import date
from flask import Flask, render_template, request, g, redirect, url_for
import secrets

# Production functions
from scripts.articles import fetch_articles
from scripts.games import get_games_by_letter, load_games
from scripts.energy import fetch_energy_forecast_data, fetch_energy_forecast_metadata, fetch_energy_activity_log

# Testing functions
from scripts.testing import handle_websub_callback, ask_rag_assistant

# Configure logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Security: Limit request body size
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024


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
    response.headers["X-Content-Type-Options"] = "nosniff"

    # Prevent clickjacking attacks
    response.headers["X-Frame-Options"] = "DENY"

    # XSS protection
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # Content Security Policy
    nonce = getattr(g, "csp_nonce", "")
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        f"script-src 'self' https://cdn.jsdelivr.net https://unpkg.com https://cdnjs.cloudflare.com https://maxcdn.bootstrapcdn.com https://api.mapbox.com https://cdn.plot.ly 'nonce-{nonce}' blob:; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://api.mapbox.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://maxcdn.bootstrapcdn.com; "
        "img-src 'self' data: https://api.mapbox.com https://miro.medium.com https://cdn-images-1.medium.com https://i.gifer.com; "
        "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com data:; "
        "connect-src 'self' https://api.mapbox.com https://mnist-api-622916111375.us-central1.run.app http://localhost:8001; "
        "worker-src 'self' blob:; "
        "object-src 'none'; frame-ancestors 'none'; base-uri 'self'; form-action 'self';"
    )

    # Referrer Policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Force HTTPS in production
    if request.is_secure:
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

    response.headers["Permissions-Policy"] = (
        "geolocation=(), microphone=(), camera=(), payment=(), usb=(), accelerometer=(), gyroscope=(), "
        "magnetometer=(), interest-cohort=(), fullscreen=(self)"
    )

    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"

    response.headers["Origin-Agent-Cluster"] = "?1"

    # Cache static assets (skip in debug so local changes show without a hard refresh)
    if request.path.startswith('/static/') and not app.debug:
        response.cache_control.max_age = 31536000  # 1 year
        response.cache_control.public = True

    return response


############################## PAGE ROUTES ##############################
@app.route("/")
def home():
    """
    Renders the homepage (profile, bio, and experience timeline).

    Returns:
        Template: The index.html landing page.
    """
    return render_template("pages/index.html")


@app.route("/about")
def about():
    """Permanent redirect for the old /about URL to the landing page."""
    return redirect(url_for("home"), code=301)


@app.route("/blog")
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
        return render_template(
            "pages/blog.html",
            articles=[],
            feed_error=error_message,
            status_code=status_code,
        )

    return render_template("pages/blog.html", articles=articles)


@app.route("/map")
def map_page():
    """
    Renders the travel map page with Mapbox integration.

    Returns:
        Template: The map.html template for the Map section.
    """
    mapbox_token = os.getenv("MAPBOX_ACCESS_TOKEN")
    return render_template("pages/map.html", mapbox_token=mapbox_token)


@app.route("/games")
def games():
    """
    Renders the finished games page: stats header, auto list of the games
    finished this year, Top 10 shelf, and the searchable archive grid. All
    derived from games.json at render time.
    """
    games_list = load_games()

    platforms = {}
    for game in games_list:
        p = platforms.setdefault(game["platform_id"], {"id": game["platform_id"], "name": game["platform"], "count": 0})
        p["count"] += 1
    platforms = sorted(platforms.values(), key=lambda f: (-f["count"], f["name"]))

    current_year = date.today().year
    years = [game["year"] for game in games_list]
    stats = {
        "total": len(games_list),
        "n_platforms": len(platforms),
        "year_min": min(years) if years else 0,
        "year_max": max(years) if years else 0,
        "current_year": current_year,
    }
    recent = sorted(
        (game for game in games_list if game.get("beaten") == current_year),
        key=lambda game: game["title"],
    )
    top10 = sorted(
        (game for game in games_list if game.get("top_10")),
        key=lambda game: game["top_10"],
    )
    return render_template(
        "pages/game.html",
        get_games_by_letter=get_games_by_letter,
        platforms=platforms,
        total=len(games_list), top10_count=len(top10),
        stats=stats, recent=recent, top10=top10,
    )


@app.route("/mnist_api")
def mnist():
    """
    Renders the MNIST 3D Visualization page with the API endpoint.

    Returns:
        Template: The mnist_visual.html template with the MNIST API endpoint.
    """
    mnist_endpoint = os.getenv("MNIST_ENDPOINT")
    return render_template("pages/mnist_visual.html", mnist_endpoint=mnist_endpoint)


@app.route("/energy_forecast")
def energy_forecast():
    """
    Renders the Brazilian Energy Consumption Forecast page.
    Fetches the latest Plotly figure JSON from the AutoML repo and passes it
    to the template for client-side rendering via Plotly.js.
    """
    figure_data = fetch_energy_forecast_data()
    metadata = fetch_energy_forecast_metadata()
    activity_log = fetch_energy_activity_log()
    return render_template(
        "pages/energy_forecast.html",
        figure_data=figure_data, metadata=metadata, activity_log=activity_log,
    )


############################## TESTING FEATURES ##############################
#### RAG Assistant (chat proxy):
@app.route("/api/chat", methods=["POST"])
def api_chat():
    """
    Thin proxy to the private rag-assistant service on Cloud Run.

    The browser can't hold credentials, so this route authenticates on its
    behalf (ID token da site-sa) and relays the message. Business logic,
    guardrails and cost control live in the website-RAG-assistant repo.
    """
    data = request.get_json(silent=True)
    if not data or not isinstance(data.get("message"), str):
        return {"error": "Expected JSON body with a 'message' string."}, 400

    message = data["message"].strip()
    if not message or len(message) > 2000:
        return {"error": "Message must be between 1 and 2000 characters."}, 400

    payload, status_code = ask_rag_assistant(message)
    return payload, status_code


#### WebSub Callback:
@app.route("/websub/callback", methods=["GET", "POST"])
def websub_callback():
    """
    Endpoint to receive YouTube WebSub notifications.

    GET: Hub Challenge verification
    POST: Receives notifications of new videos
    
    Validates videos and dispatches processing to GitHub Actions.
    """
    result = handle_websub_callback(
        request_method=request.method,
        request_args=request.args,
        request_data=request.get_data(as_text=False),
        request_headers=request.headers,
    )

    if isinstance(result, tuple):
        return result
    
    return result


@app.route("/websub/health", methods=["GET"])
def websub_health():
    """
    Health check endpoint for WebSub functionality.
    
    Returns diagnostic information about WebSub configuration.
    """
    import os
    
    health_status = {
        "status": "ok",
        "endpoint": "/websub/callback",
        "hmac_configured": bool(os.getenv("WEBHOOK_HMAC_SECRET")),
        "github_app_configured": bool(
            os.getenv("GRENALBOT_ID") and 
            os.getenv("GRENALBOT_INSTALLATION_ID") and 
            os.getenv("GRENALBOT_PRIVATE_KEY")
        ),
        "youtube_api_configured": bool(os.getenv("YOUTUBE_API_KEY")),
        "gcs_configured": bool(os.getenv("GCS_BUCKET_NAME")),
        "timestamp": request.headers.get("X-Request-Time", "unknown")
    }
    
    return health_status, 200
 
############################## MAIN EXECUTION ##############################
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
