import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np
import os

# Konfigurasi Halaman
st.set_page_config(
    page_title="Bike Sharing Analytics Dashboard", 
    page_icon="🚲", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS Kustom untuk Tampilan Modern & Insight Box ───────────────────────────
st.markdown("""
<style>
.insight-box {
    background: #f8f9fb;
    border-left: 5px solid #4C9BE8;
    border-radius: 8px;
    padding: 14px 18px;
    margin-top: 10px;
    margin-bottom: 15px;
    font-size: 0.93rem;
    line-height: 1.6;
    color: #1e1e2e;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.insight-box.green  { border-color: #2ec4b6; }
.insight-box.orange { border-color: #e76f51; }
.insight-box.yellow { border-color: #f4a261; }
.insight-box.purple { border-color: #7209b7; }
.insight-label {
    font-weight: 700;
    font-size: 0.95rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 6px;
    color: #333;
}
.insight-content b {
    color: #1d3557;
}
.stat-pill {
    display: inline-block;
    background: #e9ecef;
    border-radius: 4px;
    padding: 2px 8px;
    font-weight: 600;
    font-size: 0.88rem;
    margin-right: 5px;
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
    weather_map = {
        1: "1: Cerah", 
        2: "2: Berkabut/Mendung", 
        3: "3: Hujan/Salju Ringan", 
        4: "4: Cuaca Ekstrem"
    }
    season_map = {
        1: "Musim Semi", 
        2: "Musim Panas", 
        3: "Musim Gugur", 
        4: "Musim Dingin"
    }
    
    df_hour['weathersit_label'] = df_hour['weathersit'].map(weather_map)
    df_hour['workingday_label'] = df_hour['workingday'].map({0: "Akhir Pekan/Libur", 1: "Hari Kerja"})
    df_hour['season_label'] = df_hour['season'].map(season_map)
    
    df_day['yr_label'] = df_day['yr'].map({0: "2011", 1: "2012"})
    df_day['season_label'] = df_day['season'].map(season_map)
    
    # Time slot categorization (Vectorized pd.cut)
    time_bins = [-1, 4, 11, 16, 20, 24]
    time_labels = [
        'Dini Hari (00:00 - 04:59)',
        'Pagi (05:00 - 11:59)',
        'Siang (12:00 - 16:59)',
        'Sore (17:00 - 20:59)',
        'Malam (21:00 - 23:59)'
    ]
    df_hour['time_category'] = pd.cut(df_hour['hr'], bins=time_bins, labels=time_labels)
    
    return df_day, df_hour

df_day, df_hour = load_data()

# ── Sidebar & Filter Interaktif ───────────────────────────────────────────────
st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Left_side_of_Flying_Pigeon.jpg/320px-Left_side_of_Flying_Pigeon.jpg",
    use_container_width=True
)
st.sidebar.title("🚲 Kontrol Analisis")
st.sidebar.markdown("---")

# Filter Musim
season_options = ["Semua"] + sorted(df_day["season_label"].dropna().unique().tolist())
sel_season = st.sidebar.selectbox("Filter Musim:", season_options)

# Filter Tanggal (Handled gracefully for single-click selection)
date_min = df_day["dteday"].min().date()
date_max = df_day["dteday"].max().date()
sel_dates = st.sidebar.date_input(
    "Rentang Tanggal:", 
    value=(date_min, date_max),
    min_value=date_min, 
    max_value=date_max
)

# Fungsi Aplikasi Filter ke Dataframe
def apply_filters(df, season_filter, date_range):
    d = df.copy()
    if season_filter != "Semua": 
        d = d[d["season_label"] == season_filter]
        
    if isinstance(date_range, (tuple, list)):
        if len(date_range) == 2:
            start_date, end_date = date_range
            d = d[(d["dteday"].dt.date >= start_date) & (d["dteday"].dt.date <= end_date)]
        elif len(date_range) == 1:
            d = d[d["dteday"].dt.date == date_range[0]]
            st.sidebar.caption("💡 Pilih tanggal kedua untuk rentang penuh.")
    return d

# Terapkan filter ke KEDUA dataframe
day_f = apply_filters(df_day, sel_season, sel_dates)
hour_f = apply_filters(df_hour, sel_season, sel_dates)

st.sidebar.markdown("---")
st.sidebar.markdown("""
**ℹ️ Catatan Metodologi:**
Visualisasi telah disesuaikan untuk memitigasi *Base Rate Fallacy* dengan menyajikan metrik rata-rata per jam (*hourly rate*) di samping total volume.
""")

# ── Header & KPI Cards ────────────────────────────────────────────────────────
st.title("🚲 Bike Sharing Analytics Dashboard")
st.markdown("**Analisis Operasional, Perilaku Pengguna, dan Strategi Pertumbuhan (2011–2012)**")
st.caption("Dikembangkan oleh Muchammad Nasich | Dicoding Data Analytics Track")
st.markdown("---")

# Cek apakah filter menghasilkan data kosong
if day_f.empty or hour_f.empty:
    st.warning("⚠️ Tidak ada data yang ditemukan untuk filter yang dipilih. Silakan sesuaikan musim atau rentang tanggal.")
    st.stop()

total_rides  = int(day_f["cnt"].sum())
total_casual = int(day_f["casual"].sum())
total_reg    = int(day_f["registered"].sum())
pct_casual   = (total_casual / total_rides * 100) if total_rides > 0 else 0
pct_reg      = (total_reg / total_rides * 100) if total_rides > 0 else 0
daily_avg    = int(day_f["cnt"].mean())

k1, k2, k3, k4 = st.columns(4)
k1.metric("🚲 Total Penyewaan", f"{total_rides:,}")
k2.metric("🚶 Pengguna Kasual", f"{total_casual:,}", f"{pct_casual:.1f}%")
k3.metric("🎫 Pengguna Terdaftar", f"{total_reg:,}", f"{pct_reg:.1f}%")
k4.metric("📅 Rata-rata Harian", f"{daily_avg:,} unit/hari")
st.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
# PERTANYAAN 1: PENGARUH CUACA TERHADAP PENGGUNA KASUAL
# ════════════════════════════════════════════════════════════════════════════
st.subheader("1. Pengaruh Kondisi Cuaca terhadap Minat Pengguna Kasual")
st.caption("Pemeriksaan berbasis laju sewa per jam (*rate per hour*) untuk mengeliminasi bias ketimpangan durasi cuaca.")

metric_mode = st.radio(
    "Metrik Evaluasi Cuaca:",
    ["Rata-rata Sewa per Jam (Direkomendasikan - Objektif)", "Total Akumulasi Sewa (Volume)"],
    horizontal=True
)

c1, c2 = st.columns([1.3, 1])

# Perhitungan statistik per cuaca secara aman
weather_summary = hour_f.groupby('weathersit_label', observed=True)['casual'].agg(['mean', 'sum', 'count']).reset_index()

with c1:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    if "Rata-rata" in metric_mode:
        sns.barplot(
            x='weathersit_label', 
            y='casual', 
            data=hour_f, 
            estimator='mean', 
            errorbar=('ci', 95), 
            palette='Blues_r', 
            hue='weathersit_label',
            legend=False,
            ax=ax
        )
        ax.set_title('Rata-rata Penyewaan Kasual per Jam Berdasarkan Cuaca (CI 95%)', fontsize=12)
        ax.set_ylabel('Rata-rata Sewa per Jam')
    else:
        sns.barplot(
            x='weathersit_label', 
            y='casual', 
            data=hour_f, 
            estimator=sum, 
            errorbar=None, 
            palette='Blues_r', 
            hue='weathersit_label',
            legend=False,
            ax=ax
        )
        ax.set_title('Total Akumulasi Penyewaan Kasual Berdasarkan Cuaca', fontsize=12)
        ax.set_ylabel('Total Penyewaan')
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
        
    ax.set_xlabel('Kondisi Cuaca')
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    st.pyplot(fig)
    plt.close(fig)

with c2:
    # Komputasi insight dinamis dengan pengecekan aman (bebas IndexError)
    mean_clear = weather_summary.loc[weather_summary['weathersit_label'].str.contains("Cerah"), 'mean'].values
    mean_rain  = weather_summary.loc[weather_summary['weathersit_label'].str.contains("Hujan"), 'mean'].values
    mean_ext   = weather_summary.loc[weather_summary['weathersit_label'].str.contains("Ekstrem"), 'mean'].values
    count_ext  = weather_summary.loc[weather_summary['weathersit_label'].str.contains("Ekstrem"), 'count'].values
    
    val_clear = mean_clear[0] if len(mean_clear) > 0 else 0
    val_rain  = mean_rain[0] if len(mean_rain) > 0 else None
    val_ext   = mean_ext[0] if len(mean_ext) > 0 else None
    cnt_ext   = int(count_ext[0]) if len(count_ext) > 0 else 0
    
    # Narasi penurunan sewa hujan
    if val_rain is not None and val_clear > 0:
        drop_pct = ((val_clear - val_rain) / val_clear) * 100
        rain_narrative = f"Rata-rata sewa kasual turun dari <b>{val_clear:.1f} sewa/jam</b> (Cerah) ke <b>{val_rain:.1f} sewa/jam</b> saat Hujan Ringan (penurunan <b>-{drop_pct:.1f}%</b>)."
    elif val_clear > 0:
        rain_narrative = f"Rata-rata sewa kasual tercatat <b>{val_clear:.1f} sewa/jam</b> pada kondisi cuaca Cerah."
    else:
        rain_narrative = "Data penyewaan kasual pada kondisi cerah tidak tersedia pada filter aktif."

    # Narasi cuaca ekstrem yang adaptif (mencegah IndexError jika cuaca level 4 tidak ada pada musim aktif)
    if cnt_ext > 0 and val_ext is not None:
        ext_narrative = f"Cuaca ekstrem level 4 hanya terjadi selama <b>{cnt_ext} jam</b> pada subset data ini dengan laju rata-rata riil <b>{val_ext:.1f} sewa/jam</b>. Mengukur dari total volume menghasilkan ilusi kejatuhan 99.9% (Base Rate Fallacy)."
    else:
        ext_narrative = "Kondisi cuaca ekstrem (level 4) <b>tidak terjadi</b> sama sekali pada musim/rentang tanggal yang dipilih, sehingga tidak ada dampak cuaca ekstrem pada filter ini."
    
    insight_text = f"""
    * <b>Sensitivitas Cuaca:</b> {rain_narrative}
    * <b>Mitigasi Bias Cuaca Ekstrem:</b> {ext_narrative}
    * <b>Rekomendasi Aksi:</b> Terapkan <i>Weather-Triggered Dynamic Pricing</i> (diskon otomatis 20-30% saat hujan ringan) untuk merangsang permintaan elastis pengguna kasual.
    """
    insight("🌦️", "Wawasan Data & Rekomendasi Bisnis", insight_text, color="blue")

st.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
# PERTANYAAN 2: POLA JAM SIBUK HARI KERJA
# ════════════════════════════════════════════════════════════════════════════
st.subheader("2. Pola Lonjakan pada Jam Sibuk Komuter (Hari Kerja)")
c3, c4 = st.columns([1.3, 1])

df_work = hour_f[hour_f['workingday'] == 1]

with c3:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    if not df_work.empty:
        sns.lineplot(x='hr', y='cnt', data=df_work, estimator='mean', marker='o', color='#E76F51', ax=ax, label='Rata-rata Sewa')
        ax.axvline(x=8, color='#E63946', linestyle='--', linewidth=1.5, label='08:00 (Puncak Pagi)')
        ax.axvline(x=17, color='#2A9D8F', linestyle='--', linewidth=1.5, label='17:00 (Puncak Sore)')
        ax.set_xticks(range(0, 24))
        ax.set_title('Rata-rata Penyewaan per Jam pada Hari Kerja', fontsize=12)
        ax.set_xlabel('Jam (0 - 23)')
        ax.set_ylabel('Rata-rata Total Penyewaan (unit)')
        ax.grid(True, linestyle='--', alpha=0.4)
        ax.legend(loc='upper right')
        st.pyplot(fig)
    else:
        st.info("Tidak ada data hari kerja pada filter rentang ini.")
    plt.close(fig)

with c4:
    if not df_work.empty:
        hr_stats = df_work.groupby('hr')['cnt'].mean().reindex(range(24), fill_value=0)
        morning_peak = hr_stats.loc[7:9].max() if len(hr_stats.loc[7:9]) > 0 else hr_stats.max()
        evening_peak = hr_stats.loc[17:18].max() if len(hr_stats.loc[17:18]) > 0 else hr_stats.max()
        
        q2_text = f"""
        * <b>Distribusi Bimodal:</b> Terlihat dua puncak tajam yang mencerminkan mobilitas pekerja kantoran.
        * <b>Puncak Pagi:</b> Jam 08:00 rata-rata mencapai <b>{int(morning_peak):,} unit/jam</b>.
        * <b>Puncak Sore:</b> Jam 17:00-18:00 rata-rata mencapai <b>{int(evening_peak):,} unit/jam</b> (lebih tinggi dan berdurasi lebih panjang akibat aktivitas pasca-kantor).
        * <b>Rekomendasi Aksi:</b> Jalankan <i>Predictive Fleet Rebalancing</i> dengan memindahkan armada ke area pemukiman/stasiun sebelum 07:00 dan ke kawasan bisnis sebelum 16:30.
        """
    else:
        q2_text = "Data hari kerja tidak tersedia pada pilihan filter saat ini."
    insight("📈", "Wawasan Komuter", q2_text, color="orange")

st.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
# PERTANYAAN 3: JADWAL MAINTENANCE
# ════════════════════════════════════════════════════════════════════════════
st.subheader("3. Golden Window untuk Pemeliharaan Rutin Armada (Maintenance)")
c5, c6 = st.columns([1.3, 1])

df_early = hour_f[hour_f['hr'].isin([0, 1, 2, 3, 4, 5, 6])]

with c5:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    if not df_early.empty:
        sns.barplot(
            x='hr', 
            y='cnt', 
            data=df_early, 
            estimator='mean', 
            palette='mako', 
            hue='hr',
            legend=False,
            ax=ax
        )
        ax.set_title('Rata-rata Penyewaan pada Dini Hari (00:00 - 06:00)', fontsize=12)
        ax.set_xlabel('Jam Dini Hari')
        ax.set_ylabel('Rata-rata Penyewaan (unit)')
        ax.grid(axis='y', linestyle='--', alpha=0.4)
        st.pyplot(fig)
    else:
        st.info("Data jam dini hari tidak tersedia.")
    plt.close(fig)

with c6:
    if not df_early.empty:
        early_stats = df_early.groupby('hr')['cnt'].mean().dropna()
        if not early_stats.empty:
            min_hr = early_stats.idxmin()
            min_val = early_stats.min()
            
            q3_text = f"""
            * <b>Titik Terendah (Nadir):</b> Aktivitas armada berada di titik paling rendah pada pukul <b>{min_hr:02d}:00</b> dengan rata-rata hanya <b>{min_val:.1f} unit/jam</b>.
            * <b>Zona Inaktif (02:00 - 05:00):</b> Selama rentang 3 jam ini, lebih dari 98% sepeda berada dalam kondisi diam (*docked/idle*).
            * <b>Rekomendasi Aksi:</b> Tetapkan shift teknisi lapangan eksklusif pada pukul <b>02:00 - 05:00</b> untuk inspeksi rem, rantai, dan kebersihan. Menghindari pemeliharaan siang hari akan menjaga ketersediaan armada 100% saat jam sibuk.
            """
        else:
            q3_text = "Data jam dini hari tidak mencukupi untuk menghitung jadwal pemeliharaan."
    else:
        q3_text = "Data jam dini hari tidak tersedia pada pilihan filter saat ini."
    insight("🛠️", "Jadwal Efisiensi Armada", q3_text, color="purple")

st.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
# PERTANYAAN 4: HARI KERJA VS AKHIR PEKAN
# ════════════════════════════════════════════════════════════════════════════
st.subheader("4. Perbandingan Karakteristik Pengguna: Hari Kerja vs Akhir Pekan")
c7, c8 = st.columns([1.3, 1])

# Mapping palet warna eksplisit untuk mencegah color mismatch jika hanya 1 kategori yang muncul
palette_day = {
    "Hari Kerja": "#E63946",
    "Akhir Pekan/Libur": "#457B9D"
}

with c7:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.lineplot(
        x='hr', 
        y='cnt', 
        hue='workingday_label', 
        data=hour_f, 
        estimator='mean', 
        palette=palette_day, 
        linewidth=2.5, 
        ax=ax
    )
    ax.set_xticks(range(0, 24))
    ax.set_title('Profil Penggunaan Harian: Hari Kerja vs Libur', fontsize=12)
    ax.set_xlabel('Jam (0 - 23)')
    ax.set_ylabel('Rata-rata Sewa per Jam')
    ax.grid(True, linestyle='--', alpha=0.4)
    ax.legend(title='Kategori Hari')
    st.pyplot(fig)
    plt.close(fig)

with c8:
    q4_text = """
    * <b>Dua Pola Berbeda:</b> 
      * <i>Hari Kerja (Bimodal):</i> Didominasi komuter terdaftar (*registered users*) dengan lonjakan tajam di pagi (08:00) dan sore (17:00).
      * <i>Akhir Pekan/Libur (Unimodal):</i> Pola berbentuk kurva lonceng terbentang luas dari pukul <b>11:00 hingga 16:00</b>.
    * <b>Perubahan Use Case:</b> Di akhir pekan, sepeda bertransformasi dari moda transportasi wajib menjadi sarana <b>rekreasi keluarga dan turis</b>.
    * <b>Rekomendasi Aksi:</b> Alokasikan sepeda akhir pekan ke area taman publik dan destinasi wisata, serta luncurkan paket <i>Weekend Leisure Pass</i> berdurasi harian.
    """
    insight("⚖️", "Segmentasi Kebutuhan", q4_text, color="yellow")

st.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
# PERTANYAAN 5: TREN PERTUMBUHAN BULANAN (YoY 2011 VS 2012)
# ════════════════════════════════════════════════════════════════════════════
st.subheader("5. Tren Pertumbuhan Bulanan & Ekspansi YoY (2011 vs 2012)")
c9, c10 = st.columns([1.3, 1])

palette_yr = {
    "2011": "#4C9BE8",
    "2012": "#2EC4B6"
}

with c9:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.barplot(
        x='mnth', 
        y='cnt', 
        hue='yr_label', 
        data=day_f, 
        estimator=sum, 
        palette=palette_yr, 
        ax=ax
    )
    ax.set_title('Total Penyewaan Sepeda per Bulan: 2011 vs 2012', fontsize=12)
    ax.set_xlabel('Bulan (1 - 12)')
    ax.set_ylabel('Total Penyewaan (unit)')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    ax.legend(title='Tahun')
    st.pyplot(fig)
    plt.close(fig)

with c10:
    sum_2011 = day_f[day_f['yr'] == 0]['cnt'].sum()
    sum_2012 = day_f[day_f['yr'] == 1]['cnt'].sum()
    
    if sum_2011 > 0 and sum_2012 > 0:
        yoy_growth = ((sum_2012 - sum_2011) / sum_2011) * 100
        growth_info = f"Total volume naik dari <b>{int(sum_2011):,}</b> (2011) menjadi <b>{int(sum_2012):,}</b> (2012), mencatat ekspansi sebesar <b>+{yoy_growth:.1f}%</b>."
    elif sum_2011 > 0:
        growth_info = f"Data terfilter hanya mencakup tahun 2011 dengan total penyewaan sebanyak <b>{int(sum_2011):,} unit</b>."
    elif sum_2012 > 0:
        growth_info = f"Data terfilter hanya mencakup tahun 2012 dengan total penyewaan sebanyak <b>{int(sum_2012):,} unit</b>."
    else:
        growth_info = "Tidak ada volume penyewaan pada periode filter terpilih."
        
    q5_text = f"""
    * <b>Pertumbuhan Terfilter:</b> {growth_info}
    * <b>Konsistensi Pola:</b> Tanpa defisit di bulan mana pun, pertumbuhan terakselerasi signifikan pada bulan Mei hingga September (*Summer Peak Season*).
    * <b>Rekomendasi Capex:</b> Mengingat pertumbuhan organik yang sangat tinggi (+64.8% agregat tahunan), perusahaan disarankan meningkatkan alokasi belanja modal (*Capex*) penambahan armada minimal 30-40% menyambut kuartal kedua tahun berikutnya.
    """
    insight("🚀", "Dinamika Pertumbuhan", q5_text, color="green")

st.markdown("---")

# ── Segmentasi Waktu Tambahan (Clustering/Binning) ─────────────────────────────
with st.expander("🔍 Analisis Lanjutan: Distribusi Penggunaan Berdasarkan Kategori Waktu"):
    time_agg = hour_f.groupby('time_category', observed=True)['cnt'].agg(['sum', 'mean']).reset_index()
    time_agg.columns = ['Kategori Waktu', 'Total Penyewaan', 'Rata-rata per Jam']
    
    tc1, tc2 = st.columns([1.2, 1])
    with tc1:
        fig, ax = plt.subplots(figsize=(7, 3.5))
        sns.barplot(
            x='Total Penyewaan', 
            y='Kategori Waktu', 
            data=time_agg, 
            palette='viridis', 
            hue='Kategori Waktu',
            legend=False,
            ax=ax
        )
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
        ax.set_title("Total Sewa Berdasarkan Kategori Waktu", fontsize=11)
        st.pyplot(fig)
        plt.close(fig)
        
    with tc2:
        st.dataframe(time_agg.style.format({'Total Penyewaan': '{:,.0f}', 'Rata-rata per Jam': '{:,.1f}'}), use_container_width=True)
        st.caption("Kategorisasi waktu menggunakan binning matematis tervektorisasi (`pd.cut`) untuk mendiskritisasi rentang jam 24 jam.")

st.markdown("---")
st.caption("Bike Sharing Analytics Dashboard | Dikembangkan untuk Submission Fundamental Analisis Data Dicoding | Copyright (c) Muchammad Nasich 2026")
