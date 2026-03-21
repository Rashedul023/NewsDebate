from django.core.management.base import BaseCommand
from interactions.models import Ad

class Command(BaseCommand):
    help = 'Load sample advertisements for the project'

    def handle(self, *args, **options):
        self.stdout.write('Loading sample advertisements...')
        
        sample_ads = [
            {
                'title': 'My GitHub Profile',
                'description': 'Check out my open-source projects and contributions',
                'image_url': 'https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png',
                'link_url': 'https://github.com/Rashedul023',
                'priority': 10,
            },
            {
                'title': 'LeetCode Profile',
                'description': 'Solving coding challenges daily - 450+ problems solved',
                'image_url': 'https://leetcode.com/static/images/LeetCode_logo.png',
                'link_url': 'https://leetcode.com/u/Rashedul_023/',
                'priority': 9,
            },
            {
                'title': 'Codeforces',
                'description': 'Competitive programming journey',
                'image_url': 'https://codeforces.org/s/0/images/codeforces-logo.png',
                'link_url': 'https://codeforces.com/profile/Rashedul023',
                'priority': 8,
            },
          
            {
                'title': 'LinkedIn Profile',
                'description': 'Connect with me professionally',
                'image_url': 'https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Bug.svg.original.svg',
                'link_url': 'https://www.linkedin.com/in/md-rashedul-islam-8bb09733a',
                'priority': 7,
            },
      
        ]
        
        created_count = 0
        for ad_data in sample_ads:
            ad, created = Ad.objects.get_or_create(
                title=ad_data['title'],
                defaults=ad_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created: {ad.title}')
            else:
                self.stdout.write(f'Already exists: {ad.title}')
        
        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully loaded {created_count} new ads!'))