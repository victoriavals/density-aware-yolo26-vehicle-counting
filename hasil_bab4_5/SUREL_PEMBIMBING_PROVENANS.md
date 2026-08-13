# Draf surel Dr. Sandfreni — dua pertanyaan kewenangan institusional

> **Revisi 2** menurut Bagian 4 dan butir 2 keputusan pembimbing teknis (13 Agu 2026):
> kedua pertanyaan **dinaikkan ke bagian atas** agar tidak terlewat oleh pembaca cepat,
> dan cakupannya dipersempit dari sepuluh hal menjadi **dua** — sisanya sudah diputuskan
> pembimbing teknis dan sudah dijalankan.
>
> ⚠️ Periksa dan sunting sebelum dikirim — ini surat Naufal, bukan surat saya.

---

**Subjek:** Dua pertanyaan kewenangan institusional — temuan provenans dataset sebelum pengiriman artikel

Yang terhormat Ibu Sandfreni,

Saya menemukan persoalan provenans pada dataset penelitian saya, sudah menelusurinya sampai
selesai, dan sudah mengukur dampaknya terhadap hasil. Pembimbing teknis telah memutuskan
seluruh hal yang bersifat metodologis dan penyuntingan, dan koreksinya sudah saya jalankan
pada naskah artikel. **Yang tersisa dan hanya dapat diputuskan pihak program studi ada dua,
dan saya letakkan di depan agar tidak terlewat:**

**Pertanyaan 1.** Sebanyak 315 dari 3.389 citra memuat tanda air pihak ketiga, dan 248 di
antaranya berada di subset latih sehingga bobot model sudah terlatih dengannya. Membersihkan
seluruhnya menuntut pelatihan ulang delapan varian, sekitar 49 jam GPU. Posisi yang saya
ambil, dan yang disetujui pembimbing teknis secara metodologis, adalah mempertahankan bobot
yang ada, melaporkan uji ketegaran tanpa citra tersebut, dan menyatakan status lisensi secara
terbuka pada bagian keterbatasan. **Apakah posisi itu dapat diterima menurut kebijakan
integritas publikasi program studi?**

**Pertanyaan 2.** Naskah tesis yang telah disidangkan memuat tiga pernyataan yang terbukti
tidak sesuai bukti, yaitu lokasi dataset, klaim data primer, dan komposisi data. **Apakah
tesis perlu diajukan koreksi formal, dan melalui prosedur apa?** Saya belum menyentuh naskah
tesis dan menahannya sampai memperoleh arahan Ibu.

---

**Ringkas temuannya, sebagai latar kedua pertanyaan di atas.**

Pertama, **315 citra memuat tanda air pihak cipta ketiga** — sebagian besar Shutterstock,
dan empat citra berlogo kanal video "NL Cycling" yang kedudukan hukumnya berbeda karena
materi kanal tidak tercakup lisensi stok mana pun. Sebarannya: 248 latih, 34 validasi,
33 uji. Temuan awal saya hanya 67 citra karena bersandar pada pola nama berkas; setelah
seluruh 1.477 citra kelompok rekaman-layar diperiksa satu perwakilan per kelompok,
angkanya menjadi 315.

Kedua, **lokasi CCTV bukan Jakarta.** Overlay pada citra menunjukkan **Yogyakarta**
(ATCS Pemkot), **Demak**, dan **Banjarmasin** (Dishub Kota). Terdapat pula rekaman stok dari
Seoul, Mekkah, New York, dan Belanda. Hanya **1.427 citra (42,1 %)** yang benar-benar CCTV
lalu lintas Indonesia; **1.597 (47,1 %)** adalah gambar katalog kendaraan, dan **365
(10,8 %)** rekaman stok.

Ketiga, sumber CCTV adalah **umpan ATCS dan Dishub yang direkam dari layar**, bukan kamera
yang dipasang sendiri sebagaimana tertulis pada Bab 3.

Sebagai pemeriksaan tambahan saya menjalankan uji kemiripan perseptual untuk kebocoran
antar-subset yang tidak terdeteksi pemeriksaan md5. **Ditemukan tiga pasangan citra identik
dengan berkas berbeda**, satu di antaranya antara subset latih dan uji. Satu citra uji itu
saya keluarkan dari evaluasi, dan hasilnya saya laporkan apa adanya di naskah.

**Dampak terhadap hasil sudah saya ukur, dan kesimpulan tesis bertahan.** Evaluasi saya
jalankan ulang pada tiga versi subset uji, tanpa melatih ulang model dan tanpa mengubah
bobot:

| Hipotesis | Uji penuh (338) | Tanpa bertanda air (304) | Hanya CCTV (160) |
|---|---|---|---|
| V8 vs V1 | p = 0,565 | p = 0,303 | p = 0,079 |
| V4 vs V1 | p = 0,208 | p = 0,252 | p = 0,546 |
| **V8 vs V5** | **p = 0,037** ✅ | **p = 0,040** ✅ | **p = 0,023** ✅ |

Hipotesis utama yang signifikan tetap signifikan pada ketiga versi, selang bootstrapnya
tidak memuat nol pada ketiganya, dan arah dua hipotesis lainnya tidak berubah. Keunggulan
pada oklusi parsial dan objek kecil juga bertahan. Saya **tidak** menjadikan subset CCTV
sebagai hasil utama, karena memilih subset setelah melihat hasilnya sama dengan menyeleksi
pada data uji.

**Yang sudah saya kerjakan atas keputusan pembimbing teknis.** Koreksi lokasi menjadi tiga
kota, penghapusan klaim data primer beserta atribusi lembaga penyedia umpan, paragraf
komposisi dataset yang menyatakan proporsi apa adanya, pernyataan lisensi pada keterbatasan,
pelaporan tiga subset berdampingan, dan gambar kualitatif baru.

> ⚠️ **Naufal — periksa dulu sebelum mengirim:** kalimat berikut hanya boleh disertakan bila
> Anda memang sudah membatasi visibilitas dataset di Roboflow (butir 1 urutan pembimbing,
> tindakan yang hanya dapat Anda lakukan sendiri). Bila belum, lakukan dulu, atau hapus
> kalimat ini.
>
> "Visibilitas dataset di Roboflow juga sudah saya batasi."

Saya menahan pengiriman artikel sampai memperoleh jawaban atas kedua pertanyaan di atas.
Seluruh bukti, daftar citra, dan hasil pengujian sudah saya rapikan dan siap saya tunjukkan
bila Ibu memerlukannya.

Hormat saya,
Naufal Firdaus, NIM 20240804017
