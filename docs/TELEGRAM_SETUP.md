# Setup Telegram Bot

1. Di Telegram, chat **@BotFather** → `/newbot` → salin token.
2. `cp .env.example .env` lalu isi `TELEGRAM_BOT_TOKEN=...` (jangan di-commit). Opsional: `BOT_TIMEZONE=Asia/Jakarta`.
3. Install & jalankan (database yang sama dengan backend; jalankan `python seed.py`/backend minimal sekali agar tabel ada):
   ```bash
   cd telegram_bot
   python -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   python bot.py
   ```
4. Di website: menu **Telegram** → *Buat kode* → kirim `/start KODE` ke bot.

## Catatan
- Pengingat & briefing dicek tiap menit (JobQueue PTB, berbasis APScheduler). Setiap pengingat dicatat di `notification_logs` sehingga tidak terkirim ulang; jika pengiriman gagal, dicoba lagi pada siklus berikutnya.
- Waktu event dianggap waktu lokal (`BOT_TIMEZONE`). Briefing dikirim pada jam yang diatur, dengan toleransi 3 jam jika bot baru menyala.
- Hanya logika bot yang teruji otomatis (`cd telegram_bot && python -m pytest`). Koneksi ke Telegram sungguhan belum diuji.
