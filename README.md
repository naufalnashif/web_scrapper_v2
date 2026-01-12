---
title: Web Scrapper Specialist
emoji: 🚀
colorFrom: blue
colorTo: red
sdk: streamlit
sdk_version: 1.52.2
app_file: app.py
pinned: false
---


# 🚀 Multi-Platform Social & E-Commerce Intelligence Dashboard

Platform *Data Intelligence* terintegrasi yang dirancang untuk melakukan ekstraksi, pemrosesan, dan visualisasi data secara *real-time* dari **Instagram**, **TikTok**, dan **Shopee**. Aplikasi ini menyediakan solusi otomatis untuk riset pasar, pemantauan kompetitor, dan analisis performa produk dalam satu dashboard interaktif.

---

## 📺 Demo & Tutorial
Klik gambar di bawah ini untuk melihat demonstrasi cara penggunaan alat ini di YouTube:

[![Tutorial Demo Scraper](assets/image/yutub-demo.png)](https://youtu.be/qUwAoj7KjAQ)

---

## ✨ Fitur Per Platform

### 📸 Instagram Analytics
* **Profile Insights**: Ekstraksi jumlah pengikut, mengikuti, jumlah postingan, dan biografi akun.
* **Content Performance**: Analisis metrik interaksi pada postingan terbaru.
* **Engagement Analysis**: Perhitungan otomatis *Engagement Rate* (ER) berbasis performa konten terhadap total pengikut.

### 🎵 TikTok Analytics
* **Account Intelligence**: Monitoring statistik profil (followers, likes, video count).
* **Video Content Tracking**: Pengambilan data caption, jumlah putar (views), dan interaksi pada video terbaru.
* **Trend Analysis**: Visualisasi distribusi performa konten untuk mengidentifikasi video yang viral.

### 🛍️ Shopee Analytics
* **Shop Performance**: Ekstraksi rating toko, total pengikut, dan performa respon chat.
* **Product Catalog Analysis**: Pengambilan data daftar produk mencakup harga SKU, jumlah stok, dan total unit terjual secara historis.
* **Sales Visualization**: Scatter plot untuk menganalisis korelasi antara popularitas (likes) dengan angka penjualan (sold).

---

## 📖 Panduan Pengguna

### 1. Instalasi dengan Docker (Rekomendasi)

```bash
# 1. Build image aplikasi
docker build -t web-scraper-app .

# 2. Jalankan container
# Memetakan port 8501 lokal ke port 7860 container
docker run -p 8501:7860 --name running-scraper web-scraper-app   

```
Akses melalui browser di: 
```
http://localhost:8501
```

Beberapa perintah penting untuk mengelola container Anda:
- Melihat log proses scraping:

```Bash
docker logs -f running-scraper
```

- Menghentikan aplikasi:
```Bash
docker stop running-scraper
```

- Menghapus container (setelah selesai digunakan):
```Bash
docker rm -f running-scraper
```

### 2. Kloning Repositori & Instalasi Manual
Buka terminal dan jalankan perintah berikut:
```bash
git clone [https://github.com/naufalnashif/web_scrapper.git](https://github.com/naufalnashif/web_scrapper.git)
cd web_scrapper
```

#### Buat virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # Untuk Windows: .venv\Scripts\activate
```

#### Install dependensi
```bash
pip install -r requirements.txt
```

#### Jalankan aplikasi
```bash
streamlit run app.py
```

### 2. Cara Penggunaan
1. Pilih Platform: Gunakan dropdown pada sidebar untuk memilih antara Instagram, TikTok, atau Shopee.

2. Input Target: Masukkan username (IG/TikTok) atau URL Toko/Produk (Shopee). Anda dapat memasukkan banyak target sekaligus menggunakan pemisah koma.

3. Eksekusi: Klik tombol "Start Scraping". Pantau progres pada tab Logs.

4. Visualisasi: Lihat hasil analisis pada tab Dashboard yang akan terisi secara otomatis setelah proses selesai.


### 🛠️ Teknologi Utama
- Interface: Streamlit (Framework dashboard berbasis web).
- Networking: Httpx (Library HTTP client asinkron untuk performa tinggi).
- Data Engine: Pandas (Pemrosesan dan transformasi data tabel).
- Visualization: Plotly (Pembuatan grafik interaktif dan responsif).
- Environment: Docker (Untuk standarisasi deployment).


### 📥 Input & 📤 Output
Input Parameter
- Instagram/TikTok: Username akun (Contoh: brand_account).
- Shopee: URL Toko (Contoh: https://shopee.co.id/shop_name) atau URL Produk spesifik.
- Global Filters: Batasan jumlah postingan (Max Posts) dan rentang tanggal (Since Date).

Output Data
- Data Profil: Informasi metadata akun/toko.
- Data Post/Produk: Detail metrik setiap konten atau item produk.
- Exportable Files: Laporan dalam format Excel (XLSX), CSV, dan JSON.

### 📦 Dependensi
Daftar library utama (tercantum dalam requirements.txt):
- `streamlit`
- `pandas`
- `httpx`
- `plotly`
- `xlsxwriter`

### 🏆 Keunggulan Sistem
1. Lightweight & Fast: Tidak menggunakan browser automation (Selenium/Playwright) sehingga menghemat penggunaan CPU dan RAM.
2. Universal Dashboard: Menyajikan data dari berbagai platform dalam format visual yang seragam dan mudah dipahami.
3. Clean Architecture: Pemisahan antara logika scraper engine dan UI dashboard memudahkan skalabilitas di masa depan.
4. Ready for Enterprise: Dilengkapi dengan penanganan error yang tangguh dan proteksi data untuk memastikan dashboard tetap stabil meskipun terdapat kegagalan koneksi.

Developed for High-Precision Data Extraction.



## 🛠️ Strategi Teknis & Spesialisasi Scraping
*Bagian ini menjelaskan pendekatan profesional dalam menangani tantangan teknis pada platform media sosial dan e-commerce.*

### 1. Simulating Real Mobile Sessions
Untuk melewati deteksi bot berbasis web standar, sistem ini dirancang untuk meniru perilaku aplikasi mobile asli dengan:
* **Custom Headers Extraction**: Menggunakan header spesifik aplikasi seperti `X-Shopee-Language`, `X-Requested-With: com.shopee.id`, dan `User-Agent` dari perangkat mobile populer (iOS/Android).
* **Protocol Emulation**: Menggunakan HTTP/2 atau HTTP/3 (jika tersedia) untuk mencocokkan pola lalu lintas data yang dihasilkan oleh library *networking* aplikasi mobile asli.

### 2. Rotating Device Fingerprints
Sistem meminimalisir risiko pemblokiran akun/IP dengan teknik rotasi sidik jari perangkat:
* **Canvas & WebGL Randomization**: Memanipulasi nilai render grafis di tingkat browser untuk mencegah pelacakan identitas perangkat yang unik.
* **Header Jittering**: Merotasi urutan header dan nilai `Accept-Language` serta `Sec-CH-UA` di setiap sesi request agar tidak membentuk pola yang statis.

### 3. Avoiding Rate Limits
Strategi manajemen ambang batas permintaan (request) dilakukan melalui:
* **Exponential Backoff**: Jika server merespon dengan status `429 (Too Many Requests)`, sistem akan berhenti sejenak dan melipatgandakan waktu tunggu sebelum mencoba kembali.
* **Randomized Jitter**: Menambahkan jeda waktu acak (misal 1-5 detik) di antara setiap request untuk meniru ritme navigasi manusia yang tidak teratur.
* **Distributed Proxies**: Integrasi dengan layanan *Residential Proxy* yang merotasi alamat IP di setiap request.

### 4. Token Refresh Mechanism
Untuk menjaga kontinuitas akses tanpa intervensi manual:
* **Session Interception**: Sistem secara otomatis memantau masa berlaku token (JWT/Cookie). Jika terdeteksi kedaluwarsa (status `401` atau `403`), sistem akan memicu fungsi *Handshake* ulang untuk mendapatkan *Guest Token* atau *Session ID* baru melalui endpoint otentikasi publik.

### 5. Solving Captcha
Penanganan tantangan visual (Captcha) dilakukan dengan pendekatan bertingkat:
* **Prevention First**: Menggunakan teknik *Stealth Scraping* agar Captcha tidak muncul sejak awal.
* **API Integration**: Jika Captcha muncul, sistem disiapkan untuk terintegrasi dengan layanan *Third-party Solver* seperti 2Captcha atau CapSolver melalui middleware API untuk penyelesaian secara otomatis.

### 6. Mimicking Touch Events & App-like Behaviour
Untuk platform yang menggunakan sistem keamanan berbasis perilaku (*Behavioral Analysis*):
* **Human-like Interaction**: Menggunakan library seperti *Playwright* atau *Puppeteer Stealth* untuk mensimulasikan gerakan kursor yang tidak linear, durasi *scroll* yang bervariasi, dan *click events* pada koordinat elemen yang acak, meniru interaksi sentuhan pada layar smartphone.

---
