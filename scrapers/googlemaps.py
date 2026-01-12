import httpx
from datetime import datetime
import re

class GoogleMapsScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://www.google.com/"
        }

    def get_data(self, keyword, max_posts=15):
        scraped_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        search_url = f"https://www.google.com/search?q={keyword.replace(' ', '+')}&tbm=lcl"
        
        result_template = {
            "platform": "GoogleMaps",
            "metadata": {"scraped_at": scraped_at, "status": "Success", "keyword": keyword},
            "profile_info": {
                "username": keyword,
                "category": "Map Search",
                "scraped_at": scraped_at,
                "followers": 0
            },
            "posts": []
        }

        try:
            with httpx.Client(headers=self.headers, timeout=20.0, follow_redirects=True) as client:
                response = client.get(search_url)
                if response.status_code != 200:
                    return {"error": f"Google Status {response.status_code}", "platform": "GoogleMaps", "profile_info": {"username": keyword}, "posts": []}

                html = response.text
                
                # Gunakan regex persis seperti di test.py Anda
                business_names = re.findall(r'div class=".*?"><span>(.*?)</span></div>', html)
                ratings = re.findall(r'<span>(\d[,\.]\d)</span>.*?<span>\(', html)

                # Filter Kata Sampah agar tidak muncul "Rute" sebagai Nama Toko
                blacklist = ["Rute", "Situs", "Telepon", "Panggil", "Simpan", "Bagikan", "Website"]

                count = 0
                for i in range(len(business_names)):
                    if count >= max_posts: break
                    
                    name = re.sub(r'<.*?>', '', business_names[i]).strip()
                    
                    # VALIDASI: Hanya ambil jika bukan kata sampah dan bukan string kosong
                    if name and name not in blacklist and len(name) > 1:
                        rating = ratings[count] if count < len(ratings) else "0.0"
                        
                        item = {
                            "name": name,
                            "rating": float(rating.replace(',', '.')),
                            "reviews_count": "Cek Google",
                            "category": "Local Business",
                            "address": "Lokasi Tertera di Peta",
                            "url": f"https://www.google.com/search?q={name.replace(' ', '+')}",
                            "scraped_at": scraped_at,
                            "date": scraped_at, # Wajib untuk app.py
                            "caption": f"Bisnis: {name} (Rating: {rating})",
                            "likes": 0
                        }
                        result_template["posts"].append(item)
                        count += 1

                return result_template

        except Exception as e:
            return {"error": str(e), "platform": "GoogleMaps", "profile_info": {"username": keyword}, "posts": []}