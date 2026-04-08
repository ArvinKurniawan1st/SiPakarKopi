# SiPakar Kopi — Sistem Pakar Diagnosis Penyakit Tanaman Kopi
> Mesin Inferensi: **Certainty Factor (CF)**  |  Stack: **Python Flask + SQLite**

---

## Fitur Utama
- ✅ Diagnosa berbasis **28 gejala** dan **6 penyakit** utama kopi
- ✅ Mesin inferensi **Certainty Factor** (CF) sesuai formula Shortliffe & Buchanan
- ✅ Slider keyakinan pengguna (CF user) per gejala
- ✅ Tampilan hasil: peringkat, persentase keyakinan, penanganan & pencegahan
- ✅ Halaman detail penyakit + tabel aturan CF pakar
- ✅ Database SQLite otomatis terisi data awal saat pertama kali dijalankan

---

## Penyakit yang Dideteksi
| Kode | Penyakit                    | Patogen                         |
|------|-----------------------------|---------------------------------|
| P001 | Karat Daun Kopi             | *Hemileia vastatrix*            |
| P002 | Bercak Daun Cercospora      | *Cercospora coffeicola*         |
| P003 | Antraknosa Kopi             | *Colletotrichum gloeosporioides*|
| P004 | Busuk Buah Kopi (CBD)       | *Colletotrichum kahawae*        |
| P005 | Penyakit Akar Kopi          | *Fusarium / Phytophthora*       |
| P006 | Serangan Penggerek Batang   | *Xylotrechus / Zeuzera*         |

---

## Instalasi & Menjalankan

```bash
# 1. Clone / ekstrak folder proyek
cd sistem_pakar_kopi

# 2. Buat virtual environment (opsional tapi disarankan)
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Install dependensi
pip install -r requirements.txt

# 4. Jalankan aplikasi
python app.py
```

Buka browser: **http://localhost:5000**

Database SQLite (`sistem_pakar.db`) akan otomatis dibuat dan diisi data saat pertama kali dijalankan.

---

## Cara Kerja Certainty Factor

### Formula Dasar
```
CF(H, E) = CF(H|E) × CF(E)
```
- `CF(H|E)` = bobot keyakinan pakar (disimpan di tabel `aturan`)
- `CF(E)`   = keyakinan pengguna terhadap gejala (0.1 – 1.0, diatur via slider)

### Kombinasi Beberapa Aturan
```
CF1 ≥ 0 dan CF2 ≥ 0 :  CF_gabung = CF1 + CF2 × (1 - CF1)
CF1 < 0 dan CF2 < 0  :  CF_gabung = CF1 + CF2 × (1 + CF1)
Salah satu negatif   :  CF_gabung = (CF1 + CF2) / (1 - min(|CF1|, |CF2|))
```

---

## Struktur Database

```
penyakit     → id, kode, nama, nama_latin, deskripsi, penanganan, pencegahan
gejala       → id, kode, nama, kategori
aturan       → id, penyakit_id, gejala_id, cf_pakar
riwayat      → id, tanggal, gejala_input, hasil_utama, cf_utama
```

---

## Struktur Proyek
```
sistem_pakar_kopi/
├── app.py              ← Entry point Flask + routing
├── cf_engine.py        ← Logika Certainty Factor
├── database.py         ← Model SQLAlchemy + seed data
├── requirements.txt
├── README.md
└── templates/
    ├── base.html
    ├── index.html          ← Halaman diagnosa utama
    ├── penyakit.html       ← Daftar penyakit
    ├── penyakit_detail.html ← Detail + aturan CF
    └── tentang.html        ← Penjelasan metode CF
```
