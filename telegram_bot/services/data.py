
"""Logika bot JOBBY yang terhubung dengan database backend."""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Pastikan backend dapat ditemukan sebelum mengimpor modul app.
TELEGRAM_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TELEGRAM_DIR.parent
BACKEND_DIR = PROJECT_ROOT / "backend"

for path in (str(BACKEND_DIR), str(TELEGRAM_DIR)):
    if path not in sys.path:
        sys.path.insert(0, path)

import config

from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError

from app.models import (
    db,
    User,
    Application,
    Event,
    Note,
    ChecklistItem,
    TelegramAccount,
    UserPreference,
    NotificationLog,
    STATUSES,
)

from app.routes import log_status, IN_PROGRESS
from app.services import consume_link_code


_app = None


def set_app(app):
    """Menghubungkan Flask application ke modul data."""
    global _app
    _app = app


def ctx():
    """Menghasilkan application context Flask."""
    global _app

    if _app is None:
        from app import create_app
        _app = create_app()

    return _app.app_context()


def now():
    return datetime.now(ZoneInfo(config.TZ)).replace(tzinfo=None)


def fdt(d):
    return d.strftime("%d %b %Y, %H:%M")


def user_for(tg_id):
    account = TelegramAccount.query.filter_by(
        telegram_user_id=tg_id
    ).first()

    return db.session.get(User, account.user_id) if account else None


def link(code, tg_id):
    return consume_link_code(code, tg_id)


def disconnect(tg_id):
    TelegramAccount.query.filter_by(
        telegram_user_id=tg_id
    ).delete()

    db.session.commit()


def own(u, app_id):
    return Application.query.filter_by(
        id=app_id,
        user_id=u.id
    ).first()


def last_change(application):
    return max(
        (history.changed_at for history in application.history),
        default=application.created_at
    )


def summary_text(u):
    rows = (
        db.session.query(
            Application.status,
            func.count()
        )
        .filter_by(user_id=u.id)
        .group_by(Application.status)
        .all()
    )

    counts = dict(rows)

    recent = (
        Application.query
        .filter_by(user_id=u.id)
        .order_by(Application.created_at.desc())
        .limit(5)
        .all()
    )

    result = (
        f"Ringkasan lamaran {u.name}\n"
        f"Total: {sum(counts.values())}\n"
        f"Dalam proses: {sum(counts.get(s, 0) for s in IN_PROGRESS)}\n"
        f"Interview: {counts.get('Interview', 0)}\n"
        f"Diterima: {counts.get('Accepted', 0)}\n"
        f"Ditolak: {counts.get('Rejected', 0)}\n\n"
        "Terbaru:\n"
    )

    return result + (
        "\n".join(
            f"- {a.position} @ {a.company_name} [{a.status}]"
            for a in recent
        )
        or "Belum ada lamaran."
    )


def applications_text(u):
    rows = (
        Application.query
        .filter_by(user_id=u.id)
        .order_by(Application.created_at.desc())
        .limit(20)
        .all()
    )

    if not rows:
        return "Belum ada lamaran."

    return "Lamaran (20 terbaru):\n" + "\n".join(
        f"- {a.position} @ {a.company_name} [{a.status}]"
        for a in rows
    )


def find_apps(u, q):
    search = f"%{q}%"

    return (
        Application.query
        .filter(
            Application.user_id == u.id,
            or_(
                Application.company_name.ilike(search),
                Application.position.ilike(search)
            )
        )
        .limit(8)
        .all()
    )


def status_text(a):
    history = "\n".join(
        f"  {item.changed_at.strftime('%d %b %Y')}: "
        f"{item.from_status or 'dibuat'} -> {item.to_status}"
        for item in a.history
    )

    return (
        f"{a.position} @ {a.company_name}\n"
        f"Status: {a.status}\n"
        f"Tanggal melamar: {a.applied_date or '-'}\n"
        f"Riwayat:\n{history}"
    )


def upcoming_text(u):
    current = now()
    items = []

    events = (
        Event.query
        .filter(
            Event.user_id == u.id,
            Event.starts_at >= current
        )
        .order_by(Event.starts_at)
        .limit(10)
        .all()
    )

    for event in events:
        items.append((
            event.starts_at,
            f"{fdt(event.starts_at)} - "
            f"{event.event_type}: {event.title}"
        ))

    deadlines = Application.query.filter(
        Application.user_id == u.id,
        Application.status == "Wishlist",
        Application.deadline >= current.date()
    ).all()

    for application in deadlines:
        items.append((
            datetime.combine(
                application.deadline,
                datetime.min.time()
            ),
            f"{application.deadline:%d %b %Y} - Deadline: "
            f"{application.position} @ {application.company_name}"
        ))

    for application in followup_apps(u):
        items.append((
            current,
            f"Sekarang - Follow-up: "
            f"{application.position} @ {application.company_name}"
        ))

    items.sort(key=lambda item: item[0])

    if not items:
        return "Tidak ada aktivitas mendatang."

    return "Aktivitas mendatang:\n" + "\n".join(
        f"- {description}"
        for _, description in items
    )


def followup_apps(u, days=7):
    cutoff = now() - timedelta(days=days)

    applications = Application.query.filter(
        Application.user_id == u.id,
        Application.status.in_(IN_PROGRESS)
    ).all()

    return [
        application
        for application in applications
        if last_change(application) <= cutoff
    ]


def followups_text(u):
    rows = followup_apps(u)

    if not rows:
        return "Tidak ada follow-up yang tertunda."

    return (
        "Perlu follow-up (tanpa kabar >7 hari):\n"
        + "\n".join(
            f"- {a.position} @ {a.company_name} [{a.status}]"
            for a in rows
        )
    )


def pending_items(u, limit=5):
    return (
        ChecklistItem.query
        .filter_by(user_id=u.id, done=False)
        .order_by(ChecklistItem.id)
        .limit(limit)
        .all()
    )


def prefs(u):
    preference = UserPreference.query.filter_by(
        user_id=u.id
    ).first()

    if not preference:
        preference = UserPreference(user_id=u.id)
        db.session.add(preference)
        db.session.commit()

    return preference


def reminders_text(u):
    preference = prefs(u).to_dict()

    events = (
        Event.query
        .filter(
            Event.user_id == u.id,
            Event.starts_at >= now()
        )
        .order_by(Event.starts_at)
        .limit(5)
        .all()
    )

    result = (
        f"Pengingat: H-{', H-'.join(map(str, preference['reminder_days']))} "
        f"| notifikasi "
        f"{'aktif' if preference['telegram_notifications'] else 'mati'}\n"
    )

    if events:
        result += "Jadwal berikutnya:\n"
        result += "\n".join(
            f"- {fdt(event.starts_at)} {event.title}"
            for event in events
        )
    else:
        result += "Belum ada jadwal."

    return result


def set_status(u, app_id, status):
    application = own(u, app_id)

    if not application or status not in STATUSES:
        return None

    if application.status != status:
        log_status(application, status)
        db.session.commit()

    return application


def add_note(u, app_id, text):
    application = own(u, app_id)

    if not application:
        return None

    existing_notes = application.notes or ""

    application.notes = (
        existing_notes
        + ("\n" if existing_notes else "")
        + f"[{now():%d %b %Y}] {text.strip()}"
    )

    db.session.commit()
    return application


def toggle_day(u, day):
    preference = prefs(u)

    days = set(preference.to_dict()["reminder_days"]) ^ {day}

    preference.reminder_days = ",".join(
        str(value)
        for value in sorted(days, reverse=True)
    )

    db.session.commit()


def toggle_notif(u):
    preference = prefs(u)
    preference.telegram_notifications = (
        not preference.telegram_notifications
    )
    db.session.commit()


def set_time(u, hhmm):
    try:
        datetime.strptime(hhmm, "%H:%M")
    except ValueError:
        return False

    prefs(u).briefing_time = hhmm
    db.session.commit()

    return True


def event_text(event, delta):
    when = "HARI INI" if delta == 0 else f"H-{delta}"

    application = (
        db.session.get(Application, event.application_id)
        if event.application_id
        else None
    )

    result = (
        f"Pengingat {when}: {event.event_type}\n"
        f"{event.title}\n"
    )

    if application:
        result += (
            f"Perusahaan: {application.company_name}\n"
            f"Posisi: {application.position}\n"
        )

    result += (
        f"Waktu: {fdt(event.starts_at)}\n"
        f"Lokasi/Link: {event.location or '-'}"
    )

    if application:
        notes = Note.query.filter_by(
            application_id=application.id,
            user_id=event.user_id
        ).all()

        if notes:
            result += "\n\nCatatan persiapan:\n"
            result += "\n".join(
                f"- {note.title} "
                f"({sum(1 for item in note.items if item.done)}/{len(note.items)})"
                for note in notes
            )

    return result


def briefing_text(u, current):
    active = Application.query.filter(
        Application.user_id == u.id,
        Application.status.in_(IN_PROGRESS)
    ).count()

    start = datetime.combine(
        current.date(),
        datetime.min.time()
    )

    end = start + timedelta(days=1)

    today_events = (
        Event.query
        .filter(
            Event.user_id == u.id,
            Event.starts_at >= start,
            Event.starts_at < end
        )
        .order_by(Event.starts_at)
        .all()
    )

    deadlines = Application.query.filter(
        Application.user_id == u.id,
        Application.status == "Wishlist",
        Application.deadline >= current.date(),
        Application.deadline <= current.date() + timedelta(days=3)
    ).all()

    pending = pending_items(u)

    return (
        f"Briefing pagi, {u.name}\n"
        f"Lamaran aktif: {active}\n\n"
        "Jadwal hari ini:\n"
        + (
            "\n".join(
                f"- {event.starts_at:%H:%M} {event.title}"
                for event in today_events
            )
            or "- tidak ada"
        )
        + "\n\nDeadline 3 hari ke depan:\n"
        + (
            "\n".join(
                f"- {a.deadline:%d %b} {a.position} @ {a.company_name}"
                for a in deadlines
            )
            or "- tidak ada"
        )
        + "\n\nPerlu follow-up:\n"
        + (
            "\n".join(
                f"- {a.position} @ {a.company_name}"
                for a in followup_apps(u)
            )
            or "- tidak ada"
        )
        + "\n\nChecklist belum selesai:\n"
        + (
            "\n".join(f"- {item.text}" for item in pending)
            or "- tidak ada"
        )
    )


def due_messages(current=None):
    """Mengambil pesan pengingat yang jatuh tempo dan belum dikirim."""

    current = current or now()
    today = current.date()
    output = []

    for account in TelegramAccount.query.all():
        user = db.session.get(User, account.user_id)

        if not user:
            continue

        preference = prefs(user)

        if not preference.telegram_notifications:
            continue

        reminder_days = preference.to_dict()["reminder_days"]

        def add(key, message):
            exists = NotificationLog.query.filter_by(
                user_id=user.id,
                ref=key
            ).first()

            if not exists:
                output.append({
                    "chat_id": account.telegram_user_id,
                    "user_id": user.id,
                    "key": key,
                    "text": message
                })

        events = Event.query.filter(
            Event.user_id == user.id,
            Event.starts_at >= current
        ).all()

        for event in events:
            delta = (event.starts_at.date() - today).days

            if delta in reminder_days:
                add(
                    f"ev:{event.id}:d{delta}",
                    event_text(event, delta)
                )

        applications = Application.query.filter(
            Application.user_id == user.id,
            Application.status == "Wishlist",
            Application.deadline.isnot(None)
        ).all()

        for application in applications:
            delta = (application.deadline - today).days

            if delta in reminder_days:
                label = "HARI INI" if delta == 0 else f"H-{delta}"

                add(
                    f"dl:{application.id}:d{delta}",
                    f"Deadline {label}: "
                    f"{application.position} @ {application.company_name} "
                    f"({application.deadline:%d %b %Y})"
                )

        for application in followup_apps(user):
            changed = last_change(application)

            add(
                f"fu:{application.id}:{changed:%Y%m%d}",
                f"Follow-up: {application.position} @ "
                f"{application.company_name} belum ada kabar sejak "
                f"{changed:%d %b %Y} (status {application.status})."
            )

        yesterday = today - timedelta(days=1)

        interviews = Event.query.filter(
            Event.user_id == user.id,
            Event.event_type == "Interview"
        ).all()

        for event in interviews:
            if event.starts_at.date() == yesterday:
                add(
                    f"fi:{event.id}",
                    f"Kemarin kamu interview: {event.title}. "
                    "Sudah kirim email terima kasih/follow-up?"
                )

        briefing_time = datetime.strptime(
            preference.briefing_time,
            "%H:%M"
        ).time()

        briefing_at = datetime.combine(today, briefing_time)

        if briefing_at <= current <= briefing_at + timedelta(hours=3):
            add(
                f"brief:{today}",
                briefing_text(user, current)
            )

    return output


def mark_sent(user_id, key):
    db.session.add(
        NotificationLog(
            user_id=user_id,
            kind=key.split(":")[0],
            ref=key
        )
    )

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()