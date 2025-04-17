import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from transformers import pipeline
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import requests
from datetime import datetime, timedelta

class MarketSentimentAnalyzer:
    def __init__(self):
        self.sentiment_analyzer = pipeline("sentiment-analysis")
        self.sia = SentimentIntensityAnalyzer()
        nltk.download('vader_lexicon')
        
    def analyze_news_sentiment(self, news_articles: List[Dict]) -> Dict[str, float]:
        """Analyze sentiment from news articles"""
        sentiments = []
        for article in news_articles:
            # Analyze headline
            headline_sentiment = self.sentiment_analyzer(article['headline'])[0]
            # Analyze content
            content_sentiment = self.sia.polarity_scores(article['content'])
            
            # Combine sentiments
            combined_score = (
                (headline_sentiment['score'] if headline_sentiment['label'] == 'POSITIVE' else -headline_sentiment['score']) +
                content_sentiment['compound']
            ) / 2
            
            sentiments.append(combined_score)
        
        return {
            'average_sentiment': np.mean(sentiments),
            'sentiment_std': np.std(sentiments),
            'sentiment_count': len(sentiments)
        }
    
    def analyze_social_media(self, tweets: List[str]) -> Dict[str, float]:
        """Analyze sentiment from social media posts"""
        sentiments = []
        for tweet in tweets:
            sentiment = self.sia.polarity_scores(tweet)
            sentiments.append(sentiment['compound'])
        
        return {
            'average_sentiment': np.mean(sentiments),
            'sentiment_std': np.std(sentiments),
            'sentiment_count': len(sentiments)
        }
    
    def get_market_sentiment(self, symbol: str) -> Dict:
        """Get overall market sentiment for a symbol"""
        # TODO: Implement actual API calls to news and social media
        # For now, using mock data
        news_articles = [
            {'headline': f'Positive news about {symbol}', 'content': 'Great performance...'},
            {'headline': f'Mixed news about {symbol}', 'content': 'Some concerns...'}
        ]
        
        tweets = [
            f'$ {symbol} looking strong today!',
            f'Not sure about {symbol} future prospects'
        ]
        
        news_sentiment = self.analyze_news_sentiment(news_articles)
        social_sentiment = self.analyze_social_media(tweets)
        
        # Combine sentiments with weights
        combined_sentiment = (
            news_sentiment['average_sentiment'] * 0.6 +
            social_sentiment['average_sentiment'] * 0.4
        )
        
        return {
            'combined_sentiment': combined_sentiment,
            'news_sentiment': news_sentiment,
            'social_sentiment': social_sentiment,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_sentiment_trend(self, symbol: str, days: int = 7) -> pd.DataFrame:
        """Get sentiment trend over time"""
        # TODO: Implement actual historical data retrieval
        # For now, generating mock data
        dates = pd.date_range(end=datetime.now(), periods=days)
        sentiments = np.random.normal(0, 0.2, days)
        
        return pd.DataFrame({
            'date': dates,
            'sentiment': sentiments
        }) 