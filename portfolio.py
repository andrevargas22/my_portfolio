import mlflow
import re
import os
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
import pickle
from flask import Flask, render_template, request

nltk.download("stopwords")
stemmer = PorterStemmer()

TRACKING_URI = "https://mlflow-server-wno7iop4fa-uc.a.run.app/"
mlflow.set_tracking_uri(TRACKING_URI)

def review_to_words(review):
    text = BeautifulSoup(review, "html.parser").get_text() # Remove HTML tags
    text = re.sub(r"[^a-zA-Z0-9]", " ", text.lower()) # Convert to lower case
    words = text.split() # Split string into words
    words = [w for w in words if w not in stopwords.words("english")] # Remove stopwords
    words = [PorterStemmer().stem(w) for w in words] # Stemming    
    return words

def preprocess_input(review):
    # Preprocess the input review
    words = review_to_words(review)
    
    # Convert the input review into BoW features
    vectorizer = CountVectorizer(vocabulary=vocabulary)
    features = vectorizer.transform([' '.join(words)]).toarray()
    
    return features  

app = Flask(__name__)

with open("model_files/vocabulary.pkl", "rb") as f:
    vocabulary = pickle.load(f)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/sentiment_analysis')
def sentiment_analysis():
    return render_template('sentiment_analysis.html')

@app.route('/sentiment_results', methods=['POST', 'GET'])
def sentiment_results():
    
    # Fetch the model from the Model Registry
    model_name = "sentiment_analysis"
    stage = "staging"

    model_uri = f"models:/{model_name}/{stage}"
    loaded_model = mlflow.pyfunc.load_model(model_uri=model_uri)

    if request.method == 'POST':
        text = request.form['textArea1']  # Get text from textarea
        features = preprocess_input(text)
        prediction = loaded_model.predict(features)
        pred = prediction[0]
        print(text)
        print(pred)
        return render_template('sentiment_analysis_results.html', text=text, pred=pred)
    
if __name__ == '__main__':
    # Development:
    #app.run(debug=True)
    
    # Production:
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
