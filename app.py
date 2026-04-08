from flask import Flask, render_template, request, jsonify
from database import db, init_db
from cf_engine import CertaintyFactorEngine

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sistem_pakar.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'kopi_pakar_secret'

db.init_app(app)

@app.route('/')
def index():
    from database import Gejala
    gejala_list = Gejala.query.order_by(Gejala.kategori, Gejala.nama).all()
    kategori_dict = {}
    for g in gejala_list:
        if g.kategori not in kategori_dict:
            kategori_dict[g.kategori] = []
        kategori_dict[g.kategori].append(g)
    return render_template('index.html', kategori_dict=kategori_dict)

@app.route('/diagnosa', methods=['POST'])
def diagnosa():
    from database import Gejala, Penyakit, Aturan
    data = request.get_json()
    gejala_input = data.get('gejala', {})  # {gejala_id: cf_user}

    if not gejala_input:
        return jsonify({'error': 'Pilih minimal satu gejala'}), 400

    engine = CertaintyFactorEngine()

    # Load semua aturan dari database
    aturan_list = Aturan.query.all()
    rules = []
    for a in aturan_list:
        rules.append({
            'id': a.id,
            'penyakit_id': a.penyakit_id,
            'gejala_id': a.gejala_id,
            'cf_pakar': a.cf_pakar
        })

    # Load semua penyakit
    penyakit_list = Penyakit.query.all()
    penyakit_dict = {p.id: p for p in penyakit_list}

    # Load semua gejala
    gejala_dict = {str(g.id): g for g in Gejala.query.all()}

    # Jalankan mesin inferensi CF
    hasil_cf = engine.hitung_semua(rules, gejala_input)

    # Susun hasil diagnosis
    hasil = []
    for penyakit_id, cf_total in hasil_cf.items():
        p = penyakit_dict.get(penyakit_id)
        if p:
            hasil.append({
                'penyakit_id': penyakit_id,
                'nama': p.nama,
                'nama_latin': p.nama_latin,
                'cf_nilai': cf_total,
                'persentase': round(cf_total * 100, 2),
                'deskripsi': p.deskripsi,
                'penanganan': p.penanganan,
                'pencegahan': p.pencegahan,
                'tingkat': engine.tingkat_keyakinan(cf_total),
                'status': 'Mendukung' if cf_total > 0 else 'Menolak'
            })

    hasil.sort(key=lambda x: x['cf_nilai'], reverse=True)

    # Ambil detail gejala yang dipilih
    gejala_terpilih = []
    for gid, cf_user in gejala_input.items():
        g = gejala_dict.get(str(gid))
        if g:
            gejala_terpilih.append({'nama': g.nama, 'cf_user': cf_user})

    return jsonify({
        'hasil': hasil,
        'gejala_terpilih': gejala_terpilih,
        'total_gejala': len(gejala_input)
    })

@app.route('/penyakit')
def penyakit_list():
    from database import Penyakit
    penyakit = Penyakit.query.all()
    return render_template('penyakit.html', penyakit=penyakit)

@app.route('/penyakit/<int:id>')
def penyakit_detail(id):
    from database import Penyakit, Aturan, Gejala
    p = Penyakit.query.get_or_404(id)
    aturan = Aturan.query.filter_by(penyakit_id=id).all()
    gejala_dict = {g.id: g for g in Gejala.query.all()}
    return render_template('penyakit_detail.html', penyakit=p, aturan=aturan, gejala_dict=gejala_dict)

@app.route('/tentang')
def tentang():
    return render_template('tentang.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_db()
    app.run(debug=True, port=5000)
