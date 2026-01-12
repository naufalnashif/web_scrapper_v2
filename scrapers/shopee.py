import httpx
import re
from datetime import datetime

class ShopeeScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://shopee.co.id/",
        }

    def extract_ids(self, input_string):
        # 1. Cek jika input adalah URL Produk (paling spesifik)
        product_match = re.search(r"product/(\d+)/(\d+)", input_string)
        if product_match:
            return product_match.group(1) # Mengambil Shop ID
        
        # 2. Cek jika input adalah URL Toko dengan ID angka
        shop_id_match = re.search(r"shop/(\d+)", input_string)
        if shop_id_match:
            return shop_id_match.group(1)
            
        # 3. Jika input adalah Username (basecomtech, cinta66898)
        # Ambil bagian terakhir dari URL jika itu bukan angka
        clean_url = input_string.split('?')[0].rstrip('/')
        username = clean_url.split('/')[-1]
        
        try:
            # Request ke Shopee untuk mendapatkan ID dari username
            search_api = f"https://shopee.co.id/api/v4/shop/get_shop_detail?username={username}"
            with httpx.Client(headers=self.headers) as client:
                res = client.get(search_api).json()
                return str(res.get('data', {}).get('shopid'))
        except:
            return None

    def get_data(self, input_target, max_posts=10, since_date=None):
        scraped_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        shop_id = self.extract_ids(input_target)
        
        # Fallback data jika error agar app.py tidak crash
        empty_res = {
            "platform": "Shopee",
            "metadata": {"scraped_at": scraped_at, "status": "Error"},
            "profile_info": {"username": input_target, "followers": 0, "scraped_at": scraped_at},
            "posts": []
        }

        if not shop_id:
            return empty_res

        try:
            with httpx.Client(headers=self.headers, timeout=20.0) as client:
                # 1. Ambil Profil Toko (Setara Profile Info di Sosmed)
                shop_api = f"https://shopee.co.id/api/v4/shop/get_shop_detail?shopid={shop_id}"
                shop_res = client.get(shop_api).json()
                s_data = shop_res.get('data', {})

                data = {
                    "platform": "Shopee",
                    "metadata": {"scraped_at": scraped_at, "status": "Success"},
                    "profile_info": {
                        "userid": s_data.get('shopid'),
                        "username": s_data.get('account', {}).get('username', shop_id),
                        "full_name": s_data.get('name', 'Shopee Seller'),
                        "bio": s_data.get('description', 'No Bio'),
                        "profile_pic": f"https://down-id.img.susercontent.com/file/{s_data.get('portrait')}" if s_data.get('portrait') else "",
                        "followers": s_data.get('follower_count', 0),
                        "following": 0,
                        "rating": round(s_data.get('rating_star', 0), 2),
                        "is_verified": s_data.get('is_shopee_verified', False),
                        "engagement_rate": 0, # Akan dihitung dari produk
                        "scraped_at": scraped_at
                    },
                    "posts": [] # Diisi dengan Produk (sebagai pengganti Posts)
                }

                # 2. Ambil Daftar Produk menggunakan Search API (Lebih Stabil)
                # Kita menggunakan endpoint 'search_items' dengan parameter 'order_by=sales' untuk produk terlaris
                item_api = f"https://shopee.co.id/api/v4/guide/get_search_items?limit={max_posts}&offset=0&order_by=sales&shopid={shop_id}"
                item_res = client.get(item_api).json()

                # Struktur response search_items sedikit berbeda
                items = item_res.get('data', {}).get('items', [])

                # Jika search_items kosong, kita coba fallback ke API rekomendasi yang lama
                if not items:
                    rec_api = f"https://shopee.co.id/api/v4/recommend/recommend?bundle=shop_page_product_tab_main&limit={max_posts}&shopid={shop_id}"
                    rec_res = client.get(rec_api).json()
                    items = rec_res.get('data', {}).get('sections', [{}])[0].get('data', {}).get('item', [])

                total_sold = 0
                for item in items:
                    # Beberapa API Shopee membungkus data produk di dalam key 'item_basic'
                    basic_info = item.get('item_basic', item) 
                    
                    sold = basic_info.get('historical_sold', 0)
                    total_sold += sold
                    
                    data["posts"].append({
                        "username": data["profile_info"]["username"],
                        "date": scraped_at,
                        "caption": basic_info.get('name'),
                        "likes": basic_info.get('liked_count', 0),
                        "price": basic_info.get('price') / 100000 if basic_info.get('price') else 0,
                        "sold": sold,
                        "stock": basic_info.get('stock', 0),
                        "url": f"https://shopee.co.id/product/{shop_id}/{basic_info.get('itemid')}",
                        "is_video": False
                    })

                # Hitung ER Sederhana (Likes per Product / Followers)
                if data["profile_info"]["followers"] > 0 and data["posts"]:
                    avg_likes = sum(p['likes'] for p in data['posts']) / len(data['posts'])
                    data["profile_info"]["engagement_rate"] = round((avg_likes / data["profile_info"]["followers"]) * 100, 2)

                return data

        except Exception as e:
            empty_res["error"] = str(e)
            return empty_res