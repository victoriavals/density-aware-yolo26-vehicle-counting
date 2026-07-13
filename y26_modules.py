"""
y26_modules.py — Modul Atensi Hibrida (HAM) untuk YOLO26.

Implementasi Subbab 3.6.1 tesis: kaskade atensi kanal lalu atensi spasial,
mengadopsi prinsip CBAM (Woo et al., ECCV 2018) [10] dengan atensi kanal
mengikuti prinsip Squeeze-and-Excitation (Hu et al., CVPR 2018) [20].

Diverifikasi terhadap ultralytics 8.4.92:
- parse_model meresolusi nama modul via globals() di ultralytics/nn/tasks.py
  (baris ~1942), sehingga registrasi cukup dengan menyuntikkan kelas HAM ke
  namespace modul tasks (register_ham()).
- Modul di luar `base_modules` menerima args YAML apa adanya dan channel
  keluarannya dianggap sama dengan masukan (c2 = ch[f]) — cocok untuk HAM
  yang memang tidak mengubah dimensi tensor.
"""

from __future__ import annotations

import torch
import torch.nn as nn

VERIFIED_ULTRALYTICS = "8.4.92"


class HAM(nn.Module):
    """Hybrid Attention Module: Channel Attention -> Spatial Attention (kaskade).

    Args:
        c1: jumlah kanal masukan (= kanal keluaran; HAM tidak mengubah bentuk tensor).
        reduction: rasio reduksi MLP atensi kanal (default 16, mengikuti CBAM).
        spatial_k: ukuran kernel konvolusi atensi spasial (default 7, mengikuti CBAM).
    """

    def __init__(self, c1: int, reduction: int = 16, spatial_k: int = 7):
        super().__init__()
        cm = max(c1 // reduction, 8)  # kanal tersembunyi MLP, dijaga >= 8
        # --- Atensi kanal (shared MLP untuk jalur avg-pool dan max-pool) ---
        self.mlp = nn.Sequential(
            nn.Conv2d(c1, cm, 1, bias=False),
            nn.SiLU(inplace=True),
            nn.Conv2d(cm, c1, 1, bias=False),
        )
        # --- Atensi spasial: concat(avg_c, max_c) -> conv k x k -> sigmoid ---
        self.spatial = nn.Conv2d(2, 1, spatial_k, padding=spatial_k // 2, bias=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Atensi kanal
        att_c = torch.sigmoid(
            self.mlp(torch.nn.functional.adaptive_avg_pool2d(x, 1))
            + self.mlp(torch.nn.functional.adaptive_max_pool2d(x, 1))
        )
        x = x * att_c
        # Atensi spasial
        att_s = torch.sigmoid(
            self.spatial(torch.cat([x.mean(1, keepdim=True), x.amax(1, keepdim=True)], dim=1))
        )
        return x * att_s


def register_ham() -> None:
    """Registrasikan HAM ke namespace ultralytics agar dikenali parse_model.

    Wajib dipanggil SEBELUM membangun model dari YAML yang memuat layer HAM.
    Aman dipanggil berulang (idempoten).
    """
    import ultralytics
    import ultralytics.nn.tasks as tasks

    if ultralytics.__version__ != VERIFIED_ULTRALYTICS:
        print(
            f"[peringatan] Kode diverifikasi pada ultralytics=={VERIFIED_ULTRALYTICS}, "
            f"terpasang {ultralytics.__version__}. Jalankan test_smoke.py untuk memastikan kompatibilitas."
        )
    setattr(tasks, "HAM", HAM)
    # Ekspos juga di paket modules agar deserialisasi checkpoint (torch.load) menemukan kelasnya.
    import ultralytics.nn.modules as unm

    setattr(unm, "HAM", HAM)
    import sys

    # torch.load pada checkpoint menyimpan path kelas asli (y26_modules.HAM);
    # pastikan modul ini dapat diimpor dengan nama yang sama di proses lain.
    sys.modules.setdefault("y26_modules", sys.modules[__name__])
