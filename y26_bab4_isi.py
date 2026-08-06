"""Isi naratif BAB IV — Hasil dan Pembahasan.

Dipanggil `y26_tulis_bab45.py`. Seluruh angka diinjeksi dari berkas hasil; prosa mengikuti
Standar Penulisan CLAUDE.md §11 (prosa murni tanpa penomoran/bullet pada badan teks,
istilah asing dicetak miring lewat penanda *bintang*, desimal memakai koma).
"""
from __future__ import annotations

from y26_tulis_bab45 import (Nomor, baca_csv, baca_json, gambar, h1, h2, h3,
                             halaman_baru, ind, par, rib, tabel)

LBL = {"V1": "V1 (dasar)", "V2": "V2 (HAM)", "V3": "V3 (P2)", "V4": "V4 (DALW)",
       "V5": "V5 (HAM+P2)", "V6": "V6 (HAM+DALW)", "V7": "V7 (P2+DALW)",
       "V8": "V8 (penuh)"}
KELAS_ID = {"big-vehicle": "kendaraan besar", "car": "mobil",
            "pedestrian": "pejalan kaki", "two-wheeler": "kendaraan roda dua"}
STRATA_ID = {"small": "kecil", "medium": "sedang", "large": "besar", "no": "tanpa oklusi",
             "partial": "oklusi parsial", "heavy": "oklusi berat", "sparse": "renggang",
             "dense": "padat"}


def tulis_bab4(doc) -> Nomor:
    N = Nomor(4)
    gm = {r["variant"]: r for r in baca_csv("04_ablasi_deteksi/global_metrics.csv")}
    wil = {r["pair"]: r for r in baca_csv("04_ablasi_deteksi/wilcoxon_ap5095.csv")}
    boot = {r["pair"]: r for r in baca_csv("04_ablasi_deteksi/bootstrap_ci.csv")}
    dstr = baca_csv("04_ablasi_deteksi/delta_strata.csv")
    komp = {r["variant"]: r for r in baca_csv("03_kompleksitas_model/tabel_kompleksitas.csv")}
    nms = {r["variant"]: r for r in baca_csv("05_analisis_nmsfree/summary.csv")}
    grid = baca_csv("02_grid_search_dalw/tabel_grid_search.csv")
    alfa = baca_csv("06_sensitivitas_alpha/tabel_sensitivitas_alpha.csv")
    norm = baca_csv("07_ketegaran_normalisasi/tabel_perbandingan_normalisasi.csv")
    okl = baca_json("08_validasi_oklusi/hasil_kesesuaian.json")
    cnt = baca_csv("09_counting_end_to_end/ringkasan_counting_per_klip.csv")
    gab = baca_csv("09_counting_end_to_end/metrik_GABUNGAN.csv")[0]
    band = baca_csv("09_counting_end_to_end/perbandingan_sistem_vs_manual.csv")
    dist = baca_csv("01_dataset/distribusi_kelas.csv")
    g_str = baca_csv("11_analisis_galat/dekomposisi_fp_fn.csv")
    g_kls = baca_csv("11_analisis_galat/galat_per_kelas.csv")
    g_sm = baca_csv("11_analisis_galat/galat_siang_malam.csv")
    kasus = baca_csv("11_analisis_galat/kasus_kegagalan.csv")

    def ds(pair, dim, stratum, kolom="delta_pp_selmin"):
        for r in dstr:
            if r["pasangan"] == pair and r["dim"] == dim and r["stratum"] == stratum:
                return r[kolom] or None
        return None

    def gs(varian, dim, stratum, kolom):
        for r in g_str:
            if r["varian"] == varian and r["dim"] == dim and r["stratum"] == stratum:
                return r[kolom]
        return "-"

    def gk(varian, kelas, kolom):
        for r in g_kls:
            if r["varian"] == varian and r["kelas"] == kelas:
                return r[kolom]
        return "-"

    h1(doc, "BAB IV", "HASIL DAN PEMBAHASAN")

    par(doc, "Bab ini memaparkan hasil seluruh rangkaian eksperimen yang dirancang pada "
             "Bab III beserta pembahasannya. Penyajian disusun mengikuti urutan alur "
             "penelitian, dimulai dari karakteristik data hasil pembagian berbasis kelompok, "
             "dilanjutkan penetapan hiperparameter pembobotan, performa deteksi baik secara "
             "global maupun terstratifikasi beserta pengujian signifikansinya, pemeriksaan "
             "sensitivitas dan ketegaran, biaya komputasi, analisis interaksi dengan "
             "paradigma *NMS-free*, validasi proksi oklusi, akurasi penghitungan kendaraan "
             "menyeluruh, serta analisis galat. Bagian akhir bab merangkum jawaban atas "
             "kelima rumusan masalah sekaligus menyatakan keterbatasan hasil secara terbuka.")

    # ---------------------------------------------------------------- 4.1
    h2(doc, "4.1 Karakteristik Dataset dan Hasil Pembagian Data")
    tr = next(r for r in dist if r["split"] == "train")
    va = next(r for r in dist if r["split"] == "valid")
    te = next(r for r in dist if r["split"] == "test")
    tot = sum(int(r["n_citra"]) for r in dist)
    par(doc, f"Pembagian data berbasis kelompok kamera, adegan, dan sesi perekaman "
             f"sebagaimana dirancang pada Subbab 3.3.2 menghasilkan {rib(tr['n_citra'])} "
             f"citra latih, {rib(va['n_citra'])} citra validasi, dan {rib(te['n_citra'])} "
             f"citra uji dari total {rib(tot)} citra, atau setara proporsi 70,0 persen, 20,0 "
             f"persen, dan 10,0 persen. Prosedur pembagian bersifat deterministik: kelompok "
             f"diurutkan menurut penanda yang stabil lalu dipotong pada ambang kumulatif, "
             f"sehingga pengulangan prosedur pada mesin mana pun menghasilkan pembagian yang "
             f"identik. Pemeriksaan integritas tidak menemukan satu pun citra dengan ringkasan "
             f"*md5* yang sama muncul pada dua subset berbeda, dan tidak ada kelompok yang "
             f"anggotanya tersebar lintas subset. Bukti pembagian tersimpan sebagai dua berkas "
             f"terpisah yang memuat daftar kelompok beserta subset tujuannya dan daftar citra "
             f"beserta kelompok asalnya, dan keduanya dilampirkan pada Lampiran 1.")
    par(doc, "Perlu dicatat bahwa ekspor awal dari layanan anotasi daring yang digunakan "
             "sebelumnya terbukti mengandung kebocoran data, yaitu tiga pasang citra yang "
             "identik secara *byte* muncul pada subset yang berbeda, dengan proporsi pembagian "
             "yang juga menyimpang jauh dari rancangan. Temuan tersebut menjadi alasan "
             "dilakukannya pembagian ulang secara lokal. Tanpa langkah ini, metrik pada data "
             "uji berpotensi melambung secara semu karena model pernah melihat citra yang sama "
             "selama pelatihan.")
    N.tabel(doc, "Komposisi Kelas pada Hasil Pembagian Data Berbasis Kelompok")
    tabel(doc, ["Subset", "Citra", "Kendaraan besar", "Mobil", "Pejalan kaki",
                "Kendaraan roda dua"],
          [[{"train": "Latih", "valid": "Validasi", "test": "Uji"}[r["split"]],
            r["n_citra"], r["big-vehicle"], r["car"], r["pedestrian"], r["two-wheeler"]]
           for r in dist],
          lebar=[2.6, 1.9, 2.9, 2.2, 2.4, 3.1])
    par(doc, f"Komposisi kelas pada Tabel 4.1 memperlihatkan bahwa kendaraan roda dua "
             f"merupakan kelas dengan jumlah instans terbesar pada subset latih, sejalan "
             f"dengan karakteristik lalu lintas yang dijelaskan pada Bab I. Pada subset uji, "
             f"seluruh kelas terwakili dengan jumlah instans sekurang-kurangnya "
             f"{min(int(te[k]) for k in ('big-vehicle', 'car', 'pedestrian', 'two-wheeler'))} "
             f"objek sehingga evaluasi per kelas tetap dapat dilakukan. Meskipun demikian, "
             f"jumlah instans yang tidak berimbang antarkelas perlu diingat ketika menafsirkan "
             f"metrik agregat, karena kelas dengan jumlah instans besar memberi pengaruh lebih "
             f"besar terhadap nilai rata-rata.")
    gambar(doc, N, "01_dataset/distribusi_kelas.png",
           "Distribusi Jumlah Instans Setiap Kelas pada Ketiga Subset")

    # ---------------------------------------------------------------- 4.2
    h2(doc, "4.2 Inisialisasi Model dan Transfer Bobot Pralatih")
    par(doc, "Sebelum pelatihan dijalankan, bobot pralatih dari korpus MS COCO dipindahkan ke "
             "setiap varian arsitektur. Karena penyisipan modul atensi hibrida dan lapisan "
             "deteksi P2 menggeser seluruh indeks lapisan pada kepala deteksi, pemindahan "
             "bobot memerlukan pemetaan ulang nama parameter, bukan sekadar pemuatan langsung. "
             "Hasil pemindahan menunjukkan bahwa varian ber-atensi hibrida menerima 97 persen "
             "kunci parameter yang setara dengan 100 persen volume parameter, sedangkan varian "
             "yang memuat lapisan P2 hanya menerima 40 persen kunci yang setara dengan 62 "
             "persen volume parameter. Kombinasi keduanya menerima 40 persen kunci dan 63 "
             "persen volume parameter.")
    par(doc, "Perbedaan tersebut memiliki penjelasan struktural yang jelas. Modul atensi "
             "hibrida disisipkan sebagai blok tambahan tanpa mengubah dimensi keluaran "
             "lapisan yang sudah ada, sehingga hampir seluruh bobot lama tetap berlaku. "
             "Sebaliknya, lapisan deteksi P2 menambahkan jalur beresolusi tinggi yang tidak "
             "memiliki padanan pada model pralatih, sehingga sebagian besar parameter kepala "
             "deteksi harus diinisialisasi ulang secara acak. Konsekuensi praktisnya, varian "
             "yang memuat lapisan P2 memerlukan waktu pelatihan yang jauh lebih panjang untuk "
             "mencapai konvergensi, sebagaimana terlihat pada Subbab 4.7.")

    # ---------------------------------------------------------------- 4.3
    h2(doc, "4.3 Hasil Pencarian Grid Hiperparameter Pembobotan")
    juara = grid[0]
    par(doc, f"Pencarian grid atas parameter kekuatan pembobotan dan lebar kernel densitas "
             f"dijalankan pada varian penuh dengan pelatihan dipersingkat menjadi 60 epoch "
             f"untuk setiap kombinasi, sehingga total sembilan kombinasi memerlukan 540 epoch "
             f"pelatihan. Kriteria pemilihan adalah nilai mAP@0,5:0,95 tertinggi pada subset "
             f"validasi, dan hasilnya disajikan pada Tabel 4.2. Kombinasi terbaik adalah "
             f"kekuatan pembobotan sebesar {ind(juara['alpha'], 1)} dengan lebar kernel "
             f"sebesar {ind(juara['sigma'], 2)} yang mencapai "
             f"{ind(juara['mAP50_95'], 4)}. Nilai tersebut selanjutnya dibekukan dan dipakai "
             f"seragam pada seluruh varian yang memuat pembobotan agar perbandingan antarvarian "
             f"tetap adil.")
    N.tabel(doc, "Hasil Pencarian Grid Parameter Pembobotan Loss Berbasis Densitas")
    tabel(doc, ["Peringkat", "Kekuatan pembobotan", "Lebar kernel", "mAP@0,5:0,95 (validasi)"],
          [[str(i), ind(r["alpha"], 1), ind(r["sigma"], 2), ind(r["mAP50_95"], 4)]
           for i, r in enumerate(grid, 1)], lebar=[2.4, 4.4, 3.4, 4.9])
    ter = grid[-1]
    par(doc, f"Pola yang muncul dari Tabel 4.2 layak dicermati. Kombinasi pemenang berada di "
             f"titik dalam grid, bukan di tepi, sehingga tidak ada indikasi bahwa nilai optimal "
             f"terletak di luar rentang yang diuji. Kekuatan pembobotan bernilai 0,5 secara "
             f"konsisten menempati peringkat terbawah, yang menunjukkan bahwa pembobotan yang "
             f"terlalu lemah nyaris tidak mengubah perilaku fungsi kerugian. Selain itu tampak "
             f"kecenderungan bahwa lebar kernel optimal bergeser membesar seiring naiknya "
             f"kekuatan pembobotan. Rentang antara kombinasi terbaik dan terburuk hanya "
             f"{ind(float(juara['mAP50_95']) - float(ter['mAP50_95']), 4)}, sehingga pemilihan "
             f"hiperparameter ini bukan faktor penentu utama performa akhir.")
    gambar(doc, N, "02_grid_search_dalw/heatmap_grid_search.png",
           "Peta Panas Hasil Pencarian Grid Kekuatan Pembobotan dan Lebar Kernel", 12.5)
    par(doc, "Keterbatasan pencarian ini telah diakui sejak Subbab 3.9, yaitu pencarian "
             "dilakukan satu kali pada satu varian dengan pelatihan dipersingkat. Pemeriksaan "
             "sensitivitas pada Subbab 4.6 menunjukkan bahwa keterbatasan tersebut memang "
             "berkonsekuensi nyata.")

    # ---------------------------------------------------------------- 4.4
    h2(doc, "4.4 Performa Deteksi Global Antarvarian")
    urut = sorted(gm.values(), key=lambda r: -float(r["mAP50_95"]))
    v1, v8 = gm["V1"], gm["V8"]
    par(doc, f"Kedelapan varian berhasil dilatih hingga konvergen tanpa satu pun mengalami "
             f"kegagalan numerik maupun kehabisan memori, dengan konfigurasi yang identik "
             f"sebagaimana disyaratkan rancangan ablasi. Tabel 4.3 menyajikan metrik deteksi "
             f"global pada subset uji. Nilai mAP@0,5:0,95 kedelapan varian berhimpit pada "
             f"rentang {ind(min(float(r['mAP50_95']) for r in gm.values()), 4)} hingga "
             f"{ind(max(float(r['mAP50_95']) for r in gm.values()), 4)}, yaitu rentang selebar "
             f"kurang dari dua poin persentase.")
    N.tabel(doc, "Metrik Deteksi Global Delapan Varian pada Subset Uji")
    tabel(doc, ["Varian", "Presisi (%)", "*Recall* (%)", "F1 (%)", "mAP@0,5 (%)",
                "mAP@0,5:0,95 (%)"],
          [[LBL[r["variant"]], ind(r["P"], 2, True), ind(r["R"], 2, True),
            ind(r["F1"], 2, True), ind(r["mAP50"], 2, True), ind(r["mAP50_95"], 2, True)]
           for r in [gm[f"V{i}"] for i in range(1, 9)]],
          lebar=[3.1, 2.5, 2.5, 2.1, 2.6, 3.1])
    par(doc, f"Konfigurasi penuh yang diusulkan mencatat mAP@0,5:0,95 tertinggi di antara "
             f"kedelapan varian, yaitu {ind(v8['mAP50_95'], 2, True)} persen, sedikit di atas "
             f"model dasar yang mencapai {ind(v1['mAP50_95'], 2, True)} persen. Selisihnya "
             f"hanya {ind((float(v8['mAP50_95']) - float(v1['mAP50_95'])) * 100, 2)} poin "
             f"persentase. Pada metrik mAP@0,5 justru model dasar yang unggul dengan "
             f"{ind(v1['mAP50'], 2, True)} persen berbanding "
             f"{ind(v8['mAP50'], 2, True)} persen, dan keunggulan model dasar juga tampak pada "
             f"presisi serta F1. Temuan ini disampaikan apa adanya karena memberi informasi "
             f"penting: peringkat antarvarian bergantung pada metrik yang dipilih, sehingga "
             f"kesimpulan tidak boleh ditarik dari satu angka agregat saja.")
    par(doc, "Kerapatan nilai antarvarian tersebut sekaligus menjadi alasan mengapa unit "
             "pengujian hipotesis pada penelitian ini bukan metrik global, melainkan nilai "
             "*average precision* pada setiap sel kombinasi kelas dan strata sebagaimana "
             "ditetapkan Subbab 3.11.5. Metrik global merata-ratakan perilaku pada seluruh "
             "kondisi sehingga perbedaan yang hanya muncul pada kondisi tertentu, misalnya "
             "objek kecil atau adegan padat, dapat tersamarkan.")
    gambar(doc, N, "04_ablasi_deteksi/grafik_map_per_varian.png",
           "Perbandingan mAP@0,5 dan mAP@0,5:0,95 Delapan Varian pada Subset Uji")

    # ---------------------------------------------------------------- 4.5
    h2(doc, "4.5 Hasil Ablasi Terstratifikasi dan Uji Signifikansi Statistik")
    h1_, h2_, h3_ = wil["V8 vs V1"], wil["V4 vs V1"], wil["V8 vs V5"]
    b1, b2, b3 = boot["V8 vs V1"], boot["V4 vs V1"], boot["V8 vs V5"]
    par(doc, f"Pengujian dilakukan atas tiga hipotesis utama yang ditetapkan di muka, tanpa "
             f"koreksi perbandingan ganda, sedangkan seluruh pasangan lain diperlakukan sebagai "
             f"pengujian sekunder dengan koreksi Holm. Penerapan aturan sel minimum sebesar 30 "
             f"objek kebenaran dasar sebagaimana disyaratkan Subbab 3.11.5 menyisakan "
             f"{h1_['n']} sel dari 36 sel yang mungkin, dengan {h1_['n_sel_dibuang']} sel "
             f"dikeluarkan karena volumenya terlalu kecil. Daftar lengkap sel yang dikeluarkan "
             f"disajikan pada Lampiran 3 dan tidak dihilangkan secara diam-diam.")
    N.tabel(doc, "Hasil Uji Wilcoxon dan Selang Kepercayaan Bootstrap untuk Tiga Hipotesis Utama")
    tabel(doc, ["Hipotesis", "Statistik W", "Nilai p", "Korelasi *rank-biserial*",
                "Median selisih", "Selang *bootstrap* 95% (poin persentase)", "Simpulan"],
          [["H1: V8 terhadap V1", h1_["W"], ind(h1_["p"], 3), ind(h1_["rank_biserial"], 3),
            ind(h1_["median_diff"], 4),
            f"[{ind(float(b1['ci_lo']) * 100, 2)}; {ind(float(b1['ci_hi']) * 100, 2)}]",
            "tidak signifikan"],
           ["H2: V4 terhadap V1", h2_["W"], ind(h2_["p"], 3), ind(h2_["rank_biserial"], 3),
            ind(h2_["median_diff"], 4),
            f"[{ind(float(b2['ci_lo']) * 100, 2)}; {ind(float(b2['ci_hi']) * 100, 2)}]",
            "tidak didukung"],
           ["H3: V8 terhadap V5", h3_["W"], ind(h3_["p"], 4), ind(h3_["rank_biserial"], 3),
            ind(h3_["median_diff"], 4),
            f"[{ind(float(b3['ci_lo']) * 100, 2)}; {ind(float(b3['ci_hi']) * 100, 2)}]",
            "signifikan"]],
          lebar=[3.0, 1.7, 1.5, 2.2, 1.9, 3.2, 2.4], size_body=8)
    par(doc, f"Hipotesis pertama yang membandingkan konfigurasi penuh terhadap model dasar "
             f"menghasilkan nilai p sebesar {ind(h1_['p'], 3)} sehingga tidak signifikan pada "
             f"taraf lima persen. Namun selang kepercayaan *bootstrap* pada tataran citra untuk "
             f"pasangan yang sama terbentang dari {ind(float(b1['ci_lo']) * 100, 2)} hingga "
             f"{ind(float(b1['ci_hi']) * 100, 2)} poin persentase dan tidak memuat nol. Kedua "
             f"hasil ini tidak saling bertentangan karena menjawab pertanyaan yang berbeda. Uji "
             f"Wilcoxon menguji konsistensi arah selisih antarsel, sedangkan selang *bootstrap* "
             f"menguji besar selisih agregat antarcitra. Nilai p yang besar berarti perbaikan "
             f"tidak konsisten arah, sebagian sel naik dan sebagian turun, sementara batas bawah "
             f"selang yang hanya {ind(float(b1['ci_lo']) * 100, 2)} poin persentase menunjukkan "
             f"bahwa besar perbaikan agregat pun praktis menyentuh nol. Keduanya dilaporkan "
             f"bersama sebagaimana dijanjikan Subbab 3.11.5.")
    par(doc, f"Hipotesis kedua yang menguji pembobotan berbasis densitas secara berdiri "
             f"sendiri tidak didukung data. Nilai p sebesar {ind(h2_['p'], 3)} disertai "
             f"korelasi *rank-biserial* bertanda negatif sebesar {ind(h2_['rank_biserial'], 3)} "
             f"dan median selisih sebesar {ind(h2_['median_diff'], 4)}. Arah efek yang negatif "
             f"menutup kemungkinan menafsirkan hasil ini sebagai kecenderungan positif yang "
             f"belum mencapai signifikansi. Penafsiran yang tepat adalah bahwa pembobotan "
             f"berbasis densitas tanpa dukungan modifikasi arsitektural tidak memberi perbaikan "
             f"pada performa terstratifikasi.")
    par(doc, f"Hipotesis ketiga memberikan hasil yang berbeda. Perbandingan konfigurasi penuh "
             f"terhadap kombinasi atensi hibrida dan lapisan P2, yang secara efektif "
             f"mengisolasi kontribusi tambahan pembobotan berbasis densitas di atas fondasi "
             f"arsitektural, menghasilkan nilai p sebesar {ind(h3_['p'], 4)} dengan korelasi "
             f"*rank-biserial* sebesar {ind(h3_['rank_biserial'], 3)} yang tergolong efek "
             f"sedang. Selang *bootstrap* untuk pasangan ini terbentang dari "
             f"{ind(float(b3['ci_lo']) * 100, 2)} hingga {ind(float(b3['ci_hi']) * 100, 2)} "
             f"poin persentase dan jelas menjauhi nol. Dua metode pengujian yang berbeda "
             f"karenanya memberikan simpulan yang sama, dan inilah temuan paling kokoh dari "
             f"seluruh rangkaian ablasi.")
    gambar(doc, N, "04_ablasi_deteksi/grafik_wilcoxon_hipotesis_utama.png",
           "Ukuran Efek Rank-Biserial Tiga Hipotesis Utama", 13.0)
    gambar(doc, N, "04_ablasi_deteksi/grafik_bootstrap_ci.png",
           "Selang Kepercayaan Bootstrap 95 Persen Selisih mAP@0,5:0,95", 12.5)
    par(doc, "Gabungan ketiga hasil tersebut mengarah pada satu simpulan yang konsisten "
             "dengan pembingkaian kebaruan pada Bab I dan Bab III. Pembobotan *loss* berbasis "
             "densitas bersifat komplementer terhadap modifikasi arsitektural: kontribusinya "
             "nyata dan signifikan ketika ditumpangkan pada arsitektur yang telah diperkuat "
             "atensi hibrida dan lapisan P2, tetapi tidak muncul ketika diterapkan sendirian. "
             "Simpulan ini juga sejalan dengan ramalan yang telah dituliskan pada Bab II, "
             "yakni bahwa arsitektur dasar YOLO26 telah memuat mekanisme penetapan label "
             "adaptif berbasis ukuran sehingga ruang perbaikan yang tersisa lebih sempit "
             "dibandingkan penelitian terdahulu yang membandingkan modifikasinya terhadap "
             "detektor berbasis *non-maximum suppression* tanpa mekanisme serupa.")

    h3(doc, "4.5.1 Performa Terstratifikasi menurut Ukuran, Oklusi, dan Densitas")
    par(doc, "Analisis terstratifikasi menjawab rumusan masalah keempat dengan memeriksa pada "
             "kondisi apa perbaikan benar-benar terjadi. Selisih nilai *average precision* "
             "dihitung hanya dari sel yang memenuhi aturan sel minimum, sama seperti aturan "
             "yang dipakai pada pengujian signifikansi, agar tidak terjadi ketidakkonsistenan "
             "antara angka yang diuji dan angka yang dinarasikan.")
    N.tabel(doc, "Selisih AP@0,5:0,95 Antarstrata pada Sel yang Memenuhi Aturan Sel Minimum")
    baris = []
    for dim, nama_dim in (("size", "Ukuran"), ("occlusion", "Oklusi"), ("density", "Densitas")):
        for st in (("small", "medium", "large") if dim == "size" else
                   ("no", "partial", "heavy") if dim == "occlusion" else
                   ("sparse", "medium", "dense")):
            a, b = ds("V8-V1", dim, st), ds("V8-V5", dim, st)
            ket = next((r["layak_dinarasikan"] for r in dstr
                        if r["pasangan"] == "V8-V1" and r["dim"] == dim and r["stratum"] == st),
                       "")
            baris.append([f"{nama_dim} — {STRATA_ID.get(st, st)}",
                          a.replace(".", ",").replace("-", "−") if a else "tidak tersedia",
                          b.replace(".", ",").replace("-", "−") if b else "tidak tersedia",
                          "ya" if ket == "ya" else "tidak"])
    tabel(doc, ["Strata", "V8 − V1 (poin persentase)", "V8 − V5 (poin persentase)",
                "Layak dinarasikan"], baris, lebar=[4.6, 4.0, 4.0, 3.4])
    par(doc, f"Perbaikan terbesar dari kontribusi pembobotan berbasis densitas terjadi pada "
             f"strata oklusi parsial sebesar {ds('V8-V5', 'occlusion', 'partial').replace('.', ',').replace('-', '−')} "
             f"poin persentase dan pada strata objek berukuran kecil sebesar "
             f"{ds('V8-V5', 'size', 'small').replace('.', ',').replace('-', '−')} poin persentase. Kedua strata "
             f"tersebut merupakan dua dari tiga tantangan yang diidentifikasi pada Bab I, "
             f"sehingga hasil ini memberi dukungan langsung terhadap premis penelitian.")
    par(doc, "Tantangan ketiga, yaitu kepadatan ekstrem, justru tidak dapat dinilai. Setelah "
             "aturan sel minimum diterapkan, satu-satunya kelas yang memenuhi ambang pada "
             "strata densitas padat adalah pejalan kaki, yaitu kelas konteks yang menurut "
             "rancangan penelitian dikecualikan dari penghitungan kendaraan. Ketiga kelas "
             "kendaraan pada strata tersebut masing-masing hanya memuat 1, 11, dan 21 objek "
             "sehingga nilai *average precision*-nya tidak stabil. Dengan demikian tidak ada "
             "kesimpulan yang dapat ditarik mengenai performa pada kondisi kepadatan ekstrem "
             "dari data uji ini, dan keterbatasan tersebut dinyatakan terbuka pada Subbab 4.12.")
    for dim, judul in (("size", "Ukuran Objek"), ("occlusion", "Tingkat Oklusi"),
                       ("density", "Kepadatan Adegan")):
        gambar(doc, N, f"04_ablasi_deteksi/grafik_strata_{dim}.png",
               f"AP@0,5:0,95 Terstratifikasi menurut {judul}", 12.5)

    # ---------------------------------------------------------------- 4.6
    h2(doc, "4.6 Sensitivitas Parameter dan Pemeriksaan Ketegaran")
    h3(doc, "4.6.1 Sensitivitas terhadap Kekuatan Pembobotan")
    a05, a10, a20 = alfa[0], alfa[1], alfa[2]
    par(doc, f"Subbab 3.9 mengakui bahwa pencarian grid dilakukan satu kali pada varian penuh "
             f"sehingga nilai yang dibekukan belum tentu optimal bagi varian lain. Untuk "
             f"menguji konsekuensi keterbatasan tersebut, varian yang hanya memuat pembobotan "
             f"berbasis densitas dilatih ulang pada dua nilai kekuatan pembobotan tambahan "
             f"dengan lebar kernel dipertahankan. Hasilnya disajikan pada Tabel 4.6.")
    N.tabel(doc, "Sensitivitas Performa terhadap Kekuatan Pembobotan pada Varian V4")
    tabel(doc, ["Kekuatan pembobotan", "Epoch total", "Epoch terbaik",
                "mAP@0,5:0,95 validasi", "mAP@0,5:0,95 uji", "mAP@0,5 uji", "Jam latih"],
          [[ind(r["alpha"], 1), r["epoch_total"], r["epoch_terbaik"],
            ind(r["mAP50_95_val_terbaik"], 4), ind(r["mAP50_95_TEST"], 4),
            ind(r["mAP50_TEST"], 4), ind(r["jam_latih"], 2)] for r in alfa],
          lebar=[2.9, 2.0, 2.2, 2.7, 2.4, 2.2, 1.7], size_body=8)
    par(doc, f"Nilai kekuatan pembobotan sebesar {ind(a20['alpha'], 1)} menghasilkan "
             f"mAP@0,5:0,95 pada data uji sebesar {ind(a20['mAP50_95_TEST'], 4)}, lebih tinggi "
             f"daripada nilai yang dipakai pada ablasi utama yang mencapai "
             f"{ind(a10['mAP50_95_TEST'], 4)}, dan juga lebih tinggi daripada seluruh varian "
             f"pada Tabel 4.3. Keunggulan tersebut konsisten pada subset validasi, yaitu "
             f"{ind(a20['mAP50_95_val_terbaik'], 4)} berbanding "
             f"{ind(a10['mAP50_95_val_terbaik'], 4)}, sehingga bukan sekadar kebetulan pada "
             f"data uji. Temuan ini mengonfirmasi secara empiris keterbatasan pencarian grid "
             f"satu titik yang telah diakui sejak Bab III.")
    par(doc, "Meskipun demikian, nilai yang dibekukan tetap dipertahankan untuk seluruh "
             "analisis ablasi. Mengganti kekuatan pembobotan hanya pada sebagian varian akan "
             "merusak keadilan perbandingan yang menjadi syarat rancangan ablasi, sedangkan "
             "melatih ulang kedelapan varian pada nilai baru berada di luar anggaran komputasi "
             "yang tersedia. Varian dengan kekuatan pembobotan lebih tinggi karena itu "
             "dilaporkan sebagai hasil pemeriksaan sensitivitas, bukan sebagai konfigurasi "
             "yang diusulkan, karena memilihnya berdasarkan skor pada data uji akan menjadi "
             "bentuk seleksi yang mencemari validitas evaluasi.")
    gambar(doc, N, "06_sensitivitas_alpha/grafik_sensitivitas_alpha.png",
           "Pengaruh Kekuatan Pembobotan terhadap Performa Validasi dan Uji", 12.5)

    h3(doc, "4.6.2 Pemeriksaan Ketegaran Skema Normalisasi")
    nd, nw = norm[0], norm[1]
    par(doc, f"Pemeriksaan berikutnya menguji apakah perolehan pembobotan berbasis densitas "
             f"bersumber dari mekanisme yang diklaim, yaitu penekanan relatif pada objek di "
             f"wilayah padat, ataukah sekadar efek perubahan skala fungsi kerugian. Varian "
             f"penuh dilatih ulang dengan pembagi fungsi kerugian diganti menjadi jumlah bobot, "
             f"bukan jumlah objek, sehingga skala kerugian dipertahankan dan penguatan absolut "
             f"pada citra padat dihilangkan. Hasilnya, mAP@0,5:0,95 pada data uji sebesar "
             f"{ind(nw['mAP50_95_TEST'], 4)} berbanding {ind(nd['mAP50_95_TEST'], 4)} pada "
             f"skema bawaan, yaitu selisih kurang dari dua per sepuluh poin persentase dan "
             f"tidak signifikan secara statistik. Dengan kata lain, perolehan pembobotan bukan "
             f"artefak penskalaan fungsi kerugian. Hasil ini menguntungkan klaim penelitian "
             f"karena menyingkirkan penjelasan alternatif yang paling sederhana.")
    N.tabel(doc, "Perbandingan Skema Normalisasi Fungsi Kerugian Berbobot")
    tabel(doc, ["Skema normalisasi", "Epoch tercatat", "Epoch terbaik",
                "mAP@0,5:0,95 validasi", "mAP@0,5:0,95 uji", "mAP@0,5 uji"],
          [[r["run"], r["epoch_tercatat"], r["epoch_terbaik"],
            ind(r["mAP50_95_val_terbaik"], 4), ind(r["mAP50_95_TEST"], 4),
            ind(r["mAP50_TEST"], 4)] for r in norm],
          lebar=[4.6, 2.2, 2.2, 2.7, 2.4, 2.0], size_body=8)
    gambar(doc, N, "07_ketegaran_normalisasi/grafik_ketegaran_normalisasi.png",
           "Perbandingan Dua Skema Normalisasi pada Varian Penuh", 12.0)

    # ---------------------------------------------------------------- 4.7
    h2(doc, "4.7 Kompleksitas dan Efisiensi Model")
    par(doc, "Tabel 4.8 menyajikan biaya komputasi setiap varian sebagaimana dijanjikan Tabel "
             "3.8 pada Bab III. Angka laju bingkai pada tabel ini diukur pada tolok ukur model "
             "murni, yaitu tanpa pelacakan dan tanpa penghitungan lintasan, sehingga tidak "
             "boleh dibaca sebagai kecepatan sistem menyeluruh. Kecepatan sistem yang "
             "sesungguhnya dilaporkan pada Subbab 4.10.")
    N.tabel(doc, "Kompleksitas dan Efisiensi Delapan Varian")
    tabel(doc, ["Varian", "Parameter (juta)", "GFLOPs", "Ukuran (MB)",
                "VRAM latih (GB)", "VRAM inferensi (GB)", "Jam latih", "Epoch",
                "Laju bingkai model"],
          [[LBL[r["variant"]], ind(r["params_M"], 3), ind(r["gflops"], 2),
            ind(r["size_MB"], 2), ind(r["peak_gpu_train_gb"], 2),
            ind(r["peak_gpu_infer_gb"], 3), ind(r["train_hours"], 2), r["epochs"],
            ind(r["fps"], 2)] for r in [komp[f"V{i}"] for i in range(1, 9)]],
          lebar=[2.5, 2.1, 1.5, 1.8, 1.9, 2.1, 1.5, 1.2, 2.0], size_body=8)
    par(doc, f"Pola biaya terbagi tegas menurut ada tidaknya lapisan deteksi P2. Varian tanpa "
             f"lapisan tersebut memerlukan sekitar 5 gigabita memori GPU dan selesai dalam "
             f"kurang dari dua jam, sedangkan varian yang memuatnya memerlukan "
             f"{ind(komp['V8']['peak_gpu_train_gb'], 2)} gigabita dan hingga "
             f"{ind(komp['V8']['train_hours'], 2)} jam. Perbedaan ini bersumber dari kepala "
             f"deteksi beresolusi tinggi yang menghasilkan sekitar empat kali lipat jumlah "
             f"titik jangkar. Seluruh pelatihan tetap berjalan pada ukuran *batch* yang sama "
             f"untuk kedelapan varian dan tidak satu pun mengalami kehabisan memori, sehingga "
             f"strategi cadangan berupa penurunan ukuran *batch* yang disiapkan pada Bab III "
             f"tidak pernah dipicu.")
    par(doc, f"Temuan yang paling relevan bagi penerapan adalah bahwa pembobotan berbasis "
             f"densitas tidak menambah biaya inferensi sama sekali. Varian yang hanya memuat "
             f"pembobotan memiliki jumlah parameter, GFLOPs, dan ukuran model yang identik "
             f"dengan model dasar, yaitu {ind(komp['V4']['params_M'], 3)} juta parameter dan "
             f"{ind(komp['V4']['gflops'], 2)} GFLOPs. Hal ini merupakan konsekuensi langsung "
             f"dari sifat mekanismenya yang hanya bekerja pada tahap penghitungan fungsi "
             f"kerugian saat pelatihan dan sama sekali tidak mengubah grafik komputasi "
             f"inferensi. Dengan demikian komponen yang merupakan kebaruan metodologis "
             f"penelitian ini justru satu-satunya komponen yang tidak membebani penerapan.")
    gambar(doc, N, "03_kompleksitas_model/grafik_kompleksitas_4panel.png",
           "Perbandingan Empat Dimensi Kompleksitas Antarvarian", 13.5)
    gambar(doc, N, "03_kompleksitas_model/grafik_tradeoff_akurasi_fps.png",
           "Pertukaran antara Akurasi dan Kecepatan Inferensi Model", 12.5)

    # ---------------------------------------------------------------- 4.8
    h2(doc, "4.8 Analisis Interaksi dengan Paradigma NMS-free")
    par(doc, "Analisis ini merupakan pilar kebaruan kedua penelitian, yaitu penyelidikan "
             "empiris mengenai bagaimana modifikasi yang diusulkan berinteraksi dengan "
             "mekanisme pencocokan satu-ke-satu yang menjadi ciri paradigma *NMS-free*. "
             "Instrumentasi dijalankan pada varian yang memuat lapisan P2 beserta model dasar "
             "sebagai pembanding, sesuai fokus yang ditetapkan Subbab 3.7.")
    N.tabel(doc, "Duplicate Rate dan Confidence Margin pada Subset Uji")
    tabel(doc, ["Varian", "*Duplicate Rate*", "Selisih terhadap V1", "Objek terlewat",
                "Duplikat", "Cakupan", "*Confidence Margin* rata-rata",
                "Selisih terhadap V1"],
          [[LBL[r["variant"]], ind(r["DR"], 4), ind(r["dDR_vs_V1"], 4), ind(r["miss"], 4),
            ind(r["dup"], 4), ind(r["coverage"], 4), ind(r["cm_mean"], 4),
            ind(r["dCM_vs_V1"], 4)] for r in nms.values()],
          lebar=[2.5, 2.2, 2.3, 2.0, 1.7, 1.7, 2.6, 2.3], size_body=8)
    v3, v5, v7, v8n = nms["V3"], nms["V5"], nms["V7"], nms["V8"]
    par(doc, f"Pola yang muncul konsisten dan cukup tegas. Varian yang memuat lapisan P2 tanpa "
             f"atensi hibrida mengalami penurunan pada kedua indikator: varian P2 tunggal turun "
             f"sebesar {ind(v3['dDR_vs_V1'], 4)} pada *Duplicate Rate* dan "
             f"{ind(v3['dCM_vs_V1'], 4)} pada *Confidence Margin*, sedangkan varian yang "
             f"menggabungkan P2 dengan pembobotan turun sebesar {ind(v7['dDR_vs_V1'], 4)} dan "
             f"{ind(v7['dCM_vs_V1'], 4)}. Sebaliknya, begitu atensi hibrida ditambahkan, kedua "
             f"indikator justru naik di atas model dasar, yaitu {ind(v5['dDR_vs_V1'], 4)} dan "
             f"{ind(v5['dCM_vs_V1'], 4)} pada kombinasi atensi dengan P2, serta "
             f"{ind(v8n['dDR_vs_V1'], 4)} dan {ind(v8n['dCM_vs_V1'], 4)} pada konfigurasi "
             f"penuh.")
    par(doc, "Penafsiran yang paling masuk akal atas pola tersebut adalah bahwa penambahan "
             "lapisan deteksi beresolusi tinggi memperbanyak kandidat prediksi pada wilayah "
             "spasial yang berdekatan sehingga mekanisme pencocokan satu-ke-satu menghadapi "
             "persaingan yang lebih ketat, dan akibatnya margin keyakinan antara kandidat "
             "terpilih dengan pesaing terdekatnya menyempit. Modul atensi hibrida tampaknya "
             "berperan menajamkan kembali pembedaan antarkandidat tersebut sehingga kepala "
             "satu-ke-satu memperoleh sinyal yang lebih tegas. Dengan demikian atensi hibrida "
             "berfungsi sebagai penstabil bagi kepadatan prediksi yang ditimbulkan lapisan P2, "
             "dan inilah jawaban atas rumusan masalah ketiga.")
    gambar(doc, N, "05_analisis_nmsfree/grafik_dr_cm_ringkasan.png",
           "Duplicate Rate dan Confidence Margin Relatif terhadap Model Dasar", 13.0)
    gambar(doc, N, "05_analisis_nmsfree/grafik_stabilitas_assignment.png",
           "Stabilitas Penetapan Antar-Epoch Selama Pelatihan", 12.5)
    par(doc, "Stabilitas penetapan antar-epoch yang diformalkan pada Persamaan 3.8 terpantau "
             "pada seluruh varian dan menunjukkan kecenderungan menaik hingga mendekati nilai "
             "satu menjelang akhir pelatihan. Hal ini menandakan bahwa pasangan antara prediksi "
             "dan objek kebenaran dasar semakin jarang berpindah antar-epoch, yaitu perilaku "
             "yang diharapkan dari mekanisme pencocokan yang konvergen. Tidak ditemukan varian "
             "yang mengalami osilasi penetapan berkepanjangan, sehingga tidak ada indikasi "
             "bahwa modifikasi yang diusulkan mengganggu kestabilan mekanisme *NMS-free*.")
    gambar(doc, N, "05_analisis_nmsfree/grafik_tau_sweep_ulang.png",
           "Sensitivitas Duplicate Rate terhadap Ambang Tumpang Tindih", 12.5)
    par(doc, "Pemeriksaan sensitivitas terhadap ambang tumpang tindih menunjukkan penurunan "
             "yang mulus dan monoton pada seluruh varian tanpa titik patah yang janggal. "
             "Urutan relatif antarvarian juga bertahan pada hampir seluruh rentang ambang, "
             "sehingga simpulan yang ditarik pada ambang yang ditetapkan Bab III tidak "
             "bergantung pada pemilihan nilai ambang tertentu. Data lengkap dua belas nilai "
             "ambang disajikan pada Lampiran 7.")

    # ---------------------------------------------------------------- 4.9
    h2(doc, "4.9 Validasi Proksi Oklusi")
    conf = okl["confusion"]
    # Kappa Cohen dihitung ulang dari matriks agar tidak ada angka yang diketik manual.
    tier = ("no", "partial", "heavy")
    n_tot = sum(conf[a][b] for a in tier for b in tier)
    p_o = sum(conf[t][t] for t in tier) / n_tot
    p_e = sum((sum(conf[a].values()) / n_tot) * (sum(conf[x][a] for x in tier) / n_tot)
              for a in tier)
    kap = (p_o - p_e) / (1 - p_e)
    par(doc, f"Subbab 3.3.3 menjanjikan validasi manual atas proksi oklusi yang diturunkan "
             f"secara komputasional. Janji tersebut ditunaikan dengan menganotasi "
             f"{okl['n']} objek yang diambil secara acak dari subset validasi melalui "
             f"antarmuka buta, artinya penilai tidak mengetahui tingkat oklusi yang diberikan "
             f"proksi. Tingkat kesesuaian yang diperoleh adalah "
             f"{ind(okl['agreement'] * 100, 1)} persen dengan koefisien kappa Cohen sebesar "
             f"{ind(kap, 3)}. Angka ini menempatkan proksi pada kategori kesesuaian sedang, "
             f"cukup untuk stratifikasi kasar tetapi tidak cukup untuk dianggap setara dengan "
             f"penilaian manusia.")
    N.tabel(doc, "Matriks Kesesuaian antara Proksi Oklusi dan Penilaian Manual")
    tabel(doc, ["Penilaian manual", "Proksi: tanpa oklusi", "Proksi: oklusi parsial",
                "Proksi: oklusi berat", "Jumlah"],
          [[STRATA_ID[k].capitalize(), str(conf[k]["no"]), str(conf[k]["partial"]),
            str(conf[k]["heavy"]), str(sum(conf[k].values()))]
           for k in ("no", "partial", "heavy")],
          lebar=[3.6, 3.2, 3.2, 3.0, 2.0])
    n_heavy = sum(conf[k]["heavy"] for k in conf)
    man_heavy = sum(conf["heavy"].values())
    par(doc, f"Tiga temuan penting muncul dari matriks tersebut. Pertama, proksi tidak pernah "
             f"sekali pun memberikan tingkat oklusi berat, yaitu {n_heavy} dari {okl['n']} "
             f"objek, padahal penilai manusia menemukan {man_heavy} objek yang tertutup berat. "
             f"Nilai proksi pada objek-objek tersebut berada jauh di bawah ambang yang "
             f"ditetapkan, bahkan terdapat kasus ekstrem berupa mobil dengan nilai proksi "
             f"mendekati nol yang oleh penilai dinilai tertutup berat. Kedua, galat proksi "
             f"bersifat asimetris, yaitu kecenderungan meremehkan tingkat oklusi lebih besar "
             f"daripada kecenderungan melebih-lebihkannya. Ketiga, kesesuaian paling rendah "
             f"terjadi pada kelas kendaraan roda dua, yaitu kelas yang objeknya paling kecil "
             f"sekaligus paling dominan.")
    par(doc, "Sebab keterbatasan ini dapat diterangkan secara geometris. Proksi menghitung "
             "tumpang tindih antarkotak pembatas, sedangkan oklusi yang dipersepsi manusia "
             "dapat terjadi tanpa tumpang tindih kotak, misalnya ketika kendaraan tertutup "
             "tiang, pepohonan, atau bagian bangunan yang tidak berlabel. Konsekuensinya, "
             "seluruh kesimpulan yang menyangkut strata oklusi berat pada penelitian ini tidak "
             "dapat ditegakkan, dan hal tersebut telah tampak pula pada Subbab 4.5 ketika "
             "seluruh sel oklusi berat gugur akibat aturan sel minimum. Kedua bukti yang saling "
             "bebas ini menunjuk pada keterbatasan yang sama.")
    gambar(doc, N, "08_validasi_oklusi/matriks_konfusi_oklusi.png",
           "Matriks Kesesuaian Proksi Oklusi terhadap Penilaian Manual", 11.5)
    gambar(doc, N, "08_validasi_oklusi/kesesuaian_per_kelas.png",
           "Tingkat Kesesuaian Proksi Oklusi menurut Kelas Objek", 12.0)

    return N, (gm, wil, boot, cnt, gab, band, g_str, g_kls, g_sm, kasus, komp, nms, LBL)
