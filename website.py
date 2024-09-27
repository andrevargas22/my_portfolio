"""
This module defines the Flask web application for André Vargas's personal website. The application serves different 
routes to render templates for various sections of the website, including English and Portuguese (PT-BR) versions 
of the homepage and other pages.

The deployed application is hosted on Google Cloud Run and can be accessed at the following URL: andrevargas.com.br

Author: André Vargas
"""

import os
import io
from google.cloud import storage
import csv
from flask import Flask, render_template, redirect, url_for, request
import feedparser
from datetime import datetime, timedelta
    
app = Flask(__name__)

############################## ENGLISH ROUTES ##############################
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

############################## PORTUGUESE ROUTES ##############################
@app.route('/br')
def home_pt():
    """
    Renders the Portuguese homepage.

    Returns:
        Template: The index.html template for the Portuguese homepage.
    """
    return render_template('pt/index.html')

@app.route('/br/about')
def about_pt():
    """
    Renders the Portuguese 'About' page.

    Returns:
        Template: The about.html template for the Portuguese section.
    """
    return render_template('pt/about.html')

@app.route('/br/blog')
def blog_pt():
    """
    Renders the Portuguese blog page with articles fetched from the Medium feed.

    Returns:
        Template: The blog.html template populated with Medium articles in Portuguese.
    """
    articles = fetch_articles()
    return render_template('pt/blog.html', articles=articles)

@app.route('/br/map')
def world_pt():
    """
    Renders the Portuguese map page.

    Returns:
        Template: The map.html template for the Portuguese section.
    """
    return render_template('pt/map.html')

@app.route('/br/games')
def games_pt():
    """
    Renders the Portuguese games page.

    Returns:
        Template: The game.html template for the Portuguese section.
    """
    return render_template('pt/game.html')

@app.route('/br/mnist_api')
def mnist_pt():
    """
    Renders the MNIST page in Portuguese and passes the MNIST API endpoint.

    Returns:
        Template: The mnist.html template with the MNIST API endpoint for the Portuguese section.
    """
    mnist_endpoint = os.getenv('MNIST_ENDPOINT')
    return render_template('pt/mnist.html', mnist_endpoint=mnist_endpoint)

client = storage.Client()
bucket_name = 'remedios_andre'
blob_name = 'data_remedios.csv'

@app.route('/remedios', methods=['GET', 'POST'])
def remedios():
    """
    Handles the '/remedios' route for displaying and updating medication quantities.

    - On GET request: Displays the current medication data.
    - On POST request: Updates the medication quantities based on form input.
    """
    try:
        
        # Get the bucket and blob from Google Cloud Storage
        bucket = client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)

        # Download the content of the blob as text
        content = blob.download_as_text()

        # Read CSV content
        csv_reader = csv.reader(io.StringIO(content))
        data = []

        # Get headers from the CSV and convert them to lowercase
        headers = [h.strip().lower() for h in next(csv_reader)]

        # Read CSV data and create a list of dictionaries
        for row in csv_reader:
            if not row or len(row) != len(headers):
                print("Invalid or empty row ignored:", row)
                continue
            item = dict(zip(headers, row))
            print("Item:", item)  
            data.append(item)

        if request.method == 'POST':
            # Get the values from the form submission, defaulting to 0 if not provided
            n_tacrolimus_add = int(request.form.get('n_tacrolimus', 0))
            n_azathioprine_add = int(request.form.get('n_azatioprina', 0))

            # Update the medication quantities
            for item in data:
                if 'n_tacrolimus' in item and 'n_azatioprina' in item:
                    item['n_tacrolimus'] = str(int(item['n_tacrolimus']) + n_tacrolimus_add)
                    item['n_azatioprina'] = str(int(item['n_azatioprina']) + n_azathioprine_add)
                else:
                    print("Item with missing keys:", item)

            # Write the updated data back to CSV
            output = io.StringIO()
            csv_writer = csv.writer(output)
            csv_writer.writerow(headers)
            for item in data:
                row = [item.get(header, '') for header in headers]
                csv_writer.writerow(row)
            updated_content = output.getvalue()

            # Upload the updated content back to the blob
            blob.upload_from_string(updated_content, content_type='text/csv')

            # Redirect to the same route to display updated data
            return redirect(url_for('remedios'))

        # Render the template with the current data
        return render_template('pt/remedios.html', dados=data, headers=headers)

    except Exception as e:
        # Render an error template with the exception message
        return render_template('erro.html', mensagem=str(e)), 500

@app.route('/calcular')
def calcular():
    """
    Handles the '/calcular' route to calculate and display the remaining days of medication supply.

    - Reads medication quantities from a CSV file in Google Cloud Storage.
    - Calculates how many days are left based on daily consumption rates.
    - Renders a result template with the calculated data.
    """
    try:
        # Get the bucket and blob from Google Cloud Storage
        bucket = client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)

        # Download the content of the blob as text
        content = blob.download_as_text()

        # Read CSV content
        csv_reader = csv.reader(io.StringIO(content))

        # Get headers from the CSV and convert them to lowercase
        headers = [h.strip().lower() for h in next(csv_reader)]

        # Read the last valid row from the CSV (assuming it contains current quantities)
        for row in csv_reader:
            if not row or len(row) != len(headers):
                continue
            item = dict(zip(headers, row))

        # Get medication quantities, defaulting to 0 if not present
        n_tacrolimus = int(item.get('n_tacrolimus', 0))
        n_azathioprine = int(item.get('n_azatioprina', 0))

        # Define daily consumption rates
        tacrolimus_consumption = 6
        azathioprine_consumption = 4

        # Calculate the number of days left for each medication
        days_tacrolimus = n_tacrolimus // tacrolimus_consumption if tacrolimus_consumption > 0 else 0
        days_azathioprine = n_azathioprine // azathioprine_consumption if azathioprine_consumption > 0 else 0

        # Determine the minimum days left between the two medications
        days_remaining = min(days_tacrolimus, days_azathioprine)
        days_remaining = max(days_remaining, 0)  # Ensure non-negative value

        today = datetime.now().date()
        last_day = today + timedelta(days=days_remaining)

        # Render the result template with the calculated data
        return render_template(
            'pt/resultado.html',
            ultimo_dia=last_day.strftime('%d/%m/%Y'),
            dias_restantes=days_remaining
        )

    except Exception as e:
        # Render an error template with the exception message if an error occurs
        return render_template('erro.html', mensagem=str(e)), 500


############################## COMMON FUNCTIONS ##############################

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
