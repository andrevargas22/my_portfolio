import requests
import yaml
import os
from flask import Flask, render_template, request

SENTIMENT_API = "https://sentiment-analysis-api-p6kayhv22a-uc.a.run.app/predict"

# Load configuration from config.yaml
with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)
    
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/sentiment_analysis')
def sentiment_analysis():
    return render_template('sentiment_analysis.html')

@app.route('/sentiment_results', methods=['POST', 'GET'])
def sentiment_results():

    if request.method == 'POST':
        text = request.form['textArea1']  # Get text from textarea

        # Send a POST request to the FastAPI endpoint
        response = requests.post(SENTIMENT_API, json={"text": text})
                
        if response.status_code == 200:
            
            # Get the predicted sentiment label from the response
            pred = response.json()["sentiment"]
            return render_template('sentiment_analysis_results.html', text=text, pred=pred)
    
if __name__ == '__main__':

    if config.get('env') == 'production':
        port = int(os.environ.get("PORT", 8080))
        app.run(host='0.0.0.0', port=port)
    
    else:
        app.run(debug=True)

