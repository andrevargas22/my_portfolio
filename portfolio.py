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

@app.route('/map')
def world():
    return render_template('eng/map.html')

@app.route('/games')
def games():
    return render_template('eng/game.html')

############################## PT-BR ##############################
@app.route('/br')
def home_pt():
    return render_template('pt/index.html')

@app.route('/br/about')
def about_pt():
    return render_template('pt/about.html')

@app.route('/br/map')
def world_pt():
    return render_template('pt/map.html')

@app.route('/br/games')
def games_pt():
    return render_template('pt/game.html')

if __name__ == '__main__':

    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)