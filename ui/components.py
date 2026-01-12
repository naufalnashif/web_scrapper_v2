import streamlit as st

def render_header():
    st.markdown("""
        <div style="background-color:#004A99;padding:20px;border-radius:10px;margin-bottom:25px">
            <h1 style="color:white;text-align:center;margin:0;">🚀 Scraper Engine v2.0</h1>
            <p style="color:white;text-align:center;opacity:0.8;">High-Performance Data Extraction Specialist Tool</p>
        </div>
    """, unsafe_allow_html=True)


def render_terminal_logs(logs):
    st.markdown("### 🖥️ System Activity")
    
    if not logs:
        st.info("Waiting for action...")
    else:
        # Menambahkan nomor baris dan menggabungkannya menjadi satu string
        log_text = ""
        for i, entry in enumerate(logs, 1):
            log_text += f"{i:02d}. {entry}\n"
        
        # Menggunakan widget standar Streamlit
        st.code(log_text, language="bash")

def render_documentation():
    st.title("📖 Dokumentasi & Panduan Pengguna")
    st.markdown("""
    Selamat datang di **Paragon Scraper Specialist**. Platform ini dirancang untuk memudahkan pengambilan data publik dari media sosial dan e-commerce secara efisien dan terstruktur.
    """)

    # --- BAGIAN 1: ALUR KERJA ---
    st.subheader("🚀 Cara Penggunaan")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**1. Konfigurasi Sidebar**")
        st.markdown("Pilih platform (IG/TikTok/Shopee) dan masukkan target (username atau ID produk).")
        
    with col2:
        st.warning("**2. Proses Scraping**")
        st.markdown("Klik 'Start Scraping'. Engine akan memproses data sesuai antrean yang Anda masukkan.")
        
    with col3:
        st.success("**3. Analisis & Ekspor**")
        st.markdown("Lihat visualisasi di Dashboard dan unduh data dalam format pilihan Anda.")

    st.divider()

    # --- BAGIAN 2: FITUR UTAMA ---
    st.subheader("🛠️ Fitur Unggulan")
    
    tab1, tab2, tab3 = st.tabs(["📥 Metode Input", "📊 Visualisasi", "💾 Ekspor Data"])
    
    with tab1:
        st.markdown("""
        * **Manual Text:** Ketik username langsung (pisahkan dengan koma atau baris baru).
        * **Batch Upload:** Mendukung file `.csv`, `.txt`, dan `.xlsx` untuk memproses ratusan akun sekaligus.
        """)
        
    with tab2:
        st.markdown("""
        * **Overview Dashboard:** Perbandingan jumlah pengikut (Followers/Fans) antar akun.
        * **Post Analysis:** Grafik frekuensi postingan untuk melihat keaktifan kompetitor.
        * **Detail Table:** Tabel interaktif yang bisa difilter dan dicari (searchable).
        """)
        
    with tab3:
        st.markdown("Simpan hasil riset Anda dalam berbagai format standar industri:")
        st.code("CSV, Excel (XLSX), JSON, dan Plain Text (TXT)")

    st.divider()

    # --- BAGIAN 3: FAQ ---
    st.subheader("❓ FAQ (Pertanyaan Sering Diajukan)")
    
    with st.expander("Berapa batas maksimal akun yang bisa di-scrape sekaligus?"):
        st.write("""
        Secara teknis tidak ada batas, namun untuk menghindari pemblokiran (IP Ban) dari platform, 
        disarankan untuk tidak melakukan scraping lebih dari **50 akun** secara bersamaan dalam satu sesi.
        """)

    with st.expander("Mengapa grafik 'Post Frequency' terkadang kosong?"):
        st.write("""
        Hal ini terjadi jika:
        1. Akun yang di-scrape bersifat private.
        2. Platform (seperti TikTok atau Shopee) sedang membatasi akses metadata tanggal postingan.
        3. Tidak ada data postingan yang ditemukan pada rentang tanggal yang dipilih.
        """)

    with st.expander("Apa perbedaan Mode Direct dan Mode API?"):
        st.write("""
        * **Direct:** Menggunakan engine langsung dari aplikasi ini. Cocok untuk penggunaan personal.
        * **API:** Menghubungkan aplikasi ke server backend terpisah (Flask). Cocok untuk skalabilitas tinggi dan integrasi antar sistem.
        """)

    with st.expander("Apakah aplikasi ini menyimpan data saya?"):
        st.write("""
        Tidak. Data hanya disimpan di **Session State** browser Anda. Jika Anda me-refresh halaman atau menutup tab tanpa mengunduh data, maka data hasil scraping akan hilang.
        """)

    # --- FOOTER NOTE ---
    st.caption("---")
    st.error("⚠️ **Peringatan Keamanan:** Gunakan alat ini secara bijak dan patuhi syarat & ketentuan dari masing-masing platform. Kami tidak bertanggung jawab atas penyalahgunaan akun.")