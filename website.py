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
import jsonify
    
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

############################## TESTING ##############################

# Inicializa o cliente do GCS fora da função
client = storage.Client()
bucket_name = 'remedios_andre'
blob_name = 'data_remedios.csv'

@app.route('/remedios', methods=['GET', 'POST'])
def remedios():
    try:
        # Obtém o bucket e o blob (arquivo)
        bucket = client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)

        # Faz o download do conteúdo do blob como string
        conteudo = blob.download_as_text()

        # Usa o módulo csv para ler o conteúdo
        leitor_csv = csv.reader(io.StringIO(conteudo))
        dados = []

        # Lê o cabeçalho do CSV e padroniza
        headers = [h.strip().lower() for h in next(leitor_csv)]
        print("Cabeçalhos padronizados:", headers)  # Para depuração

        # Itera sobre as linhas e cria uma lista de dicionários
        for linha in leitor_csv:
            if not linha or len(linha) != len(headers):
                print("Linha inválida ou vazia ignorada:", linha)
                continue
            item = dict(zip(headers, linha))
            print("Item:", item)  # Para depuração
            dados.append(item)

        # Verifica se é uma requisição POST (formulário enviado)
        if request.method == 'POST':
            # Obtém os valores do formulário
            n_tacrolimus_adicionar = int(request.form.get('n_tacrolimus', 0))
            n_azatioprina_adicionar = int(request.form.get('n_azatioprina', 0))

            # Atualiza os valores
            for item in dados:
                if 'n_tacrolimus' in item and 'n_azatioprina' in item:
                    item['n_tacrolimus'] = str(int(item['n_tacrolimus']) + n_tacrolimus_adicionar)
                    item['n_azatioprina'] = str(int(item['n_azatioprina']) + n_azatioprina_adicionar)
                else:
                    print("Item com chaves ausentes:", item)

            # Converte os dados de volta para o formato CSV
            saida = io.StringIO()
            escritor_csv = csv.writer(saida)
            escritor_csv.writerow(headers)
            for item in dados:
                linha = [item.get(header, '') for header in headers]
                escritor_csv.writerow(linha)
            conteudo_atualizado = saida.getvalue()

            # Faz o upload do conteúdo atualizado para o GCS
            blob.upload_from_string(conteudo_atualizado, content_type='text/csv')

            # Redireciona para a mesma página para evitar reenvio de formulário
            return redirect(url_for('remedios'))

        # Renderiza o template HTML com os dados
        return render_template('remedios.html', dados=dados, headers=headers)

    except Exception as e:
        return render_template('erro.html', mensagem=str(e)), 500

@app.route('/calcular')
def calcular():
    try:
        # Obtém o bucket e o blob (arquivo)
        bucket = client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)

        # Faz o download do conteúdo do blob como string
        conteudo = blob.download_as_text()

        # Usa o módulo csv para ler o conteúdo
        leitor_csv = csv.reader(io.StringIO(conteudo))

        # Lê o cabeçalho do CSV e padroniza
        headers = [h.strip().lower() for h in next(leitor_csv)]
        print("Cabeçalhos padronizados:", headers)  # Para depuração

        # Itera sobre as linhas e cria um dicionário com os dados
        for linha in leitor_csv:
            if not linha or len(linha) != len(headers):
                print("Linha inválida ou vazia ignorada:", linha)
                continue
            item = dict(zip(headers, linha))
            print("Item:", item)  # Para depuração

        # Extrai as quantidades atuais dos remédios
        n_tacrolimus = int(item.get('n_tacrolimus', 0))
        n_azatioprina = int(item.get('n_azatioprina', 0))

        # Consumo diário
        consumo_tacrolimus = 6
        consumo_azatioprina = 4

        # Calcula o número de dias restantes para cada remédio
        dias_tacrolimus = n_tacrolimus // consumo_tacrolimus if consumo_tacrolimus > 0 else 0
        dias_azatioprina = n_azatioprina // consumo_azatioprina if consumo_azatioprina > 0 else 0

        # Determina o último dia em que será possível tomar todos os remédios
        dias_restantes = min(dias_tacrolimus, dias_azatioprina)
        dias_restantes = max(dias_restantes, 0)  # Garante que não seja negativo
        hoje = datetime.now().date()
        ultimo_dia = hoje + timedelta(days=dias_restantes)

        # Renderiza o resultado em um template
        return render_template('resultado.html', ultimo_dia=ultimo_dia.strftime('%d/%m/%Y'), dias_restantes=dias_restantes)

    except Exception as e:
        return render_template('erro.html', mensagem=str(e)), 500

    
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
