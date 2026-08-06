"""LAMPIRAN naskah BAB IV-V: seluruh data mentah hasil eksperimen dalam bentuk tabel.

Setiap lampiran dibangun langsung dari berkas hasil sehingga isinya selalu sinkron dengan
artefak eksperimen. Lampiran memuat data LENGKAP; badan bab hanya memuat ringkasannya.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

from y26_tulis_bab45 import HB, ROOT, baca_csv, baca_json, h1, h2, halaman_baru, ind, par, tabel

KELAS_ID = {"big-vehicle": "kendaraan besar", "car": "mobil",
            "pedestrian": "pejalan kaki", "two-wheeler": "kendaraan roda dua"}


def _num(s: str) -> str:
    """Ubah desimal titik menjadi koma bila nilainya memang angka."""
    try:
        float(s)
    except (TypeError, ValueError):
        return s
    return str(s).replace(".", ",").replace("-", "−")


def dari_csv(doc, rel: str, header: list[str], kolom: list[str],
             lebar: list[float], size_body: int = 8, batas: int | None = None,
             filter_fn=None, absolut: bool = False):
    rows = (list(csv.DictReader(open(ROOT / rel, encoding="utf-8-sig")))
            if absolut else baca_csv(rel))
    if filter_fn:
        rows = [r for r in rows if filter_fn(r)]
    dipakai = rows[:batas] if batas else rows
    tabel(doc, header, [[_num(r.get(k, "")) for k in kolom] for r in dipakai],
          lebar=lebar, size_body=size_body)
    return len(rows), len(dipakai)


def tulis_lampiran(doc, N4, N5=None):
    h1(doc, "LAMPIRAN", "DATA LENGKAP HASIL EKSPERIMEN")
    par(doc, "Lampiran ini memuat data lengkap yang menjadi dasar seluruh angka pada Bab IV. "
             "Setiap tabel dibangkitkan langsung dari berkas keluaran program sehingga tidak "
             "ada angka yang disalin secara manual. Nama berkas sumber dicantumkan pada awal "
             "setiap lampiran agar dapat ditelusuri kembali.")

    # ---------------------------------------------------- daftar tabel & gambar
    h2(doc, "Daftar Tabel dan Gambar pada Bab IV")
    tabel(doc, ["Nomor", "Judul tabel"], [[f"Tabel {no}", jd] for no, jd in N4.daftar_t],
          lebar=[2.4, 11.6], size_body=9)
    doc.add_paragraph()
    tabel(doc, ["Nomor", "Judul gambar"], [[f"Gambar {no}", jd] for no, jd in N4.daftar_g],
          lebar=[2.6, 11.4], size_body=9)
    halaman_baru(doc)

    # ---------------------------------------------------- L2 bukti split
    h2(doc, "Lampiran 1 Bukti Pembagian Data Berbasis Kelompok")
    par(doc, "Sumber: bukti_split_grup.csv dan bukti_split_citra.csv. Tabel berikut menyajikan "
             "ringkasan jumlah kelompok per subset beserta dua puluh baris pertama daftar "
             "kelompok sebagai contoh. Daftar lengkap tersedia pada berkas sumber karena "
             "memuat ratusan baris.")
    grup = baca_csv("01_dataset/bukti_split_grup.csv")
    citra = baca_csv("01_dataset/bukti_split_citra.csv")
    kol_split = "split" if "split" in grup[0] else list(grup[0])[-1]
    ring = {}
    for r in grup:
        ring[r[kol_split]] = ring.get(r[kol_split], 0) + 1
    ringc = {}
    for r in citra:
        k = r.get("split", r.get(kol_split, "-"))
        ringc[k] = ringc.get(k, 0) + 1
    tabel(doc, ["Subset", "Jumlah kelompok", "Jumlah citra"],
          [[k, str(v), str(ringc.get(k, "-"))] for k, v in ring.items()],
          lebar=[4.0, 4.0, 4.0], size_body=9)
    doc.add_paragraph()
    dari_csv(doc, "01_dataset/bukti_split_grup.csv", list(grup[0].keys()),
             list(grup[0].keys()), [14.0 / max(len(grup[0]), 1)] * len(grup[0]), batas=20)
    halaman_baru(doc)

    # ---------------------------------------------------- L3 AP terstratifikasi
    h2(doc, "Lampiran 2 Nilai Average Precision Terstratifikasi Lengkap")
    par(doc, "Sumber: strata_ap.csv. Tabel memuat nilai AP@0,5 dan AP@0,5:0,95 untuk setiap "
             "kombinasi varian, kelas, dimensi stratifikasi, dan tingkat strata pada subset "
             "uji, beserta jumlah objek kebenaran dasar pada setiap sel. Sel dengan jumlah "
             "objek di bawah tiga puluh dikeluarkan dari pengujian signifikansi namun tetap "
             "disajikan di sini.")
    n_tot, _ = dari_csv(doc, "04_ablasi_deteksi/strata_ap.csv",
                        ["Varian", "Kelas", "Dimensi", "Strata", "Objek", "AP@0,5",
                         "AP@0,5:0,95"],
                        ["variant", "class", "dim", "stratum", "n_gt", "AP50", "AP50_95"],
                        [2.0, 2.6, 2.0, 1.9, 1.5, 2.0, 2.4], size_body=7,
                        filter_fn=lambda r: r["dim"] != "global")
    par(doc, f"Jumlah baris: {n_tot}.")
    halaman_baru(doc)

    # ---------------------------------------------------- L4 Wilcoxon
    h2(doc, "Lampiran 3 Hasil Uji Wilcoxon Seluruh Pasangan Varian")
    par(doc, "Sumber: wilcoxon_ap5095.csv. Keluarga *primary* memuat tiga hipotesis utama yang "
             "ditetapkan di muka dan tidak dikoreksi, sedangkan keluarga *secondary* memuat "
             "seluruh pasangan lain yang dikoreksi dengan prosedur Holm. Kolom p terkoreksi "
             "hanya berlaku bagi keluarga sekunder.")
    dari_csv(doc, "04_ablasi_deteksi/wilcoxon_ap5095.csv",
             ["Pasangan", "Keluarga", "n sel", "W", "p", "p Holm", "Median selisih",
              "Rank-biserial", "Signifikan"],
             ["pair", "family", "n", "W", "p", "p_holm", "median_diff", "rank_biserial",
              "signif_5pct"],
             [2.4, 1.9, 1.2, 1.2, 1.8, 1.8, 2.0, 1.9, 1.6], size_body=7)
    doc.add_paragraph()
    par(doc, "Dua belas sel berikut dikeluarkan dari seluruh pengujian karena jumlah objek "
             "kebenaran dasarnya kurang dari tiga puluh, sesuai aturan sel minimum pada "
             "Subbab 3.11.5.")
    wil = baca_csv("04_ablasi_deteksi/wilcoxon_ap5095.csv")[0]
    sel = [s.strip() for s in wil["sel_dibuang"].split(";") if s.strip()]
    tabel(doc, ["No", "Sel yang dikeluarkan (kelas / dimensi / strata dan jumlah objek)"],
          [[str(i), s] for i, s in enumerate(sel, 1)], lebar=[1.6, 12.4], size_body=8)
    halaman_baru(doc)

    # ---------------------------------------------------- L5 bootstrap
    h2(doc, "Lampiran 4 Selang Kepercayaan Bootstrap")
    par(doc, "Sumber: bootstrap_ci.csv. Selang dihitung dengan seribu kali pengambilan sampel "
             "ulang berpasangan pada tataran citra, bukan pada tataran deteksi, agar "
             "ketergantungan antarobjek dalam satu citra tidak diabaikan. Prosedur bersifat "
             "deterministik terhadap *seed* sehingga dapat direproduksi.")
    dari_csv(doc, "04_ablasi_deteksi/bootstrap_ci.csv",
             ["Pasangan", "Ulangan", "Citra", "mAP varian A", "mAP varian B",
              "Selisih titik", "Batas bawah", "Batas atas", "Selang tanpa nol"],
             ["pair", "n_boot", "n_images", "map_a", "map_b", "diff_point", "ci_lo",
              "ci_hi", "selang_tanpa_nol"],
             [2.4, 1.5, 1.3, 1.9, 1.9, 1.8, 1.8, 1.8, 2.0], size_body=8)
    doc.add_paragraph()
    h2(doc, "Lampiran 5 Selisih AP Antarstrata Beserta Kelayakan Narasi")
    par(doc, "Sumber: delta_strata.csv. Kolom pertama memuat selisih yang dihitung dari seluruh "
             "sel, kolom kedua hanya dari sel yang memenuhi aturan sel minimum. Perbedaan "
             "keduanya memperlihatkan pengaruh sel bervolume kecil terhadap rata-rata, dan "
             "kolom terakhir menandai strata yang tidak layak dinarasikan.")
    dari_csv(doc, "04_ablasi_deteksi/delta_strata.csv",
             ["Pasangan", "Dimensi", "Strata", "Kelas (semua)", "Selisih semua sel",
              "Kelas (sel min)", "Selisih sel min", "Kelas dipakai", "Layak dinarasikan"],
             ["pasangan", "dim", "stratum", "n_kelas_semua", "delta_pp_semua_sel",
              "n_kelas_selmin", "delta_pp_selmin", "kelas_dipakai", "layak_dinarasikan"],
             [1.7, 1.7, 1.5, 1.6, 1.9, 1.6, 1.8, 2.4, 2.6], size_body=7)
    halaman_baru(doc)

    # ---------------------------------------------------- L7 kompleksitas + nmsfree
    h2(doc, "Lampiran 6 Metrik Kompleksitas dan Efisiensi Lengkap")
    par(doc, "Sumber: tabel_kompleksitas.csv. Laju bingkai pada tabel ini diukur pada tolok "
             "ukur model murni tanpa pelacakan.")
    dari_csv(doc, "03_kompleksitas_model/tabel_kompleksitas.csv",
             ["Varian", "Parameter (juta)", "GFLOPs", "Ukuran (MB)", "VRAM latih (GB)",
              "VRAM inferensi (GB)", "Jam latih", "Epoch", "Laju bingkai", "Latensi (ms)"],
             ["variant", "params_M", "gflops", "size_MB", "peak_gpu_train_gb",
              "peak_gpu_infer_gb", "train_hours", "epochs", "fps", "latency_ms"],
             [1.4, 1.8, 1.3, 1.5, 1.7, 1.9, 1.4, 1.1, 1.4, 1.5], size_body=7)
    doc.add_paragraph()
    h2(doc, "Lampiran 7 Analisis Interaksi NMS-free Lengkap")
    par(doc, "Sumber: summary.csv dan tau_sweep.csv.")
    dari_csv(doc, "05_analisis_nmsfree/summary.csv",
             ["Varian", "Citra", "Objek", "Duplicate Rate", "Terlewat", "Duplikat",
              "Cakupan", "CM rata-rata", "CM median", "CM persentil 10"],
             ["variant", "images", "M", "DR", "miss", "dup", "coverage", "cm_mean",
              "cm_median", "cm_p10"],
             [1.4, 1.2, 1.2, 1.9, 1.4, 1.4, 1.4, 1.7, 1.6, 1.8], size_body=7)
    doc.add_paragraph()
    par(doc, "Sensitivitas Duplicate Rate terhadap dua belas nilai ambang tumpang tindih:")
    tau = baca_csv("05_analisis_nmsfree/tau_sweep.csv")
    dari_csv(doc, "05_analisis_nmsfree/tau_sweep.csv",
             ["Ambang"] + [k for k in tau[0] if k != "tau"],
             ["tau"] + [k for k in tau[0] if k != "tau"],
             [2.0] + [2.4] * (len(tau[0]) - 1), size_body=8)
    halaman_baru(doc)

    # ---------------------------------------------------- L9 counting
    h2(doc, "Lampiran 8 Hasil Penghitungan Kendaraan per Interval")
    par(doc, "Sumber: berkas counting_errors.csv setiap klip. Kolom y memuat hitungan manual "
             "dan kolom prediksi memuat hitungan sistem pada setiap interval enam puluh detik, "
             "untuk setiap kelas dan arah. Klip yang dikeluarkan dari evaluasi tetap "
             "dicantumkan sebagai bukti dan diberi keterangan.")
    for klip in ("2_vidiouji", "3_vidiouji", "4_vidiouji"):
        par(doc, f"Klip {klip.replace('_vidiouji', '')}:")
        dari_csv(doc, f"09_counting_end_to_end/{klip}_counting_errors.csv",
                 ["Interval", "Kelas", "Arah", "Manual", "Sistem", "Galat absolut"],
                 ["interval", "class", "direction", "y", "yhat", "abs_err"],
                 [2.0, 3.0, 2.0, 2.2, 2.2, 2.6], size_body=7)
        doc.add_paragraph()
    par(doc, "Klip 1 yang DIKELUARKAN dari evaluasi, disajikan sebagai bukti sebagaimana "
             "dijelaskan pada Subbab 4.10.1. Perhatikan bahwa seluruh baris kelas mobil dan "
             "kendaraan besar bernilai nol pada kolom sistem sementara kolom manual berisi "
             "nilai positif, yaitu pola yang menandakan garis maya tidak memotong lajur yang "
             "dilalui kedua kelas tersebut.")
    dari_csv(doc, "counting_out/1_vidiouji/counting_errors.csv",
             ["Interval", "Kelas", "Arah", "Manual", "Sistem", "Galat absolut"],
             ["interval", "class", "direction", "y", "yhat", "abs_err"],
             [2.0, 3.0, 2.0, 2.2, 2.2, 2.6], size_body=7, absolut=True)
    doc.add_paragraph()
    par(doc, "Konfigurasi garis maya, resolusi, laju bingkai, dan jumlah bingkai setiap klip "
             "tersimpan pada berkas konfigurasi_garis.json yang disertakan bersama data "
             "penelitian.")
    halaman_baru(doc)

    # ---------------------------------------------------- L10 galat
    h2(doc, "Lampiran 9 Analisis Galat Lengkap")
    par(doc, "Sumber: dekomposisi_fp_fn.csv, galat_per_kelas.csv, galat_siang_malam.csv, "
             "kasus_kegagalan.csv, dan matriks_kekeliruan_<varian>.csv.")
    dari_csv(doc, "11_analisis_galat/dekomposisi_fp_fn.csv",
             ["Varian", "Dimensi", "Strata", "Objek", "Terlewat", "Terlewat (%)",
              "Salah kelas", "Prediksi palsu"],
             ["varian", "dim", "stratum", "n_gt", "n_fn", "fn_persen", "n_salah_kelas",
              "n_fp_prediksi"],
             [1.6, 1.9, 1.8, 1.5, 1.7, 2.1, 1.9, 2.1], size_body=7)
    doc.add_paragraph()
    par(doc, "Galat menurut kelas:")
    dari_csv(doc, "11_analisis_galat/galat_per_kelas.csv",
             ["Varian", "Kelas", "Objek", "Terlewat", "Terlewat (%)", "Salah kelas"],
             ["varian", "kelas", "n_gt", "n_terlewat", "fn_persen", "n_salah_kelas"],
             [2.0, 3.2, 2.0, 2.2, 2.4, 2.6], size_body=8)
    doc.add_paragraph()
    par(doc, "Galat menurut kondisi pencahayaan adegan:")
    dari_csv(doc, "11_analisis_galat/galat_siang_malam.csv",
             ["Varian", "Kelompok", "Citra", "Objek", "Terlewat", "Terlewat (%)"],
             ["varian", "kelompok", "n_citra", "n_gt", "n_terlewat", "fn_persen"],
             [2.2, 2.4, 2.2, 2.2, 2.4, 2.6], size_body=8)
    doc.add_paragraph()
    par(doc, "Sepuluh citra dengan objek terlewat terbanyak pada konfigurasi penuh:")
    dari_csv(doc, "11_analisis_galat/kasus_kegagalan.csv",
             ["Peringkat", "Berkas citra", "Objek", "Terlewat", "Prediksi palsu",
              "Kepadatan"],
             ["peringkat", "citra", "n_gt", "n_terlewat", "n_prediksi_palsu", "kepadatan"],
             [1.7, 5.6, 1.5, 1.7, 2.0, 1.9], size_body=7)
    doc.add_paragraph()
    for v in ("V1", "V5", "V8"):
        par(doc, f"Matriks kekeliruan varian {v} pada subset uji:")
        rows = baca_csv(f"11_analisis_galat/matriks_kekeliruan_{v}.csv")
        kol = list(rows[0].keys())
        tabel(doc, [k.replace("gt\\pred", "GT \\ Prediksi") for k in kol],
              [[r[k] for k in kol] for r in rows],
              lebar=[3.4] + [2.1] * (len(kol) - 1), size_body=8)
        doc.add_paragraph()
    halaman_baru(doc)

    # ---------------------------------------------------- L11 oklusi
    h2(doc, "Lampiran 10 Data Validasi Proksi Oklusi")
    okl = baca_json("08_validasi_oklusi/hasil_kesesuaian.json")
    par(doc, f"Sumber: hasil_kesesuaian.json dan manual_oklusi.csv. Sebanyak {okl['n']} objek "
             f"dianotasi secara manual melalui antarmuka buta. Tingkat kesesuaian keseluruhan "
             f"{ind(okl['agreement'] * 100, 1)} persen.")
    tier = ("no", "partial", "heavy")
    nama = {"no": "Tanpa oklusi", "partial": "Oklusi parsial", "heavy": "Oklusi berat"}
    tabel(doc, ["Penilaian manual", "Proksi: tanpa oklusi", "Proksi: oklusi parsial",
                "Proksi: oklusi berat", "Jumlah"],
          [[nama[a]] + [str(okl["confusion"][a][b]) for b in tier] +
           [str(sum(okl["confusion"][a].values()))] for a in tier],
          lebar=[3.4, 3.0, 3.0, 2.8, 1.8], size_body=8)
    doc.add_paragraph()
    par(doc, "Dua puluh baris pertama hasil anotasi manual sebagai contoh; daftar lengkap "
             "tersedia pada berkas sumber.")
    mo = baca_csv("08_validasi_oklusi/manual_oklusi.csv")
    kol = list(mo[0].keys())[:5]
    dari_csv(doc, "08_validasi_oklusi/manual_oklusi.csv",
             kol, kol, [14.0 / len(kol)] * len(kol), batas=20, size_body=7)
    halaman_baru(doc)

    # ---------------------------------------------------- L12 grid + sensitivitas
    h2(doc, "Lampiran 11 Pencarian Grid, Sensitivitas, dan Ketegaran")
    par(doc, "Sumber: tabel_grid_search.csv, tabel_sensitivitas_alpha.csv, dan "
             "tabel_perbandingan_normalisasi.csv.")
    dari_csv(doc, "02_grid_search_dalw/tabel_grid_search.csv",
             ["Kekuatan pembobotan", "Lebar kernel", "mAP@0,5:0,95 validasi"],
             ["alpha", "sigma", "mAP50_95"], [4.6, 4.6, 4.8], size_body=9)
    doc.add_paragraph()
    dari_csv(doc, "06_sensitivitas_alpha/tabel_sensitivitas_alpha.csv",
             ["Run", "Kekuatan", "Epoch total", "Epoch terbaik", "mAP validasi",
              "Jam latih", "mAP@0,5:0,95 uji", "mAP@0,5 uji"],
             ["run", "alpha", "epoch_total", "epoch_terbaik", "mAP50_95_val_terbaik",
              "jam_latih", "mAP50_95_TEST", "mAP50_TEST"],
             [2.0, 1.6, 1.8, 1.9, 2.0, 1.5, 2.2, 1.8], size_body=8)
    doc.add_paragraph()
    dari_csv(doc, "07_ketegaran_normalisasi/tabel_perbandingan_normalisasi.csv",
             ["Skema", "Epoch", "Epoch terbaik", "mAP validasi", "Status",
              "mAP@0,5:0,95 uji", "mAP@0,5 uji", "Presisi uji", "Recall uji"],
             ["run", "epoch_tercatat", "epoch_terbaik", "mAP50_95_val_terbaik", "status",
              "mAP50_95_TEST", "mAP50_TEST", "P_TEST", "R_TEST"],
             [2.6, 1.3, 1.6, 1.7, 2.0, 1.8, 1.5, 1.4, 1.4], size_body=7)
    halaman_baru(doc)

    # ---------------------------------------------------- L13 rujukan baru
    h2(doc, "Lampiran 12 Rujukan Baru yang Digunakan pada Bab IV")
    par(doc, "Tiga rujukan berikut baru muncul pertama kali pada Bab IV sehingga menerima "
             "nomor lanjutan setelah rujukan Bab I sampai Bab III. Karena daftar pustaka "
             "naskah dikelola melalui perangkat manajemen referensi, ketiga entri ini WAJIB "
             "dimasukkan melalui perangkat tersebut, bukan diketik langsung pada berkas Word, "
             "agar penomorannya tidak tertimpa ketika daftar pustaka disegarkan.")
    tabel(doc, ["Nomor", "Entri rujukan", "Dipakai pada"],
          [["[31]", "D. Lewis, Industrial and Business Forecasting Methods: A Practical "
                    "Guide to Exponential Smoothing and Curve Fitting. London: "
                    "Butterworth Scientific, 1982.", "Subbab 4.10.4 — skala interpretasi "
                                                     "galat persentase"],
           ["[32]", "New York State Department of Transportation, Traffic Monitoring "
                    "Standards for Short Count Data Collection, EB 23-032, 2023. "
                    "Diturunkan dari Federal Highway Administration, Traffic Monitoring "
                    "Guide.", "Subbab 4.10.4 — ambang akurasi pemantauan lalu lintas"],
           ["[33]", "M. O. Ahmed et al., \"Automated Vehicle Counting from Pre-Recorded "
                    "Video Using You Only Look Once (YOLO) Object Detection Model,\" "
                    "Journal of Imaging, vol. 9, no. 7, art. 131, 2023.",
            "Subbab 4.10.4 — pembanding akurasi penelitian sejenis"]],
          lebar=[1.5, 8.5, 4.0], size_body=8)
    par(doc, "Catatan: penambahan ketiga nomor ini tidak menggeser penomoran rujukan [1] "
             "sampai [30] pada Bab I sampai Bab III, karena penomoran mengikuti urutan "
             "kemunculan pertama dan seluruh rujukan baru muncul setelahnya.")

    h2(doc, "Lampiran 13 Berkas Artefak dan Cara Reproduksi")
    par(doc, "Seluruh tabel dan gambar pada naskah ini dibangkitkan ulang secara otomatis dari "
             "berkas keluaran program. Daftar berkas sumber beserta perintah pembangkitannya "
             "disajikan pada tabel berikut sebagai penunjang keterulangan penelitian.")
    tabel(doc, ["Kelompok artefak", "Berkas sumber", "Perintah pembangkit"],
          [["Pembagian data", "bukti_split_grup.csv, bukti_split_citra.csv",
            "make_group_split.py"],
           ["Pencarian grid", "runs_tesis/tune_*/results.csv, dalw_best.json",
            "train_ablation.py --tune-dalw"],
           ["Pelatihan varian", "runs_tesis/<varian>/results.csv, weights/best.pt",
            "train_ablation.py --variant all"],
           ["Evaluasi terstratifikasi", "eval_out/global_metrics.csv, strata_ap.csv, "
                                        "wilcoxon_ap5095.csv, bootstrap_ci.csv",
            "evaluate_all.py --split test"],
           ["Analisis NMS-free", "nmsfree_out/summary.csv, tau_sweep.csv",
            "analyze_nmsfree.py --split test"],
           ["Kompleksitas", "eval_out/complexity.csv", "y26_complexity.py"],
           ["Penghitungan kendaraan", "counting_out/<klip>/counting_errors.csv, summary.json",
            "y26_counting.py"],
           ["Validasi oklusi", "anotasi_oklusi/manual_oklusi.csv",
            "make_oklusi_sample.py lalu anotasi manual"],
           ["Analisis galat", "hasil_bab4_5/11_analisis_galat/*",
            "y26_bangun_hasil_bab45.py"],
           ["Naskah Bab IV dan V", "TESIS_BAB4-5.docx", "y26_tulis_bab45.py"]],
          lebar=[3.4, 6.4, 4.2], size_body=8)
