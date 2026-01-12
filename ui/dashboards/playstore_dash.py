import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def render_playstore_dashboard(df_profiles, df_posts):
    st.title("📱 Play Store Advanced Analytics")
    
    if df_profiles.empty or df_posts.empty:
        st.warning("Data tidak mencukupi untuk analisis.")
        return

    # --- PRE-PROCESSING & CLEANING ---
    df_posts['date'] = pd.to_datetime(df_posts['date'])
    if 'app_name' not in df_posts.columns:
        df_posts['app_name'] = df_posts['username']

    # --- GLOBAL FILTER (Top Level) ---
    # Filter ini akan mengontrol seluruh dashboard (KPI & Charts)
    all_apps = df_profiles['title'].unique().tolist()
    selected_app = st.selectbox("🎯 Select Target Application:", all_apps)

    # Filter Data berdasarkan pilihan
    filtered_profile = df_profiles[df_profiles['title'] == selected_app].iloc[0]
    filtered_posts = df_posts[df_posts['app_name'] == selected_app].copy()

    # --- SECTION 1: DYNAMIC KPI (Filtered by App) ---
    st.subheader(f"📊 Performance Overview: {selected_app}")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    with kpi1:
        st.image(filtered_profile['icon'], width=70)
    with kpi2:
        st.metric("Global Rating", f"⭐ {filtered_profile['rating']}")
    with kpi3:
        st.metric("Total Installs", filtered_profile['installs'])
    with kpi4:
        st.metric("Total Reviews Scraped", len(filtered_posts))

    st.divider()

    # --- SECTION 2: ANALYTICS STRATEGY (TABS) ---
    tab_trend, tab_heatmap, tab_raw, res_tab_dict = st.tabs([
        "📈 Time Series Trend", 
        "🌡️ Version Analysis", 
        "📋 Profile & Raw Data",
        "📝 Data Dictionary"
    ])

    with tab_trend:
        st.markdown("#### 📅 Review Sentiment Trend")
        
        # --- DYNAMIC TIME SERIES FILTER ---
        # Meniru fitur Instagram Dash (Daily, Weekly, Monthly)
        time_granularity = st.radio(
            "Select Time Period:", 
            ["Daily", "Weekly", "Monthly"], 
            horizontal=True, 
            key="time_period_selector"
        )

        if time_granularity == "Daily":
            filtered_posts['period'] = filtered_posts['date'].dt.date
        elif time_granularity == "Weekly":
            filtered_posts['period'] = filtered_posts['date'].dt.to_period('W').apply(lambda r: r.start_time)
        else:
            filtered_posts['period'] = filtered_posts['date'].dt.to_period('M').apply(lambda r: r.start_time)

        # Agregasi data
        trend_data = filtered_posts.groupby(['period', 'rating']).size().reset_index(name='count')
        
        fig_trend = px.line(
            trend_data, 
            x='period', 
            y='count', 
            color='rating',
            markers=True,
            title=f"Review Distribution Trend ({time_granularity})",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            template="plotly_dark"
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    with tab_heatmap:
        st.markdown("#### 🌡️ Rating vs App Version Heatmap")
        
        # Validasi kolom app_version
        if 'app_version' in filtered_posts.columns and not filtered_posts['app_version'].isnull().all():
            # Mengurutkan versi agar tampilan heatmap logis
            heatmap_data = filtered_posts.groupby(['app_version', 'rating']).size().unstack(fill_value=0)
            
            fig_heat = px.imshow(
                heatmap_data,
                labels=dict(x="Rating Score", y="App Version", color="Total Reviews"),
                color_continuous_scale='Viridis',
                text_auto=True,
                aspect="auto"
            )
            st.plotly_chart(fig_heat, use_container_width=True)
        else:
            st.info("Data versi aplikasi tidak tersedia untuk visualisasi ini.")

    with tab_raw:
        # --- TABEL APLIKASI PINDAH KE SINI ---
        st.markdown("#### 🏁 Competitive Landscape (All Scraped Apps)")
        summary_df = df_profiles[['title', 'rating', 'installs', 'category', 'developer']].copy()
        summary_df.columns = ['Application', 'Avg Rating', 'Installs', 'Category', 'Developer']
        st.dataframe(summary_df.sort_values('Avg Rating', ascending=False), use_container_width=True, hide_index=True)
        
        st.divider()

        # --- RAW REVIEW DATA ---
        st.markdown(f"#### 💬 Raw Reviews: {selected_app}")
        st.dataframe(
            filtered_posts[['user_name', 'rating', 'content', 'date', 'app_version', 'thumbs_up']],
            use_container_width=True,
            hide_index=True
        )
    with res_tab_dict:

        with st.expander("📱 App & Developer Metadata", expanded=True):
            meta_app = [
                {"Field": "title", "Type": "String", "Description": "Nama aplikasi resmi di Google Play Store."},
                {"Field": "app_id", "Type": "ID", "Description": "Package name unik aplikasi (Contoh: com.android.chrome)."},
                {"Field": "developer", "Type": "String", "Description": "Nama perusahaan atau individu pengembang aplikasi."},
                {"Field": "category", "Type": "String", "Description": "Kategori/Genre aplikasi."},
                {"Field": "rating", "Type": "Float", "Description": "Skor rata-rata bintang (1.0 - 5.0)."},
                {"Field": "reviews_count", "Type": "Integer", "Description": "Total akumulasi ulasan sejak aplikasi rilis."},
                {"Field": "installs", "Type": "String", "Description": "Rentang jumlah unduhan (Contoh: 100,000+)."},
                {"Field": "scraped_at", "Type": "Timestamp", "Description": "Waktu pengambilan data dari Google server."},
            ]
            st.table(meta_app)

        with st.expander("💬 User Review Metrics", expanded=False):
            meta_rev = [
                {"Field": "user_name", "Type": "String", "Description": "Nama pengguna yang memberikan ulasan."},
                {"Field": "content", "Type": "Text", "Description": "Teks ulasan (Karakter non-printable telah dibersihkan)."},
                {"Field": "rating", "Type": "Integer", "Description": "Jumlah bintang yang diberikan (1-5)."},
                {"Field": "app_version", "Type": "String", "Description": "Versi aplikasi yang digunakan saat ulasan dibuat."},
                {"Field": "reply_content", "Type": "Text", "Description": "Tanggapan resmi dari tim developer/CS."},
                {"Field": "reply_date", "Type": "Datetime", "Description": "Waktu developer memberikan balasan."},
                {"Field": "thumbs_up", "Type": "Integer", "Description": "Jumlah user lain yang terbantu oleh ulasan ini."},
                {"Field": "review_id", "Type": "String", "Description": "ID unik untuk setiap baris ulasan."},
            ]
            st.table(meta_rev)

        with st.expander("🛠️ Technical Data Audit", expanded=False):
            tech_meta = [
                {"Field": "review_id", "Type": "String", "Description": "ID unik ulasan untuk tracking database."},
                {"Field": "scraped_at", "Type": "Timestamp", "Description": "Waktu presisi pengambilan data dari server."},
                {"Field": "reply_date", "Type": "Datetime", "Description": "Waktu developer memberikan respon."},
                {"Field": "user_image", "Type": "URL", "Description": "Link foto profil pengguna (Avatar)."},
            ]
            st.table(tech_meta)

        st.info("💡 **Tips:** Gunakan 'app_version' untuk menganalisis apakah update terbaru aplikasi memicu banyak ulasan negatif atau positif.")

    # Footer Insight
    st.sidebar.markdown(f"""
    ---
    **Dashboard Note:**
    Data ulasan untuk **{selected_app}** dianalisis dari periode 
    {filtered_posts['date'].min().strftime('%d %b %Y')} sampai 
    {filtered_posts['date'].max().strftime('%d %b %Y')}.
    """)