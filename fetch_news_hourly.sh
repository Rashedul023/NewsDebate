
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================"
echo "   NewsDebate News Fetcher"
echo "   Fetches 50 articles every hour"
echo "   Press Ctrl+C to stop"
echo "========================================"
echo

while true; do
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} Fetching 50 articles..."
    
    python manage.py fetch_news --count 50
    
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} Done. Waiting 1 hour..."
    echo
    
    sleep 3600  # 1 hour = 3600 seconds
done