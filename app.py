import streamlit as st
import pandas as pd
from ui.components import render_header, render_terminal_logs, render_documentation
from ui.sidebar import render_sidebar
# IMPORT DASHBOARD BARU
from ui.dashboards.instagram_dash import render_instagram_dashboard
from ui.dashboards.tiktok_dash import render_tiktok_dashboard
from ui.dashboards.shopee_dash import render_shopee_dashboard


st.set_page_config(page_title="Paragon Scraper Specialist", layout="wide")

render_header()
render_sidebar() # Memanggil sidebar yang sudah diperbaiki

if 'all_results' not in st.session_state: st.session_state.all_results = []
if 'logs' not in st.session_state: st.session_state.logs = []

# --- NAVIGATION TABS ---
tab_doc, tab_dash, tab_logs = st.tabs(["📖 Documentation", "📊 Dashboard", "⚙️ Logs"])

with tab_doc:
    render_documentation()

with tab_dash:
    if not st.session_state.all_results:
        st.info("Silahkan konfigurasi target...")
    else:
        # 1. Filter hanya hasil yang memiliki 'profile_info' dan tidak error
        valid_results = [r for r in st.session_state.all_results if 'error' not in r and 'profile_info' in r]
        
        if not valid_results:
            st.error("Gagal mendapatkan data valid. Silahkan cek tab 'Logs' (Kemungkinan terkena Rate Limit).")
        else:
            current_platform = valid_results[0].get('platform', 'Instagram')
            
            # Buat df_profiles secara aman
            df_profiles = pd.DataFrame([r['profile_info'] for r in valid_results])
            
            # 2. Buat df_posts secara aman
            all_posts = []
            for r in valid_results:
                if 'posts' in r and isinstance(r['posts'], list):
                    for p in r['posts']:
                        p_copy = p.copy()
                        p_copy['username'] = r.get('profile_info', {}).get('username', 'Unknown')
                        all_posts.append(p_copy)
            
            df_posts = pd.DataFrame(all_posts)

            # Proteksi kolom minimal agar Plotly tidak crash
            if df_profiles.empty:
                df_profiles = pd.DataFrame(columns=['username', 'followers', 'following'])
            
            if df_posts.empty:
                df_posts = pd.DataFrame(columns=['username', 'date'])

            # Proteksi kolom date
            if 'date' in df_posts.columns and not df_posts.empty:
                df_posts['date'] = pd.to_datetime(df_posts['date'], errors='coerce')


            # 3. Routing Dashboard
            if current_platform == "Instagram":
                render_instagram_dashboard(df_profiles, df_posts)
            # elif current_platform == "TikTok":
            #     render_tiktok_dashboard(df_profiles, df_posts)
            # Di dalam app.py (Bagian Dashboard TikTok)
            elif current_platform == "TikTok":
                if 'views' not in df_posts.columns:
                    df_posts['views'] = 0
                render_tiktok_dashboard(df_profiles, df_posts)
            elif current_platform == "Shopee":
                render_shopee_dashboard(df_profiles, df_posts)

with tab_logs:
    render_terminal_logs(st.session_state.logs)