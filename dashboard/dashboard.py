import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np
import os

# Konfigurasi Halaman
st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚲", layout="wide")

# ── CSS Kustom untuk Insight Box ─────────────────────────────────────────────
st.markdown("""
<style>
.insight-box {
    background: #f8f9fb;
    border-left: 5px solid #4C9BE8;
    border-radius: 8px;
    padding: 14px 18px;
    margin-top: 10px;
    margin-bottom: 15px;
    font-size: 0.95rem;
    line-height: 1.6;
    color: #1e1e2e;
}
.insight-box.green  { border-color: #6ECB8A; }
.insight-box.orange { border-color: #F4845F; }
.insight-box.yellow { border-color: #F9C846; }
.insight-box.purple { border-color: #9b5de5; }
.insight-label {
    font-weight: 700;
    font-size: 1rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 6px;
    color: #333;
}
.insight-content b {
    color: #1A6BB5;
}
</style>
""", unsafe_allow_html=True)

def insight(icon, label, text, color="blue"):
    st.markdown(f"""
    <div class="insight-box {color}">
        <div class="insight-label">{icon} {label}</div>
        <div class="insight-content">{text}</div>
    </div>""", unsafe_allow_html=True)

# ── Memuat Data & Preprocessing ───────────────────────────────────────────────
@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load dataset
    df_day = pd.read_csv(os.path.join(current_dir, "main_data_day.csv"), parse_dates=["dteday"])
    df_hour = pd.read_csv(os.path.join(current_dir, "main_data_hour.csv"), parse_dates=["dteday"])
    
    # Mapping Label untuk Visualisasi
    weather_map = {1: "1: Cerah", 2: "2: Mendung/Berkabut", 3: "3: Hujan/Salju Ringan", 4: "4: Cuaca Ekstrem"}
    season_map = {1: "Musim Semi", 2: "Musim Panas", 3: "Musim Gugur", 4: "Musim Dingin"}
    
    df_hour['weathersit_label'] = df_hour['weathersit'].map(weather_map)
    df_hour['workingday_label'] = df_hour['workingday'].map({0: "Akhir Pekan/Libur", 1: "Hari Kerja"})
    df_hour['season_label'] = df_hour['season'].map(season_map)
    
    df_day['yr_label'] = df_day['yr'].map({0: "2011", 1: "2012"})
    df_day['season_label'] = df_day['season'].map(season_map)
    
    return df_day, df_hour

df_day, df_hour = load_data()

# ── Sidebar & Filter Interaktif ───────────────────────────────────────────────
st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Left_side_of_Flying_Pigeon.jpg/320px-Left_side_of_Flying_Pigeon.jpg",
    use_column_width=True,  
)
st.sidebar.title("🚲 Kontrol Data")
st.sidebar.markdown("---")

# Filter Musim
season_options = ["Semua"] + sorted(df_day["season_label"].unique().tolist())
sel_season = st.sidebar.selectbox("Pilih Musim", season_options)

# Filter Tanggal
date_min  = df_day["dteday"].min().date()
date_max  = df_day["dteday"].max().date()
sel_dates = st.sidebar.date_input("Rentang Tanggal", value=(date_min, date_max),
                                min_value=date_min, max_value=date_max)

# Fungsi Aplikasi Filter ke Dataframe
def apply_filters(df):
    d = df.copy()
    if sel_season != "Semua": 
        d = d[d["season_label"] == sel_season]
    if len(sel_dates) == 2:
        d = d[(d["dteday"].dt.date >= sel_dates[0]) & (d["dteday"].dt.date <= sel_dates[1])]
    return d

# Terapkan filter ke KEDUA dataframe
day_f = apply_filters(df_day)
hour_f = apply_filters(df_hour)

# ── Header & KPI Cards ────────────────────────────────────────────────────────
st.title("🚲 Bikeshare Analytics Dashboard")
st.markdown("Analisis Operasional, Tren Pengguna, dan Strategi Pertumbuhan (2011–2012)")
st.markdown("---")

# Cek apakah filter menghasilkan data kosong
if day_f.empty or hour_f.empty:
    st.warning("⚠️ Tidak ada data yang ditemukan untuk filter yang dipilih. Silakan sesuaikan musim atau rentang tanggal.")
    st.stop() # Hentikan eksekusi kode di bawahnya agar grafik tidak error

total_rides  = int(day_f["cnt"].sum())
total_casual = int(day_f["casual"].sum())
total_reg    = int(day_f["registered"].sum())

k1, k2, k3 = st.columns(3)
k1.metric("🚲 Total Penyewaan (Terfilter)", f"{total_rides:,}")
k2.metric("🚶 Pengguna Kasual", f"{total_casual:,}")
k3.metric("🎫 Pengguna Terdaftar", f"{total_reg:,}")
st.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
# PERTANYAAN 1: PENGARUH CUACA EKSTREM
# ════════════════════════════════════════════════════════════════════════════
st.subheader("1. Pengaruh Cuaca terhadap Penyewa Kasual")
c1, c2 = st.columns([1.2, 1])

with c1:
    fig, ax = plt.subplots(figsize=(8, 5))
    # PERHATIKAN: Menggunakan hour_f (data yang sudah difilter)
    sns.barplot(x='weathersit_label', y='casual', data=hour_f, estimator=sum, errorbar=None, palette='Blues_r', ax=ax)
    ax.set_title('Total Penyewaan Pengguna Kasual Berdasarkan Cuaca', fontsize=13)
    ax.set_xlabel('Kondisi Cuaca')
    ax.set_ylabel('Total Penyewaan')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    st.pyplot(fig); plt.close(fig)

with c2:
    insight("📉", "Insight Visual", "Grafik bar menunjukkan penurunan tajam. Cuaca cerah mendominasi secara absolut, sementara cuaca ekstrem nyaris tidak terlihat di grafik.")
    

st.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
# PERTANYAAN 2: POLA JAM SIBUK
# ════════════════════════════════════════════════════════════════════════════
st.subheader("2. Pola Lonjakan Penyewaan pada Jam Sibuk (Hari Kerja)")
c3, c4 = st.columns([1.2, 1])

with c3:
    fig, ax = plt.subplots(figsize=(8, 5))
    # Filter tambahan untuk hari kerja saja
    df_work = hour_f[hour_f['workingday'] == 1]
    
    if not df_work.empty:
        sns.lineplot(x='hr', y='cnt', data=df_work, estimator='mean', marker='o', color='#F4845F', ax=ax)
        ax.axvline(x=8, color='red', linestyle='--', label='08:00 (Pagi)')
        ax.axvline(x=17, color='green', linestyle='--', label='17:00 (Sore)')
        ax.set_xticks(range(0, 24))
        ax.set_title('Rata-rata Penyewaan per Jam pada Hari Kerja', fontsize=13)
        ax.set_xlabel('Jam (0-23)')
        ax.set_ylabel('Rata-rata Total Penyewaan')
        ax.legend()
        st.pyplot(fig)
    else:
        st.info("Tidak ada data hari kerja pada rentang filter ini.")
    plt.close(fig)

with c4:
    insight("📈", "Insight Visual", "Kurva membentuk distribusi Bimodal yang tajam. Terdapat dua puncak yang terpusat di jam komuter pagi (08.00) dan sore (17.00).", color="orange")
    

st.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
# PERTANYAAN 3: JADWAL MAINTENANCE
# ════════════════════════════════════════════════════════════════════════════
st.subheader("3. Waktu Paling Optimal untuk Maintenance Sepeda")
c5, c6 = st.columns([1.2, 1])

with c5:
    fig, ax = plt.subplots(figsize=(8, 5))
    df_early = hour_f[hour_f['hr'].isin([0, 1, 2, 3, 4, 5, 6])]
    sns.barplot(x='hr', y='cnt', data=df_early, estimator='mean', palette='magma', ax=ax)
    ax.set_title('Rata-rata Penyewaan Dini Hari', fontsize=13)
    ax.set_xlabel('Jam Dini Hari')
    ax.set_ylabel('Rata-rata Penyewaan')
    st.pyplot(fig); plt.close(fig)

with c6:
    insight("🛠️", "Insight Visual", "Terlihat penurunan aktivitas hingga membentuk titik terendah antara pukul 02:00 hingga 05:00 pagi.", color="purple")

st.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
# PERTANYAAN 4: HARI KERJA VS AKHIR PEKAN
# ════════════════════════════════════════════════════════════════════════════
st.subheader("4. Perbandingan Pola Hari Kerja vs Akhir Pekan")
c7, c8 = st.columns([1.2, 1])

with c7:
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.lineplot(x='hr', y='cnt', hue='workingday_label', data=hour_f, estimator='mean', palette='Set1', linewidth=2.5, ax=ax)
    ax.set_xticks(range(0, 24))
    ax.set_title('Pola Harian: Hari Kerja vs Libur', fontsize=13)
    ax.set_xlabel('Jam (0-23)')
    ax.set_ylabel('Rata-rata Penyewaan')
    ax.legend(title='Kategori Hari')
    st.pyplot(fig); plt.close(fig)

with c8:
    insight("⚖️", "Insight Visual", "Garis hari kerja memiliki dua lonjakan pagi/sore. Sebaliknya, garis akhir pekan membentuk satu bukit yang puncaknya terbentang datar di siang hari.", color="yellow")
    

st.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
# PERTANYAAN 5: TREN YoY (2011 VS 2012)
# ════════════════════════════════════════════════════════════════════════════
st.subheader("5. Tren Pertumbuhan Bulanan")
c9, c10 = st.columns([1.2, 1])

with c9:
    fig, ax = plt.subplots(figsize=(8, 5))
    # Menggunakan day_f agar bisa difilter
    sns.barplot(x='mnth', y='cnt', hue='yr_label', data=day_f, estimator=sum, palette='viridis', ax=ax)
    ax.set_title('Total Penyewaan Sepeda per Bulan', fontsize=13)
    ax.set_xlabel('Bulan (1 - 12)')
    ax.set_ylabel('Total Penyewaan')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    st.pyplot(fig); plt.close(fig)

with c10:
    insight("🚀", "Insight Visual", "Pertumbuhan terjadi konsisten. Setiap batang di tahun 2012 (jika tidak difilter) selalu mengungguli bulan yang sama di 2011.", color="green")


st.caption("Bikeshare Analytical Dashboard | Dikembangkan oleh Dawood")
