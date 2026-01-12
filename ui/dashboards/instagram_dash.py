import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.exporter import get_download_link

def render_instagram_dashboard(df_profiles, df_posts):
    st.subheader("📸 Instagram Performance Analytics")
    # PROTEKSI AWAL: Jika dataframe kosong atau kolom 'username' hilang
    if df_profiles.empty or 'username' not in df_profiles.columns:
        st.warning("Data profil tidak ditemukan untuk divisualisasikan. Pastikan scraping berhasil di tab Logs.")
        return

    res_tab_ov, res_tab_det, res_tab_dict = st.tabs(["🏠 Overview Visuals", "📋 Result Details", "📝 Data Dictionary"])
    with res_tab_ov:
        with st.expander("📊 Key Metrics", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 👥 Follower vs Following")
                fig = px.bar(df_profiles, x='username', y=['followers', 'following'],
                            barmode='group', template="plotly_dark",
                            color_discrete_sequence=["#338CF9", "#35FAAE"])

                fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=300)
                st.plotly_chart(fig, use_container_width=True)
                
            # Kolom 2: Total Postingan (Bar Chart Compare)
            with col2:
                st.markdown("#### 📊 Total Postingan per Akun")
                
                # Menghitung jumlah postingan unik per username
                # Pastikan df_posts tidak kosong untuk menghindari error
                if not df_posts.empty:
                    post_counts = df_posts['username'].value_counts().reset_index()
                    post_counts.columns = ['username', 'total_posts']
                    
                    # Membuat Bar Chart dengan gradasi warna yang konsisten
                    # Menggunakan list warna Hex agar terdeteksi VS Code
                    fig_posts = px.bar(
                        post_counts,
                        x='username',
                        y='total_posts',
                        color='total_posts',
                        # Skala warna dari Biru Muda ke Biru Tua (Paragon Theme)
                        # Anda bisa mengganti kode Hex ini langsung di VS Code
                        color_continuous_scale=["#00D4FF", "#0354B8"], 
                        template="plotly_dark",
                        labels={'total_posts': 'Jumlah Post', 'username': 'User'}
                    )

                    # Pengaturan Layout agar rapi dan simetris dengan Kolom 1
                    fig_posts.update_layout(
                        margin=dict(l=20, r=20, t=20, b=20), 
                        height=300, 
                        coloraxis_showscale=False # Menyembunyikan bar warna di samping
                    )
                    
                    # Menghilangkan garis grid X untuk tampilan lebih clean
                    fig_posts.update_xaxes(showgrid=False)
                    
                    st.plotly_chart(fig_posts, use_container_width=True)
                else:
                    st.info("Belum ada data postingan untuk dikomparasi.")
            

            st.divider()
            
        with st.expander("📈 Post Frequency Analysis", expanded=True):
            # Filters for Line Chart
            fcol1, fcol2, fcol3 = st.columns([2, 2, 1])
            
            with fcol1:
                available_users = df_profiles['username'].tolist() if not df_profiles.empty else []
                selected_users = st.multiselect(
                    "Pilih Akun untuk Dibandingkan", 
                    options=available_users,
                    default=available_users,
                    key="ms_freq_analysis" # Key unik untuk mencegah bug state
                )
            
            with fcol2:
                # Proteksi nilai min/max date
                if not df_posts.empty and df_posts['date'].notna().any():
                    min_d = df_posts['date'].min().date()
                    max_d = df_posts['date'].max().date()
                    date_range = st.date_input("Periode Tanggal", [min_d, max_d], key="di_freq_analysis")
                else:
                    date_range = []
                    st.warning("Data tanggal tidak tersedia")
            
            with fcol3:
                granularity = st.selectbox(
                    "Granularitas", 
                    ["Daily", "Weekly", "Monthly", "Yearly"],
                    key="sb_freq_granularity"
                )

            # Inisialisasi Grafik
            fig_line = go.Figure()

            # Resampling Map
            resample_map = {"Daily": "D", "Weekly": "W", "Monthly": "M", "Yearly": "Y"}

            # PALET WARNA (Format Hex 6-digit agar muncul color picker di VS Code)
            line_colors = [
                "#0354B8", # Biru Utama
                "#FFD001", # Kuning
                "#E1306C", # Merah
                "#00D4FF", # Biru Muda
                "#28A745", # Hijau
                "#FF8C00"  # Orange
            ]

            # Hanya jalankan jika ada user yang dipilih dan rentang tanggal lengkap
            if selected_users and len(date_range) == 2:
                has_plot_data = False
                
                for idx, user in enumerate(selected_users):
                    user_df = df_posts[df_posts['username'] == user].copy()
                    
                    # Filter Tanggal
                    user_df = user_df[
                        (user_df['date'].dt.date >= date_range[0]) & 
                        (user_df['date'].dt.date <= date_range[1])
                    ]
                    
                    if not user_df.empty:
                        has_plot_data = True
                        timeline_df = user_df.set_index('date').resample(resample_map[granularity]).size().reset_index()
                        timeline_df.columns = ['date', 'count']

                        current_color = line_colors[idx % len(line_colors)]

                        fig_line.add_trace(go.Scatter(
                            x=timeline_df['date'], 
                            y=timeline_df['count'],
                            name=user,
                            fill='tozeroy', 
                            mode='lines+markers',
                            line=dict(width=3, color=current_color),
                            marker=dict(size=6, color=current_color),
                            hovertemplate=f"<b>{user}</b><br>Tanggal: %{{x}}<br>Post: %{{y}}<extra></extra>"
                        ))

                if has_plot_data:
                    fig_line.update_layout(
                        template="plotly_dark",
                        hovermode="x unified",
                        xaxis_title="Timeline",
                        yaxis_title="Jumlah Postingan",
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        margin=dict(l=20, r=20, t=50, b=20),
                        height=450,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                    )
                    
                    fig_line.update_xaxes(showgrid=False)
                    fig_line.update_yaxes(showgrid=True, gridcolor='#333333')
                    
                    st.plotly_chart(fig_line, use_container_width=True)
                else:
                    st.info("Tidak ada data untuk ditampilkan pada periode ini.")
            elif len(date_range) < 2:
                st.info("Silahkan pilih rentang tanggal (Mulai & Selesai).")

    with res_tab_det:
        # Profile Table
        # st.markdown("#### 👤 Profil Umum Lengkap")
        with st.expander("👤 Profil Umum Lengkap", expanded=True):
            df_profiles = pd.DataFrame([r['profile_info'] for r in st.session_state.all_results if 'error' not in r])
            st.dataframe(df_profiles, use_container_width=True)
            
            # Download Options for Profile
            c1, c2, c3, c4 = st.columns(4)
            for fmt, col in zip(["CSV", "Excel", "JSON", "TXT"], [c1, c2, c3, c4]):
                data, mime = get_download_link(df_profiles.to_dict('records'), fmt)
                col.download_button(f"Download Profil ({fmt})", data, file_name=f"profiles.{fmt.lower()}", mime=mime)

            st.divider()
        
        # Post Table
        # st.markdown("#### 📝 Post Detail Terkumpul")
        with st.expander("#### 📝 Post Detail Terkumpul", expanded=True):
            all_posts = []
            for r in st.session_state.all_results:
                if 'posts' in r:
                    for p in r['posts']:
                        p['owner'] = r['profile_info']['username']
                        all_posts.append(p)
            
            if all_posts:
                df_posts = pd.DataFrame(all_posts)
                st.dataframe(df_posts, use_container_width=True)
                
                cp1, cp2, cp3, cp4 = st.columns(4)
                for fmt, col in zip(["CSV", "Excel", "JSON", "TXT"], [cp1, cp2, cp3, cp4]):
                    data, mime = get_download_link(all_posts, fmt)
                    col.download_button(f"Download Posts ({fmt})", data, file_name=f"posts.{fmt.lower()}", mime=mime)
    with res_tab_dict:

        # --- SECTION 1: PROFILE METADATA ---
        with st.expander("👤 Profile Information Metadata", expanded=True):
            st.markdown("""
            Data ini berkaitan dengan identitas akun dan performa akumulatif profil.
            """)
            profile_meta = [
                {"Field": "userid", "Type": "Numeric ID", "Description": "ID unik internal Instagram untuk akun tersebut."},
                {"Field": "username", "Type": "String", "Description": "Handle akun yang digunakan untuk login dan URL profil."},
                {"Field": "followers", "Type": "Integer", "Description": "Jumlah total akun yang mengikuti profil ini."},
                {"Field": "engagement_rate", "Type": "Float (%)", "Description": "Rata-rata interaksi (Likes + Comments) dibagi jumlah followers."},
                {"Field": "is_business", "Type": "Boolean", "Description": "Menandakan apakah akun dikategorikan sebagai akun Bisnis/Kreator."},
                {"Field": "is_verified", "Type": "Boolean", "Description": "Status centang biru (Authenticity Verified)."},
            ]
            st.table(profile_meta)

        # --- SECTION 2: POST METRICS ---
        with st.expander("📝 Content & Engagement Metrics", expanded=False):
            st.markdown("""
            Definisi data yang diekstrak dari setiap postingan individu di timeline.
            """)
            post_meta = [
                {"Field": "date", "Type": "Datetime", "Description": "Waktu publikasi postingan (Waktu Lokal/WIB)."},
                {"Field": "caption", "Type": "Text", "Description": "Isi teks atau deskripsi yang ditulis oleh pemilik akun."},
                {"Field": "likes", "Type": "Integer", "Description": "Jumlah tanda suka (Heart) pada saat pengambilan data."},
                {"Field": "comments_count", "Type": "Integer", "Description": "Jumlah total komentar publik pada postingan."},
                {"Field": "is_video", "Type": "Boolean", "Description": "True jika postingan berupa Reels atau Video tunggal."},
                {"Field": "video_view_count", "Type": "Integer", "Description": "Jumlah tayangan video (Hanya tersedia jika is_video = True)."},
                {"Field": "hashtags", "Type": "List/Array", "Description": "Kumpulan tagar (#) yang digunakan dalam caption."},
                {"Field": "tagged_users", "Type": "List/Array", "Description": "Username akun lain yang ditandai di dalam foto/video."},
            ]
            st.table(post_meta)

        # --- SECTION 3: TECHNICAL AUDIT ---
        with st.expander("🛠️ Technical Data Audit", expanded=False):
            st.markdown("""
            Metadata sistem untuk kebutuhan audit dan validasi data.
            """)
            tech_meta = [
                {"Field": "scraped_at", "Type": "Timestamp", "Description": "Waktu presisi saat mesin scraper mengambil data dari server."},
                {"Field": "platform", "Type": "String", "Description": "Sumber asal data (Instagram)."},
                {"Field": "url", "Type": "String URL", "Description": "Direct link menuju postingan asli."},
                {"Field": "location", "Type": "String/None", "Description": "Nama lokasi geotag jika dicantumkan pada postingan."},
            ]
            st.table(tech_meta)

        st.info("💡 **Tips:** Data Dictionary ini sangat berguna saat Anda mengekspor data ke Excel untuk memastikan tim analis menggunakan kolom yang tepat untuk rumus kalkulasi mereka.")

        # Section Raw JSON yang bisa di-hide (Expander)
        st.divider()
        with st.expander("📦 Lihat Raw JSON Data", expanded=False):
            st.json(st.session_state.all_results)