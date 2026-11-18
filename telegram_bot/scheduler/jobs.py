import logging
from services import data

log = logging.getLogger("jobby.scheduler")


async def tick(context):
    """Dijalankan tiap menit: kirim pengingat/briefing yang jatuh tempo, catat agar tidak terkirim ulang."""
    with data.ctx():
        msgs = data.due_messages()
    for m in msgs:
        try:
            await context.bot.send_message(m["chat_id"], m["text"][:4000])
        except Exception as e:  # gagal kirim -> tidak dicatat, dicoba lagi di tick berikutnya
            log.warning("Gagal kirim %s: %s", m["key"], e); continue
        with data.ctx():
            data.mark_sent(m["user_id"], m["key"])
