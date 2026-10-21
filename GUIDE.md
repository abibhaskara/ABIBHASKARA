# GitHub Terminal Profile README Generator

Project ini dibuat serupa dan terinspirasi dari [DietrichGebert/DietrichGebert](https://github.com/DietrichGebert/DietrichGebert).

Project ini menghasilkan kartu profil GitHub bergaya terminal / `neofetch` / `fastfetch` dalam format SVG dinamis yang otomatis mendukung **Dark Mode** dan **Light Mode**. GitHub Actions akan memperbarui statistik akun GitHub Anda (commit, repo, star, follower, dan baris kode) secara otomatis setiap hari.

---

## 📁 Struktur File

```text
├── .github/
│   └── workflows/
│       └── update.yml          # GitHub Actions workflow (update harian otomatis)
├── tools/
│   └── image_to_ascii.py       # Helper CLI untuk mengonversi gambar/foto ke ASCII art
├── dark_mode.svg               # SVG profil tampilan gelap (GitHub Dark Theme)
├── light_mode.svg              # SVG profil tampilan terang (GitHub Light Theme)
├── update_profile.py           # Script utama pembuat SVG dan pengambil statistik GitHub
├── README.md                   # Profil utama yang ditampilkan di repository GitHub
└── GUIDE.md                    # Dokumentasi lengkap panduan setup
```

---

## 🚀 Fitur Unggulan

1. **Terminal Neofetch Estetik**:
   - Kolom kiri: **ASCII Art** foto profil / avatar.
   - Kolom kanan: **System Info & Live GitHub Stats** (OS, Uptime umur, Role, Tech Stack, Kontak, Total Commits, Repos, Stars, Followers, & Lines of Code `++` / `--`).
2. **Dukungan Dark Mode & Light Mode Otomatis**:
   - Menggunakan tag HTML `<picture>` dan `@media (prefers-color-scheme)`.
   - Warna otomatis menyesuaikan tema browser dan preferensi tema GitHub pengunjung.
3. **Standar Library Python Murni**:
   - `update_profile.py` hanya menggunakan standard library Python (`urllib`, `ssl`, `json`, `calendar`, dll.) tanpa dependensi pihak ketiga, sehingga proses build GitHub Actions selesai dalam hitungan detik.
4. **Fallback Token Otomatis untuk Development Lokal**:
   - Jika dijalankan di komputer lokal dan Anda memiliki GitHub CLI (`gh`), script akan otomatis mengambil token aktif melalui `gh auth token` tanpa perlu repot export environment variable manual.
5. **Tool Konversi ASCII (`tools/image_to_ascii.py`)**:
   - Memudahkan Anda mengubah foto atau logo apa pun menjadi ASCII art berukuran pas dan langsung memasukkannya ke `update_profile.py` dengan satu perintah (`--apply`).

---

## 🛠️ Cara Kustomisasi Informasi Profil

Buka file `update_profile.py`, lalu ubah variabel berikut sesuai keinginan:

```python
# ==============================================================================
# PROFILE CONFIGURATION
# ==============================================================================
USER = "abibhaskara"
BIRTHDAY = date(2008, 1, 1)  # Ubah ke tanggal lahir Anda (Tahun, Bulan, Tanggal)
JOINED_YEAR = 2025           # Tahun akun GitHub dibuat
```

Di dalam fungsi `info_lines(s)`, Anda bisa menyesuaikan teks:
- **OS**: misal `macOS, Linux`
- **Host**: misal `Student Researcher`
- **Kernel**: misal `Web & IoT Developer`
- **IDE**: misal `VS Code, Cursor`
- **Languages.Programming**: misal `JavaScript, Python, C++, HTML/CSS`
- **Languages.Real**: misal `Indonesian, English`
- **Hobbies**: misal `IoT, AI Research, Design`
- **Email & Website**: kontak yang ingin ditampilkan

---

## 🎨 Cara Mengganti ASCII Art Avatar

Jika Anda ingin mengganti foto/logo ASCII art di sisi kiri kartu:

1. Siapkan file gambar (misal `avatar.png` atau `logo.png`).
2. Jalankan tool konversi:
   ```bash
   python3 tools/image_to_ascii.py path/ke/foto.png --apply
   ```
3. Opsi tambahan:
   - `--contrast 2.0` : Menambah ketajaman kontras
   - `--invert` : Membalik warna (hitam-putih)
   - `--width 40 --height 27` : Menyesuaikan ukuran
4. Regenerate SVG:
   ```bash
   python3 update_profile.py
   ```

---

## 🧪 Menjalankan Secara Lokal

Untuk menguji dan memperbarui file SVG di komputer lokal:

```bash
python3 update_profile.py
```

Jika berhasil, output akan menampilkan statistik Anda dan memperbarui file `dark_mode.svg` dan `light_mode.svg`.

---

## 🌐 Cara Publikasi ke GitHub Profile

Agar profil ini tampil di halaman utama profil GitHub Anda (`https://github.com/abibhaskara`):

1. **Pastikan repository bernama persis sama dengan username GitHub Anda**:
   - Nama repo: `abibhaskara`
   - Buat repository baru di GitHub dengan nama `abibhaskara` jika belum ada, atau gunakan repository yang sudah ada.
2. **Push folder project ini ke branch `main` repository tersebut**:
   ```bash
   git init -b main
   git add .
   git commit -m "feat: initial fastfetch terminal profile"
   git remote add origin https://github.com/abibhaskara/abibhaskara.git
   git push -u origin main
   ```
3. **Konfigurasi GitHub Actions Permissions**:
   - Di halaman repository GitHub: buka **Settings** > **Actions** > **General**.
   - Pada bagian **Workflow permissions**, pilih:
     - ✅ **Read and write permissions**
   - Klik **Save**.
4. **(Opsional) Private Repository Lines of Code (LOC)**:
   - Secara default, GitHub Actions menggunakan `GITHUB_TOKEN` bawaan yang sudah mencakup seluruh kontribusi publik dan privat untuk commit.
   - Jika Anda ingin script juga menghitung baris kode (Lines of Code) dari repositori **privat**:
     1. Buat **Personal Access Token (PAT)** di GitHub: **Settings > Developer Settings > Personal access tokens (classic)** dengan cakupan `repo`.
     2. Tambahkan token tersebut ke **Settings > Secrets and variables > Actions > New repository secret** dengan nama `ACCESS_TOKEN`.
