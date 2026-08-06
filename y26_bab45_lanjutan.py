"""Lanjutan BAB IV (4.10-4.13), BAB V, dan LAMPIRAN.

Dipanggil `y26_tulis_bab45.py` setelah `y26_bab4_isi.tulis_bab4`.
"""
from __future__ import annotations

import csv
from pathlib import Path

from y26_tulis_bab45 import (HB, ROOT, Nomor, baca_csv, baca_json, gambar, h1, h2, h3,
                             halaman_baru, ind, par, rib, tabel)

KELAS_ID = {"big-vehicle": "kendaraan besar", "car": "mobil",
            "pedestrian": "pejalan kaki", "two-wheeler": "kendaraan roda dua"}
STRATA_ID = {"small": "kecil", "medium": "sedang", "large": "besar", "no": "tanpa oklusi",
             "partial": "oklusi parsial", "heavy": "oklusi berat", "sparse": "renggang",
             "dense": "padat"}


def tulis_bab4_lanjutan(doc, N: Nomor, data):
    (gm, wil, boot, cnt, gab, band, g_str, g_kls, g_sm, kasus, komp, nms, LBL) = data
    fps = baca_csv("../counting_out/fps_probe/ringkasan.csv") if (
        HB / "../counting_out/fps_probe/ringkasan.csv").exists() else None

    def gs(v, dim, st, k):
        return next((r[k] for r in g_str
                     if r["varian"] == v and r["dim"] == dim and r["stratum"] == st), "-")

    def gk(v, kelas, k):
        return next((r[k] for r in g_kls if r["varian"] == v and r["kelas"] == kelas), "-")

    def gsm(v, kel, k):
        return next((r[k] for r in g_sm if r["varian"] == v and r["kelompok"] == kel), "-")

    # ---------------------------------------------------------------- 4.10
    h2(doc, "4.10 Penghitungan Kendaraan Menyeluruh")
    par(doc, f"Rumusan masalah kelima dijawab dengan menjalankan sistem penghitungan "
             f"menyeluruh, yaitu detektor konfigurasi penuh yang dirangkai dengan pelacak "
             f"ByteTrack dan penghitungan lintasan garis maya, pada rekaman lalu lintas yang "
             f"tidak pernah dipakai selama pelatihan. Setiap klip berdurasi tepat sepuluh menit "
             f"dan diamati dalam interval enam puluh detik, sehingga terdapat sepuluh jendela "
             f"pengamatan per klip. Setiap jendela mencatat hitungan untuk tiga kelas kendaraan "
             f"pada dua arah, sehingga terkumpul {gab['n_pengamatan']} pasangan pengamatan "
             f"antara hitungan sistem dan hitungan manual. Pejalan kaki dikecualikan sesuai "
             f"rancangan.")
    h3(doc, "4.10.1 Dua Koreksi Metodologis Sebelum Pelaporan")
    par(doc, "Dua persoalan ditemukan pada tahap awal dan keduanya dikoreksi sebelum metrik "
             "akhir dihitung. Persoalan pertama menyangkut konvensi arah. Pustaka penghitungan "
             "lintasan menetapkan arah masuk dan keluar berdasarkan orientasi titik awal dan "
             "titik akhir garis, sedangkan penghitung manusia memakai definisi visualnya "
             "sendiri, yaitu arah menuju kiri bawah bingkai dianggap masuk. Penelusuran "
             "pergerakan objek bingkai demi bingkai pada saat terjadinya setiap peristiwa "
             "lintasan membuktikan bahwa kedua konvensi berlawanan secara seragam pada seluruh "
             "klip. Koreksi dilakukan dengan membalik urutan titik penyusun garis sehingga "
             "geometrinya tetap identik dan hanya arah pembacaannya yang berubah. Dampaknya "
             "besar: galat persentase pada salah satu klip turun dari lebih dari lima puluh "
             "persen menjadi sekitar dua puluh tujuh persen. Tanpa koreksi ini, galat sistem "
             "akan terinflasi oleh pertukaran yang sepenuhnya bersifat konvensi.")
    par(doc, "Persoalan kedua menyangkut satu klip yang akhirnya dikeluarkan dari evaluasi. "
             "Pada klip tersebut sistem sama sekali tidak mencatat mobil sedangkan penghitung "
             "manual mencatat dua puluh mobil. Diagnosis menunjukkan bahwa dua puluh empat "
             "jejak mobil memang terbentuk, tetapi hanya dua di antaranya yang benar-benar "
             "berpindah sisi terhadap garis maya, karena segmen garis yang dipilih berakhir "
             "sebelum mencapai lajur yang dilalui mobil. Ketika garis diganti dengan segmen "
             "tegak lurus yang memotong seluruh lebar jalan, sistem mencatat tepat dua mobil, "
             "sama dengan hitungan manual pada menit yang bersesuaian. Dengan demikian hitungan "
             "manual dan keluaran sistem pada klip tersebut mengukur populasi kendaraan yang "
             "berbeda, sehingga selisihnya merupakan cacat validitas pengukuran, bukan ukuran "
             "performa model. Klip tersebut dikeluarkan dan alasannya dinyatakan terbuka di "
             "sini agar tidak disalahpahami sebagai penyaringan hasil; berkas mentahnya tetap "
             "disimpan sebagai bukti dan dilampirkan pada Lampiran 8.")
    h3(doc, "4.10.2 Akurasi Penghitungan")
    N.tabel(doc, "Metrik Penghitungan Kendaraan per Klip dan Gabungan")
    baris = [[r["klip"].replace("_vidiouji", ""), ind(r["MAE"], 3), ind(r["RMSE"], 3),
              ind(r["MAPE_persen"], 2), r["n_pengamatan"], r["n_dikecualikan_y0"],
              r["total_sistem"], r["total_manual"], ind(r["selisih_agregat_persen"], 1)]
             for r in cnt]
    baris.append(["Gabungan", ind(gab["MAE"], 3), ind(gab["RMSE"], 3),
                  ind(gab["MAPE_persen"], 2), gab["n_pengamatan"],
                  gab["n_dikecualikan_y0"], gab["total_sistem"], gab["total_manual"],
                  ind(gab["selisih_agregat_persen"], 1)])
    tabel(doc, ["Klip", "MAE", "RMSE", "MAPE (%)", "Pengamatan", "Dikecualikan",
                "Sistem", "Manual", "Selisih agregat (%)"], baris,
          lebar=[1.9, 1.5, 1.6, 1.8, 2.1, 2.2, 1.6, 1.6, 2.3], size_body=8)
    par(doc, f"Secara gabungan sistem mencatat *mean absolute error* sebesar "
             f"{ind(gab['MAE'], 3)}, *root mean square error* sebesar {ind(gab['RMSE'], 3)}, "
             f"dan *mean absolute percentage error* sebesar {ind(gab['MAPE_persen'], 2)} "
             f"persen. Sesuai aturan pada Subbab 3.11.3, galat persentase hanya dihitung pada "
             f"interval yang hitungan manualnya bernilai positif, sehingga "
             f"{gab['n_dikecualikan_y0']} dari {gab['n_pengamatan']} pengamatan dikecualikan "
             f"dan proporsinya dilaporkan di sini sebagaimana dijanjikan. Secara agregat sistem "
             f"mencatat {rib(gab['total_sistem'])} perlintasan berbanding {rib(gab['total_manual'])} "
             f"perlintasan hasil hitungan manual, yaitu selisih sebesar "
             f"{ind(gab['selisih_agregat_persen'], 1)} persen.")
    par(doc, "Pola yang paling menonjol adalah kenaikan galat absolut seiring meningkatnya "
             "kepadatan lalu lintas. Pada klip berarus lengang galat rata-rata kurang dari satu "
             "kendaraan per interval, meningkat sedikit pada klip berarus arteri, lalu melonjak "
             "pada klip terpadat. Kecenderungan ini sejalan dengan dugaan bahwa oklusi "
             "antarobjek dan pergantian identitas jejak menyulitkan pelacakan pada kondisi "
             "padat, dan sekaligus menjadi jawaban substantif atas rumusan masalah kelima "
             "meskipun tanpa penetapan ambang kelulusan tunggal.")
    gambar(doc, N, "09_counting_end_to_end/grafik_sistem_vs_manual.png",
           "Perbandingan Hitungan Sistem terhadap Hitungan Manual per Klip dan Kelas", 13.0)
    gambar(doc, N, "09_counting_end_to_end/grafik_sebar_per_interval.png",
           "Sebaran Galat Penghitungan pada Setiap Interval Pengamatan", 13.0)

    h3(doc, "4.10.3 Keandalan menurut Kelas dan Sumber Defisit")
    per_kelas = {}
    for r in band:
        s, m = per_kelas.setdefault(r["kelas"], [0, 0])
        per_kelas[r["kelas"]] = [s + int(r["sistem"]), m + int(r["manual"])]
    N.tabel(doc, "Akurasi Penghitungan Agregat menurut Kelas Kendaraan")
    tabel(doc, ["Kelas", "Sistem", "Manual", "Akurasi (%)", "Selisih (%)"],
          [[KELAS_ID[k].capitalize(), str(s), str(m), ind(100 * s / m, 1),
            ind(100 * (s - m) / m, 1)]
           for k, (s, m) in sorted(per_kelas.items(), key=lambda x: -x[1][1])],
          lebar=[4.0, 2.4, 2.4, 3.0, 3.2])
    tot_s = sum(v[0] for v in per_kelas.values())
    tot_m = sum(v[1] for v in per_kelas.values())
    defisit = sorted(band, key=lambda r: int(r["manual"]) - int(r["sistem"]), reverse=True)
    kurang = lambda r: int(r["manual"]) - int(r["sistem"])
    d1 = defisit[0]
    d2 = next(r for r in defisit if r["kelas"] == "big-vehicle" and kurang(r) > 0)
    andil = 100 * (kurang(d1) + kurang(d2)) / (tot_m - tot_s)
    par(doc, f"Keandalan sistem berbanding lurus dengan proporsi kelas dalam data latih. "
             f"Kendaraan roda dua, yang merupakan kelas mayoritas, mencapai akurasi agregat "
             f"{ind(100 * per_kelas['two-wheeler'][0] / per_kelas['two-wheeler'][1], 1)} "
             f"persen. Mobil berada di posisi menengah dengan "
             f"{ind(100 * per_kelas['car'][0] / per_kelas['car'][1], 1)} persen, sedangkan "
             f"kendaraan besar sebagai kelas minoritas hanya mencapai "
             f"{ind(100 * per_kelas['big-vehicle'][0] / per_kelas['big-vehicle'][1], 1)} "
             f"persen.")
    par(doc, f"Penelusuran lebih lanjut menunjukkan bahwa angka agregat tersebut tidak boleh "
             f"dibaca sebagai ukuran murni akurasi deteksi dan pelacakan. Dari total "
             f"{rib(tot_m - tot_s)} kendaraan yang tidak tercatat sistem, sekitar {ind(andil, 1)} "
             f"persen berasal dari hanya dua sel pada klip terpadat, yaitu mobil dan kendaraan "
             f"besar, dengan pola yang sejenis dengan cacat geometri yang menyebabkan satu klip "
             f"lain dikeluarkan. Pada sel kendaraan besar bahkan sistem sama sekali tidak "
             f"mencatat perlintasan padahal penghitung manual mencatat {kurang(d2)} kendaraan. "
             f"Karena itu pelaporan per kelas menjadi keharusan, dan angka agregat sebaiknya "
             f"dipahami sebagai akurasi sistem beserta penempatan garis mayanya.")

    h3(doc, "4.10.4 Kecepatan Pemrosesan dan Penilaian terhadap Standar Praktis")
    par(doc, f"Kecepatan pemrosesan menyeluruh diukur langsung pada saat penghitungan berjalan, "
             f"yaitu mencakup deteksi, pelacakan, dan penghitungan lintasan sekaligus. Rata-rata "
             f"laju pemrosesan mencapai {ind(gab['fps_pipeline_rata2'], 2)} bingkai per detik "
             f"dengan rentang {ind(gab['fps_pipeline_min'], 2)} hingga "
             f"{ind(gab['fps_pipeline_maks'], 2)} bingkai per detik. Angka ini berbeda dari laju "
             f"bingkai model murni pada Tabel 4.8 dan harus dibedakan secara tegas, karena "
             f"selisih keduanya merupakan biaya pelacakan yang nyata dan tidak dapat diabaikan "
             f"pada penerapan.")
    par(doc, "Kriteria kecepatan ditetapkan secara *a-priori*, yaitu sistem disebut bekerja "
             "secara *real-time* apabila laju pemrosesan menyeluruh sekurang-kurangnya sama "
             "dengan laju bingkai sumber. Seluruh klip uji direkam pada tiga puluh bingkai per "
             "detik sehingga ambangnya adalah tiga puluh bingkai per detik. Berdasarkan kriteria "
             "tersebut, konfigurasi penuh belum memenuhi syarat karena hanya mencapai sekitar "
             "dua per tiga laju sumber. Laju tersebut memadai untuk pemantauan lalu lintas "
             "dengan penjarangan bingkai terkendali maupun untuk pemrosesan rekaman, tetapi "
             "belum memadai untuk memproses setiap bingkai secara serentak pada laju penuh.")
    par(doc, f"Untuk menilai akurasi terhadap standar penerapan praktis, tiga rujukan dari luar "
             f"penelitian ini digunakan agar penilaian tidak bersifat *post-hoc*. Skala "
             f"interpretasi galat persentase yang lazim dipakai menempatkan nilai antara dua "
             f"puluh dan lima puluh persen pada kategori wajar [31], sehingga galat sebesar "
             f"{ind(gab['MAPE_persen'], 2)} persen berada dalam kategori tersebut. Sebaliknya, "
             f"standar pemantauan lalu lintas yang mensyaratkan akurasi sekurang-kurangnya "
             f"sembilan puluh persen untuk kelompok kelas berisi tiga puluh kendaraan atau "
             f"lebih dan sembilan puluh lima persen untuk volume keseluruhan [32] belum "
             f"terpenuhi: kelas mayoritas mencapai "
             f"{ind(100 * per_kelas['two-wheeler'][0] / per_kelas['two-wheeler'][1], 1)} persen "
             f"sehingga gagal secara tipis, sedangkan akurasi volume keseluruhan sebesar "
             f"{ind(100 * tot_s / tot_m, 1)} persen. Penelitian sejenis pada bidang penglihatan "
             f"komputer melaporkan akurasi penghitungan pada kisaran sembilan puluh hingga "
             f"sembilan puluh delapan persen [33], namun angka tersebut umumnya dihitung pada "
             f"total agregat dalam kondisi arus bebas sehingga satuannya tidak setara dengan "
             f"galat per interval yang dipakai penelitian ini.")
    par(doc, "Penilaian yang jujur karena itu bersifat campuran: akurasi tergolong wajar "
             "menurut skala interpretasi galat persentase, tetapi belum memenuhi standar "
             "peralatan pemantauan terkalibrasi maupun kriteria kecepatan yang ditetapkan di "
             "muka. Hasil campuran semacam ini justru memperkuat kredibilitas pelaporan, karena "
             "skema penilaian yang membuat seluruh kriteria terpenuhi akan mengundang "
             "pertanyaan mengenai cara ambang tersebut dipilih.")

    # ---------------------------------------------------------------- 4.11
    h2(doc, "4.11 Analisis Galat")
    fn_v1 = sum(int(gs("V1", "size", s, "n_fn")) for s in ("small", "medium", "large"))
    fn_v8 = sum(int(gs("V8", "size", s, "n_fn")) for s in ("small", "medium", "large"))
    n_gt = sum(int(gs("V1", "size", s, "n_gt")) for s in ("small", "medium", "large"))
    par(doc, f"Analisis galat dijalankan pada subset uji sebagaimana disyaratkan Subbab 3.11.6, "
             f"menggunakan objek pencocokan yang sama dengan yang dipakai pada evaluasi "
             f"terstratifikasi agar angkanya konsisten. Pencocokan dilakukan pada ambang "
             f"tumpang tindih 0,50 dengan ambang keyakinan 0,25. Perlu ditegaskan bahwa matriks "
             f"kekeliruan yang dihasilkan pustaka pelatihan secara otomatis dihitung pada subset "
             f"validasi, bukan subset uji, sehingga tidak dipakai pada bab ini.")
    N.tabel(doc, "Dekomposisi Objek Terlewat dan Prediksi Palsu menurut Strata")
    baris = []
    for dim, tiers in (("size", ("small", "medium", "large")),
                       ("occlusion", ("no", "partial", "heavy")),
                       ("density", ("sparse", "medium", "dense"))):
        for st in tiers:
            if gs("V1", dim, st, "n_gt") == "-":
                continue
            baris.append([f"{ {'size': 'Ukuran', 'occlusion': 'Oklusi', 'density': 'Densitas'}[dim] } — {STRATA_ID[st]}",
                          gs("V1", dim, st, "n_gt"),
                          f"{gs('V1', dim, st, 'n_fn')} ({ind(gs('V1', dim, st, 'fn_persen'), 2)}%)",
                          f"{gs('V8', dim, st, 'n_fn')} ({ind(gs('V8', dim, st, 'fn_persen'), 2)}%)",
                          gs("V1", dim, st, "n_fp_prediksi") or "tidak berlaku",
                          gs("V8", dim, st, "n_fp_prediksi") or "tidak berlaku"])
    tabel(doc, ["Strata", "Objek", "Terlewat V1", "Terlewat V8", "Prediksi palsu V1",
                "Prediksi palsu V8"], baris,
          lebar=[3.8, 1.6, 2.9, 2.9, 2.5, 2.5], size_body=8)
    par(doc, f"Temuan pertama, konfigurasi penuh menurunkan jumlah objek yang terlewat pada "
             f"seluruh strata tanpa terkecuali. Secara total, objek yang tidak terdeteksi turun "
             f"dari {rib(fn_v1)} menjadi {rib(fn_v8)} dari {rib(n_gt)} objek uji. Penurunan paling mencolok "
             f"terjadi pada objek berukuran besar dan pada strata oklusi parsial. Konsistensi "
             f"arah ini berbeda dari hasil *average precision* yang campuran, dan perbedaan "
             f"tersebut bukan kontradiksi karena *average precision* menggabungkan presisi "
             f"dengan *recall*, sedangkan tabel ini hanya memotret sisi *recall*.")
    par(doc, f"Temuan kedua menjelaskan mengapa presisi konfigurasi penuh justru lebih rendah "
             f"daripada model dasar. Penurunan objek terlewat dibayar dengan naiknya prediksi "
             f"palsu, khususnya pada objek berukuran kecil yang meningkat dari "
             f"{gs('V1', 'size', 'small', 'n_fp_prediksi')} menjadi "
             f"{gs('V8', 'size', 'small', 'n_fp_prediksi')} dan pada adegan berkepadatan "
             f"sedang yang meningkat dari {gs('V1', 'density', 'medium', 'n_fp_prediksi')} "
             f"menjadi {gs('V8', 'density', 'medium', 'n_fp_prediksi')}. Perilaku ini konsisten "
             f"dengan mekanisme pembobotan berbasis densitas: memberi bobot lebih besar pada "
             f"objek di wilayah padat menaikkan sensitivitas model pada wilayah tersebut, dan "
             f"sensitivitas yang meningkat membawa serta prediksi yang keliru. Pertukaran ini "
             f"dilaporkan terbuka karena merupakan konsekuensi terukur dari mekanisme yang "
             f"diusulkan, bukan cacat yang perlu disembunyikan.")
    par(doc, "Prediksi palsu tidak dapat distratifikasi menurut tingkat oklusi karena proksi "
             "oklusi pada Persamaan 3.1 memerlukan pasangan objek kebenaran dasar yang menurut "
             "definisinya tidak dimiliki oleh prediksi palsu. Kolom yang bersangkutan karena itu "
             "sengaja dikosongkan dan tidak diisi nilai nol yang akan menyesatkan.")
    N.tabel(doc, "Laju Objek Terlewat menurut Kelas pada Konfigurasi Penuh")
    tabel(doc, ["Kelas", "Objek uji", "Terlewat", "Persentase terlewat",
                "Salah klasifikasi"],
          [[KELAS_ID[k].capitalize(), gk("V8", k, "n_gt"), gk("V8", k, "n_terlewat"),
            ind(gk("V8", k, "fn_persen"), 2), gk("V8", k, "n_salah_kelas")]
           for k in sorted(KELAS_ID, key=lambda x: -float(gk("V8", x, "fn_persen")))],
          lebar=[4.0, 2.4, 2.3, 3.2, 3.1])
    par(doc, f"Temuan ketiga menyangkut kelas. Kendaraan roda dua merupakan kelas dengan laju "
             f"objek terlewat tertinggi, yaitu {ind(gk('V8', 'two-wheeler', 'fn_persen'), 1)} "
             f"persen, sekaligus merupakan kelas dengan jumlah instans terbesar. Kombinasi "
             f"kedua sifat tersebut mendukung langsung premis yang dibangun pada Bab I bahwa "
             f"dominasi objek berukuran kecil merupakan tantangan utama pada lalu lintas "
             f"heterogen, dan sekaligus menjelaskan mengapa kelas ini menyumbang galat absolut "
             f"terbesar pada penghitungan meskipun persentase galatnya paling baik.")
    N.tabel(doc, "Perbandingan Galat pada Adegan Siang dan Adegan Malam")
    tabel(doc, ["Kelompok adegan", "Citra", "Objek uji", "Terlewat V1 (%)",
                "Terlewat V5 (%)", "Terlewat V8 (%)"],
          [[k.capitalize(), gsm("V8", k, "n_citra"), gsm("V8", k, "n_gt"),
            ind(gsm("V1", k, "fn_persen"), 2), ind(gsm("V5", k, "fn_persen"), 2),
            ind(gsm("V8", k, "fn_persen"), 2)] for k in ("malam", "siang")],
          lebar=[3.4, 2.0, 2.4, 2.8, 2.8, 2.8])
    dm, dsg = float(gsm("V8", "malam", "fn_persen")), float(gsm("V8", "siang", "fn_persen"))
    par(doc, f"Temuan keempat merupakan yang paling tidak terduga. Galat sangat terkonsentrasi "
             f"pada adegan malam, dengan laju objek terlewat sebesar {ind(dm, 2)} persen "
             f"berbanding {ind(dsg, 2)} persen pada adegan siang, yaitu sekitar "
             f"{ind(dm / dsg, 1)} kali lipat. Menariknya, perbaikan yang dibawa konfigurasi "
             f"penuh jauh lebih besar pada adegan siang daripada adegan malam, sehingga "
             f"modifikasi yang diusulkan membantu tetapi tidak menutup jurang pencahayaan. "
             f"Ketiga citra dengan objek terlewat terbanyak seluruhnya berasal dari rangkaian "
             f"rekaman malam.")
    par(doc, f"Satu fakta pada tabel tersebut wajib diperhatikan ketika menafsirkan seluruh "
             f"angka pada bab ini. Adegan malam menyumbang {rib(gsm('V8', 'malam', 'n_gt'))} objek "
             f"dari {rib(int(gsm('V8', 'malam', 'n_gt')) + int(gsm('V8', 'siang', 'n_gt')))} objek "
             f"uji, atau sekitar tujuh puluh dua persen, meskipun jumlah citranya hanya sekitar "
             f"tiga puluh delapan persen. Hal ini terjadi karena adegan malam pada dataset ini "
             f"jauh lebih padat. Konsekuensinya, seluruh metrik global yang dilaporkan pada bab "
             f"ini secara efektif didominasi kondisi malam, dan fakta tersebut tidak terlihat "
             f"dari metrik agregat mana pun.")
    for v in ("V1", "V8"):
        gambar(doc, N, f"11_analisis_galat/grafik_matriks_kekeliruan_{v}.png",
               f"Matriks Kekeliruan {LBL[v]} pada Subset Uji", 11.0)
    gambar(doc, N, "11_analisis_galat/grafik_fn_per_strata_size.png",
           "Laju Objek Terlewat menurut Strata Ukuran", 12.5)
    gambar(doc, N, "11_analisis_galat/grafik_fn_per_kelas.png",
           "Laju Objek Terlewat menurut Kelas Objek", 12.5)
    gambar(doc, N, "11_analisis_galat/grafik_kasus_kegagalan.png",
           "Tiga Kasus Kegagalan dengan Objek Terlewat Terbanyak", 15.0)
    par(doc, "Montase pada Gambar terakhir memperlihatkan bahwa kegagalan terberat terjadi pada "
             "adegan malam berkepadatan tinggi dengan objek berukuran sangat kecil yang saling "
             "berdekatan. Pada kondisi demikian batas antarobjek menjadi kabur akibat "
             "keterbatasan pencahayaan, dan kotak kebenaran dasar yang berdempetan mempersulit "
             "pencocokan satu-ke-satu.")

    # ---------------------------------------------------------------- 4.12
    h2(doc, "4.12 Keterbatasan Hasil")
    par(doc, "Bagian ini menyatakan secara terbuka keterbatasan yang melekat pada hasil di "
             "atas, sesuai prinsip pelaporan yang dianut penelitian ini. Keterbatasan pertama "
             "menyangkut ketiadaan pengulangan pelatihan pada beberapa nilai *seed* acak "
             "sebagaimana direncanakan pada Bab III. Estimasi kebutuhan tambahan mencapai "
             "sekitar empat puluh sembilan jam komputasi GPU, terutama disebabkan varian yang "
             "memuat lapisan deteksi P2 yang masing-masing memerlukan sepuluh hingga sebelas "
             "jam per pengulangan, dan anggaran tersebut tidak tersedia. Seluruh hasil pada bab "
             "ini karena itu merepresentasikan satu realisasi pelatihan dengan *seed* tetap. "
             "Keterbatasan ini paling relevan bagi hipotesis pertama dan kedua yang selisihnya "
             "kecil, karena tanpa data antar-*seed* tidak dapat dipastikan apakah selisih "
             "sekecil itu berada di dalam atau di luar rentang fluktuasi inisialisasi.")
    par(doc, "Keterbatasan kedua menyangkut strata kepadatan ekstrem yang tidak dapat dinilai "
             "pada dua jalur evaluasi sekaligus. Pada evaluasi deteksi, seluruh sel kendaraan "
             "pada strata tersebut gugur akibat aturan sel minimum sehingga hanya menyisakan "
             "kelas konteks. Pada evaluasi penghitungan, tidak satu pun interval pengamatan "
             "yang tergolong kepadatan ekstrem karena keterbatasan lokasi kamera yang dapat "
             "dijangkau. Karena kepadatan merupakan salah satu dari tiga tantangan yang "
             "diangkat Bab I, keterbatasan ini bersifat mendasar dan tidak boleh diabaikan "
             "pembaca.")
    par(doc, "Keterbatasan ketiga menyangkut proksi oklusi yang terbukti tidak pernah "
             "membentuk tingkat oklusi berat sehingga kesimpulan pada strata tersebut tidak "
             "dapat ditegakkan. Keterbatasan keempat menyangkut acuan kebenaran penghitungan "
             "yang berasal dari satu penghitung sebagaimana dinyatakan pada Subbab 3.10.1, "
             "sehingga keandalan antarpenilai tidak terkuantifikasi. "
             "Keterbatasan kelima menyangkut pencarian grid hiperparameter yang dilakukan satu "
             "kali pada satu varian dengan pelatihan dipersingkat, yang konsekuensinya telah "
             "terbukti nyata pada Subbab 4.6. Keterbatasan keenam menyangkut satu klip yang "
             "dikeluarkan dari evaluasi penghitungan beserta alasannya, dan keterbatasan "
             "ketujuh menyangkut dominasi adegan malam pada subset uji sebagaimana diuraikan "
             "pada Subbab 4.11.")

    # ---------------------------------------------------------------- 4.13
    h2(doc, "4.13 Ringkasan Jawaban atas Rumusan Masalah")
    h1_, h3_ = wil["V8 vs V1"], wil["V8 vs V5"]
    par(doc, "Rumusan masalah pertama mengenai perancangan modifikasi yang kompatibel dengan "
             "paradigma *NMS-free* terjawab secara afirmatif. Kedelapan varian berhasil dilatih "
             "hingga konvergen tanpa kegagalan, menghasilkan prediksi satu-ke-satu yang valid "
             "dengan cakupan di atas sembilan puluh lima persen, dan seluruhnya berjalan dalam "
             "anggaran memori perangkat yang tersedia.")
    par(doc, f"Rumusan masalah kedua mengenai kontribusi setiap komponen terjawab dengan "
             f"nuansa. Pembobotan *loss* berbasis densitas memberi kontribusi yang signifikan "
             f"secara statistik ketika ditumpangkan pada fondasi arsitektural, dengan nilai p "
             f"sebesar {ind(h3_['p'], 4)} dan ukuran efek {ind(h3_['rank_biserial'], 3)}, "
             f"tetapi tidak memberi perbaikan ketika berdiri sendiri. Konfigurasi penuh belum "
             f"terbukti unggul secara signifikan atas model dasar dengan nilai p sebesar "
             f"{ind(h1_['p'], 3)}.")
    par(doc, "Rumusan masalah ketiga mengenai pengaruh lapisan P2 dan atensi hibrida terhadap "
             "kestabilan pencocokan satu-ke-satu terjawab melalui pola yang konsisten pada "
             "kedua indikator: lapisan P2 tanpa atensi menurunkan tingkat duplikasi dan margin "
             "keyakinan, sedangkan penambahan atensi hibrida mengembalikannya di atas model "
             "dasar. Atensi hibrida karena itu berperan sebagai penstabil terhadap kepadatan "
             "prediksi yang ditimbulkan lapisan P2.")
    par(doc, "Rumusan masalah keempat mengenai performa terstratifikasi terjawab sebagian. "
             "Perbaikan terkonsentrasi pada strata oklusi parsial dan objek berukuran kecil, "
             "sedangkan strata kepadatan ekstrem tidak dapat dinilai karena keterbatasan data "
             "uji. Rumusan masalah kelima mengenai akurasi menyeluruh terjawab dengan angka "
             "yang telah dilaporkan pada Subbab 4.10 beserta penilaiannya terhadap tiga rujukan "
             "eksternal, yang hasilnya bersifat campuran.")
    halaman_baru(doc)


def tulis_bab5(doc, data):
    (gm, wil, boot, cnt, gab, band, g_str, g_kls, g_sm, kasus, komp, nms, LBL) = data
    h1_, h2_, h3_ = wil["V8 vs V1"], wil["V4 vs V1"], wil["V8 vs V5"]
    b3 = boot["V8 vs V5"]
    h1(doc, "BAB V", "KESIMPULAN DAN SARAN")

    h2(doc, "5.1 Kesimpulan")
    par(doc, "Penelitian ini mengembangkan dan mengevaluasi modifikasi detektor *NMS-free* "
             "YOLO26 yang memadukan pembobotan *loss* berbasis densitas sebagai kebaruan "
             "metodologis dengan modul atensi hibrida dan lapisan deteksi P2 sebagai instrumen "
             "pendukung, kemudian merangkainya bersama pelacak ByteTrack menjadi sistem "
             "penghitung kendaraan. Berdasarkan seluruh hasil pada Bab IV, lima kesimpulan "
             "dapat ditarik.")
    par(doc, "Pertama, modifikasi yang diusulkan terbukti kompatibel dengan paradigma "
             "*NMS-free*. Seluruh varian dapat dilatih hingga konvergen tanpa kegagalan "
             "numerik, menghasilkan prediksi satu-ke-satu yang valid, dan berjalan dalam "
             "anggaran memori perangkat dengan kapasitas delapan gigabita. Pembobotan berbasis "
             "densitas dapat disuntikkan pada kedua cabang kepala deteksi tanpa mengubah "
             "mekanisme pencocokan maupun menambah parameter.")
    par(doc, f"Kedua, kontribusi pembobotan *loss* berbasis densitas bersifat komplementer, "
             f"bukan mandiri. Ketika ditumpangkan pada arsitektur yang telah diperkuat atensi "
             f"hibrida dan lapisan P2, kontribusinya signifikan secara statistik dengan nilai p "
             f"sebesar {ind(h3_['p'], 4)}, ukuran efek *rank-biserial* sebesar "
             f"{ind(h3_['rank_biserial'], 3)}, dan selang kepercayaan *bootstrap* antara "
             f"{ind(float(b3['ci_lo']) * 100, 2)} dan {ind(float(b3['ci_hi']) * 100, 2)} poin "
             f"persentase yang tidak memuat nol. Sebaliknya, penerapannya tanpa dukungan "
             f"arsitektural tidak memberi perbaikan, dengan nilai p sebesar "
             f"{ind(h2_['p'], 3)} dan arah efek yang justru negatif. Konfigurasi penuh pun "
             f"belum terbukti unggul secara signifikan atas model dasar, dengan nilai p sebesar "
             f"{ind(h1_['p'], 3)}. Temuan ini konsisten dengan ramalan pada Bab II bahwa "
             f"arsitektur dasar YOLO26 telah memuat mekanisme penetapan label adaptif berbasis "
             f"ukuran sehingga ruang perbaikan yang tersisa lebih sempit dibandingkan "
             f"penelitian terdahulu yang membandingkan modifikasinya terhadap detektor berbasis "
             f"*non-maximum suppression*.")
    par(doc, "Ketiga, penyelidikan empiris terhadap interaksi dengan mekanisme pencocokan "
             "satu-ke-satu menghasilkan temuan yang belum pernah dilaporkan sebelumnya, yaitu "
             "bahwa lapisan deteksi beresolusi tinggi menurunkan tingkat duplikasi dan margin "
             "keyakinan, sedangkan modul atensi hibrida mengembalikan keduanya di atas taraf "
             "model dasar. Dengan demikian atensi hibrida berperan sebagai penstabil terhadap "
             "kepadatan prediksi yang ditimbulkan lapisan P2, dan interaksi antarkomponen ini "
             "tidak dapat disimpulkan dari metrik deteksi agregat semata.")
    par(doc, f"Keempat, perbaikan yang dibawa modifikasi terkonsentrasi pada dua dari tiga "
             f"tantangan yang diangkat penelitian, yaitu oklusi parsial dan objek berukuran "
             f"kecil. Tantangan ketiga berupa kepadatan ekstrem tidak dapat dinilai karena data "
             f"uji tidak memuat cukup objek kendaraan pada strata tersebut, baik pada evaluasi "
             f"deteksi maupun pada evaluasi penghitungan.")
    par(doc, f"Kelima, sistem penghitungan menyeluruh mencapai *mean absolute error* sebesar "
             f"{ind(gab['MAE'], 3)} kendaraan per interval, *root mean square error* sebesar "
             f"{ind(gab['RMSE'], 3)}, dan *mean absolute percentage error* sebesar "
             f"{ind(gab['MAPE_persen'], 2)} persen pada laju pemrosesan menyeluruh sebesar "
             f"{ind(gab['fps_pipeline_rata2'], 2)} bingkai per detik. Akurasi tersebut "
             f"tergolong wajar menurut skala interpretasi galat persentase, namun belum "
             f"memenuhi standar peralatan pemantauan lalu lintas terkalibrasi maupun kriteria "
             f"kecepatan yang ditetapkan di muka. Galat meningkat seiring kepadatan lalu lintas "
             f"dan keandalan per kelas berbanding lurus dengan proporsi kelas dalam data latih.")

    h2(doc, "5.2 Implikasi Penelitian")
    par(doc, "Dari sisi teoretis, penelitian ini menunjukkan bahwa penambahan mekanisme "
             "pembobotan berbasis densitas pada detektor yang telah memiliki mekanisme "
             "penetapan label adaptif tidak otomatis memberikan perbaikan. Nilainya baru muncul "
             "ketika arsitektur menyediakan kapasitas representasi yang memadai, dalam hal ini "
             "melalui lapisan beresolusi tinggi dan penajaman fitur oleh atensi. Temuan ini "
             "melengkapi literatur yang selama ini melaporkan perbaikan besar dari modifikasi "
             "serupa, karena memperlihatkan bahwa besar perbaikan sangat bergantung pada "
             "kekuatan *baseline* yang menjadi pembanding.")
    par(doc, "Dari sisi praktis, hasil kompleksitas menunjukkan bahwa pembobotan berbasis "
             "densitas tidak menambah biaya inferensi sama sekali karena hanya bekerja pada "
             "tahap pelatihan. Bagi penerapan dengan kendala perangkat, komponen ini merupakan "
             "pilihan yang menarik karena perbaikan yang dibawanya tidak dibayar dengan "
             "penurunan kecepatan, berbeda dengan lapisan deteksi P2 yang menurunkan laju "
             "pemrosesan secara nyata. Selain itu, temuan bahwa sebagian besar defisit "
             "penghitungan bersumber dari penempatan garis maya, bukan dari kegagalan model, "
             "menegaskan bahwa kalibrasi geometri pengamatan merupakan faktor keberhasilan yang "
             "setara pentingnya dengan kualitas detektor.")

    h2(doc, "5.3 Keterbatasan Penelitian")
    par(doc, "Keterbatasan penelitian ini telah dinyatakan pada Subbab 4.12 dan dirangkum "
             "kembali di sini. Pelatihan hanya dijalankan satu kali per varian dengan *seed* "
             "tetap sehingga variabilitas akibat inisialisasi tidak terkuantifikasi. Strata "
             "kepadatan ekstrem tidak terwakili memadai baik pada data uji deteksi maupun pada "
             "klip penghitungan. Proksi oklusi berbasis tumpang tindih kotak pembatas terbukti "
             "meremehkan oklusi yang dipersepsi manusia dan tidak pernah membentuk tingkat "
             "oklusi berat. Acuan kebenaran penghitungan berasal dari satu penghitung sehingga "
             "keandalan antarpenilai tidak terkuantifikasi. Pencarian hiperparameter dilakukan "
             "satu kali pada satu varian dengan pelatihan dipersingkat. Satu klip dikeluarkan "
             "dari evaluasi penghitungan karena cacat penempatan garis. Subset uji didominasi "
             "adegan malam sehingga metrik global lebih mencerminkan kondisi tersebut. "
             "Terakhir, seluruh data berasal dari kamera pengawas di wilayah Jakarta sehingga "
             "generalisasi ke wilayah dengan komposisi kendaraan berbeda perlu diuji "
             "tersendiri.")

    h2(doc, "5.4 Saran")
    par(doc, "Saran pertama ditujukan bagi penelitian lanjutan yang ingin memperkuat "
             "kesimpulan statistik. Pengulangan pelatihan pada sekurang-kurangnya tiga nilai "
             "*seed* untuk varian kunci beserta pelaporan simpangan bakunya akan memungkinkan "
             "penilaian apakah selisih kecil antarvarian berada di luar rentang fluktuasi "
             "inisialisasi. Pengumpulan data uji tambahan pada ruas dengan kepadatan melampaui "
             "dua puluh lima objek per bingkai juga diperlukan agar strata kepadatan ekstrem "
             "dapat dievaluasi sebagaimana dirancang.")
    par(doc, "Saran kedua menyangkut penyempurnaan proksi oklusi. Proksi berbasis tumpang "
             "tindih kotak pembatas sebaiknya dilengkapi atau digantikan oleh pendekatan yang "
             "mampu menangkap penghalang di luar objek berlabel, misalnya melalui segmentasi "
             "atau anotasi tingkat keterlihatan secara langsung. Validasi manual pada penelitian "
             "ini menunjukkan bahwa perbaikan pada titik ini akan berdampak langsung pada "
             "kesahihan seluruh analisis terstratifikasi menurut oklusi.")
    par(doc, "Saran ketiga menyangkut arah perbaikan model yang muncul langsung dari analisis "
             "galat. Kondisi cahaya rendah merupakan sumber galat terbesar sehingga penanganan "
             "khusus melalui augmentasi yang menirukan kondisi malam, penyesuaian kontras "
             "adaptif, atau pemanfaatan kanal inframerah layak diprioritaskan. Selain itu, "
             "kenaikan prediksi palsu pada objek berukuran kecil di adegan padat menunjukkan "
             "perlunya mekanisme penekanan prediksi keliru yang bekerja selaras dengan "
             "pembobotan densitas, agar kenaikan sensitivitas tidak dibayar terlalu mahal oleh "
             "penurunan presisi. Penguatan kelas kendaraan roda dua sebagai kelas dengan laju "
             "objek terlewat tertinggi juga perlu menjadi perhatian khusus.")
    par(doc, "Saran keempat menyangkut penerapan. Untuk mencapai pemrosesan pada laju bingkai "
             "penuh, optimasi inferensi melalui kompilasi khusus perangkat, kuantisasi, atau "
             "penjarangan bingkai terkendali perlu ditempuh. Kalibrasi geometri garis maya "
             "sebaiknya diverifikasi per kelas kendaraan sebelum pengumpulan data acuan "
             "kebenaran, mengingat sebagian besar defisit penghitungan pada penelitian ini "
             "bersumber dari persoalan tersebut. Terakhir, pengumpulan acuan kebenaran "
             "sebaiknya melibatkan sekurang-kurangnya dua penghitung independen beserta "
             "pelaporan tingkat kesesuaian awal, sehingga galat sistem dapat dipisahkan dari "
             "ketidakpastian acuan kebenaran itu sendiri.")
    halaman_baru(doc)
