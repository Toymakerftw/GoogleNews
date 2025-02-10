import os
from flask import Flask, request, render_template, jsonify
import requests
from datetime import datetime, timedelta
from scraper.google_news_scraper import GoogleBusinessNewsScraper

# Hugging Face Sentiment Analysis Configuration
SENTIMENT_API_URL = "https://api-inference.huggingface.co/models/mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
HF_TOKEN = os.getenv('HUGGINGFACE_TOKEN', '<token>')

class NewsSentimentAnalyzer:
    def __init__(self):
        self.scraper = GoogleBusinessNewsScraper(max_articles=20)
        self.headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    def fetch_news(self, company):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        return self.scraper.scrape(company, start_date, end_date)

    def analyze_sentiment(self, text):
        try:
            response = requests.post(
                SENTIMENT_API_URL, 
                headers=self.headers, 
                json={"inputs": text}
            )
            return response.json()[0]
        except Exception as e:
            return [{"label": "ERROR", "score": 0}]

    def analyze_news_sentiment(self, company):
        news_articles = self.fetch_news(company)
        sentiments = []

        for article in news_articles:
            # Combine title and description for sentiment analysis
            text = f"{article.get('title', '')} {article.get('description', '')}"
            sentiment = self.analyze_sentiment(text)
            
            sentiments.append({
                "title": article.get('title', ''),
                "url": article.get('url', ''),
                "source": article.get('source', ''),
                "date": article.get('date', ''),
                "sentiment": sentiment[0]['label'],
                "confidence": sentiment[0]['score']
            })

        return sentiments

app = Flask(__name__)
analyzer = NewsSentimentAnalyzer()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        company = request.form.get('company')
        try:
            results = analyzer.analyze_news_sentiment(company)
            
            # Aggregate sentiment statistics
            sentiment_counts = {
                'POSITIVE': len([r for r in results if r['sentiment'] == 'POSITIVE']),
                'NEGATIVE': len([r for r in results if r['sentiment'] == 'NEGATIVE']),
                'NEUTRAL': len([r for r in results if r['sentiment'] == 'NEUTRAL'])
            }
            
            return render_template('index.html', 
                                   results=results, 
                                   company=company,
                                   sentiment_counts=sentiment_counts)
        except Exception as e:
            return render_template('index.html', error=str(e))
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Change the port here