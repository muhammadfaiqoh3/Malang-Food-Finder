import streamlit as st
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

# Fungsi Search lokasi
def get_coordinates(city_name):
    try:
        geolocator = Nominatim("user_agent='food_finder_malang")
        location = geolocator.geocode(f"{city_name}, Malang, Indonesia")
        if location:
            return location.latitude, location.longitude
        return None
    except:
        return None

# Buat cek koordinat
def haversine(lat1, lon1, lat2, lon2):
    # mengubah derajat ke radian
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    
    # selisih koordinat
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    # Rumus haversine
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    r = 6371 # Radius bumi dalam kilometer
    return c * r

#  KONFIGURASI HALAMAN 
st.set_page_config(page_title="Food Decision Mate", layout="wide")

# 1. DATA ACQUISITION (Membaca Matriks dari CSV)
@st.cache_data # Biar aplikasi kencang/efisien (CPMK-5)
def load_data():
        data = pd.read_csv('data_makanan.csv')
        return data

df = load_data()

# SIDEBAR: LOKASI USER DINAMIS 
# FUNGSI SEARCH LOKASI (GEOCODING)
def get_coordinates(city_name):
    try:
        # Nominatim adalah layanan pencarian koordinat gratis
        geolocator = Nominatim(user_agent="food_finder_malang_student")
        # Kita kunci di Malang agar hasilnya akurat
        location = geolocator.geocode(f"{city_name}, Malang, Indonesia")
        if location:
            return location.latitude, location.longitude
        return None
    except:
        return None

# --- SIDEBAR: LOKASI USER DINAMIS (VERSI SEARCH) ---
st.sidebar.header("Lokasi Kamu")
search_lokasi = st.sidebar.text_input("Cari Alamat/Tempat di Malang:", "Alun-Alun Malang")

# Jalankan fungsi pencarian
coords = get_coordinates(search_lokasi)

if coords:
    user_lat, user_lon = coords
    st.sidebar.success(f"Terdeteksi: {user_lat:.4f}, {user_lon:.4f}")
else:
    st.sidebar.error("Lokasi tidak ditemukan. Menggunakan default: Alun-Alun.")
    user_lat, user_lon = -7.9826, 112.6308 # Titik Alun-Alun Malang

# --- HITUNG JARAK DINAMIS ---
# Rumus Haversine tetap dipakai di sini (CPMK-5)
df['Jarak_KM'] = df.apply(lambda row: haversine(user_lat, user_lon, row['Lat'], row['Lon']), axis=1)

# FILTER SEPERTI BIASA
st.sidebar.header("Filter")
budget_user = st.sidebar.number_input("Budget (Rp)", 5000, 100000, 25000)
jarak_max = st.sidebar.slider("Jarak Maks (KM)", 0.1, 3.0, 10.0)

mask = (df['Harga'] <= budget_user) & (df['Jarak_KM'] <= jarak_max)
filtered_df = df[mask].copy()

# --- DISPLAY ---
st.title("Malang Food Finder: Dynamic Edition")
st.write(f"Menghitung jarak otomatis dari **{search_lokasi}** ke {len(df)} tempat makan.")

if not filtered_df.empty:
    # Ranking
    filtered_df['Skor'] = (filtered_df['Rating'] * 0.7) + ((1 - (filtered_df['Harga'] / 100000)) * 0.3)
    hasil = filtered_df.sort_values(by='Skor', ascending=False)
    
    # MAPS (Gimmick paling ampuh buat bikin bengong)
    st.subheader("Sebaran Warung Terdekat")
    # Streamlit butuh kolom bernama 'lat' dan 'lon' (huruf kecil) untuk map
    map_data = hasil[['Lat', 'Lon']].rename(columns={'Lat': 'lat', 'Lon': 'lon'})
    st.map(map_data)
    
    st.dataframe(hasil[['Nama', 'Harga', 'Rating', 'Jarak_KM', 'Kategori']], use_container_width=True)
else:
    st.warning("Gak ada makanan di radius segitu, coba jauhan dikit!")