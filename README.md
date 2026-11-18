# JOBBY — Your Career Journey, Organized.

Job application tracker bergaya **Y2K Dreamy Digital**: dashboard, Kanban tracker, kalender, direktori perusahaan, catatan + checklist persiapan, dan **JOBBY Assistant** (Telegram Bot) untuk pengingat otomatis.

## Fitur
- **Auth:** register, login, profil, ubah password, forgot/reset password (lihat keterbatasan), protected routes, JWT.
- **Overview:** greeting dinamis, ringkasan angka, grafik status (Recharts), jadwal terdekat, lamaran terbaru, Quick Actions, widget Telegram, checklist persiapan.
- **My Applications:** CRUD, search, filter status, sort tanggal, ubah status, konfirmasi hapus.
- **Tracker:** Kanban 9 status dengan drag-and-drop (+ menu status untuk layar sentuh), riwayat status dengan tanggal.
- **Calendar:** tampilan bulanan & mingguan, tambah/edit/hapus jadwal (Interview, Assessment, Deadline, dst).
- **Companies:** CRUD, pencarian, logo, career page, deskripsi, catatan riset.
- **Notes:** 6 kategori, pencarian, tautan ke lamaran, checklist interaktif dengan progress.
- **Telegram Bot:** account linking (kode 10 menit, sekali pakai), 11 command, update status & catatan dari bot, pengingat H-3/H-1/H-0, follow-up, briefing harian, tanpa pengiriman ganda.

## Tech stack
React 18 + Vite + TypeScript + Tailwind + React Router + Recharts + Lucide · Flask + Flask-SQLAlchemy + Flask-JWT-Extended + Flask-CORS · SQLite · python-telegram-bot 21 (JobQueue/APScheduler).

## Struktur folder
```
JOBBY/
├── frontend/       React app (src/pages, components, contexts, api.ts)
├── backend/        Flask API (app/models.py, routes.py, routes_more.py, services.py), seed.py, tests
├── telegram_bot/   bot.py, handlers/, services/data.py, scheduler/, tests
├── docs/           API.md, DATABASE.md, TELEGRAM_SETUP.md
├── .env.example  .gitignore  LICENSE  README.md
```

## Prasyarat
Python 3.10+ (diuji 3.12), Node.js 18+ dan npm, Git, Visual Studio Code.

## Instalasi & menjalankan (VS Code → Terminal)
**1. Environment**
```bash
cp .env.example .env          # Windows: copy .env.example .env  (isi SECRET_KEY & JWT_SECRET_KEY dengan nilai acak)
```
**2. Backend + database** (terminal 1)
```bash
cd backend
python -m venv venv && source venv/bin/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env       # backend membaca .env di folder backend (atau root)
python seed.py                # membuat database SQLite + akun demo
python run.py                 # http://localhost:5000/api
```
Tabel dibuat otomatis (`db.create_all()`); file DB ada di `backend/instance/jobby.db`.

**3. Frontend** (terminal 2)
```bash
cd frontend
npm install
npm run dev                   # http://localhost:5173  (proxy /api → :5000)
npm run build                 # build produksi + type-check
```
**4. Telegram Bot** (terminal 3, opsional) — langkah lengkap di `docs/TELEGRAM_SETUP.md`
```bash
cd telegram_bot
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# isi TELEGRAM_BOT_TOKEN di .env (dari @BotFather)
python bot.py
```
**Tes:** `cd backend && pip install pytest && python -m pytest` · `cd telegram_bot && python -m pytest`

## Akun demo
`demo@jobby.dev` / `demo12345` (dibuat oleh `python seed.py`, hanya untuk development).

## Environment variables
| Variabel | Fungsi |
|---|---|
| `SECRET_KEY`, `JWT_SECRET_KEY` | Kunci aplikasi/JWT — **wajib diganti** |
| `DATABASE_URL` | Default `sqlite:///jobby.db` |
| `FRONTEND_ORIGIN` | Origin CORS & basis link reset password |
| `APP_ENV` | `production` menyembunyikan link reset dari response |
| `TELEGRAM_BOT_TOKEN` | Token bot (jangan di-commit) |
| `BOT_TIMEZONE` | Default `Asia/Jakarta` |

## Dokumentasi
`docs/API.md` (endpoint) · `docs/DATABASE.md` (skema) · `docs/TELEGRAM_SETUP.md` (bot).

## Troubleshooting
- **Login gagal / 401 setelah ganti kunci:** token lama tidak valid; login ulang.
- **`no such column` / `no such table`:** hapus `backend/instance/jobby.db`, jalankan `python seed.py` (belum ada Alembic).
- **Frontend tidak bisa memanggil API:** pastikan backend jalan di port 5000 dan frontend lewat `npm run dev` (proxy aktif).
- **Bot: `TELEGRAM_BOT_TOKEN belum diisi`:** isi `.env` di root. Jalankan backend/seed sekali dulu agar tabel ada.
- **Jadwal demo bergeser jam:** waktu event dianggap waktu lokal sesuai `BOT_TIMEZONE`.
- **Error 429:** rate limit login/register/reset (10/menit/IP); tunggu sebentar.

## Keterbatasan yang diketahui
- Reset password: belum ada layanan email. Di development link reset ada di response/log; di production email belum terkirim sampai SMTP diintegrasikan.
- Telegram Bot teruji hanya pada level logika (otomatis); koneksi Telegram sungguhan belum diuji.
- UI belum dites visual lintas browser/perangkat; reminder custom di luar H-3/H-1/H-0, Alembic, serta Framer Motion/React Hook Form/Zod belum diterapkan; rate limiting in-memory (satu proses).

## Push ke GitHub
```bash
git init
git add .
git commit -m "Initial commit: JOBBY Job Application Tracker"
git branch -M main
git remote add origin https://github.com/USERNAME/REPOSITORY.git
git push -u origin main
```
