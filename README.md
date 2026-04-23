# 🚲 Bike Sharing Analytics Dashboard

Dashboard interaktif ini dibuat menggunakan **Streamlit** untuk menganalisis dan memvisualisasikan tren penyewaan sepeda berdasarkan dataset historis (2011-2012). Analisis berfokus pada pengaruh cuaca, musim, pola harian, dan komposisi tipe pengguna (Casual vs Registered).

## ✨ Fitur Utama
* **Filter Dinamis:** Pengguna dapat memfilter data berdasarkan rentang tanggal dan musim tertentu melalui *sidebar*.
* **Key Performance Indicators (KPI):** Ringkasan metrik utama seperti total penyewaan, rata-rata harian, serta jumlah penyewa *Casual* dan *Registered*.
* **Visualisasi Pengaruh Cuaca:** Grafik regresi yang menunjukkan korelasi antara suhu (temperatur) dan kelembapan udara terhadap minat menyewa sepeda.
* **Analisis Temporal:** Distribusi penyewaan berdasarkan hari dalam seminggu dan perbandingan musim.
* **Perbandingan Hari:** *Stacked bar chart* yang menunjukkan perbedaan mencolok komposisi tipe penyewa pada hari kerja (*working day*) versus akhir pekan/hari libur.
* **Insight Otomatis:** Setiap visualisasi dilengkapi dengan kotak *insight* (kesimpulan) interaktif untuk memudahkan pemahaman bisnis.

---

## 📂 Struktur Direktori

Pastikan struktur direktori di komputer Anda seperti berikut sebelum menjalankan aplikasi:

```text
📁 submission/
├── 📁 dashboard/
├   |── dashboard.py           <-- Script utama aplikasi Streamlit
├   ├── main_data_day.csv      <-- File dataset yang telah dibersihkan
│   ├── main_data_hour.csv     <-- File dataset yang telah dibersihkan
|    
├── 📁 data/
│   ├── day.csv            <-- Raw data harian
│   └── hour.csv           <-- Raw data per jam
├── notebook.ipynb         <-- File Jupyter Notebook proses analisis & pembersihan data
├── README.md              <-- Panduan penggunaan 
├── requirements.txt       <-- Daftar library Python yang dibutuhkan
└── url.txt                <-- Tautan ke aplikasi yang sudah di-deploy (Streamlit Cloud)
```

---

## 🚀 Cara Menjalankan Aplikasi secara Lokal (Localhost)

Ikuti langkah-langkah berikut untuk menjalankan *dashboard* di komputer Anda:

### 1. Prasyarat
Pastikan Anda sudah menginstal Python (disarankan versi 3.9 - 3.11).

### 2. Kloning Repositori (Opsional)
Jika Anda belum mengunduh kode ini, lakukan kloning (clone) repositori:
```bash
git clone https://github.com/dawooodd/Dashboard.git
cd Dashboard
```

### 3. Setup Virtual Environment (Disarankan)
Sangat disarankan menggunakan *virtual environment* agar pustaka (*library*) proyek ini tidak bentrok dengan proyek yang lain.

**Di Windows:**
```bash
python -m venv env
env\Scripts\activate
```

**Di macOS / Linux:**
```bash
python3 -m venv env
source env/bin/activate
```

### 4. Instalasi Library (Requirements)
Instal semua pustaka yang dibutuhkan menggunakan `pip`:
```bash
pip install -r requirements.txt
```


### 5. Jalankan Aplikasi
Jalankan Streamlit dengan menunjuk ke file `dashboard.py` yang ada di dalam folder `dashboard`:
```bash
streamlit run dashboard/dashboard.py
```

Setelah perintah ini dijalankan, *browser* utama akan terbuka secara otomatis dan menampilkan *dashboard* di alamat `http://localhost:8501`.

---

## ☁️ Deployment (Streamlit Cloud)
Jika ingin melihat aplikasi ini secara *online*, silakan kunjungi tautan yang terdapat di dalam file `url.txt`. Aplikasi ini dapat di-deploy secara gratis menggunakan layanan Streamlit Community Cloud dengan menautkan repositori GitHub.

---
**Copyright (c) Muchammad Nasich 2026**
```
# Dashboard