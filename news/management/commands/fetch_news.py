from django.core.management.base import BaseCommand
from news.service import PoliticalNewsService
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fetch US political news from NewsAPI'
    
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
        
        self.stdout.write(self.style.SUCCESS(f'Fetching {count} articles from {country.upper()}...'))
        logger.info("="*50)
        logger.info(f"FETCH_NEWS STARTED - {count} articles")
        
        service = PoliticalNewsService()
        
        try:
            result = service.fetch_and_save(country=country, page_size=count)
            
            self.stdout.write(self.style.SUCCESS(
                f"\nDone! Saved: {result['saved']}, Skipped: {result['skipped']}, Errors: {result['errors']}"
            ))
            
            logger.info(f"FETCH_NEWS COMPLETED - {result}")
            
        except Exception as e:
            logger.error(f" Command failed: {str(e)}")
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))