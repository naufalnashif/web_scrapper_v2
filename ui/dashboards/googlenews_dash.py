import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.exporter import get_download_link

def render_googlenews_dashboard(df_profiles, df_posts):
    st.subheader("📰 Google News Media Intelligence")
    
    if df_posts.empty:
        st.warning("Data berita tidak ditemukan.")
        return

    # --- DATA PREPARATION (Internal Aliasing) ---
    # Pastikan kolom date adalah datetime
    df_posts['date'] = pd.to_datetime(df_posts['date'], errors='coerce')
    
    # Mapping kolom agar lebih profesional (dengan proteksi jika kolom tidak ada)
    rename_dict = {
        'name': 'Headline',
        'publisher': 'Media/Publisher',
        'username': 'Topic/Keyword',
        'scraped_at': 'Extraction Date'
    }
    
    # Hanya rename kolom yang benar-benar ada di df_posts
    existing_rename = {k: v for k, v in rename_dict.items() if k in df_posts.columns}
    df_display = df_posts.rename(columns=existing_rename)
    
    # Pastikan kolom hasil rename ada, jika tidak buat kolom dummy agar tidak KeyError
    if 'Extraction Date' not in df_display.columns:
        df_display['Extraction Date'] = "N/A"
    if 'Topic/Keyword' not in df_display.columns:
        df_display['Topic/Keyword'] = "General"
    if 'Media/Publisher' not in df_display.columns:
        df_display['Media/Publisher'] = "Unknown"
    if 'Headline' not in df_display.columns:
        df_display['Headline'] = df_display.get('name', 'No Title')

    # --- FILTERS SECTION ---
    with st.expander("🎯 Dynamic Filters", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            all_topics = ["All Topics"] + sorted(df_display['Topic/Keyword'].unique().tolist())
            selected_topic = st.selectbox("Filter by Topic", all_topics)
        with c2:
            available_pubs = df_display
            if selected_topic != "All Topics":
                available_pubs = df_display[df_display['Topic/Keyword'] == selected_topic]
            all_pubs = ["All Publishers"] + sorted(available_pubs['Media/Publisher'].unique().tolist())
            selected_pub = st.selectbox("Filter by Media", all_pubs)

    # --- FILTER LOGIC ---
    mask = pd.Series([True] * len(df_display))
    if selected_topic != "All Topics":
        mask &= (df_display['Topic/Keyword'] == selected_topic)
    if selected_pub != "All Publishers":
        mask &= (df_display['Media/Publisher'] == selected_pub)
    
    df_filtered = df_display[mask]

    res_tab_ov, res_tab_det, res_tab_dict = st.tabs(["📊 Analytics Overview", "📋 News Details", "📝 Data Dictionary"])

    with res_tab_ov:
        # ROW 1: Key Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Articles", len(df_filtered))
        m2.metric("Active Media", df_filtered['Media/Publisher'].nunique())
        m3.metric("Topic Segments", df_filtered['Topic/Keyword'].nunique())
        m4.metric("Last Update", df_filtered['date'].max().strftime('%d/%m/%y') if not df_filtered['date'].isnull().all() else "-")

        st.divider()

        # ROW 2: Multi-Topic Publisher Analysis
        st.markdown("#### 🏆 Media Share by Topic")
        top_pubs = df_filtered.groupby(['Topic/Keyword', 'Media/Publisher']).size().reset_index(name='Articles')
        top_pubs = top_pubs.sort_values(['Topic/Keyword', 'Articles'], ascending=[True, False]).groupby('Topic/Keyword').head(7)
        
        fig_share = px.bar(
            top_pubs, x='Articles', y='Media/Publisher', color='Topic/Keyword',
            barmode='group', orientation='h', template="plotly_dark",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_share.update_layout(yaxis={'categoryorder':'total ascending'}, height=400)
        st.plotly_chart(fig_share, use_container_width=True)

        # ROW 3: Time Trend Analysis (Dengan Filter di Atasnya)
        st.divider()
        t_col1, t_col2 = st.columns([2, 1])
        with t_col1:
            st.markdown("#### 📈 Publication Trend Analysis")
        with t_col2:
            time_filter = st.selectbox("Period", ["Daily", "Weekly", "Monthly", "Yearly"], label_visibility="collapsed")
        
        # Logika Trend
        resample_map = {"Daily": "D", "Weekly": "W", "Monthly": "ME", "Yearly": "YE"}
        df_trend_base = df_filtered.dropna(subset=['date']).copy()
        
        if not df_trend_base.empty:
            df_trend_base = df_trend_base.set_index('date')
            dim = 'Topic/Keyword' if selected_topic == "All Topics" else 'Media/Publisher'
            df_resampled = df_trend_base.groupby([pd.Grouper(freq=resample_map[time_filter]), dim]).size().reset_index(name='Count')
            
            fig_trend = px.line(
                df_resampled, x='date', y='Count', color=dim,
                markers=True, template="plotly_dark"
            )
            fig_trend.update_layout(hovermode="x unified", xaxis_title="Timeline")
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("Data waktu tidak tersedia untuk menampilkan tren.")

    with res_tab_det:
        st.markdown("#### 🔍 Filtered News Feed")
        search_query = st.text_input("🔍 Search headline or media...", "")
        
        display_data = df_filtered.copy()
        if search_query:
            display_data = display_data[display_data['Headline'].str.contains(search_query, case=False) | 
                                        display_data['Media/Publisher'].str.contains(search_query, case=False)]

        # Safety Columns for Table
        final_cols = ['date', 'Topic/Keyword', 'Media/Publisher', 'Headline', 'url', 'Extraction Date']
        available_cols = [c for c in final_cols if c in display_data.columns]
        st.dataframe(display_data[available_cols], use_container_width=True)
        
        # --- EXPORT ---
        with st.expander("📥 Export Filtered Data", expanded=False):
        
            c1, c2, c3, c4 = st.columns(4)
            df_export = df_filtered.copy()
            for col in df_export.columns:
                if pd.api.types.is_datetime64_any_dtype(df_export[col]):
                    df_export[col] = df_export[col].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            data_dict_export = df_export.to_dict('records')
            formats = [("CSV", c1), ("Excel", c2), ("JSON", c3), ("TXT", c4)]
            for fmt, col in formats:
                data, mime = get_download_link(data_dict_export, fmt)
                col.download_button(label=f"Download {fmt}", data=data, 
                                    file_name=f"gnews_report.{fmt.lower()}", mime=mime)

    with res_tab_dict:
        st.markdown("### 📝 Google News Data Dictionary")
        meta_data = [
            {"Field": "Headline", "Type": "Text", "Description": "Judul berita utama dari sumber media."},
            {"Field": "Media/Publisher", "Type": "String", "Description": "Nama institusi media penerbit."},
            {"Field": "Topic/Keyword", "Type": "String", "Description": "Kata kunci pencarian."},
            {"Field": "date", "Type": "Datetime", "Description": "Tanggal publikasi artikel."},
            {"Field": "Extraction Date", "Type": "Timestamp", "Description": "Waktu saat data diambil sistem."},
            {"Field": "url", "Type": "URL", "Description": "Link artikel asli."},
            {"Field": "description", "Type": "Text", "Description": "Snippet/ringkasan berita."}
        ]
        st.table(meta_data)