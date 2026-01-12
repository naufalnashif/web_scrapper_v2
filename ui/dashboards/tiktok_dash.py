import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.exporter import get_download_link

def render_tiktok_dashboard(df_profiles, df_posts):
    st.subheader("🎵 TikTok Creator Performance Analytics")

    if df_profiles.empty:
        st.warning("Data profil tidak ditemukan. Pastikan scraping berhasil di tab Logs.")
        return

    # --- TABS NAVIGATION ---
    res_tab_ov, res_tab_det = st.tabs(["🏠 Overview Visuals", "📋 Result Details"])

    with res_tab_ov:
        # --- SECTION 1: KPI PER USER (DIPISAHKAN) ---
        with st.expander("📊 Account Performance Metrics", expanded=True):
            selected_kpi_user = st.selectbox("Pilih Akun untuk Detail KPI", df_profiles['username'].unique())
            
            # Filter data khusus user yang dipilih
            user_prof = df_profiles[df_profiles['username'] == selected_kpi_user].iloc[0]
            user_posts = df_posts[df_posts['username'] == selected_kpi_user] if not df_posts.empty else pd.DataFrame()

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Engagement Rate", f"{user_prof.get('engagement_rate', 0):.2f}%")
            
            t_views = user_posts['views'].sum() if not user_posts.empty and 'views' in user_posts.columns else 0
            m2.metric("Total Views (Captured)", f"{t_views:,}")
            
            m3.metric("Followers", f"{user_prof.get('followers', 0):,}")
            
            avg_l = user_posts['likes'].mean() if not user_posts.empty else 0
            m4.metric("Avg. Likes/Post", f"{avg_l:.0f}")

            st.divider()

            # --- COMPARISON CHART ---
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 👥 Follower vs Following")
                fig_foll = px.bar(df_profiles, x='username', y=['followers', 'following'],
                                barmode='group', template="plotly_dark",
                                color_discrete_sequence=["#2C48FE", "#25F4EE"])
                fig_foll.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=300)
                st.plotly_chart(fig_foll, use_container_width=True)
                
            with col2:
                st.markdown("#### 📊 Total Postingan (Captured)")
                if not df_posts.empty:
                    post_counts = df_posts['username'].value_counts().reset_index()
                    post_counts.columns = ['username', 'total_posts']
                    fig_posts = px.bar(post_counts, x='username', y='total_posts',
                                     color='total_posts', template="plotly_dark",
                                     color_continuous_scale=["#25F4EE", "#2C48FE"])
                    fig_posts.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=300, coloraxis_showscale=False)
                    st.plotly_chart(fig_posts, use_container_width=True)

        # --- SECTION 2: TIMELINE ANALYSIS ---
        with st.expander("📈 Post Frequency Analysis", expanded=True):
            fcol1, fcol2, fcol3 = st.columns([2, 2, 1])
            with fcol1:
                selected_users = st.multiselect("Bandingkan Akun", options=df_profiles['username'].tolist(), default=df_profiles['username'].tolist(), key="tk_ms_users")
            with fcol2:
                if not df_posts.empty and df_posts['date'].notna().any():
                    min_d, max_d = df_posts['date'].min().date(), df_posts['date'].max().date()
                    date_range = st.date_input("Periode Tanggal", [min_d, max_d], key="tk_di_range")
                else: date_range = []
            with fcol3:
                granularity = st.selectbox("Granularitas", ["Daily", "Weekly", "Monthly"], key="tk_sb_gran")

            if selected_users and len(date_range) == 2:
                fig_line = go.Figure()
                resample_map = {"Daily": "D", "Weekly": "W", "Monthly": "M"}
                line_colors = ["#2C48FE", "#25F4EE", "#FFFFFF", "#FFD001", "#00D4FF"]

                for idx, user in enumerate(selected_users):
                    user_df = df_posts[(df_posts['username'] == user) & 
                                     (df_posts['date'].dt.date >= date_range[0]) & 
                                     (df_posts['date'].dt.date <= date_range[1])]
                    if not user_df.empty:
                        timeline = user_df.set_index('date').resample(resample_map[granularity]).size().reset_index()
                        timeline.columns = ['date', 'count']
                        fig_line.add_trace(go.Scatter(
                            x=timeline['date'], y=timeline['count'], name=user,
                            mode='lines+markers', line=dict(width=3, color=line_colors[idx % len(line_colors)]),
                            fill='tozeroy'
                        ))
                fig_line.update_layout(template="plotly_dark", hovermode="x unified", height=400)
                st.plotly_chart(fig_line, use_container_width=True)

    with res_tab_det:
        # Profile Data Table
        with st.expander("👤 Profil Umum Lengkap", expanded=True):
            st.dataframe(df_profiles, use_container_width=True, hide_index=True)
            c1, c2, c3, c4 = st.columns(4)
            # Konversi dict ke record agar aman dari Timestamp sebelum export JSON
            profile_export = df_profiles.copy()
            for fmt, col in zip(["CSV", "Excel", "JSON", "TXT"], [c1, c2, c3, c4]):
                data, mime = get_download_link(profile_export.to_dict('records'), fmt)
                col.download_button(f"Download Profil ({fmt})", data, file_name=f"tk_profiles.{fmt.lower()}", mime=mime)

        # Post Data Table dengan Perbaikan Serialisasi Timestamp
        with st.expander("📝 Post Detail Terkumpul", expanded=True):
            if not df_posts.empty:
                st.dataframe(df_posts, use_container_width=True, hide_index=True)
                
                # FIX: Konversi Timestamp ke String khusus untuk export JSON/Excel
                posts_export = df_posts.copy()
                if 'date' in posts_export.columns:
                    posts_export['date'] = posts_export['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
                
                cp1, cp2, cp3, cp4 = st.columns(4)
                for fmt, col in zip(["CSV", "Excel", "JSON", "TXT"], [cp1, cp2, cp3, cp4]):
                    # Gunakan posts_export yang sudah di-string-kan tanggalnya
                    data, mime = get_download_link(posts_export.to_dict('records'), fmt)
                    col.download_button(f"Download Posts ({fmt})", data, file_name=f"tk_posts.{fmt.lower()}", mime=mime)
            else:
                st.info("Tidak ada data postingan.")