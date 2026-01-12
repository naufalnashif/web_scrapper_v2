import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.exporter import get_download_link

def render_linkedin_dashboard(df_profiles, df_posts):
    st.subheader("💼 LinkedIn Market Intelligence Professional")

    if df_posts.empty:
        st.warning("Data LinkedIn tidak ditemukan.")
        return

    # --- DATA PREPARATION ---
    df_posts['date'] = pd.to_datetime(df_posts['date'], errors='coerce')
    
    # --- TABS ---
    res_tab_ov, res_tab_det, res_tab_dict = st.tabs([
        "🏠 Market Overview", 
        "📋 Data Explorer", 
        "📝 Tech Dictionary"
    ])

    with res_tab_ov:
        # --- SECTION: ADVANCED FILTERS (Inspired by Instagram Dash) ---
        with st.expander("🔍 Filter Controls", expanded=True):
            f1, f2, f3 = st.columns(3)
            
            with f1:
                all_keywords = sorted(df_posts['username'].unique())
                selected_keywords = st.multiselect("Filter by Input Keyword:", all_keywords, default=all_keywords)
            
            with f2:
                all_publishers = sorted(df_posts['publisher'].unique())
                selected_publishers = st.multiselect("Filter by Publisher:", all_publishers, default=all_publishers)
            
            with f3:
                time_unit = st.selectbox("Group Trend By:", ["Daily", "Weekly", "Monthly", "Yearly"])
                # Map time unit to pandas resample alias
                time_map = {"Daily": "D", "Weekly": "W", "Monthly": "ME", "Yearly": "YE"}

        # Apply Filters
        filtered_df = df_posts[
            (df_posts['username'].isin(selected_keywords)) & 
            (df_posts['publisher'].isin(selected_publishers))
        ].copy()

        # --- SECTION: KEY METRICS ---
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Opportunities", len(filtered_df))
        m2.metric("Market Players", filtered_df['publisher'].nunique())
        m3.metric("Top Industry", filtered_df['industries'].mode()[0] if not filtered_df.empty else "N/A")
        m4.metric("Avg Applicants", "Rich Data Available")

        st.divider()

        
        # --- SECTION: BAR CHART PUBLISHERS ---
        st.markdown("#### 🏢 Top Hiring Entities")
        if not filtered_df.empty:
            comp_chart = filtered_df['publisher'].value_counts().nlargest(10).reset_index()
            fig_comp = px.bar(
                comp_chart, x='count', y='publisher', 
                orientation='h',
                color='count', 
                color_continuous_scale="Blues", 
                template="plotly_dark"
            )
            fig_comp.update_layout(yaxis={'categoryorder':'total ascending'}, height=400)
            st.plotly_chart(fig_comp, use_container_width=True)

# --- SECTION: LINE CHART TREND (Stand Alone) ---
        st.markdown(f"#### 📈 Job Posting Trend ({time_unit})")
        
        if not filtered_df.empty:
            # Resample data based on time_unit selection
            trend_data = filtered_df.set_index('date').resample(time_map[time_unit]).size().reset_index()
            trend_data.columns = ['Date', 'Job Count']
            
            fig_trend = px.line(
                trend_data, 
                x='Date', 
                y='Job Count',
                markers=True,
                template="plotly_dark",
                color_discrete_sequence=["#00a0dc"] # LinkedIn Blue
            )
            
            fig_trend.update_layout(
                hovermode="x unified",
                xaxis_title="Timeline",
                yaxis_title="Number of Postings",
                height=450
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("No data available for the selected filters.")

        st.divider()

    with res_tab_det:
        st.markdown("#### 🔍 Deep Data Explorer")
        
        # Search box internal
        search_query = st.text_input("Search in Description/Title:", "")
        if search_query:
            table_df = filtered_df[filtered_df['description'].str.contains(search_query, case=False) | 
                                   filtered_df['name'].str.contains(search_query, case=False)]
        else:
            table_df = filtered_df

        st.dataframe(table_df, use_container_width=True, hide_index=True)

        # Export System (Sudah Fix Timestamp Error)
        with st.expander("📥 Export Data", expanded=False):
            export_final = table_df.copy()
            for col in export_final.columns:
                if pd.api.types.is_datetime64_any_dtype(export_final[col]):
                    export_final[col] = export_final[col].dt.strftime('%Y-%m-%d %H:%M:%S')

            e1, e2, e3, e4 = st.columns(4)
            data_dict_export = export_final.to_dict('records')
            for fmt, col in zip(["CSV", "Excel", "JSON", "TXT"], [e1, e2, e3, e4]):
                data_dl, mime = get_download_link(data_dict_export, fmt)
                col.download_button(f"Export as {fmt}", data_dl, file_name=f"linkedin_pro_data.{fmt.lower()}", mime=mime)

    with res_tab_dict:
        st.markdown("### 📝 Technical Data Dictionary")
        st.info("Struktur metadata ini dirancang untuk integrasi sistem BI (Business Intelligence) tingkat lanjut.")
        
        meta_data = [
            {"Field": "name", "Type": "String (Categorical)", "Description": "Judul posisi pekerjaan resmi."},
            {"Field": "publisher", "Type": "String (Categorical)", "Description": "Nama entitas bisnis/perusahaan."},
            {"Field": "location", "Type": "String (Geographic)", "Description": "Lokasi penempatan kerja (City, Country)."},
            {"Field": "description", "Type": "Long Text (NLP Ready)", "Description": "Detail kualifikasi dan tanggung jawab pekerjaan."},
            {"Field": "date", "Type": "Datetime", "Description": "ISO-8601 Tanggal publikasi lowongan."},
            {"Field": "seniority_level", "Type": "Enum", "Description": "Level pengalaman (Internship, Entry, Mid, Senior)."},
            {"Field": "employment_type", "Type": "Enum", "Description": "Kontrak kerja (Full-time, Contract, etc)."},
            {"Field": "job_function", "Type": "String", "Description": "Departemen atau fungsi organisasi."},
            {"Field": "industries", "Type": "String", "Description": "Sektor industri perusahaan."},
            {"Field": "applicants_count", "Type": "Integer/String", "Description": "Jumlah kompetisi pelamar saat ini."},
            {"Field": "url", "Type": "URL", "Description": "Source of truth link asli."},
            {"Field": "scraped_at", "Type": "Timestamp", "Description": "Waktu ekstraksi sistem."}
        ]
        st.table(meta_data)