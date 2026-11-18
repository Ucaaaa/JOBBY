import re
from functools import wraps
from telegram import InlineKeyboardButton as B, InlineKeyboardMarkup as M, Update
from telegram.ext import ContextTypes
from services import data
from app.models import STATUSES

HELP = ("/summary - ringkasan\n/applications - daftar lamaran\n/status <nama> - cek status\n/upcoming - aktivitas mendatang\n"
        "/reminders - pengingat\n/update - ubah status / tambah catatan\n/followup - daftar follow-up\n"
        "/settings - pengaturan (mis. /settings 07:30 untuk jam briefing)\n/disconnect - putuskan akun")


async def reply(update, text, kb=None):
    await update.effective_message.reply_text(text[:4000], reply_markup=kb)


def linked(fn):
    @wraps(fn)
    async def w(update: Update, context: ContextTypes.DEFAULT_TYPE):
        with data.ctx():
            u = data.user_for(update.effective_user.id)
            if not u:
                return await reply(update, "Akun belum terhubung. Buat kode di website JOBBY (menu Telegram), lalu kirim /start KODE.")
            return await fn(update, context, u)
    return w


async def start(update, context):
    with data.ctx():
        tg = update.effective_user.id
        if context.args:
            ok, msg = data.link(context.args[0], tg)
            return await reply(update, ("Akun terhubung ke JOBBY. Ketik /help untuk perintah." if ok else msg))
        u = data.user_for(tg)
        await reply(update, f"Halo {u.name}! Ketik /help." if u else "Halo, aku JOBBY Assistant. Hubungkan akunmu: buat kode di website lalu kirim /start KODE.")


async def help_(update, context): await reply(update, HELP)


@linked
async def summary(update, context, u): await reply(update, data.summary_text(u))
@linked
async def applications(update, context, u): await reply(update, data.applications_text(u))
@linked
async def upcoming(update, context, u): await reply(update, data.upcoming_text(u))
@linked
async def reminders(update, context, u): await reply(update, data.reminders_text(u))
@linked
async def followup(update, context, u): await reply(update, data.followups_text(u))


def app_buttons(rows, prefix):
    return M([[B(f"{a.position} @ {a.company_name}", callback_data=f"{prefix}:{a.id}")] for a in rows])


@linked
async def status(update, context, u):
    q = " ".join(context.args)
    if not q: return await reply(update, "Contoh: /status Gojek")
    rows = data.find_apps(u, q)
    if not rows: return await reply(update, "Tidak ada lamaran yang cocok.")
    if len(rows) == 1: return await send_status(update, rows[0])
    await reply(update, "Ada beberapa hasil, pilih satu:", app_buttons(rows, "st"))


async def send_status(update, a):
    await reply(update, data.status_text(a), M([[B("Tambah catatan", callback_data=f"nt:{a.id}"), B("Ubah status", callback_data=f"up:{a.id}")]]))


@linked
async def update_cmd(update, context, u):
    rows = data.find_apps(u, " ".join(context.args)) if context.args else data.Application.query.filter_by(user_id=u.id).order_by(data.Application.created_at.desc()).limit(8).all()
    await reply(update, "Pilih lamaran:" if rows else "Tidak ada lamaran.", app_buttons(rows, "up") if rows else None)


@linked
async def settings(update, context, u):
    if context.args:
        ok = data.set_time(u, context.args[0])
        if not ok: return await reply(update, "Format jam: /settings 07:30")
    await show_settings(update, u)


async def show_settings(update, u):
    p = data.prefs(u).to_dict()
    kb = M([[B(f"{'✅' if d in p['reminder_days'] else '⬜'} H-{d}", callback_data=f"rd:{d}") for d in (3, 1, 0)],
            [B(f"Notifikasi: {'aktif' if p['telegram_notifications'] else 'mati'}", callback_data="rd:n")]])
    await reply(update, f"Pengaturan\nBriefing harian: {p['briefing_time']}\nPengingat: H-{', H-'.join(map(str, p['reminder_days'])) or 'tidak ada'}", kb)


@linked
async def disconnect(update, context, u):
    data.disconnect(update.effective_user.id)
    await reply(update, "Akun diputuskan. Kamu bisa menghubungkan lagi kapan saja dengan kode baru.")


@linked
async def callback(update, context, u):
    q = update.callback_query; await q.answer()
    kind, _, val = q.data.partition(":")
    if kind == "st":
        a = data.own(u, int(val))
        return await send_status(update, a) if a else await reply(update, "Lamaran tidak ditemukan.")
    if kind == "up":
        kb = M([[B(s, callback_data=f"us:{val}:{i}")] for i, s in enumerate(STATUSES)])
        return await reply(update, "Pilih status baru:", kb)
    if kind == "us":
        i, idx = val.split(":")
        a = data.set_status(u, int(i), STATUSES[int(idx)])
        return await reply(update, f"Status {a.position} @ {a.company_name} sekarang: {a.status}" if a else "Gagal memperbarui.")
    if kind == "nt":
        context.user_data["note_for"] = int(val)
        return await reply(update, "Kirim catatan singkat (hasil interview/assessment dll.) sebagai pesan berikutnya.")
    if kind == "rd":
        data.toggle_notif(u) if val == "n" else data.toggle_day(u, int(val))
        await show_settings(update, u)


async def text(update, context):
    """Pesan biasa: kode linking (belum terhubung) atau catatan (setelah menekan Tambah catatan)."""
    with data.ctx():
        tg, msg = update.effective_user.id, (update.message.text or "").strip()
        u = data.user_for(tg)
        if not u:
            if re.fullmatch(r"[A-Za-z0-9]{6}", msg):
                ok, m = data.link(msg, tg)
                return await reply(update, "Akun terhubung ke JOBBY. Ketik /help." if ok else m)
            return await reply(update, "Kirim kode linking dari website, atau /start.")
        app_id = context.user_data.pop("note_for", None)
        if app_id:
            a = data.add_note(u, app_id, msg)
            return await reply(update, "Catatan disimpan ke lamaran." if a else "Lamaran tidak ditemukan.")
        await reply(update, "Ketik /help untuk daftar perintah.")
