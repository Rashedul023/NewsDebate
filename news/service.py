import requests
import logging
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from .models import Article
from django.db import IntegrityError, DataError

logger = logging.getLogger(__name__)

class PoliticalNewsService:
    """Service to fetch US political news from NewsAPI.org"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'NEWS_API_KEY', None)
        if not self.api_key:
            logger.error("NEWS_API_KEY not found in settings")
            raise ValueError("NEWS_API_KEY not found in settings")
        self.base_url = "https://newsapi.org/v2"
        logger.info("PoliticalNewsService initialized")
    
    def fetch_political_news(self, country='us', page_size=10):
        """
        Fetch political news from NewsAPI
        """
        url = f"{self.base_url}/top-headlines"
        params = {
            'country': country,
            'category': 'politics',
            'apiKey': self.api_key,
            'pageSize': page_size
        }
        
        logger.info(f"📡 Fetching {page_size} articles from {country.upper()}...")
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('status') == 'ok':
                articles = data.get('articles', [])
                logger.info(f"Fetched {len(articles)} articles")
                # Log to success file
                logging.getLogger('news.success').info(f"Fetched {len(articles)} articles")
                return articles
            else:
                error_msg = data.get('message', 'Unknown error')
                logger.error(f"API Error: {error_msg}")
                return []
                
        except requests.exceptions.Timeout:
            logger.error("Request timeout")
            return []
        except requests.exceptions.ConnectionError:
            logger.error("Connection error")
            return []
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return []
    
    def save_articles(self, articles_data):
        """
        Save fetched articles to database
        """
        saved_count = 0
        skipped_count = 0
        error_count = 0
        
        logger.info(f"Saving {len(articles_data)} articles...")
        
        for article_data in articles_data:
            try:
                # Skip articles without title
                if not article_data.get('title') or article_data['title'] == '[Removed]':
                    skipped_count += 1
                    continue
                
                # Parse date
                published_at = article_data.get('publishedAt')
                if published_at:
                    published_at = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                else:
                    published_at = timezone.now()
                
                # Get source name
                source_name = article_data.get('source', {}).get('name', 'Unknown')
                
                # Prepare data
                article_defaults = {
                    'content': article_data.get('description', '')[:10000] if article_data.get('description') else '',
                    'image_url': article_data.get('urlToImage', '')[:500] if article_data.get('urlToImage') else '',
                    'published_at': published_at,
                    'url': article_data.get('url', '')[:500],
                }
                
                # Save to database
                article, created = Article.objects.get_or_create(
                    title=article_data['title'][:500],
                    source_name=source_name[:200],
                    defaults=article_defaults
                )
                
                if created:
                    saved_count += 1
                    logger.info(f"Saved: {article.title[:50]}...")
                else:
                    skipped_count += 1
                    logger.info(f"Duplicate: {article_data['title'][:50]}...")
                    
            except Exception as e:
                logger.error(f"Error saving article: {str(e)}")
                error_count += 1
        
        # Summary
        logger.info(f"Summary - Saved: {saved_count}, Skipped: {skipped_count}, Errors: {error_count}")
        
        if saved_count > 0:
            logging.getLogger('news.success').info(f"Successfully saved {saved_count} articles")
        
        return {
            'saved': saved_count,
            'skipped': skipped_count,
            'errors': error_count,
            'total': len(articles_data)
        }
    
    def fetch_and_save(self, country='us', page_size=10):
        """
        Main function - fetch and save
        """
        logger.info(f"Starting fetch_and_save for {page_size} articles")
        
        articles = self.fetch_political_news(country=country, page_size=page_size)
        
        if not articles:
            logger.warning("No articles fetched")
            return {'saved': 0, 'skipped': 0, 'errors': 0, 'total': 0}
        
        result = self.save_articles(articles)
        logger.info(f"Completed: {result}")
        return result