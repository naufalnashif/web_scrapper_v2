from gnews import GNews
from datetime import datetime
import urllib.parse

class GoogleJobsScraper:
    def __init__(self):
        # Menggunakan setting yang sama dengan GNews Anda yang stabil
        self.gn = GNews(language='id', country='ID', period='7d')
        self.gn.full_article = True 

    def get_data(self, keyword, max_posts=10):
        scraped_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Mengoptimasi keyword agar yang muncul adalah lowongan kerja
        # Misal: "Paragon" menjadi "Paragon lowongan kerja"
        job_keyword = f"{keyword.strip()} lowongan kerja"
        encoded_keyword = urllib.parse.quote(job_keyword)
        
        self.gn.max_results = max_posts
        
        try:
            results = self.gn.get_news(encoded_keyword)
            
            data = {
                "platform": "GoogleJobs",
                "profile_info": {
                    "username": keyword, 
                    "category": "Talent Intelligence", 
                    "followers": 0
                },
                "posts": []
            }

            for article in results:
                pub_date = str(article.get('published date', scraped_at))
                
                # Standarisasi kolom agar sesuai dengan Dashboard App Anda
                item = {
                    "name": article.get('title', 'N/A'), # Judul Posisi
                    "publisher": article.get('publisher', {}).get('title', 'N/A'), # Sumber/Portal
                    "date": pub_date,
                    "published_date": pub_date,
                    "caption": article.get('description', 'N/A'),
                    "url": article.get('url', 'N/A'),
                    "description": article.get('description', 'N/A'),
                    "content": article.get('content', 'N/A'),
                    "username": keyword, # Nama perusahaan yang dicari
                    "category": "Job Listing",
                    "scraped_at": scraped_at
                }
                data["posts"].append(item)
            return data
            
        except Exception as e:
            print(f"DEBUG GJOBS ERROR: {str(e)}")
            return {
                "platform": "GoogleJobs",
                "error": str(e),
                "profile_info": {"username": keyword, "followers": 0},
                "posts": []
            }