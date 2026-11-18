# REST API (prefix `/api`, JSON, header `Authorization: Bearer <token>` kecuali auth publik)
Error: `{"error": "pesan"}` dengan status 400/401/404/409/429.

**Auth** — POST `/auth/register`, `/auth/login` (rate limit 10/menit/IP) · GET `/auth/me` · PUT `/auth/profile` · PUT `/auth/change-password` · POST `/auth/forgot-password`, `/auth/reset-password` (token berlaku 1 jam, sekali pakai). Tanpa layanan email, link reset dicetak di log server dan dikembalikan di response selama `APP_ENV` ≠ `production`. (Logout dilakukan di klien dengan menghapus token.)

**Applications** — GET/POST `/applications` (query: `search`, `status`, `location`, `employment_type`, `sort=asc|desc`) · GET/PUT/DELETE `/applications/:id` · PUT `/applications/:id/status` `{status}` · GET `/applications/:id/history` · GET `/tracker` (kolom per status).

**Companies** — GET/POST `/companies` · PUT/DELETE `/companies/:id`.
**Events** — GET `/events?from=&to=` (ISO) · POST `/events` · PUT/DELETE `/events/:id`.
**Notes** — GET `/notes?search=&category=&application_id=` · POST · PUT/DELETE `/notes/:id`.
**Checklists** — GET `/checklists?note_id=&pending=1` · POST `{text, note_id}` · PUT `/checklists/:id` `{text?, done?}` · DELETE.
**Dashboard** — GET `/dashboard/summary`, `/dashboard/statistics`, `/dashboard/recent-applications`, `/dashboard/upcoming-events`.
**Telegram** — POST `/telegram/link-code` · GET `/telegram/status` · POST `/telegram/disconnect` · GET/PUT `/telegram/settings` `{reminder_days:[3,1,0], briefing_time:"HH:MM", telegram_notifications}`.

Status valid: Wishlist, Applied, Document Screening, Assessment Test, Interview, Offering, Accepted, Rejected, Withdrawn.
