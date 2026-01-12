import httpx
import json
from datetime import datetime

def test_instagram_extraction(username):
    print(f"--- 🔍 TESTING EXTRACTION FOR: {username} ---")
    
    # Header wajib agar dianggap sebagai request AJAX internal web
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "X-IG-App-ID": "936619743392459", # ID App Publik Instagram Web
        "X-ASBD-ID": "129477",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": f"https://www.instagram.com/{username}/",
    }
    
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    
    try:
        with httpx.Client(headers=headers, follow_redirects=True, timeout=20.0) as client:
            resp = client.get(url)
            print(f"📡 Status Code: {resp.status_code}")
            
            if resp.status_code != 200:
                print(f"❌ Gagal! Status: {resp.status_code}")
                return

            data = resp.json()
            user_data = data.get('data', {}).get('user', {})
            
            if not user_data:
                print("❌ User tidak ditemukan atau akun privat.")
                return

            # 1. EKSTRAKSI PROFIL
            print("\n✅ [DATA PROFIL]")
            profile = {
                "Full Name": user_data.get('full_name'),
                "Followers": user_data.get('edge_followed_by', {}).get('count'),
                "Following": user_data.get('edge_follow', {}).get('count'),
                "Bio": user_data.get('biography'),
                "Is Business": user_data.get('is_business_account'),
            }
            print(json.dumps(profile, indent=4))

            # 2. EKSTRAKSI POSTINGAN (GraphQL Nodes)
            print("\n✅ [DATA POSTINGAN TERBARU]")
            posts_edges = user_data.get('edge_owner_to_timeline_media', {}).get('edges', [])
            
            extracted_posts = []
            for edge in posts_edges[:5]:  # Ambil 5 saja untuk tes
                node = edge.get('node', {})
                
                # Konversi Timestamp ke Readable Date
                timestamp = node.get('taken_at_timestamp')
                date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                
                # Caption (Berada di dalam list edges)
                caption = ""
                cap_edges = node.get('edge_media_to_caption', {}).get('edges', [])
                if cap_edges:
                    caption = cap_edges[0].get('node', {}).get('text', '')

                post_data = {
                    "Date": date_str,
                    "Likes": node.get('edge_media_preview_like', {}).get('count'),
                    "Comments": node.get('edge_media_to_comment', {}).get('count'),
                    "Shortcode": node.get('shortcode'),
                    "URL": f"https://www.instagram.com/p/{node.get('shortcode')}/",
                    "Is Video": node.get('is_video'),
                    "Caption": caption[:50] + "..." if caption else "No Caption"
                }
                extracted_posts.append(post_data)
                print(f"- {date_str} | ❤️ {post_data['Likes']} | 💬 {post_data['Comments']} | URL: {post_data['Shortcode']}")

            if not extracted_posts:
                print("⚠️ Profil ditemukan tapi tidak ada postingan yang bisa ditarik.")

    except Exception as e:
        print(f"💥 Error Sistem: {str(e)}")

if __name__ == "__main__":
    target_user = input("Masukkan username (tanpa @): ").strip()
    test_instagram_extraction(target_user)