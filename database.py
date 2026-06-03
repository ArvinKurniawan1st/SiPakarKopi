from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# ─────────────────────────────────────────────
# MODEL
# ─────────────────────────────────────────────

class Penyakit(db.Model):
    __tablename__ = 'penyakit'
    id          = db.Column(db.Integer, primary_key=True)
    kode        = db.Column(db.String(10), unique=True, nullable=False)
    nama        = db.Column(db.String(100), nullable=False)
    nama_latin  = db.Column(db.String(150))
    deskripsi   = db.Column(db.Text)
    penanganan  = db.Column(db.Text)
    pencegahan  = db.Column(db.Text)
    gambar      = db.Column(db.String(200))
    aturan      = db.relationship('Aturan', backref='penyakit', lazy=True)


class Gejala(db.Model):
    __tablename__ = 'gejala'
    id       = db.Column(db.Integer, primary_key=True)
    kode     = db.Column(db.String(10), unique=True, nullable=False)
    nama     = db.Column(db.String(200), nullable=False)
    kategori = db.Column(db.String(50))   # daun, buah, batang, akar, umum
    deskripsi = db.Column(db.Text)
    aturan   = db.relationship('Aturan', backref='gejala', lazy=True)


class Aturan(db.Model):
    """IF gejala THEN penyakit dengan bobot CF pakar."""
    __tablename__ = 'aturan'
    id          = db.Column(db.Integer, primary_key=True)
    penyakit_id = db.Column(db.Integer, db.ForeignKey('penyakit.id'), nullable=False)
    gejala_id   = db.Column(db.Integer, db.ForeignKey('gejala.id'), nullable=False)
    cf_pakar    = db.Column(db.Float, nullable=False)   # nilai 0.0 – 1.0


class RiwayatDiagnosis(db.Model):
    __tablename__ = 'riwayat'
    id           = db.Column(db.Integer, primary_key=True)
    tanggal      = db.Column(db.DateTime, default=db.func.now())
    gejala_input = db.Column(db.Text)   # JSON string
    hasil_utama  = db.Column(db.String(100))
    cf_utama     = db.Column(db.Float)


# ─────────────────────────────────────────────
# GAMBAR PENYAKIT (relatif ke folder static/)
# ─────────────────────────────────────────────

PENYAKIT_GAMBAR = {
    'P001': 'images/bercak Bercak kuningoranye.jpg',
    'P002': 'images/bercak coklat.jpg',
    'P003': 'images/Buah membusuk.jpg',
    'P004': 'images/Ada jamur putih.png',
    'P005': 'images/Akar membusuk.jpg',
    'P006': 'images/Batang lunak.jpg',
    'P007': 'images/Daun bertepung putih.jpg',
    'P008': 'images/Cabang membusuk.jpg',
    'P009': 'images/Daun menghitam.jpg',
    'P010': 'images/Bercak basah.jpg',
    'P011': 'images/Akar bengkak.jpg',
    'P012': 'images/Layu permanen.jpg',
    'P013': 'images/Daun pucat.jpg',
    'P014': 'images/Daun tepi coklat.jpg',
    'P015': 'images/Daun kuning di tengah.jpg',
    'P016': 'images/Tanaman layu.jpg',
    'P017': 'images/Akar membusuk.jpg',
    'P018': 'images/Akar rusak.jpg',
    'P019': 'images/Produksi menurun.png',
}


def sync_penyakit_gambar():
    """Isi kolom gambar untuk data penyakit yang sudah ada di database."""
    updated = False
    for p in Penyakit.query.all():
        path = PENYAKIT_GAMBAR.get(p.kode)
        if path and p.gambar != path:
            p.gambar = path
            updated = True
    if updated:
        db.session.commit()


# ─────────────────────────────────────────────
# SEED DATA
# ─────────────────────────────────────────────

def init_db():
    # Hanya seed jika database kosong
    if Penyakit.query.count() > 0:
        sync_penyakit_gambar()
        return

    # ── PENYAKIT ──────────────────────────────
    penyakit_data = [
        {
            'kode': 'P001',
            'nama': 'Karat Daun',
            'nama_latin': 'Hemileia vastatrix',
            'deskripsi': 'Penyakit jamur yang menyerang daun kopi dengan bercak kuning/oranye dan menyebabkan defoliasi.',
            'penanganan': 'Semprot fungisida berbahan tembaga, pangkas daun terinfeksi, perbaiki sirkulasi udara.',
            'pencegahan': 'Gunakan varietas tahan, lakukan monitoring rutin, jaga sanitasi kebun.',
            'gambar': PENYAKIT_GAMBAR['P001'],
        },
        {
            'kode': 'P002',
            'nama': 'Cercospora',
            'nama_latin': 'Cercospora coffeicola',
            'deskripsi': 'Penyakit bercak daun yang menyebabkan bercak coklat dan penurunan kualitas tanaman.',
            'penanganan': 'Gunakan fungisida mankozeb/karbendazim, kurangi nitrogen berlebih.',
            'pencegahan': 'Pemupukan seimbang, sanitasi kebun, drainase baik.',
            'gambar': PENYAKIT_GAMBAR['P002'],
        },
        {
            'kode': 'P003',
            'nama': 'Antraknosa',
            'nama_latin': 'Colletotrichum gloeosporioides',
            'deskripsi': 'Menyerang buah dan ranting, menyebabkan busuk buah dan kematian cabang.',
            'penanganan': 'Semprot fungisida, buang bagian terinfeksi.',
            'pencegahan': 'Sanitasi kebun dan panen tepat waktu.',
            'gambar': PENYAKIT_GAMBAR['P003'],
        },
        {
            'kode': 'P004',
            'nama': 'Jamur Upas',
            'nama_latin': 'Upasia salmonicolor',
            'deskripsi': 'Jamur yang menyerang cabang dan batang dengan miselium putih.',
            'penanganan': 'Pangkas cabang terinfeksi dan bakar.',
            'pencegahan': 'Jaga kelembaban dan sirkulasi udara.',
            'gambar': PENYAKIT_GAMBAR['P004'],
        },
        {
            'kode': 'P005',
            'nama': 'Akar Busuk',
            'nama_latin': 'Fusarium spp. / Phytophthora spp.',
            'deskripsi': 'Penyakit pada akar yang menyebabkan tanaman layu dan mati.',
            'penanganan': 'Gunakan fungisida tanah dan perbaiki drainase.',
            'pencegahan': 'Gunakan bibit sehat dan hindari genangan.',
            'gambar': PENYAKIT_GAMBAR['P005'],
        },
        {
            'kode': 'P006',
            'nama': 'Busuk Batang',
            'nama_latin': 'Phytophthora spp.',
            'deskripsi': 'Batang menjadi lunak dan menghitam akibat infeksi jamur.',
            'penanganan': 'Potong bagian terinfeksi dan aplikasikan fungisida.',
            'pencegahan': 'Hindari kelembaban tinggi berlebih.',
            'gambar': PENYAKIT_GAMBAR['P006'],
        },
        {
            'kode': 'P007',
            'nama': 'Embun Tepung',
            'nama_latin': 'Oidium spp.',
            'deskripsi': 'Ditandai dengan lapisan putih seperti tepung pada daun.',
            'penanganan': 'Gunakan fungisida sulfur.',
            'pencegahan': 'Kurangi kelembaban dan tingkatkan sirkulasi udara.',
            'gambar': PENYAKIT_GAMBAR['P007'],
        },
        {
            'kode': 'P008',
            'nama': 'Busuk Cabang',
            'nama_latin': 'Botryodiplodia spp.',
            'deskripsi': 'Cabang membusuk dan mudah patah.',
            'penanganan': 'Pangkas dan bakar cabang terinfeksi.',
            'pencegahan': 'Jaga kesehatan tanaman.',
            'gambar': PENYAKIT_GAMBAR['P008'],
        },
        {
            'kode': 'P009',
            'nama': 'Bakteri Hawar',
            'nama_latin': 'Xanthomonas spp.',
            'deskripsi': 'Penyakit bakteri yang menyebabkan daun layu dan menghitam.',
            'penanganan': 'Gunakan bakterisida.',
            'pencegahan': 'Hindari percikan air berlebih.',
            'gambar': PENYAKIT_GAMBAR['P009'],
        },
        {
            'kode': 'P010',
            'nama': 'Bercak Bakteri',
            'nama_latin': 'Pseudomonas spp.',
            'deskripsi': 'Menimbulkan bercak basah pada daun.',
            'penanganan': 'Semprot bakterisida.',
            'pencegahan': 'Sanitasi kebun.',
            'gambar': PENYAKIT_GAMBAR['P010'],
        },
        {
            'kode': 'P011',
            'nama': 'Nematoda',
            'nama_latin': 'Meloidogyne spp.',
            'deskripsi': 'Menyerang akar dan menyebabkan pembengkakan.',
            'penanganan': 'Gunakan nematisida.',
            'pencegahan': 'Rotasi tanaman.',
            'gambar': PENYAKIT_GAMBAR['P011'],
        },
        {
            'kode': 'P012',
            'nama': 'Fusarium',
            'nama_latin': 'Fusarium oxysporum',
            'deskripsi': 'Menyebabkan layu permanen akibat kerusakan pembuluh.',
            'penanganan': 'Cabut tanaman terinfeksi.',
            'pencegahan': 'Gunakan bibit tahan penyakit.',
            'gambar': PENYAKIT_GAMBAR['P012'],
        },
        {
            'kode': 'P013',
            'nama': 'Defisiensi Nitrogen',
            'nama_latin': '-',
            'deskripsi': 'Kekurangan nitrogen menyebabkan daun pucat dan pertumbuhan lambat.',
            'penanganan': 'Tambahkan pupuk nitrogen.',
            'pencegahan': 'Pemupukan rutin.',
            'gambar': PENYAKIT_GAMBAR['P013'],
        },
        {
            'kode': 'P014',
            'nama': 'Defisiensi Kalium',
            'nama_latin': '-',
            'deskripsi': 'Ditandai dengan daun tepi coklat dan kering.',
            'penanganan': 'Tambahkan pupuk kalium.',
            'pencegahan': 'Pemupukan berimbang.',
            'gambar': PENYAKIT_GAMBAR['P014'],
        },
        {
            'kode': 'P015',
            'nama': 'Defisiensi Magnesium',
            'nama_latin': '-',
            'deskripsi': 'Daun menguning di bagian tengah.',
            'penanganan': 'Berikan dolomit atau Mg.',
            'pencegahan': 'Perbaiki pH tanah.',
            'gambar': PENYAKIT_GAMBAR['P015'],
        },
        {
            'kode': 'P016',
            'nama': 'Kekeringan',
            'nama_latin': '-',
            'deskripsi': 'Tanaman layu akibat kekurangan air.',
            'penanganan': 'Lakukan penyiraman rutin.',
            'pencegahan': 'Gunakan mulsa.',
            'gambar': PENYAKIT_GAMBAR['P016'],
        },
        {
            'kode': 'P017',
            'nama': 'Overwatering',
            'nama_latin': '-',
            'deskripsi': 'Kelebihan air menyebabkan akar busuk.',
            'penanganan': 'Kurangi penyiraman.',
            'pencegahan': 'Drainase baik.',
            'gambar': PENYAKIT_GAMBAR['P017'],
        },
        {
            'kode': 'P018',
            'nama': 'Kerusakan Akar',
            'nama_latin': '-',
            'deskripsi': 'Kerusakan akar akibat mekanis atau patogen.',
            'penanganan': 'Perbaiki kondisi tanah.',
            'pencegahan': 'Hindari kerusakan akar.',
            'gambar': PENYAKIT_GAMBAR['P018'],
        },
        {
            'kode': 'P019',
            'nama': 'Tanaman Tua',
            'nama_latin': '-',
            'deskripsi': 'Penurunan produktivitas karena usia tanaman.',
            'penanganan': 'Lakukan peremajaan.',
            'pencegahan': 'Replanting berkala.',
            'gambar': PENYAKIT_GAMBAR['P019'],
        },
    ]

    penyakit_objs = {}
    for p in penyakit_data:
        obj = Penyakit(**p)
        db.session.add(obj)
        db.session.flush()
        penyakit_objs[p['kode']] = obj

    # ── GEJALA ────────────────────────────────
    gejala_data = [
        ('G001', 'Daun menguning', 'daun'),
        ('G002', 'Bercak kuning/oranye', 'daun'),
        ('G003', 'Daun rontok', 'daun'),
        ('G004', 'Bercak coklat', 'daun'),
        ('G005', 'Daun berlubang', 'daun'),
        ('G006', 'Buah membusuk', 'buah'),
        ('G007', 'Buah menghitam', 'buah'),
        ('G008', 'Buah rontok', 'buah'),
        ('G009', 'Cabang kering', 'batang'),
        ('G010', 'Jamur putih', 'batang'),
        ('G011', 'Cabang mati', 'batang'),
        ('G012', 'Akar membusuk', 'akar'),
        ('G013', 'Tanaman layu', 'umum'),
        ('G014', 'Pertumbuhan lambat', 'umum'),
        ('G015', 'Batang menghitam', 'batang'),
        ('G016', 'Batang lunak', 'batang'),
        ('G017', 'Daun bertepung putih', 'daun'),
        ('G018', 'Daun keriting', 'daun'),
        ('G019', 'Cabang membusuk', 'batang'),
        ('G020', 'Cabang patah', 'batang'),
        ('G021', 'Daun layu', 'daun'),
        ('G022', 'Daun menghitam', 'daun'),
        ('G023', 'Bercak basah', 'daun'),
        ('G024', 'Daun rusak', 'daun'),
        ('G025', 'Akar bengkak', 'akar'),
        ('G026', 'Tanaman kerdil', 'umum'),
        ('G027', 'Layu permanen', 'umum'),
        ('G028', 'Akar rusak', 'akar'),
        ('G029', 'Daun pucat', 'daun'),
        ('G030', 'Daun tepi coklat', 'daun'),
        ('G031', 'Daun kering', 'daun'),
        ('G032', 'Daun kuning di tengah', 'daun'),
        ('G033', 'Produksi menurun', 'umum'),
        ('G034', 'Daun hijau segar', 'daun'),
        ('G035', 'Daun sehat', 'daun'),
        ('G036', 'Buah segar', 'buah'),
        ('G037', 'Akar sehat', 'akar'),
        ('G038', 'Cabang segar', 'batang'),
        ('G039', 'Daun bersih', 'daun'),
        ('G040', 'Akar normal', 'akar'),
        ('G041', 'Tanaman segar', 'umum'),
    ]

    gejala_objs = {}
    for kode, nama, kategori in gejala_data:
        obj = Gejala(kode=kode, nama=nama, kategori=kategori)
        db.session.add(obj)
        db.session.flush()
        gejala_objs[kode] = obj

    # ── ATURAN (basis pengetahuan CF) ─────────
    # Format: (kode_penyakit, kode_gejala, cf_pakar)
    aturan_data = [
        ('P001','G001',0.6),
        ('P001','G002',0.9),
        ('P001','G003',0.8),
        ('P001','G034',-0.7),


        ('P002','G004',0.8),
        ('P002','G001',0.5),
        ('P002','G005',0.6),
        ('P002','G035',-0.6),

        ('P003','G006',0.9),
        ('P003','G007',0.8),
        ('P003','G008',0.7),
        ('P003','G036',-0.7),

        ('P004','G009',0.8),
        ('P004','G010',0.9),
        ('P004','G011',0.7),
        ('P004','G038',-0.6),

        ('P005','G012',0.9),
        ('P005','G013',0.8),
        ('P005','G014',0.7),
        ('P005','G037',-0.8),

        ('P006','G015',0.8),
        ('P006','G016',0.7),

        ('P007','G017',0.9),
        ('P007','G018',0.6),
        ('P007','G039',-0.7),

        ('P008','G019',0.8),
        ('P008','G020',0.6),

        ('P009','G021',0.7),
        ('P009','G022',0.8),

        ('P010','G023',0.8),
        ('P010','G024',0.6),

        ('P011','G025',0.9),
        ('P011','G026',0.8),
        ('P011','G040',-0.7),

        ('P012','G027',0.9),
        ('P012','G028',0.7),
        ('P012','G041',-0.8),

        ('P013','G029',0.8),
        ('P013','G014',0.7),

        ('P014','G030',0.8),
        ('P014','G031',0.7),

        ('P015','G032',0.8),

        ('P016','G013',0.9),
        ('P016','G031',0.8),

        ('P017','G012',0.8),
        ('P017','G001',0.7),

        ('P018','G013',0.7),

        ('P019','G033',0.9),
    ]

    for kode_p, kode_g, cf in aturan_data:
        aturan = Aturan(
            penyakit_id=penyakit_objs[kode_p].id,
            gejala_id=gejala_objs[kode_g].id,
            cf_pakar=cf
        )
        db.session.add(aturan)

    db.session.commit()
    print("✓ Database berhasil diinisialisasi dengan data penyakit kopi.")
