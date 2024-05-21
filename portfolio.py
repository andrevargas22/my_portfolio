import os
from flask import Flask, render_template
    
app = Flask(__name__)

############################## ENGLISH ##############################
@app.route('/')
def home():
    return render_template('eng/index.html')

@app.route('/about')
def about():
    return render_template('eng/about.html')

@app.route('/world_map')
def world():
    return render_template('eng/world_map.html')

@app.route('/games')
def games():
    return render_template('eng/game.html')

############################## PT-BR ##############################
@app.route('/pt-br')
def home_pt():
    return render_template('pt/index.html')

@app.route('/sobre')
def about_pt():
    return render_template('pt/about.html')

@app.route('/mapa_mundi')
def world_pt():
    return render_template('pt/world_map.html')

@app.route('/jogos')
def jogos():
    return render_template('pt/game.html')

############################## TEST ##############################

if __name__ == '__main__':

    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)