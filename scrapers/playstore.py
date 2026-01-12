from google_play_scraper import app, reviews, Sort
import pandas as pd
import re
from datetime import datetime

class PlayStoreScraper:
    def extract_app_id(self, input_string: str):
        if "id=" in input_string:
            pattern = r'id=([a-zA-Z0-9._]+)'
            match = re.search(pattern, input_string)
            return match.group(1) if match else input_string
        return input_string.strip()

    def get_detailed_data(self, target: str, lang='id', country='id', max_posts=1000):
        try:
            app_id = self.extract_app_id(target)
            scraped_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 1. Metadata Aplikasi Lengkap
            info = app(app_id, lang=lang, country=country)
            
            # 2. Ambil Ulasan
            rvs, _ = reviews(
                app_id,
                lang=lang,
                country=country,
                sort=Sort.NEWEST,
                count=max_posts
            )

            data = {
                "platform": "PlayStore",
                "profile_info": {
                    "username": app_id,
                    "app_id": app_id,
                    "title": info.get('title'),
                    "developer": info.get('developer'),
                    "category": info.get('genre'),
                    "rating": round(info.get('score', 0), 2),
                    "reviews_count": info.get('reviews'),
                    "installs": info.get('installs'),
                    "icon": info.get('icon'),
                    "url": info.get('url'),
                    "scraped_at": scraped_at
                },
                "posts": []
            }

            for r in rvs:
                raw_content = str(r.get('content', ''))
                clean_content = "".join(char for char in raw_content if char.isprintable())
                
                data["posts"].append({
                    "review_id": r.get('reviewId'),
                    "user_name": r.get('userName'),
                    "user_image": r.get('userImage'),
                    "rating": r.get('score'),
                    "content": clean_content,
                    "app_version": r.get('reviewCreatedVersion'),
                    "date": r.get('at').strftime('%Y-%m-%d %H:%M:%S') if r.get('at') else None,
                    "reply_content": r.get('replyContent'),
                    "reply_date": r.get('repliedAt').strftime('%Y-%m-%d %H:%M:%S') if r.get('repliedAt') else None,
                    "thumbs_up": r.get('thumbsUpCount'),
                    "scraped_at": scraped_at,
                    # --- TAMBAHKAN INI AGAR DASHBOARD TIDAK ERROR ---
                    "app_name": info.get('title') 
                })

            return data
        except Exception as e:
            return {"error": str(e), "platform": "PlayStore", "target": target}