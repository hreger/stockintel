from typing import Dict, List, Optional
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import pandas as pd
from textblob import TextBlob

class FinancialSentimentAnalyzer:
    def __init__(self):
        # Initialize both ML and lexicon-based approaches
        self.tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
        self.model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
        self.financial_lexicon = self._load_financial_lexicon()
        
    def _load_financial_lexicon(self) -> Dict[str, float]:
        """Load specialized financial sentiment lexicon"""
        return {
            "bullish": 1.0,
            "bearish": -1.0,
            "outperform": 0.8,
            "underperform": -0.8,
            # ... extend with comprehensive financial terms
        }
        
    def analyze_sentiment(self, text: str, use_hybrid: bool = True) -> Dict:
        """
        Hybrid sentiment analysis combining ML and lexicon approaches
        
        Args:
            text: Financial text to analyze
            use_hybrid: Whether to use both ML and lexicon approaches
            
        Returns:
            Dict containing sentiment scores and confidence metrics
        """
        ml_sentiment = self._get_ml_sentiment(text)
        
        if not use_hybrid:
            return ml_sentiment
            
        lexicon_sentiment = self._get_lexicon_sentiment(text)
        
        # Combine both approaches with confidence weighting
        combined_score = (
            ml_sentiment['score'] * ml_sentiment['confidence'] +
            lexicon_sentiment['score'] * lexicon_sentiment['confidence']
        ) / (ml_sentiment['confidence'] + lexicon_sentiment['confidence'])
        
        return {
            'score': combined_score,
            'ml_score': ml_sentiment['score'],
            'lexicon_score': lexicon_sentiment['score'],
            'confidence': max(ml_sentiment['confidence'], lexicon_sentiment['confidence']),
            'aspects': self._extract_aspects(text),
            'limitations': self._get_analysis_limitations(text)
        }
        
    def _get_ml_sentiment(self, text: str) -> Dict:
        """Get sentiment using FinBERT model"""
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True)
        outputs = self.model(**inputs)
        probabilities = torch.nn.functional.softmax(outputs.logits, dim=1)
        
        # Handle special cases like irrealis moods
        if self._contains_irrealis(text):
            confidence_penalty = 0.2
        else:
            confidence_penalty = 0
            
        return {
            'score': probabilities[0][1].item() - probabilities[0][0].item(),
            'confidence': probabilities.max().item() - confidence_penalty
        }
        
    def _get_lexicon_sentiment(self, text: str) -> Dict:
        """Get sentiment using financial lexicon"""
        words = text.lower().split()
        sentiment_scores = [
            self.financial_lexicon.get(word, 0)
            for word in words
        ]
        
        return {
            'score': sum(sentiment_scores) / len(words) if words else 0,
            'confidence': 0.7 if any(sentiment_scores) else 0.3
        }
        
    def _contains_irrealis(self, text: str) -> bool:
        """Check for hypothetical or conditional statements"""
        irrealis_markers = ['if', 'would', 'could', 'might', 'may']
        return any(marker in text.lower() for marker in irrealis_markers)
        
    def _extract_aspects(self, text: str) -> List[str]:
        """Extract specific financial aspects mentioned in text"""
        financial_aspects = [
            'revenue', 'profit', 'growth', 'market share',
            'earnings', 'debt', 'assets', 'liabilities'
        ]
        return [aspect for aspect in financial_aspects if aspect in text.lower()]
        
    def _get_analysis_limitations(self, text: str) -> List[str]:
        """Document limitations of the analysis"""
        limitations = []
        
        if self._contains_irrealis(text):
            limitations.append("Contains hypothetical statements")
            
        if len(text.split()) < 10:
            limitations.append("Text may be too short for reliable analysis")
            
        if "?" in text:
            limitations.append("Contains questions which may affect sentiment accuracy")
            
        return limitations

class SentimentAnalysisDocumentation:
    """Documentation of sentiment analysis system limitations"""
    
    @staticmethod
    def get_limitations() -> Dict[str, str]:
        return {
            'irrealis_moods': 'System may misinterpret hypothetical scenarios or conditional statements',
            'rhetoric': 'Rhetorical questions and sarcasm may not be correctly identified',
            'dependent_opinions': 'Difficulty in distinguishing between direct and reported opinions',
            'context': 'Limited ability to understand broader market context',
            'temporal_aspects': 'May not fully capture time-dependent sentiment changes',
            'technical_language': 'Specialized financial jargon may affect accuracy',
            'reliability': 'Sentiment scores should be used as indicators, not absolute measures'
        }