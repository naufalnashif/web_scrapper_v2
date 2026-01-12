import instaloader
import httpx  
import json
from datetime import datetime

class InstagramScraper:
    def __init__(self):
        # Header dasar (akan diperbarui secara dinamis di dalam fungsi)
        self.base_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "X-IG-App-ID": "936619743392459",
            "X-ASBD-ID": "129477",
            "X-Requested-With": "XMLHttpRequest",
        }
        # Inisialisasi Instaloader untuk Metode Deep
        self.L = instaloader.Instaloader(user_agent=self.base_headers["User-Agent"])

    def get_data_hybrid(self, username, max_posts=10, since_date=None):
        """Metode Hybrid: Menggunakan logika yang terbukti berhasil di test.py"""
        clean_username = username.replace('@', '').strip()
        scraped_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Samakan Referer dengan test.py
        headers = self.base_headers.copy()
        headers["Referer"] = f"https://www.instagram.com/{clean_username}/"
        
        url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={clean_username}"
        
        try:
            with httpx.Client(headers=headers, follow_redirects=True, timeout=20.0) as client:
                resp = client.get(url)
                
                if resp.status_code != 200:
                    return {"error": f"IG Blocked (Status {resp.status_code})", "platform": "Instagram"}

                data_json = resp.json().get('data', {}).get('user', {})
                if not data_json:
                    return {"error": "User data empty or Private Account", "platform": "Instagram"}

                # 1. Profile Umum (Struktur Identik dengan get_detailed_data)
                result = {
                    "metadata": {
                        "scraped_at": scraped_at,
                        "total_posts_on_profile": data_json.get('edge_owner_to_timeline_media', {}).get('count', 0),
                        "platform": "Instagram"
                    },
                    "profile_info": {
                        "userid": data_json.get('id'),
                        "username": data_json.get('username'),
                        "full_name": data_json.get('full_name'),
                        "bio": data_json.get('biography'),
                        "profile_pic": data_json.get('profile_pic_url'),
                        "is_business": data_json.get('is_business_account'),
                        "business_category": data_json.get('business_category_name'),
                        "external_url": data_json.get('external_url'),
                        "followers": data_json.get('edge_followed_by', {}).get('count', 0),
                        "following": data_json.get('edge_follow', {}).get('count', 0),
                        "is_verified": data_json.get('is_verified'),
                        "scraped_at": scraped_at
                    },
                    "posts": []
                }

                # 2. Postingan (Struktur Identik)
                edges = data_json.get('edge_owner_to_timeline_media', {}).get('edges', [])
                total_likes = 0
                total_comments = 0

                for edge in edges:
                    if len(result["posts"]) >= max_posts:
                        break
                    
                    node = edge.get('node', {})
                    post_dt = datetime.fromtimestamp(node.get('taken_at_timestamp', 0))
                    
                    if since_date and post_dt.date() < since_date:
                        break

                    lks = node.get('edge_media_preview_like', {}).get('count', 0)
                    cmt = node.get('edge_media_to_comment', {}).get('count', 0)
                    total_likes += lks
                    total_comments += cmt

                    # Caption Extraction
                    cap = ""
                    cap_edges = node.get('edge_media_to_caption', {}).get('edges', [])
                    if cap_edges:
                        cap = cap_edges[0].get('node', {}).get('text', '')

                    result["posts"].append({
                        "username": clean_username,
                        "date": post_dt.strftime('%Y-%m-%d %H:%M:%S'),
                        "caption": cap,
                        "likes": lks,
                        "comments_count": cmt,
                        "url": f"https://www.instagram.com/p/{node.get('shortcode')}/",
                        "hashtags": list(set(part[1:] for part in cap.split() if part.startswith('#'))),
                        "mentions": list(set(part[1:] for part in cap.split() if part.startswith('@'))),
                        "is_video": node.get('is_video', False),
                        "typename": node.get('__typename'),
                        "video_view_count": node.get('video_view_count', 0) if node.get('is_video') else 0,
                        "location": node.get('location', {}).get('name') if node.get('location') else None,
                        "tagged_users": [t.get('node', {}).get('user', {}).get('username') for t in node.get('edge_media_to_tagged_user', {}).get('edges', [])]
                    })

                # 3. Analytics
                if result["posts"] and result["profile_info"]["followers"] > 0:
                    avg_eng = (total_likes + total_comments) / len(result["posts"])
                    er = (avg_eng / result["profile_info"]["followers"]) * 100
                    result["profile_info"]["engagement_rate"] = round(er, 2)
                    result["profile_info"]["avg_likes"] = round(total_likes / len(result["posts"]), 1)
                else:
                    result["profile_info"]["engagement_rate"] = 0
                    result["profile_info"]["avg_likes"] = 0

                return result

        except Exception as e:
            return {"error": f"Hybrid Error: {str(e)}", "platform": "Instagram", "target": username}
        
    def get_detailed_data(self, username, max_posts=10, since_date=None):
        try:
            profile = instaloader.Profile.from_username(self.L.context, username)
            scraped_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 1. Profile Umum
            data = {
                "metadata": {
                    "scraped_at": scraped_at,
                    "total_posts_on_profile": profile.mediacount,
                    "platform": "Instagram" # Memastikan metadata platform ada
                },
                "profile_info": {
                    "userid": profile.userid,
                    "username": profile.username,
                    "full_name": profile.full_name,
                    "bio": profile.biography,
                    "profile_pic": profile.profile_pic_url,
                    "is_business": profile.is_business_account,
                    "business_category": profile.business_category_name,
                    "external_url": profile.external_url,
                    "followers": profile.followers,
                    "following": profile.followees,
                    "is_verified": profile.is_verified,
                    "scraped_at": scraped_at
                },
                "posts": []
            }

            total_likes = 0
            total_comments = 0

            # 2. Data Postingan dengan Filter
            for post in profile.get_posts():
                # Filter 1: Batas Jumlah Postingan
                if len(data["posts"]) >= max_posts:
                    break
                
                # Filter 2: Batas Tanggal (Since Date)
                if since_date and post.date_utc.date() < since_date:
                    # Instaloader mengambil post dari yang terbaru, 
                    # jadi jika sudah melewati since_date, kita bisa berhenti (break)
                    break

                total_likes += post.likes
                total_comments += post.comments
                
                post_item = {
                    "username": username,
                    "date": post.date_utc.strftime('%Y-%m-%d %H:%M:%S'),
                    "caption": post.caption,
                    "likes": post.likes,
                    "comments_count": post.comments,
                    "url": f"https://www.instagram.com/p/{post.shortcode}/",
                    "hashtags": post.caption_hashtags,
                    "mentions": post.caption_mentions,
                    "is_video": post.is_video,
                    "typename": post.typename,
                    "video_view_count": post.video_view_count if post.is_video else 0,
                    "location": post.location.name if post.location else None,
                    "tagged_users": post.tagged_users
                }
                data["posts"].append(post_item)

            # 3. Analytics (Engagement Rate) berdasarkan data yang difilter
            post_count = len(data["posts"])
            if post_count > 0 and profile.followers > 0:
                avg_eng = (total_likes + total_comments) / post_count
                er = (avg_eng / profile.followers) * 100
                data["profile_info"]["engagement_rate"] = round(er, 2)
                data["profile_info"]["avg_likes"] = round(total_likes / post_count, 1)
            else:
                data["profile_info"]["engagement_rate"] = 0
                data["profile_info"]["avg_likes"] = 0

            return data
        except Exception as e:
            return {"error": str(e), "metadata": {"status": "Error", "platform": "Instagram"}}