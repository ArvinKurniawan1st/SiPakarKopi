"""
Mesin Inferensi Certainty Factor (CF)
======================================
Metode:
  CF(H, E) = CF(H|E) × CF(E)
    - CF(H|E) = cf_pakar  : keyakinan pakar terhadap hipotesis H jika bukti E ada
    - CF(E)   = cf_user   : keyakinan pengguna terhadap bukti E

Kombinasi CF dari beberapa aturan untuk hipotesis yang sama:
  CF_combine(CF1, CF2):
    - Jika CF1 >= 0 dan CF2 >= 0  : CF1 + CF2 * (1 - CF1)
    - Jika CF1 < 0  dan CF2 < 0   : CF1 + CF2 * (1 + CF1)
    - Jika salah satu negatif      : (CF1 + CF2) / (1 - min(|CF1|, |CF2|))

Rentang nilai CF: -1.0 (pasti tidak) hingga 1.0 (pasti ya)
"""


class CertaintyFactorEngine:

    def hitung_cf_rule(self, cf_pakar: float, cf_user: float) -> float:
        """
        Hitung CF untuk satu aturan.
        CF(H, E) = CF(H|E) × CF(E)
        """
        return cf_pakar * cf_user

    def kombinasi_cf(self, cf_lama: float, cf_baru: float) -> float:
        """
        Kombinasikan dua nilai CF untuk hipotesis yang sama.
        Digunakan saat beberapa aturan mendukung penyakit yang sama.
        """
        if cf_lama >= 0 and cf_baru >= 0:
            return cf_lama + cf_baru * (1 - cf_lama)
        elif cf_lama < 0 and cf_baru < 0:
            return cf_lama + cf_baru * (1 + cf_lama)
        else:
            penyebut = 1 - min(abs(cf_lama), abs(cf_baru))
            if penyebut == 0:
                return 0
            return (cf_lama + cf_baru) / penyebut

    def hitung_semua(self, rules: list, gejala_input: dict) -> dict:
        """
        Hitung CF total untuk setiap penyakit berdasarkan gejala yang dipilih.

        Parameters:
          rules        : list of dict {penyakit_id, gejala_id, cf_pakar}
          gejala_input : dict {gejala_id: cf_user}  (cf_user = 0.0 – 1.0)

        Returns:
          dict {penyakit_id: cf_total}
        """
        cf_penyakit = {}  # {penyakit_id: cf_gabungan}

        for rule in rules:
            gejala_id = str(rule['gejala_id'])
            penyakit_id = rule['penyakit_id']

            # Hanya proses jika gejala dipilih pengguna
            if gejala_id not in gejala_input:
                continue

            cf_user = float(gejala_input[gejala_id])
            cf_pakar = float(rule['cf_pakar'])

            # Langkah 1: Hitung CF untuk aturan ini
            cf_rule = self.hitung_cf_rule(cf_pakar, cf_user)

            # Langkah 2: Gabungkan dengan CF penyakit sebelumnya
            if penyakit_id not in cf_penyakit:
                cf_penyakit[penyakit_id] = cf_rule
            else:
                cf_penyakit[penyakit_id] = self.kombinasi_cf(
                    cf_penyakit[penyakit_id], cf_rule
                )

        return cf_penyakit

    def tingkat_keyakinan(self, cf: float) -> dict:
        """
        Konversi nilai CF ke label tingkat keyakinan.
        """
        cf_abs = abs(cf)
        if cf < 0:
            if cf_abs >= 0.8:
                label, warna = "Hampir Pasti Tidak", "danger"
            elif cf_abs >= 0.6:
                label, warna = "Kemungkinan Besar Tidak", "warning"
            else:
                label, warna = "Mungkin Tidak", "secondary"
        elif cf_abs < 0.2:
            label, warna = "Tidak Yakin", "secondary"
        elif cf_abs < 0.4:
            label, warna = "Kemungkinan Kecil", "info"
        elif cf_abs < 0.6:
            label, warna = "Kemungkinan", "primary"
        elif cf_abs < 0.8:
            label, warna = "Kemungkinan Besar", "warning"
        else:
            label, warna = "Hampir Pasti", "danger"

        return {'label': label, 'warna': warna}


# ─────────────────────────────────────────────
# Contoh penggunaan manual (tes cepat)
# ─────────────────────────────────────────────
if __name__ == '__main__':
    engine = CertaintyFactorEngine()

    rules = [
        {'penyakit_id': 1, 'gejala_id': 1, 'cf_pakar': 0.8},
        {'penyakit_id': 1, 'gejala_id': 2, 'cf_pakar': 0.7},
        {'penyakit_id': 1, 'gejala_id': 3, 'cf_pakar': 0.6},
        {'penyakit_id': 2, 'gejala_id': 2, 'cf_pakar': 0.5},
        {'penyakit_id': 2, 'gejala_id': 4, 'cf_pakar': 0.9},
    ]
    gejala_input = {'1': 0.8, '2': 0.6, '3': 1.0}

    hasil = engine.hitung_semua(rules, gejala_input)
    for pid, cf in hasil.items():
        print(f"Penyakit {pid}: CF = {cf:.4f} ({cf*100:.1f}%)")
