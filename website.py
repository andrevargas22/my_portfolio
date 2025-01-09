"""
This module defines the Flask web application for André Vargas's personal website. The application serves different 
routes to render templates for various sections of the website.

The deployed application is hosted on Google Cloud Run and can be accessed at the following URL: andrevargas.com.br

Author: André Vargas
"""

import os
from flask import Flask, render_template, request, Response, jsonify
from google.cloud import storage
import pandas as pd
from io import BytesIO
import feedparser
    
app = Flask(__name__)

############################## TEMPORARY AUTH ##############################
USERNAME = 'admin'
PASSWORD = '123'

def check_auth(username, password):
    return username == USERNAME and password == PASSWORD

def authenticate():
    return Response(
        'Acesso restrito.\n',
        401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

@app.before_request
def require_auth():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()
    
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

############################## TEMPORARY FEATURE ##############################

# Função para baixar o CSV do bucket
def download_csv_from_gcs(bucket_name, blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    csv_data = blob.download_as_bytes()
    df = pd.read_csv(BytesIO(csv_data), dtype={
        "Ordem pref.": "Int64",
        "Habitantes": "Int64",
        "Nº. defensores": "Int64"
    })
    return df

# Função para atualizar o CSV no bucket
def upload_csv_to_gcs(df, bucket_name, blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    csv_data = df.to_csv(index=False).encode("utf-8")
    blob.upload_from_string(csv_data, content_type="text/csv")

@app.route("/cidades")
def cidades():
    bucket_name = "data_cidades"
    blob_name = "cidades.csv"

    # Baixar o CSV e converter em DataFrame
    df = download_csv_from_gcs(bucket_name, blob_name)

    # Ordenar pelo campo "Ordem pref." de forma crescente
    df = df.sort_values(by="Ordem pref.", na_position="last")

    # Substituir NaN por string vazia em colunas que não são numéricas
    non_numeric_cols = df.columns.difference(["Ordem pref.", "Habitantes", "Nº. defensores"])
    df[non_numeric_cols] = df[non_numeric_cols].fillna("")

    for col in non_numeric_cols:
        df[col] = df[col].astype(str).str.replace(r'\s+', ' ', regex=True).str.strip()
   
    # Converter DataFrame para HTML
    table_html = df.to_html(classes="table table-striped table-bordered", index=False, escape=False)

    return render_template("eng/cidades.html", table_html=table_html)

@app.route("/update_cell", methods=["POST"])
@app.route("/update_cell", methods=["POST"])
def update_cell():
    data = request.json
    bucket_name = "data_cidades"
    blob_name = "cidades.csv"

    # Parâmetros recebidos
    row_index = int(data["row_index"])
    column_name = data["column_name"]
    new_value = data["new_value"]

    # Baixa o CSV e atualiza
    df = download_csv_from_gcs(bucket_name, blob_name)

    # Verifica se a coluna é "Ordem pref."
    if column_name == "Ordem pref.":
        if new_value == "":
            new_value = None  # Deixa o valor como NaN se vazio
        else:
            new_value = int(new_value)  # Converte para número

        # Identifica a cidade a ser movida
        current_city = df.iloc[row_index]
        current_order = current_city["Ordem pref."]

        if pd.isna(current_order):
            current_order = None

        if new_value != current_order:
            # Remove a cidade temporariamente
            df = df.drop(row_index).reset_index(drop=True)

            if new_value is not None:
                # Ajusta as posições das outras cidades
                df.loc[(df["Ordem pref."].notna()) & (df["Ordem pref."] >= new_value), "Ordem pref."] += 1

            # Adiciona a cidade com a nova ordem ou em branco
            new_row = current_city.copy()
            new_row["Ordem pref."] = new_value
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        # Ordena a tabela com `na_position="last"`
        df = df.sort_values(by="Ordem pref.", na_position="last").reset_index(drop=True)

        # Salva o CSV atualizado no bucket
        upload_csv_to_gcs(df, bucket_name, blob_name)

        return jsonify({"message": "CSV atualizado com sucesso!"}), 200
    else:
        if new_value == "":
            new_value = None

        if column_name in ["Habitantes", "Nº. defensores"]:
            new_value = pd.to_numeric(new_value, errors="coerce")
            if pd.notna(new_value):
                new_value = int(new_value)

        df.iloc[row_index, df.columns.get_loc(column_name)] = new_value

        upload_csv_to_gcs(df, bucket_name, blob_name)
        return jsonify({"message": "CSV atualizado com sucesso!"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)