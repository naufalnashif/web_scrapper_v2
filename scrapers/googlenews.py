from gnews import GNews
from datetime import datetime
import urllib.parse

class GoogleNewsScraper:
    def __init__(self):
        self.gn = GNews(language='id', country='ID')
        self.gn.full_article = True 

    def get_data(self, keyword, max_posts=10):
        scraped_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        encoded_keyword = urllib.parse.quote(keyword.strip())
        self.gn.max_results = max_posts
        
        try:
            results = self.gn.get_news(encoded_keyword)
            data = {
                "platform": "GoogleNews",
                "profile_info": {"username": keyword, "category": "News", "followers": 0},
                "posts": []
            }

            for article in results:
                # Kita masukkan kedua nama kolom (date dan published_date) agar aman
                pub_date = str(article.get('published date', scraped_at))
                
                item = {
                    "name": article.get('title', 'N/A'),
                    "publisher": article.get('publisher', {}).get('title', 'N/A'),
                    "date": pub_date,           # Digunakan app.py & Dashboard
                    "published_date": pub_date, # Mencegah KeyError jika dashboard memanggil ini
                    "caption": article.get('title', 'N/A'),
                    "url": article.get('url', 'N/A'),
                    "description": article.get('description', 'N/A'),
                    "username": keyword
                }
                data["posts"].append(item)
            return data
        except Exception as e:
            return {"error": str(e), "platform": "GoogleNews", "posts": []}