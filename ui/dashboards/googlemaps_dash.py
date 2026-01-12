import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.exporter import get_download_link

def render_googlemaps_dashboard(df_profiles, df_posts):
    st.subheader("🗺️ Google Maps Business Intelligence")
    
    # PROTEKSI AWAL: Jika dataframe kosong
    if df_posts.empty:
        st.warning("Data lokasi tidak ditemukan. Pastikan scraping berhasil di tab Logs.")
        return

    # Menyesuaikan Tabs agar serupa dengan Instagram (Overview, Details, Dictionary)
    res_tab_ov, res_tab_det, res_tab_dict = st.tabs([
        "🏠 Overview Visuals", 
        "📋 Result Details", 
        "📝 Data Dictionary"
    ])

    with res_tab_ov:
        # --- ROW 1: KEY METRICS & DISTRIBUTION ---
        with st.expander("📊 Business Metrics", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### ⭐ Rating per Bisnis")
                # Visualisasi Bar Chart Rating
                fig = px.bar(df_posts, x='name', y='rating',
                            color='rating', template="plotly_dark",
                            color_continuous_scale="Viridis",
                            labels={'rating': 'Rating Stars', 'name': 'Nama Bisnis'})
                fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=300)
                st.plotly_chart(fig, use_container_width=True)
                
            with col2:
                st.markdown("#### 🏢 Distribusi Kategori")
                # Pie Chart berdasarkan kategori bisnis
                if 'category' in df_posts.columns:
                    cat_counts = df_posts['category'].value_counts().reset_index()
                    cat_counts.columns = ['category', 'count']
                    fig2 = px.pie(cat_counts, values='count', names='category', 
                                 hole=0.4, template="plotly_dark",
                                 color_discrete_sequence=px.colors.qualitative.Pastel)
                    fig2.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=300)
                    st.plotly_chart(fig2, use_container_width=True)

        # --- ROW 2: REVIEW ANALYSIS ---
        with st.expander("📈 Review & Popularity Analysis", expanded=True):
            if 'reviews_count' in df_posts.columns:
                # Membersihkan string review (misal '1.2rb' jadi 1200) untuk visualisasi
                df_viz = df_posts.copy()
                df_viz['reviews_numeric'] = df_viz['reviews_count'].apply(
                    lambda x: float(str(x).replace('rb', '').replace('.', '').replace(',', '.')) * 1000 
                    if 'rb' in str(x) else float(str(x).replace('.', '').replace(',', '.') or 0)
                )
                
                fig3 = px.scatter(df_viz, x='name', y='reviews_numeric', 
                                 size='reviews_numeric', color='rating',
                                 title="Popularitas Bisnis (Jumlah Review vs Rating)",
                                 template="plotly_dark")
                st.plotly_chart(fig3, use_container_width=True)

    with res_tab_det:
        # --- DETAIL TABEL ---
        with st.expander("🏢 Tabel Hasil Scraping Lengkap", expanded=True):
            # Tampilkan kolom yang relevan saja agar rapi
            display_cols = ['name', 'rating', 'reviews_count', 'category', 'address', 'scraped_at']
            available_cols = [c for c in display_cols if c in df_posts.columns]
            st.dataframe(df_posts[available_cols], use_container_width=True)
            
            # Export Buttons (Serupa dengan platform lain)
            c1, c2, c3, c4 = st.columns(4)
            data_dict = df_posts.to_dict('records')
            for fmt, col in zip(["CSV", "Excel", "JSON", "TXT"], [c1, c2, c3, c4]):
                data, mime = get_download_link(data_dict, fmt)
                col.download_button(f"Download ({fmt})", data, 
                                  file_name=f"gmaps_export.{fmt.lower()}", mime=mime)

    with res_tab_dict:
        # --- DATA DICTIONARY (Menyamakan dengan Instagram Dash) ---
        st.markdown("### 📝 Google Maps Data Dictionary")
        
        meta_data = [
            {"Field": "name", "Type": "String", "Description": "Nama resmi bisnis di Google Maps."},
            {"Field": "rating", "Type": "Float", "Description": "Skor bintang (0.0 - 5.0)."},
            {"Field": "reviews_count", "Type": "String", "Description": "Jumlah ulasan dari pengguna (misal: 120 atau 1.1rb)."},
            {"Field": "category", "Type": "String", "Description": "Jenis kategori bisnis (misal: Restoran, Bengkel)."},
            {"Field": "address", "Type": "String", "Description": "Alamat singkat atau wilayah bisnis."},
            {"Field": "url", "Type": "URL", "Description": "Link langsung ke pencarian Google untuk bisnis tersebut."},
        ]
        st.table(meta_data)

        # Raw JSON Expander
        st.divider()
        with st.expander("📦 Lihat Raw JSON Data", expanded=False):
            st.json(st.session_state.all_results)