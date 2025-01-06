"""
This module defines the Flask web application for André Vargas's personal website. The application serves different 
routes to render templates for various sections of the website.

The deployed application is hosted on Google Cloud Run and can be accessed at the following URL: andrevargas.com.br

Author: André Vargas
"""

import os
import csv
from flask import Flask, render_template, request, jsonify
import feedparser
    
app = Flask(__name__)

CSV_FILE = 'cidades.csv'

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

@app.route('/cidades')
def cidades():
    """
    Lê o CSV e envia ao template.
    """
    with open(CSV_FILE, 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
    return render_template('eng/cidades.html', data=data)

@app.route('/cidades/ordem')
def cidades_ordem():
    """
    Mostra APENAS 'Ordem' (coluna "Ordem pref.") e 'Cidade' (coluna "Lotação")
    em ordem crescente de acordo com a coluna "Ordem pref.".
    """
    with open(CSV_FILE, 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        data = list(reader)

    # data[0] é o cabeçalho, data[1:] são as linhas de dados
    header = data[0]  # ["Lotação", "Ordem pref.", "Informações...", ...]
    rows = data[1:]

    # Precisamos identificar em qual índice está "Lotação" e "Ordem pref."
    # Supondo que:  "Lotação"     => índice 0
    #              "Ordem pref." => índice 1
    # (É como você descreveu nos exemplos anteriores.)
    idx_lotacao = 0
    idx_pref = 1

    # Ordenar as linhas pelo valor numérico da coluna idx_pref
    def to_int_or_large(s):
        try:
            return int(s)
        except:
            return 999999  # se não for número, joga pro fim
    
    sorted_rows = sorted(
        rows,
        key=lambda r: to_int_or_large(r[idx_pref])
    )

    return render_template('eng/cidades_ordem.html',
                           sorted_rows=sorted_rows,
                           idx_lotacao=idx_lotacao,
                           idx_pref=idx_pref)
    
@app.route('/update_cell', methods=['POST'])
def update_cell():
    content = request.json
    row_index = int(content['rowIndex'])  # 1-based, pois pulamos cabeçalho
    col_index = int(content['colIndex'])
    new_value = content['newValue']

    with open(CSV_FILE, 'r', encoding='utf-8', newline='') as f:
        data = list(csv.reader(f))

    header = data[0]
    rows = data[1:]  # só as linhas de dados

    # Se for outra coluna que não seja "Ordem pref." (col_index=1), faz o normal:
    if col_index != 1:
        data[row_index][col_index] = new_value
        with open(CSV_FILE, 'w', encoding='utf-8', newline='') as f:
            csv.writer(f).writerows(data)
        return jsonify({'status':'success','message':'Célula atualizada (sem shift).'})
    
    # Agora, col_index=1 => SHIFT em cadeia
    changed_idx = row_index - 1  # pois rows[0] é a 1ª linha de dados
    try:
        old_pref = int(rows[changed_idx][1])
        new_pref = int(new_value)
    except ValueError:
        # Se não dá pra converter, simplesmente salva
        data[row_index][col_index] = new_value
        with open(CSV_FILE, 'w', encoding='utf-8', newline='') as f:
            csv.writer(f).writerows(data)
        return jsonify({'status':'success','message':'Não é número, salvando sem shift.'})

    if old_pref == new_pref:
        return jsonify({'status':'success','message':'Preferência não alterada.'})

    def get_pref(r):
        try:
            return int(r[1])
        except:
            return None

    if new_pref < old_pref:
        # Ex.: 3 -> 1
        current = old_pref
        while current > new_pref:
            looking_for = current - 1
            # Achar EXATAMENTE a linha que tem 'looking_for' e transformá-la em 'current'
            for r in rows:
                if get_pref(r) == looking_for:
                    r[1] = str(current)
                    break
            current -= 1
        # No fim, atribuir new_pref à linha editada
        rows[changed_idx][1] = str(new_pref)

    else:  # new_pref > old_pref
        # Ex.: 1 -> 3
        current = old_pref
        while current < new_pref:
            looking_for = current + 1
            # Achar EXATAMENTE a linha que tem 'looking_for' e transformar em (looking_for - 1)
            for r in rows:
                if get_pref(r) == looking_for:
                    r[1] = str(looking_for - 1)
                    break
            current += 1
        rows[changed_idx][1] = str(new_pref)

    # Salva de volta
    new_data = [header] + rows
    with open(CSV_FILE, 'w', encoding='utf-8', newline='') as f:
        csv.writer(f).writerows(new_data)
    
    return jsonify({'status':'success','message':'Shift em cadeia aplicado.'})


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