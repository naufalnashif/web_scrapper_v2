from sys import platform
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from scrapers.instagram import InstagramScraper
from scrapers.playstore import PlayStoreScraper
from scrapers.tiktok import TikTokScraper
from scrapers.shopee import ShopeeScraper
from scrapers.googlemaps import GoogleMapsScraper
from scrapers.googlenews import GoogleNewsScraper
from scrapers.googlejobs import GoogleJobsScraper
from scrapers.linkedin import LinkedInScraper
from utils.logger import log_activity
import time

def render_sidebar():
    # logo_url = "https://raw.githubusercontent.com/naufalnashif/naufalnashif.github.io/main/assets/img/my-logo.png"


    with st.sidebar.expander("⚙️ Scraper Configuration", expanded=True):
    
        # col1, col2, col3 = st.columns([1, 2, 1])
        # with col2:
        #     st.image(logo_url, use_container_width=True)
        #     # st.image(logo_url, use_column_width=True)

        # Penanganan Hari dalam Bahasa Indonesia
        days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
        now = datetime.now()
        day_name = days[now.weekday()]
        
        st.markdown(f"### 🕒 System Time")
        st.info(f"📅 {day_name}, {now.strftime('%d %B %Y | %H : %M : %S')}")


        # 1. Platform Selection
        platform_choice = st.selectbox("Platform", ["Instagram", "Shopee", "TikTok", "PlayStore", "GoogleMaps", "GoogleNews", "GoogleJobs", "LinkedIn"], index=0)

        # 2. Input Section
        with st.expander("📥 Input Configuration", expanded=True):
        # st.subheader("📥 Input Configuration")
            input_method = st.radio("Metode Input", ["Manual Text", "Upload File (TXT/CSV/XLSX)"], horizontal=True)
            
            targets = []

            # Dinamis berdasarkan platform (menggunakan kode asli Anda)
            # Di dalam render_sidebar()
            if platform_choice == "Shopee":
                instruction = "Masukkan URL Produk/Toko Shopee atau SHOPID:ITEMID"
                placeholder = "https://shopee.co.id/product/1409463595/27927847951"
                default_val = "https://shopee.co.id/product/1409463595/27927847951, https://shopee.co.id/basecomtech"
            elif platform_choice == "TikTok":
                instruction, placeholder, default_val = "Masukkan username", "Contoh: novanov1_", "novanov1_, mxcvs_"
            elif platform_choice == "GoogleMaps":
                instruction, placeholder, default_val = "Masukkan nama tempat", "Contoh: KFC Terdekat", "KFC Terdekat, Mall Terdekat"
            elif platform_choice == "GoogleNews":
                instruction, placeholder, default_val = "Masukkan keyword berita", "Contoh: Ekonomi Indonesia", "Ekonomi Indonesia, Politik Nasional"
            elif platform_choice == "GoogleJobs":
                instruction, placeholder, default_val = "Masukkan keyword pekerjaan", "Contoh: Data Analyst", "Data Analyst, Software Engineer"
            elif platform_choice == "LinkedIn":
                instruction, placeholder, default_val = "Masukkan keyword pekerjaan", "Contoh: Data Analyst", "Data Analyst, Data Engieneer, Data Scientist, BI Developer"
            elif platform_choice == "Instagram":
                st.info("💡 Pilih 'Hybrid' jika di Hugging Face, 'Instaloader' jika di Lokal.")
                ig_method = st.radio("Scraping Method", ["Instaloader (Deep)", "Hybrid (Safe/Fast)"], horizontal=True)
                instruction = "Masukkan Username Instagram (delimiter koma atau baris baru)"
                placeholder = "user1, user2"
                default_val = "naufal.nashif, _self.daily"
            
            # elif platform_choice == "PlayStore":
            #     instruction, placeholder, default_val = "Masukkan App ID", "Contoh: com.shopee.id", "com.shopee.id, com.tokopedia.tkpd"
            elif platform_choice == "PlayStore":
                # Tambahkan logika untuk PlayStore yang baru
                instruction = "Masukkan URL Play Store atau App ID"
                placeholder = "https://play.google.com/store/apps/details?id=com.shopee.id atau com.shopee.id"
                
                # Tambahkan opsi default seperti script lama Anda
                app_defaults = {
                    "Shopee": "com.shopee.id",
                    "Tokopedia": "com.tokopedia.tkpd",
                    "Grab": "com.grabtaxi.passenger",
                    "Manual": ""
                }
                sel_app = st.selectbox("Aplikasi Populer", list(app_defaults.keys()))
                if sel_app != "Manual":
                    default_val = app_defaults[sel_app]

            if input_method == "Manual Text":
                raw_input = st.text_area(instruction, value=default_val, placeholder=placeholder, help="Gunakan koma atau baris baru untuk memisahkan antar target.")
                targets = [t.strip() for t in raw_input.replace("\n", ",").split(",") if t.strip()]
            else:
                uploaded_file = st.file_uploader("Pilih file", type=['csv', 'xlsx', 'txt'])
                if uploaded_file:
                    try:
                        if uploaded_file.name.endswith('.csv'):
                            df = pd.read_csv(uploaded_file)
                            targets = df.iloc[:, 0].dropna().tolist()
                        elif uploaded_file.name.endswith('.xlsx'):
                            df = pd.read_excel(uploaded_file)
                            targets = df.iloc[:, 0].dropna().tolist()
                        elif uploaded_file.name.endswith('.txt'):
                            stringio = uploaded_file.read().decode("utf-8")
                            targets = [t.strip() for t in stringio.replace("\n", ",").split(",") if t.strip()]
                    except Exception as e:
                        st.error(f"Error baca file: {e}")

        # --- EXTRACTION FILTERS (ATAS BAWAH) ---
        with st.expander("⏲️ Extraction Filters", expanded=True):
        # st.subheader("⏲️ Extraction Limits")
        
            # max_posts = st.sidebar.number_input(
            #     "Max Posts per Account", 
            #     min_value=1, 
            #     max_value=200, 
            #     value=10, 
            #     help="Batasi jumlah postingan yang diambil untuk setiap target."
            # )
            # Filter Jumlah Postingan
            use_count_limit = st.checkbox("Limit Post Count", value=False, help="Centang untuk membatasi jumlah postingan yang diambil.")
            max_posts = 9999 # Default jika tidak dilimit
            if use_count_limit:
                max_posts = st.number_input("Max Posts per Account", min_value=1, max_value=500, value=10)
            
            use_date_filter = st.checkbox("Filter by Date", help="Hanya ambil postingan sejak tanggal tertentu.")
            since_date = None
            if use_date_filter:
                since_date = st.date_input("Get posts since:", datetime.now() - timedelta(days=30))

            # 3. Mode Toggle
        mode = st.toggle("Gunakan Flask API", value=False)

        # 4. Action Button & Logic
        if st.button("🚀 Start Scraping", use_container_width=True):
            if not targets:
                st.error("Masukkan target terlebih dahulu!")
            else:
                st.session_state.all_results = [] 
                
                # --- INISIALISASI SCRAPER (Satu kali di luar loop) ---
                if platform_choice == "Instagram":
                    scraper = InstagramScraper()
                elif platform_choice == "TikTok":
                    scraper = TikTokScraper()
                elif platform_choice == "PlayStore":
                    scraper = PlayStoreScraper()
                elif platform_choice == "GoogleMaps":
                    scraper = GoogleMapsScraper()
                elif platform_choice == "GoogleNews":
                    scraper = GoogleNewsScraper()
                elif platform_choice == "GoogleJobs":
                    scraper = GoogleJobsScraper()
                elif platform_choice == "LinkedIn":
                    scraper = LinkedInScraper()
                else:
                    scraper = ShopeeScraper()
                
                progress_text = st.empty()
                progress_bar = st.progress(0)
                
                # --- LOOP TARGET ---
                for idx, t in enumerate(targets):
                    progress_text.text(f"Processing ({idx+1}/{len(targets)}): {t}")
                    log_activity(f"Scraping {t} via {platform_choice}...")
                    
                    try:
                        if platform_choice == "Instagram":
                            # Penambahan logika pemilihan metode khusus Instagram
                            if ig_method == "Hybrid (Safe/Fast)":
                                res = scraper.get_data_hybrid(t, max_posts=max_posts, since_date=since_date)
                            else:
                                res = scraper.get_detailed_data(t, max_posts=max_posts, since_date=since_date)
                        
                        elif platform_choice == "TikTok":
                            # Tetap menggunakan get_data yang sudah stabil
                            res = scraper.get_data(t, max_posts=max_posts, since_date=since_date)
                            
                        elif platform_choice == "PlayStore":
                            # Tetap menggunakan get_data yang sudah stabil
                            res = scraper.get_detailed_data(t, max_posts=max_posts)
                        # Di dalam sidebar.py pada bagian logika elif
                        elif platform_choice == "GoogleMaps":
                            res = scraper.get_data(t, max_posts=max_posts) 
                        elif platform_choice == "GoogleNews":
                            res = scraper.get_data(t, max_posts=max_posts) 
                        elif platform_choice == "GoogleJobs":
                            res = scraper.get_data(t, max_posts=max_posts) 
                        elif platform_choice == "LinkedIn":
                            res = scraper.get_data(t, max_posts=max_posts) 

                        else:
                            # Shopee atau platform lainnya
                            res = scraper.get_data(t, max_posts=max_posts, since_date=since_date)
                        
                        st.session_state.all_results.append(res)
                        
                    except Exception as e:
                        log_activity(f"Error scraping {t}: {str(e)}")
                        st.session_state.all_results.append({"error": str(e), "platform": platform_choice})
                    
                    # Update Progress
                    progress_bar.progress((idx + 1) / len(targets))
                    time.sleep(0.5) 
                
                progress_text.text("✅ Scraping Selesai!")
                st.success(f"Berhasil mengambil {len(st.session_state.all_results)} data.")
                st.rerun()