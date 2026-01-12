import yt_dlp
import httpx
from bs4 import BeautifulSoup
import json
from datetime import datetime

class TikTokScraper:
    def __init__(self):
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'skip_download': True,
        }
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }

    def get_data(self, username, max_posts=10, since_date=None):
        clean_username = username.replace('@', '').strip()
        url = f"https://www.tiktok.com/@{clean_username}"
        scraped_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # --- BAGIAN 1: AMBIL PROFIL (METODE HTTPX) ---
        profile_data = {}
        try:
            with httpx.Client(headers=self.headers, follow_redirects=True, timeout=10.0) as client:
                resp = client.get(url)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    script = soup.find('script', id='__UNIVERSAL_DATA_FOR_REHYDRATION__')
                    if script:
                        raw_json = json.loads(script.string)
                        user_info = raw_json['__DEFAULT_SCOPE__']['webapp.user-detail']['userInfo']
                        u = user_info['user']
                        s = user_info['stats']
                        profile_data = {
                            "userid": u.get('id'),
                            "username": u.get('uniqueId'),
                            "full_name": u.get('nickname'),
                            "bio": u.get('signature'),
                            "followers": s.get('followerCount', 0),
                            "following": s.get('followingCount', 0),
                            "total_likes": s.get('heartCount', 0),
                            "is_verified": u.get('verified', False),
                        }
        except Exception: pass # Fallback ke yt-dlp jika httpx gagal

        # --- BAGIAN 2: AMBIL POSTINGAN (METODE YT-DLP) ---
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Gunakan data httpx, jika kosong gunakan data yt-dlp
                data = {
                    "platform": "TikTok",
                    "profile_info": {
                        "userid": profile_data.get('userid', info.get('id')),
                        "username": clean_username,
                        "full_name": profile_data.get('full_name', info.get('uploader', clean_username)),
                        "bio": profile_data.get('bio', "No Bio"),
                        "profile_pic": info.get('thumbnails', [{}])[0].get('url', '') if info.get('thumbnails') else '',
                        "followers": profile_data.get('followers', info.get('follower_count', 0)),
                        "following": profile_data.get('following', 0),
                        "total_likes": profile_data.get('total_likes', info.get('like_count', 0)),
                        "is_verified": profile_data.get('is_verified', False),
                        "engagement_rate": 0,
                        "scraped_at": scraped_at
                    },
                    "posts": []
                }

                entries = info.get('entries', [])
                valid_posts = []
                total_likes_for_er = 0
                
                for entry in entries:
                    if len(valid_posts) >= max_posts: break
                    post_ts = entry.get('timestamp')
                    if post_ts:
                        post_dt = datetime.fromtimestamp(post_ts)
                        if since_date and post_dt.date() < since_date: continue
                            
                        likes = entry.get('like_count', 0) or 0
                        total_likes_for_er += likes
                        valid_posts.append({
                            "username": clean_username,
                            "date": post_dt.strftime('%Y-%m-%d %H:%M:%S'),
                            "caption": entry.get('title', 'No Caption'),
                            "likes": likes,
                            "comments_count": entry.get('comment_count', 0),
                            "views": entry.get('view_count', 0),
                            "shares": entry.get('repost_count', 0),
                            "url": entry.get('webpage_url', ''),
                        })

                # data["posts"] = valid_posts
                # if data['profile_info']['followers'] > 0 and valid_posts:
                #     avg_likes = total_likes_for_er / len(valid_posts)
                #     er = (avg_likes / data['profile_info']['followers']) * 100
                #     data['profile_info']['engagement_rate'] = round(er, 2)
                # return data

                data["posts"] = valid_posts
                
                # Hitung ER berdasarkan data followers dari httpx dan likes dari yt-dlp
                if data['profile_info']['followers'] > 0 and valid_posts:
                    avg_likes = total_likes_for_er / len(valid_posts)
                    er = (avg_likes / data['profile_info']['followers']) * 100
                    data['profile_info']['engagement_rate'] = round(er, 2)
                
                return data

        except Exception as e:
            return {"error": str(e), "platform": "TikTok"}