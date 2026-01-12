import streamlit as st
import pandas as pd
import plotly.express as px

def render_shopee_dashboard(df_profiles, df_posts):
    # --- HEADER & SELECTOR SEJAJAR ---
    col_title, col_select = st.columns([2, 1])
    
    with col_title:
        st.subheader("🛍️ Shopee Shop & Product Analytics")

    if df_profiles.empty:
        st.info("Data Shopee kosong atau akun tidak ditemukan.")
        return

    with col_select:
        # Menempatkan selectbox sejajar dengan judul
        shop_options = ["All Shops"] + df_profiles['username'].tolist()
        selected_shop = st.selectbox("Filter by Shop:", shop_options, label_visibility="collapsed")

    # --- LOGIKA FILTER AMAN (Mencegah KeyError) ---
    # Memastikan kolom 'username' ada di df_posts sebelum melakukan filter
    has_username_col = not df_posts.empty and 'username' in df_posts.columns

    if selected_shop != "All Shops":
        display_profiles = df_profiles[df_profiles['username'] == selected_shop]
        if has_username_col:
            display_posts = df_posts[df_posts['username'] == selected_shop]
        else:
            display_posts = pd.DataFrame(columns=['username', 'sold', 'likes', 'price', 'caption'])
    else:
        display_profiles = df_profiles
        display_posts = df_posts


    tab_ov, tab_det, res_tab_dict = st.tabs(["🏠 Analysis Overview", "📋 Detailed Data List", "📝 Data Dictionary"])

    with tab_ov:
        # --- KPI METRICS (Berdasarkan display_profiles) ---
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            avg_rating = display_profiles['rating'].mean()
            st.metric("Avg. Shop Rating", f"⭐ {avg_rating:.2f}")
        with m2:
            total_sold = display_posts['sold'].sum() if not display_posts.empty else 0
            st.metric("Total Sold (Sample)", f"{total_sold:,}")
        with m3:
            total_followers = display_profiles['followers'].sum()
            st.metric("Total Followers", f"{total_followers:,}")
        with m4:
            avg_er = display_profiles['engagement_rate'].mean()
            st.metric("Avg. ER", f"{avg_er:.2f}%")
        if display_posts.empty:
            st.warning("Tidak ada data produk (posts) untuk akun ini.")
        else:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### 📈 Sales vs Likes (Product Performance)")
                # Scatter plot per produk
                fig = px.scatter(
                    display_posts, 
                    x='likes', 
                    y='sold', 
                    size='price', 
                    hover_name='caption', 
                    color='username', 
                    template="plotly_dark",
                    title="Performa Penjualan Berdasarkan Likes"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with c2:
                st.markdown("#### 📊 Product Price Distribution")
                # Histogram harga produk
                fig_hist = px.histogram(
                    display_posts, 
                    x='price', 
                    nbins=15, 
                    template="plotly_dark", 
                    color_discrete_sequence=['#FF4B4B'],
                    title="Distribusi Harga Produk"
                )
                st.plotly_chart(fig_hist, use_container_width=True)

    with tab_det:
        st.markdown("#### 👤 Shop Profiles")
        st.dataframe(display_profiles, use_container_width=True)
        
        st.markdown("#### 📦 Product List (All Scraped Items)")
        if not display_posts.empty:
            # Menampilkan daftar produk lengkap dengan link aktif
            st.dataframe(
                display_posts[['username', 'caption', 'price', 'sold', 'likes', 'stock', 'url']], 
                use_container_width=True
            )
        else:
            st.write("Data produk tidak tersedia.")

    with res_tab_dict:

        with st.expander("🏪 Shop/Seller Information", expanded=True):
            meta_sh_p = [
                {"Field": "shop_name", "Type": "String", "Description": "Nama resmi toko di platform Shopee."},
                {"Field": "username", "Type": "String", "Description": "Handle unik penjual (Seller ID)."},
                {"Field": "followers", "Type": "Integer", "Description": "Total pengikut toko."},
                {"Field": "item_count", "Type": "Integer", "Description": "Jumlah total SKU/produk dalam toko."},
                {"Field": "rating_star", "Type": "Float", "Description": "Rating rata-rata toko dari pembeli."},
                {"Field": "response_rate", "Type": "Percentage", "Description": "Persentase kecepatan seller membalas chat."},
            ]
            st.table(meta_sh_p)

        with st.expander("📦 Product & Sales Metrics", expanded=False):
            meta_sh_v = [
                {"Field": "caption", "Type": "String", "Description": "Nama lengkap produk yang tertera di katalog."},
                {"Field": "price", "Type": "IDR (Float)", "Description": "Harga produk (Dikonversi dari satuan internal Shopee)."},
                {"Field": "sold", "Type": "Integer", "Description": "Total unit yang telah terjual (Historical Sold)."},
                {"Field": "stock", "Type": "Integer", "Description": "Jumlah stok yang tersedia untuk dipesan."},
                {"Field": "likes", "Type": "Integer", "Description": "Jumlah user yang memfavoritkan produk ini."},
                {"Field": "url", "Type": "URL", "Description": "Direct link menuju halaman produk Shopee."},
                {"Field": "date", "Type": "Timestamp", "Description": "Waktu pengambilan data harga dan stok."},
            ]
            st.table(meta_sh_v)

        with st.expander("🛠️ Technical Data Audit", expanded=False):
            tech_meta = [
                {"Field": "url", "Type": "URL", "Description": "Link langsung ke halaman produk Shopee."},
                {"Field": "date", "Type": "Timestamp", "Description": "Waktu pengambilan data harga & stok."},
                {"Field": "username", "Type": "String", "Description": "ID unik penjual untuk referensi API."},
            ]
            st.table(tech_meta)

        st.info("💡 **Tips:** Data harga diambil secara real-time. Jika ada diskon kilat (Flash Sale), harga yang tercatat adalah harga saat scraping dilakukan.")