import re
import unicodedata
from difflib import SequenceMatcher


STOPWORDS = {
    'yang', 'dan', 'di', 'pada', 'dengan', 'ada', 'ini', 'itu', 'saya', 'ku',
    'ke', 'dari', 'untuk', 'juga', 'sudah', 'sangat', 'agak', 'sedikit', 'lagi',
    'tanaman', 'kopi', 'pohon', 'tanaman', 'saya', 'melihat', 'terlihat', 'kelihatan',
    'punya', 'memiliki', 'adalah', 'akan', 'telah', 'begini', 'begitu', 'nya',
}

GEJALA_SINONIM = {
    'G001': ['daun menguning', 'daun kuning', 'menguning', 'warna kuning daun'],
    'G002': ['bercak kuning', 'bercak oranye', 'bercak orange', 'karat daun', 'noda oranye', 'bercak karat'],
    'G003': ['daun rontok', 'rontok daun', 'daun gugur', 'gugur daun'],
    'G004': ['bercak coklat', 'noda coklat', 'tompok coklat'],
    'G005': ['daun berlubang', 'lubang daun', 'berlubang'],
    'G006': ['buah membusuk', 'busuk buah', 'buah busuk'],
    'G007': ['buah menghitam', 'buah hitam', 'menghitam buah'],
    'G008': ['buah rontok', 'buah gugur'],
    'G009': ['cabang kering', 'ranting kering'],
    'G010': ['jamur putih', 'miselium putih', 'jamur di cabang', 'upas'],
    'G011': ['cabang mati', 'ranting mati'],
    'G012': ['akar membusuk', 'busuk akar', 'akar busuk'],
    'G013': ['tanaman layu', 'layu tanaman', 'layu keseluruhan'],
    'G014': ['pertumbuhan lambat', 'tumbuh lambat', 'lambat tumbuh'],
    'G015': ['batang menghitam', 'batang hitam'],
    'G016': ['batang lunak', 'batang lembek'],
    'G017': ['embun tepung', 'daun bertepung', 'tepung putih daun', 'lapisan putih daun'],
    'G018': ['daun keriting', 'daun keriput'],
    'G019': ['cabang membusuk', 'busuk cabang'],
    'G020': ['cabang patah', 'ranting patah'],
    'G021': ['daun layu', 'layu daun'],
    'G022': ['daun menghitam', 'daun hitam'],
    'G023': ['bercak basah', 'noda basah daun'],
    'G024': ['daun rusak', 'daun sobek'],
    'G025': ['akar bengkak', 'bengkak akar', 'nematoda akar'],
    'G026': ['tanaman kerdil', 'kerdil', 'tanaman pendek'],
    'G027': ['layu permanen', 'layu total', 'mati layu'],
    'G028': ['akar rusak', 'rusak akar'],
    'G029': ['daun pucat', 'pucat daun', 'kurang nitrogen'],
    'G030': ['daun tepi coklat', 'tepi daun coklat', 'kurang kalium'],
    'G031': ['daun kering', 'kering daun'],
    'G032': ['daun kuning tengah', 'kuning di tengah daun', 'kurang magnesium'],
    'G033': ['produksi menurun', 'hasil menurun', 'panen sedikit'],
    'G034': ['daun hijau segar', 'daun segar hijau'],
    'G035': ['daun sehat', 'daun normal'],
    'G036': ['buah segar', 'buah normal'],
    'G037': ['akar sehat', 'akar normal'],
    'G038': ['cabang segar', 'ranting segar'],
    'G039': ['daun bersih', 'tidak ada bercak'],
    'G040': ['akar normal'],
    'G041': ['tanaman segar', 'tanaman sehat'],
}

INTENT_DIAGNOSA = {'diagnosa', 'diagnosis', 'analisis', 'periksa', 'cek', 'proses', 'hitung'}
INTENT_RESET = {'reset', 'ulangi', 'hapus', 'mulai lagi', 'bersihkan', 'clear'}
INTENT_HELP = {'bantuan', 'help', 'panduan', 'cara pakai', 'contoh'}


def _normalize(text: str) -> str:
    text = text.lower().strip()
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r'[/\-_,.;:!?]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text


def _tokens(text: str) -> set:
    return {t for t in _normalize(text).split() if t not in STOPWORDS and len(t) > 1}


class GejalaNLP:
    def __init__(self, gejala_list):
        """
        gejala_list: iterable of objects/dicts with id, kode, nama, kategori
        """
        self.gejala = []
        for g in gejala_list:
            if hasattr(g, 'id'):
                item = {'id': g.id, 'kode': g.kode, 'nama': g.nama, 'kategori': g.kategori}
            else:
                item = dict(g)
            self.gejala.append(item)
        self._patterns = self._build_patterns()

    def _build_patterns(self):
        patterns = []
        for g in self.gejala:
            variants = {_normalize(g['nama'])}
            for part in re.split(r'[/]', g['nama']):
                variants.add(_normalize(part))
            for syn in GEJALA_SINONIM.get(g['kode'], []):
                variants.add(_normalize(syn))
            patterns.append({
                'gejala': g,
                'variants': sorted(variants, key=len, reverse=True),
            })
        return patterns

    def _score_variant(self, text_norm: str, variant: str) -> float:
        if len(variant) < 3:
            return 0.0
        if variant in text_norm:
            return 0.92

        v_words = variant.split()
        if len(v_words) >= 2:
            if all(w in text_norm for w in v_words):
                return 0.85

        t_set = set(text_norm.split())
        v_set = set(v_words)
        if v_set:
            overlap = len(v_set & t_set) / len(v_set)
            if overlap >= 0.75:
                return 0.72 + overlap * 0.15

        ratio = SequenceMatcher(None, variant, text_norm).ratio()
        if ratio >= 0.72:
            return ratio * 0.8
        return 0.0

    def extract(self, text: str, min_score: float = 0.68) -> list:
        if not text or not text.strip():
            return []

        text_norm = _normalize(text)
        found = []

        for pat in self._patterns:
            best = 0.0
            for variant in pat['variants']:
                best = max(best, self._score_variant(text_norm, variant))
            if best >= min_score:
                cf_user = round(min(0.95, 0.65 + best * 0.3), 2)
                g = pat['gejala']
                found.append({
                    'id': g['id'],
                    'kode': g['kode'],
                    'nama': g['nama'],
                    'kategori': g['kategori'],
                    'skor': round(best, 3),
                    'cf_user': cf_user,
                })

        found.sort(key=lambda x: x['skor'], reverse=True)
        return found

    def detect_intent(self, text: str) -> str:
        norm = _normalize(text)
        if not norm:
            return 'empty'
        for phrase in INTENT_RESET:
            if phrase in norm:
                return 'reset'
        for phrase in INTENT_DIAGNOSA:
            if phrase in norm or norm in phrase:
                return 'diagnosa'
        for phrase in INTENT_HELP:
            if phrase in norm:
                return 'help'
        if norm in {'halo', 'hai', 'hello', 'hi', 'selamat pagi', 'selamat siang'}:
            return 'greeting'
        return 'symptom'

    def process_message(self, text: str, session_gejala: dict) -> dict:
        """
        Proses satu pesan chat.
        session_gejala: {str(gejala_id): cf_user}
        """
        intent = self.detect_intent(text)
        session = {str(k): float(v) for k, v in (session_gejala or {}).items()}

        if intent == 'reset':
            return {
                'intent': 'reset',
                'reply': (
                    'Baik, percakapan dan gejala yang tercatat sudah direset. '
                    'Silakan ceritakan gejala tanaman kopi Anda dari awal.'
                ),
                'session_gejala': {},
                'baru': [],
                'semua': [],
            }

        if intent == 'help':
            return {
                'intent': 'help',
                'reply': self._help_text(),
                'session_gejala': session,
                'baru': [],
                'semua': self._session_summary(session),
            }

        if intent == 'greeting':
            return {
                'intent': 'greeting',
                'reply': (
                    'Halo! Saya asisten diagnosa SiPakar Kopi. '
                    'Ceritakan gejala yang Anda lihat pada tanaman kopi, '
                    'misalnya: <em>"daun ada bercak kuning oranye dan sering rontok"</em>. '
                    'Setelah cukup, ketik <strong>diagnosa</strong> atau klik tombol Jalankan Diagnosa.'
                ),
                'session_gejala': session,
                'baru': [],
                'semua': self._session_summary(session),
            }

        if intent == 'diagnosa':
            n = len(session)
            if n == 0:
                return {
                    'intent': 'diagnosa',
                    'reply': 'Belum ada gejala yang terdeteksi. Jelaskan dulu gejala yang Anda amati.',
                    'session_gejala': session,
                    'baru': [],
                    'semua': [],
                    'siap_diagnosa': False,
                }
            return {
                'intent': 'diagnosa',
                'reply': f'Memproses diagnosa berdasarkan {n} gejala…',
                'session_gejala': session,
                'baru': [],
                'semua': self._session_summary(session),
                'siap_diagnosa': True,
            }

        if intent == 'empty':
            return {
                'intent': 'empty',
                'reply': 'Ketik gejala yang Anda lihat, atau ketik <strong>bantuan</strong> untuk panduan.',
                'session_gejala': session,
                'baru': [],
                'semua': self._session_summary(session),
            }

        # Ekstrak gejala dari teks
        detected = self.extract(text)
        baru = []
        for d in detected:
            sid = str(d['id'])
            if sid not in session or session[sid] < d['cf_user']:
                session[sid] = d['cf_user']
                baru.append(d)

        if not detected:
            reply = (
                'Saya belum mengenali gejala spesifik dari kalimat itu. '
                'Coba jelaskan lebih jelas, contoh: '
                '<em>"daun bercak coklat"</em>, <em>"buah membusuk"</em>, '
                '<em>"tanaman layu"</em>, atau <em>"akar membusuk"</em>. '
                'Ketik <strong>bantuan</strong> untuk daftar contoh.'
            )
        elif baru:
            names = ', '.join(f'<strong>{b["nama"]}</strong>' for b in baru)
            reply = f'Gejala terdeteksi: {names}. '
            if len(session) > len(baru):
                reply += f'Total tercatat: {len(session)} gejala. '
            reply += 'Tambahkan gejala lain atau ketik <strong>diagnosa</strong> untuk hasil analisis.'
        else:
            reply = (
                'Gejala tersebut sudah tercatat sebelumnya. '
                'Tambahkan gejala lain atau ketik <strong>diagnosa</strong>.'
            )

        return {
            'intent': 'symptom',
            'reply': reply,
            'session_gejala': session,
            'baru': baru,
            'semua': self._session_summary(session),
        }

    def _session_summary(self, session: dict) -> list:
        by_id = {g['id']: g for g in self.gejala}
        out = []
        for sid, cf in session.items():
            g = by_id.get(int(sid))
            if g:
                out.append({
                    'id': g['id'],
                    'nama': g['nama'],
                    'kategori': g['kategori'],
                    'cf_user': cf,
                })
        return sorted(out, key=lambda x: x['nama'])

    def _help_text(self) -> str:
        contoh = [
            'daun ada bercak kuning oranye dan daun rontok',
            'buah membusuk dan cabang kering',
            'tanaman layu dengan akar membusuk',
            'daun bertepung putih seperti embun tepung',
            'batang menghitam dan batang lunak',
        ]
        items = ''.join(f'<li><em>{c}</em></li>' for c in contoh)
        return (
            '<strong>Cara pakai:</strong><ol>'
            '<li>Jelaskan gejala dengan bahasa sehari-hari.</li>'
            '<li>Sistem akan mengekstrak gejala secara otomatis (NLP).</li>'
            '<li>Ulangi hingga cukup, lalu ketik <strong>diagnosa</strong>.</li>'
            '</ol><strong>Contoh kalimat:</strong><ul>' + items + '</ul>'
        )
