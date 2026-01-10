# AplikasiR - Aplikasi Kasir / Point of Sale

Aplikasi kasir sederhana berbasis Python dengan antarmuka modern menggunakan Tkinter.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Fitur

- 🛒 **Point of Sale** - Transaksi penjualan dengan pencarian produk
- 📦 **Manajemen Produk** - CRUD produk dengan auto-generate barcode & ID
- 🧾 **Cetak Struk** - Cetak ke thermal printer
- 📊 **Laporan** - Laporan penjualan harian/bulanan
- 📜 **Riwayat** - Histori transaksi
- 🎨 **Tema Warna** - 5 tema warna yang bisa dipilih
- 💾 **Backup/Restore** - Backup dan restore database

## 📋 Persyaratan

- Python 3.8 atau lebih baru
- Windows OS (untuk fitur printer)

## 🚀 Instalasi

1. Clone repository:

```bash
git clone https://github.com/USERNAME/APLIKASIR.git
cd APLIKASIR
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Jalankan aplikasi:

```bash
python main.py
```

## 📁 Struktur Folder

```
APLIKASIR/
├── main.py              # Entry point aplikasi
├── config.py            # Konfigurasi dan tema
├── db_manager.py        # Database manager (CSV)
├── requirements.txt     # Dependencies
├── ui/                  # Komponen UI
│   ├── sidebar.py       # Sidebar navigasi
│   ├── dashboard.py     # Dashboard
│   ├── sales.py         # Point of Sale
│   ├── products.py      # Manajemen produk
│   ├── history.py       # Riwayat transaksi
│   ├── report.py        # Laporan
│   ├── settings.py      # Pengaturan
│   └── receipt.py       # Cetak struk
├── utils/               # Utility functions
│   └── helpers.py       # Helper functions
├── database/            # CSV database
│   ├── products.csv     # Data produk
│   └── transactions.csv # Data transaksi
└── assets/              # Assets (logo, dll)
```

## 🎨 Tema Warna

Tersedia 5 tema warna:

- Biru (Default)
- Hijau
- Ungu
- Oranye
- Gelap (Dark Mode)

Ubah tema di **Pengaturan > Tema Warna**.

## 📝 Lisensi

MIT License - silakan gunakan dan modifikasi sesuai kebutuhan.

## 👨‍💻 Kontributor

Dibuat dengan ❤️ menggunakan Python dan Tkinter.
