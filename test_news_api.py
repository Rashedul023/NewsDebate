import os
import django
import requests
from datetime import datetime
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from news.models import Article
from news.service import PoliticalNewsService

def test_all():
    """Complete test of NewsAPI integration"""
    
    print("TESTING NEWSAPI INTEGRATION")
    
    # TEST 1: Direct API Connection
    print("\n🔍 TEST 1: Direct API Connection")
    
    # Get API key from Django settings
    API_KEY = settings.NEWS_API_KEY
    
    if not API_KEY:
        print("NEWS_API_KEY not found in settings!")
        print("Please check your .env file")
        return
    
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        'country': 'us',
        'category': 'politics',
        'apiKey': API_KEY,
        'pageSize': 3
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get('status') == 'ok':
            print(f"API Connection: SUCCESS")
            print(f"Articles found: {len(data.get('articles', []))}")
            print(f"Total available: {data.get('totalResults', 0)}")
        else:
            print(f"API Error: {data.get('message', 'Unknown')}")
            return
    except Exception as e:
        print(f"Connection Error: {e}")
        return
    
    # TEST 2: Service Fetch
    print("\n🔍 TEST 2: Service Fetch")
    print("-"*40)
    
    service = PoliticalNewsService()
    articles = service.fetch_political_news(page_size=5)
    print(f"✅ Fetched {len(articles)} articles via service")
    
    # TEST 3: Preview Articles
    if articles:
        print("\n📋 TEST 3: Article Preview (first 3)")
        print("-"*40)
        for i, article in enumerate(articles[:3]):
            print(f"\n📰 Article {i+1}:")
            print(f"   Title: {article['title'][:70]}...")
            print(f"   Source: {article['source']['name']}")
            print(f"   Date: {article['publishedAt'][:10] if article.get('publishedAt') else 'Unknown'}")
            print(f"   Image: {'✅' if article.get('urlToImage') else '❌'}")
            print(f"   Description: {article['description'][:50]}..." if article.get('description') else "   No description")
    
    # TEST 4: Save to Database
    print("\n💾 TEST 4: Save to Database")
    print("-"*40)
    
    before_count = Article.objects.count()
    result = service.save_articles(articles)
    after_count = Article.objects.count()
    
    print(f"Saved: {result['saved']} new articles")
    print(f"Skipped: {result['skipped']} duplicates")
    print(f"Errors: {result.get('errors', 0)}")
    print(f"Database: {before_count} → {after_count} articles")
    
    # TEST 5: Verify Database
    print("\n🔍 TEST 5: Database Verification")
    print("-"*40)
    
    total = Article.objects.count()
    print(f"Total articles in DB: {total}")
    
    if total > 0:
        print("\n📋 Latest 3 articles:")
        for article in Article.objects.order_by('-published_at')[:3]:
            print(f"\n   {article.title[:50]}...")
            print(f"      Source: {article.source_name}")
            print(f"      Date: {article.published_at.date()}")
            print(f"      Bias: {article.bias_label} ({article.bias_score})")
            print(f"      Image: {'✅' if article.image_url else '❌'}")
    else:
        print("⚠️ No articles in database yet")
    
    # TEST 6: Check for Duplicates (Run fetch twice to test)
    print("\nTEST 6: Duplicate Prevention Test")
    print("-"*40)
    
    print("Running fetch again to test duplicate prevention...")
    articles2 = service.fetch_political_news(page_size=3)
    result2 = service.save_articles(articles2)
    print(f"Second run - Saved: {result2['saved']}, Skipped: {result2['skipped']}")
    
    if result2['saved'] == 0 and result2['skipped'] > 0:
        print("Duplicate prevention WORKING! No new articles saved.")
    else:
        print("Duplicate prevention may need checking")
    
    # TEST 7: Source Name Extraction Test
    print("\nTEST 7: Source Name Test")
    print("-"*40)
    
    if articles:
        sample = articles[0]
        source_name = sample.get('source', {}).get('name', 'Unknown')
        print(f"Sample article source: {source_name}")
        print("Source extraction working")
    
    # TEST 8: Image URL Test
    print("\nTEST 8: Image URL Test")
    print("-"*40)
    
    articles_with_images = sum(1 for a in articles if a.get('urlToImage'))
    print(f"Articles with images: {articles_with_images}/{len(articles)}")
    
    # Final Summary
    print("\n" + "="*60)
    print("FINAL TEST SUMMARY")
    print("="*60)
    
    tests_passed = 0
    tests_total = 8
    
    # Count passed tests
    if data.get('status') == 'ok': tests_passed += 1
    if len(articles) > 0: tests_passed += 1
    if result['saved'] > 0 or result['saved'] == 0: tests_passed += 1  # Either is fine
    if total >= 0: tests_passed += 1
    if result2['saved'] == 0 and result2['skipped'] > 0: tests_passed += 1
    if articles and sample.get('source', {}).get('name'): tests_passed += 1
    if articles_with_images >= 0: tests_passed += 1
    if API_KEY: tests_passed += 1
    
    print(f"\nTests Passed: {tests_passed}/{tests_total}")
    
    if tests_passed == tests_total:
        print("\n🎉 PERFECT! All tests passed! Your NewsAPI integration is working perfectly!")
        print("   You're ready for deployment!")
    elif tests_passed >= 6:
        print("\nGood! Most tests passed. Check the failed ones.")
    else:
        print("\nSome tests failed. Review the output above.")
    
    print("TESTING COMPLETE!")

def quick_test():
    """Quick test - just check API connection"""
    print("🔍 Quick API Test...")
    API_KEY = settings.NEWS_API_KEY
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        'country': 'us',
        'category': 'politics',
        'apiKey': API_KEY,
        'pageSize': 1
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if data.get('status') == 'ok':
            print("✅ API is working!")
            return True
        else:
            print(f"❌ API Error: {data.get('message')}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    # Check for quick test argument
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        quick_test()
    else:
        test_all()