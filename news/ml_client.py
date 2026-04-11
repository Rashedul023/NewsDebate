import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class BiasPredictionClient:
    """Client for the deployed ML bias prediction service"""
    
    def __init__(self, base_url=None):
        self.base_url = base_url or "https://bias-prediction-api.onrender.com"
        self.timeout = 30
    
    def health_check(self):
        """Check if ML service is healthy"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def predict(self, title, source):
        """
        Predict bias from article title and source
        
        Returns:
            tuple: (bias_score, bias_category)
        """
        try:
            response = requests.post(
                f"{self.base_url}/predict",
                json={
                    "title": title,
                    "source": source if source else "unknown"
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('bias_score', 0.0), data.get('bias_category', 'unclassified')
            else:
                logger.error(f"ML API error: {response.status_code}")
                return 0.0, 'unclassified'
                
        except requests.exceptions.Timeout:
            logger.error("ML service timeout")
            return 0.0, 'unclassified'
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to ML service")
            return 0.0, 'unclassified'
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return 0.0, 'unclassified'
    
    def predict_batch(self, articles):
        """
        Predict bias for multiple articles
        
        articles: list of (title, source) tuples
        """
        try:
            payload = {
                "articles": [
                    {"title": title, "source": source}
                    for title, source in articles
                ]
            }
            response = requests.post(
                f"{self.base_url}/predict/batch",
                json=payload,
                timeout=self.timeout * len(articles)
            )
            
            if response.status_code == 200:
                data = response.json()
                return [(p['bias_score'], p['bias_category']) for p in data['predictions']]
            else:
                return [(0.0, 'unclassified') for _ in articles]
        except Exception as e:
            logger.error(f"Batch prediction error: {e}")
            return [(0.0, 'unclassified') for _ in articles]

# Create a global instance
ml_client = BiasPredictionClient()