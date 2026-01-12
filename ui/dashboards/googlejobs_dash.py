import streamlit as st
import pandas as pd
import plotly.express as px
from utils.exporter import get_download_link

def render_googlejobs_dashboard(df_profiles, df_posts):
    st.subheader("💼 Google Jobs Talent Intelligence")
    
    if df_posts.empty:
        st.warning("Tidak ada data lowongan kerja ditemukan.")
        return

    # --- DATA PREPARATION ---
    df_posts['date'] = pd.to_datetime(df_posts['date'], errors='coerce')
    
    # Mapping untuk tampilan profesional
    df_display = df_posts.rename(columns={
        'name': 'Job Role',
        'publisher': 'Job Portal/Media',
        'username': 'Company Target',
        'scraped_at': 'Extraction Date'
    })

    # --- TABS ---
    res_tab_ov, res_tab_det, res_tab_dict = st.tabs(["📊 Hiring Trends", "📋 Job Openings", "📝 Data Dictionary"])

    with res_tab_ov:
        # ROW 1: Key Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Openings", len(df_display))
        m2.metric("Active Portals", df_display['Job Portal/Media'].nunique())
        m3.metric("Companies Tracked", df_display['Company Target'].nunique())
        m4.metric("Latest Post", df_display['date'].max().strftime('%d/%m/%y') if not df_display['date'].isnull().all() else "-")

        st.divider()

        # ROW 2: Charts
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 🏢 Hiring Activity by Company")
            comp_counts = df_display['Company Target'].value_counts().reset_index()
            fig_comp = px.bar(comp_counts, x='count', y='Company Target', orientation='h',
                             color='Company Target', template="plotly_dark")
            st.plotly_chart(fig_comp, use_container_width=True)

        with c2:
            st.markdown("#### 🌐 Top Job Sources")
            source_counts = df_display['Job Portal/Media'].value_counts().nlargest(10).reset_index()
            fig_source = px.pie(source_counts, values='count', names='Job Portal/Media', 
                               hole=0.4, template="plotly_dark")
            st.plotly_chart(fig_source, use_container_width=True)

    with res_tab_det:
        st.markdown("#### 🔍 Detailed Job Feed")
        
        # Search Filter
        search_q = st.text_input("Cari posisi atau portal...", "")
        df_final = df_display.copy()
        if search_q:
            df_final = df_final[df_final['Job Role'].str.contains(search_q, case=False) | 
                               df_final['Job Portal/Media'].str.contains(search_q, case=False)]

        # Display Dataframe
        cols = ['date', 'Company Target', 'Job Role', 'Job Portal/Media', 'url']
        st.dataframe(df_final[cols], use_container_width=True)

        # Export Section
        st.markdown("##### 📥 Export Recruitment Data")
        ec1, ec2, ec3, ec4 = st.columns(4)
        df_export = df_final.copy()
        for col in df_export.columns:
            if pd.api.types.is_datetime64_any_dtype(df_export[col]):
                df_export[col] = df_export[col].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        data_dict = df_export.to_dict('records')
        formats = [("CSV", ec1), ("Excel", ec2), ("JSON", ec3), ("TXT", ec4)]
        for fmt, col in formats:
            data, mime = get_download_link(data_dict, fmt)
            col.download_button(label=f"Download {fmt}", data=data, 
                                file_name=f"jobs_report.{fmt.lower()}", mime=mime)

    with res_tab_dict:
        st.markdown("### 📝 Talent Data Dictionary")
        meta_jobs = [
            {"Field": "Job Role", "Type": "Text", "Description": "Nama posisi atau jabatan yang dibuka."},
            {"Field": "Company Target", "Type": "String", "Description": "Perusahaan yang sedang kita pantau rekrutmennya."},
            {"Field": "Job Portal/Media", "Type": "String", "Description": "Website tempat lowongan dipasang (e.g. LinkedIn, Jobstreet, Glints)."},
            {"Field": "date", "Type": "Datetime", "Description": "Waktu lowongan tersebut dipublikasikan."},
            {"Field": "url", "Type": "URL", "Description": "Link menuju detail lowongan kerja."}
        ]
        st.table(meta_jobs)