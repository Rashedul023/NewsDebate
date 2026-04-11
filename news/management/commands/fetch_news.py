from django.core.management.base import BaseCommand
from news.service import PoliticalNewsService
from news.models import Article
from news.ml_client import ml_client 
import logging
from datetime import datetime
from django.utils import timezone

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fetch US political news from NewsAPI and predict bias using ML'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of articles to fetch (default: 10)'
        )
        parser.add_argument(
            '--country',
            type=str,
            default='us',
            help='Country code (default: us)'
        )
    
    def handle(self, *args, **options):
        count = options['count']
        country = options['country']
        
        self.stdout.write(self.style.SUCCESS(f'📰 Fetching {count} articles from {country.upper()}...'))
        
        # Check if ML service is healthy
        self.stdout.write("🔍 Checking ML service...")
        if ml_client.health_check():
            self.stdout.write(self.style.SUCCESS("   ✅ ML Service is healthy"))
        else:
            self.stdout.write(self.style.WARNING("   ⚠️ ML Service unreachable - using default bias"))
        
        self.stdout.write("")
        logger.info("="*50)
        logger.info(f"FETCH_NEWS STARTED - {count} articles")
        
        service = PoliticalNewsService()
        
        try:
            # Fetch articles from NewsAPI
            articles = service.fetch_political_news(country=country, page_size=count)
            
            if not articles:
                self.stdout.write(self.style.WARNING("No articles fetched"))
                return
            
            saved_count = 0
            skipped_count = 0
            error_count = 0
            
            for article_data in articles:
                try:
                    # Skip articles without title
                    if not article_data.get('title') or article_data['title'] == '[Removed]':
                        skipped_count += 1
                        continue
                    
                    title = article_data['title']
                    source = article_data.get('source', {}).get('name', 'Unknown')
                    
                    self.stdout.write(f"Predicting: {title[:50]}...")
                    bias_score, bias_category = ml_client.predict(title, source)
                    
                    published_at = article_data.get('publishedAt')
                    if published_at:
                        published_at = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    else:
                        published_at = timezone.now()
                    
                    article_defaults = {
                        'content': article_data.get('description', '')[:10000] if article_data.get('description') else '',
                        'image_url': article_data.get('urlToImage', '')[:500] if article_data.get('urlToImage') else '',
                        'published_at': published_at,
                        'url': article_data.get('url', '')[:500],
                        'bias_label': bias_category,
                        'bias_score': bias_score,
                    }
                    
                    article, created = Article.objects.get_or_create(
                        title=title[:500],
                        source_name=source[:200],
                        defaults=article_defaults
                    )
                    
                    if created:
                        saved_count += 1
                        self.stdout.write(self.style.SUCCESS(f"Saved: {bias_category} ({bias_score:+.2f})"))
                    else:
                        skipped_count += 1
                        self.stdout.write(f"    ⏭️ Skipped (duplicate)")
                        
                except Exception as e:
                    error_count += 1
                    logger.error(f"Error saving article: {e}")
                    self.stdout.write(self.style.ERROR(f"    ❌ Error: {e}"))
            

            self.stdout.write("")
            self.stdout.write(self.style.SUCCESS("=" * 50))
            self.stdout.write(self.style.SUCCESS("SUMMARY"))
            self.stdout.write(self.style.SUCCESS("=" * 50))
            self.stdout.write(f" Saved: {saved_count}")
            self.stdout.write(f" Skipped: {skipped_count}")
            self.stdout.write(f" Errors: {error_count}")
            self.stdout.write(f" Total in DB: {Article.objects.count()}")
            self.stdout.write(self.style.SUCCESS("=" * 50))
            
            logger.info(f"FETCH_NEWS COMPLETED - Saved: {saved_count}, Skipped: {skipped_count}, Errors: {error_count}")
            
        except Exception as e:
            logger.error(f"Command failed: {str(e)}")
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))