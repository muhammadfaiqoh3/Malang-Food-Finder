import requests
import pandas as pd
import random
import time

def fetch_and_enrich_data():
    print(" Proses Pengambilan data asli dari Malang (OpenStreetMap)...")
    
    # Query Overpass API untuk ambil Restoran & Cafe di Malang
    query = """
    [out:json][timeout:60];
    (
      // Mencari segala jenis tempat makan (nwr = node, way, relation)
    nwr["amenity"~"restaurant|cafe|fast_food|food_court|ice_cream"](around:10000, -7.9826, 112.6308);
    nwr["shop"~"bakery|confectionery"](around:10000, -7.9826, 112.6308);
    nwr["cuisine"](around:10000, -7.9826, 112.6308);
    );
    out center;
    """
    
    url = "http://overpass-api.de/api/interpreter"
    
    # Header penting agar tidak dikira bot jahat
    headers = {
        'User-Agent': 'DecisionMateBot/1.0 (Contact: student@example.com)'
    }
    
    try:
        response = requests.get(url, params={'data': query}, headers=headers, timeout=30)
        # Cek status code (200 = OK)
        if response.status_code == 200:
            data = response.json()
            
            if not data['elements']:
                print("Server membalas, tapi data tidak ditemukan. Mencoba area yang lebih luas...")
                return

            places = []
            kategori_list = ['Nasi', 'Mie', 'Ayam', 'Kopi', 'Cemilan', 'Bakso', 'Soto']

            for element in data['elements']:
                tags = element.get('tags', {})
                nama = tags.get('name')
                
                if not nama: continue # Skip yang tidak punya nama

                if tags.get('amenity') == 'cafe':
                    harga = random.randint(15000, 45000)
                    kategori = 'Kopi/Cafe'
                else:
                    harga = random.randint(8000, 25000)
                    kategori = random.choice(kategori_list)

                lat = element.get('lat') or element.get('center', {}).get('lat')
                lon = element.get('lon') or element.get('center', {}).get('lon')
                places.append({
                    'Nama': nama,
                    'Harga': harga,
                    'Rating': round(random.uniform(3.8, 4.9), 1),
                    'Jarak_KM': round(random.uniform(0.1, 5.0), 1),
                    'Kategori': kategori,
                    'Lat' : lat,
                    'Lon' : lon
                })

            df = pd.DataFrame(places).drop_duplicates(subset=['Nama'])
            df.to_csv('data_makanan.csv', index=False)
            print(f"BERHASIL! Mendapatkan {len(df)} tempat makan asli Malang.")
            
        else:
            print(f"Server Error: Status Code {response.status_code}")
            print("Saran: Tunggu 30 detik lalu jalankan lagi.")

    except Exception as e:
        print(f"Koneksi Gagal: {e}")

if __name__ == "__main__":
    fetch_and_enrich_data()