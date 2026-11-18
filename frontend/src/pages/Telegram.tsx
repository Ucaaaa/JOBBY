import { useEffect, useState } from "react";
import { api } from "../api";
import { Win } from "../components/ui";

export default function Telegram() {
  const [connected, setConnected] = useState(false);
  const [code, setCode] = useState("");
  const [s, setS] = useState<any>(null);
  const [err, setErr] = useState("");
  const load = () => Promise.all([api("/telegram/status"), api("/telegram/settings")])
    .then(([a, b]) => { setConnected(a.connected); setS(b.settings); }).catch((e) => setErr(e.message));
  useEffect(() => { load(); }, []);
  const run = (fn: () => Promise<any>) => fn().then(load).catch((e) => setErr(e.message));
  const save = (patch: any) => run(() => api("/telegram/settings", { method: "PUT", body: patch }));
  const days = [3, 1, 0];
  return (
    <div className="space-y-4">
      <h1 className="text-3xl font-extrabold text-choc">Telegram</h1>
      {err && <p role="alert" className="rounded-lg bg-bubble/40 p-3 text-sm">{err}</p>}
      <Win title="jobby_assistant.exe">
        {connected ? (
          <div className="space-y-2"><p className="font-semibold">Akun Telegram terhubung.</p>
            <button className="btn-ghost" onClick={() => window.confirm("Putuskan koneksi Telegram?") && run(() => api("/telegram/disconnect", { method: "POST" }))}>Putuskan koneksi</button></div>
        ) : (
          <div className="space-y-3">
            <p className="text-sm">Buat kode, lalu kirim <code>/start KODE</code> ke bot JOBBY di Telegram. Kode berlaku 10 menit dan hanya bisa dipakai sekali.</p>
            <button className="btn-primary" onClick={() => api("/telegram/link-code", { method: "POST" }).then((d) => setCode(d.code)).catch((e) => setErr(e.message))}>Buat kode</button>
            {code && <p className="rounded-xl bg-butter/60 p-3 text-center font-head text-2xl font-extrabold tracking-widest">{code}</p>}
            {code && <button className="btn-ghost" onClick={load}>Cek status koneksi</button>}
          </div>)}
      </Win>
      {s && <Win title="pengaturan_notifikasi.exe"><div className="space-y-3 text-sm">
        <label className="flex items-center gap-2"><input type="checkbox" className="accent-sky" checked={s.telegram_notifications} onChange={(e) => save({ telegram_notifications: e.target.checked })} />Aktifkan notifikasi</label>
        <div className="flex flex-wrap gap-3">{days.map((d) => (
          <label key={d} className="flex items-center gap-1"><input type="checkbox" className="accent-sky" checked={s.reminder_days.includes(d)}
            onChange={(e) => save({ reminder_days: e.target.checked ? [...s.reminder_days, d] : s.reminder_days.filter((x: number) => x !== d) })} />H-{d}</label>))}</div>
        <label className="flex items-center gap-2">Jam briefing harian<input type="time" className="input w-auto" value={s.briefing_time} onChange={(e) => e.target.value && save({ briefing_time: e.target.value })} /></label>
      </div></Win>}
    </div>
  );
}
