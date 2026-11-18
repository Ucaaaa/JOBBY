# Database (SQLite via SQLAlchemy)
Semua tabel data pengguna punya `user_id` (FK ke `users`); setiap query difilter berdasarkan pemilik. `created_at`/`updated_at` ada di tabel ber-`Stamp`.

| Tabel | Isi utama | Constraint |
|---|---|---|
| users | name, email, password_hash | email unik |
| companies | name, industry, location, website, logo_url, career_page, description, research_notes | unik (user_id, name) |
| applications | company_name, position, location, employment_type, work_arrangement, salary_range, job_url, description, notes, applied_date, deadline, status | FK user_id, company_id |
| application_status_history | application_id, from_status, to_status, changed_at | cascade hapus bersama lamaran |
| events | title, event_type, starts_at, location, description, application_id | FK user_id |
| notes | title, content, category, application_id, company_id | FK user_id |
| checklist_items | text, done, note_id | FK user_id; cascade dari note |
| telegram_accounts | user_id, telegram_user_id | keduanya unik |
| telegram_link_codes | code, expires_at, used | code unik |
| user_preferences | reminder_days, briefing_time, telegram_notifications | user_id unik |
| notification_logs | kind, ref, sent_at | unik (user_id, ref) — pencegah pengingat ganda |

Inisialisasi: `db.create_all()` saat backend start (belum ada Alembic). **Jika kamu sudah punya `backend/instance/jobby.db` dari versi lama**, hapus file itu lalu jalankan ulang `python seed.py` (kolom baru di `companies` & tabel `notification_logs`). Tabel `reminders` terpisah tidak dibuat; pengingat dihitung dari events/deadline + preferensi.
